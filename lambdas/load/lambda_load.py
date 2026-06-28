import json
import boto3
import snowflake.connector
import os
from datetime import datetime, timezone

# ── Configuración ──────────────────────────────────────────
BUCKET      = os.environ["AWS_BUCKET_NAME"]
SF_ACCOUNT  = os.environ["SF_ACCOUNT"]
SF_USER     = os.environ["SF_USER"]
SF_PASSWORD = os.environ["SF_PASSWORD"]
SF_DATABASE = os.environ["SF_DATABASE"]
SF_SCHEMA   = os.environ["SF_SCHEMA"]
SF_WH       = os.environ["SF_WAREHOUSE"]

s3 = boto3.client("s3")

# ── Conexión Snowflake ─────────────────────────────────────
def get_snowflake_conn():
    return snowflake.connector.connect(
        account   = SF_ACCOUNT,
        user      = SF_USER,
        password  = SF_PASSWORD,
        database  = SF_DATABASE,
        schema    = SF_SCHEMA,
        warehouse = SF_WH
    )

# ── Leer archivo de S3 ─────────────────────────────────────
def read_s3_file(key):
    response = s3.get_object(Bucket=BUCKET, Key=key)
    return json.loads(response["Body"].read())

# ── Carga Crypto ───────────────────────────────────────────
def load_crypto(records, cursor):
    sql = """
        INSERT INTO CRYPTO_PRICES (
            ID, SYMBOL, NAME, CURRENT_PRICE, HIGH_24H, LOW_24H,
            PRICE_CHANGE_24H, PRICE_CHANGE_PCT_24H, MARKET_CAP,
            MARKET_CAP_RANK, TOTAL_VOLUME_24H, CIRCULATING_SUPPLY,
            TOTAL_SUPPLY, ATH, ATH_DATE, ATL, ATL_DATE,
            LAST_UPDATED, INGESTED_AT
        ) VALUES (
            %(ID)s, %(SYMBOL)s, %(NAME)s, %(CURRENT_PRICE)s,
            %(HIGH_24H)s, %(LOW_24H)s, %(PRICE_CHANGE_24H)s,
            %(PRICE_CHANGE_PCT_24H)s, %(MARKET_CAP)s, %(MARKET_CAP_RANK)s,
            %(TOTAL_VOLUME_24H)s, %(CIRCULATING_SUPPLY)s, %(TOTAL_SUPPLY)s,
            %(ATH)s, %(ATH_DATE)s, %(ATL)s, %(ATL_DATE)s,
            %(LAST_UPDATED)s, %(INGESTED_AT)s
        )
    """
    cursor.executemany(sql, records)
    print(f"✅ Crypto: {len(records)} records insertados")

# ── Carga Forex ────────────────────────────────────────────
def load_forex(records, cursor):
    sql = """
        INSERT INTO FX_PRICES (
            BASE_CURRENCY, QUOTE_CURRENCY, PAIR, RATE, BID, ASK,
            OPEN_PRICE, HIGH_24H, LOW_24H, PRICE_CHANGE_24H,
            PRICE_CHANGE_PCT_24H, HIGH_7D, LOW_7D, HIGH_30D, LOW_30D,
            LAST_UPDATED, INGESTED_AT
        ) VALUES (
            %(BASE_CURRENCY)s, %(QUOTE_CURRENCY)s, %(PAIR)s, %(RATE)s,
            %(BID)s, %(ASK)s, %(OPEN_PRICE)s, %(HIGH_24H)s, %(LOW_24H)s,
            %(PRICE_CHANGE_24H)s, %(PRICE_CHANGE_PCT_24H)s, %(HIGH_7D)s,
            %(LOW_7D)s, %(HIGH_30D)s, %(LOW_30D)s,
            %(LAST_UPDATED)s, %(INGESTED_AT)s
        )
    """
    cursor.executemany(sql, records)
    print(f"✅ Forex: {len(records)} records insertados")

# ── Carga Metales ──────────────────────────────────────────
def load_metals(records, cursor):
    sql = """
        INSERT INTO METALS_PRICES (
            SYMBOL, NAME, UNIT, CURRENCY, PRICE, OPEN_PRICE,
            HIGH_24H, LOW_24H, PRICE_CHANGE_24H, PRICE_CHANGE_PCT_24H,
            HIGH_7D, LOW_7D, HIGH_30D, LOW_30D, HIGH_52W, LOW_52W,
            LAST_UPDATED, INGESTED_AT
        ) VALUES (
            %(SYMBOL)s, %(NAME)s, %(UNIT)s, %(CURRENCY)s, %(PRICE)s,
            %(OPEN_PRICE)s, %(HIGH_24H)s, %(LOW_24H)s, %(PRICE_CHANGE_24H)s,
            %(PRICE_CHANGE_PCT_24H)s, %(HIGH_7D)s, %(LOW_7D)s,
            %(HIGH_30D)s, %(LOW_30D)s, %(HIGH_52W)s, %(LOW_52W)s,
            %(LAST_UPDATED)s, %(INGESTED_AT)s
        )
    """
    cursor.executemany(sql, records)
    print(f"✅ Metales: {len(records)} records insertados")

# ── Carga Petróleo ─────────────────────────────────────────
def load_oil(records, cursor):
    sql = """
        INSERT INTO OIL_PRICES (
            SYMBOL, NAME, UNIT, CURRENCY, PRICE, OPEN_PRICE,
            HIGH_24H, LOW_24H, PRICE_CHANGE_24H, PRICE_CHANGE_PCT_24H,
            HIGH_7D, LOW_7D, HIGH_30D, LOW_30D,
            LAST_UPDATED, INGESTED_AT
        ) VALUES (
            %(SYMBOL)s, %(NAME)s, %(UNIT)s, %(CURRENCY)s, %(PRICE)s,
            %(OPEN_PRICE)s, %(HIGH_24H)s, %(LOW_24H)s, %(PRICE_CHANGE_24H)s,
            %(PRICE_CHANGE_PCT_24H)s, %(HIGH_7D)s, %(LOW_7D)s,
            %(HIGH_30D)s, %(LOW_30D)s,
            %(LAST_UPDATED)s, %(INGESTED_AT)s
        )
    """
    cursor.executemany(sql, records)
    print(f"✅ Petróleo: {len(records)} records insertados")

# ── Detecta qué tabla usar según el prefix del archivo ─────
def get_prefix(key):
    if "/crypto/"  in key: return "crypto"
    if "/forex/"   in key: return "forex"
    if "/metals/"  in key: return "metals"
    if "/oil/"     in key: return "oil"
    return None

# ── Handler principal ───────────────────────────────────────
def lambda_handler(event, context):
    conn   = get_snowflake_conn()
    cursor = conn.cursor()
    errors = []
    loaded = {}

    try:
        # Lista todos los archivos en raw/
        paginator = s3.get_paginator("list_objects_v2")
        pages     = paginator.paginate(Bucket=BUCKET, Prefix="raw/")

        for page in pages:
            for obj in page.get("Contents", []):
                key    = obj["Key"]
                prefix = get_prefix(key)

                if not prefix:
                    continue

                try:
                    records = read_s3_file(key)
                    print(f"📂 Cargando {key} ({len(records)} records)...")

                    if prefix == "crypto":
                        load_crypto(records, cursor)
                    elif prefix == "forex":
                        load_forex(records, cursor)
                    elif prefix == "metals":
                        load_metals(records, cursor)
                    elif prefix == "oil":
                        load_oil(records, cursor)

                    # Mueve el archivo a processed/ para no cargarlo dos veces
                    new_key = key.replace("raw/", "processed/")
                    s3.copy_object(
                        Bucket     = BUCKET,
                        CopySource = {"Bucket": BUCKET, "Key": key},
                        Key        = new_key
                    )
                    s3.delete_object(Bucket=BUCKET, Key=key)
                    print(f"📦 Movido a processed/: {new_key}")

                    loaded[key] = len(records)

                except Exception as e:
                    errors.append(f"{key}: {str(e)}")
                    print(f"❌ Error en {key}: {e}")

        conn.commit()

    finally:
        cursor.close()
        conn.close()

    return {
        "statusCode": 200 if not errors else 207,
        "loaded":     loaded,
        "errors":     errors
    }