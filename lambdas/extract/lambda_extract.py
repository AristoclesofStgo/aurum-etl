import json
import boto3
import requests
import yfinance as yf
import os
from datetime import datetime, timezone

# ── Configuración ──────────────────────────────────────────
BUCKET          = os.environ["AWS_BUCKET_NAME"]
FX_API_KEY      = os.environ["EXCHANGERATE_API_KEY"]

s3 = boto3.client("s3")

def upload_to_s3(data, prefix):
    """Sube una lista de records a S3 como JSON."""
    timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d/%H%M%S")
    key = f"raw/{prefix}/{timestamp}.json"
    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=json.dumps(data, default=str),
        ContentType="application/json"
    )
    print(f"✅ Subido: {key} ({len(data)} records)")
    return key

# ── Extracción Crypto ───────────────────────────────────────
def extract_crypto():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": "bitcoin,ethereum,solana,cardano,ripple",
        "order": "market_cap_desc",
        "sparkline": False,
        "price_change_percentage": "24h"
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    records = []
    for coin in response.json():
        records.append({
            "ID":                   coin.get("id"),
            "SYMBOL":               coin.get("symbol", "").upper(),
            "NAME":                 coin.get("name"),
            "CURRENT_PRICE":        coin.get("current_price"),
            "HIGH_24H":             coin.get("high_24h"),
            "LOW_24H":              coin.get("low_24h"),
            "PRICE_CHANGE_24H":     coin.get("price_change_24h"),
            "PRICE_CHANGE_PCT_24H": coin.get("price_change_percentage_24h"),
            "MARKET_CAP":           coin.get("market_cap"),
            "MARKET_CAP_RANK":      coin.get("market_cap_rank"),
            "TOTAL_VOLUME_24H":     coin.get("total_volume"),
            "CIRCULATING_SUPPLY":   coin.get("circulating_supply"),
            "TOTAL_SUPPLY":         coin.get("total_supply"),
            "ATH":                  coin.get("ath"),
            "ATH_DATE":             coin.get("ath_date"),
            "ATL":                  coin.get("atl"),
            "ATL_DATE":             coin.get("atl_date"),
            "LAST_UPDATED":         coin.get("last_updated"),
            "INGESTED_AT":          datetime.now(timezone.utc).isoformat()
        })

    return upload_to_s3(records, "crypto")

# ── Extracción Forex ────────────────────────────────────────
def extract_forex():
    pairs = ["EUR", "GBP", "JPY", "CAD", "CHF", "MXN", "BRL"]
    url = f"https://v6.exchangerate-api.com/v6/{FX_API_KEY}/latest/USD"
    response = requests.get(url)
    response.raise_for_status()
    raw = response.json()

    rates = raw.get("conversion_rates", {})
    ingested_at = datetime.now(timezone.utc).isoformat()

    records = []
    for currency in pairs:
        rate = rates.get(currency)
        if rate:
            records.append({
                "BASE_CURRENCY":        "USD",
                "QUOTE_CURRENCY":       currency,
                "PAIR":                 f"USD/{currency}",
                "RATE":                 rate,
                "BID":                  None,
                "ASK":                  None,
                "OPEN_PRICE":           None,
                "HIGH_24H":             None,
                "LOW_24H":              None,
                "PRICE_CHANGE_24H":     None,
                "PRICE_CHANGE_PCT_24H": None,
                "HIGH_7D":              None,
                "LOW_7D":               None,
                "HIGH_30D":             None,
                "LOW_30D":              None,
                "LAST_UPDATED":         raw.get("time_last_update_utc"),
                "INGESTED_AT":          ingested_at
            })

    return upload_to_s3(records, "forex")

# ── Extracción Metales y Petróleo ───────────────────────────
def extract_commodities():
    symbols = {
        "GC=F": {"name": "Gold",           "symbol": "XAU",   "unit": "troy oz", "type": "metal"},
        "SI=F": {"name": "Silver",          "symbol": "XAG",   "unit": "troy oz", "type": "metal"},
        "PL=F": {"name": "Platinum",        "symbol": "XPT",   "unit": "troy oz", "type": "metal"},
        "PA=F": {"name": "Palladium",       "symbol": "XPD",   "unit": "troy oz", "type": "metal"},
        "CL=F": {"name": "WTI Crude Oil",   "symbol": "WTI",   "unit": "barrel",  "type": "oil"},
        "BZ=F": {"name": "Brent Crude Oil", "symbol": "BRENT", "unit": "barrel",  "type": "oil"},
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/",
        "Origin": "https://finance.yahoo.com"
    }

    metals_records = []
    oil_records    = []
    ingested_at    = datetime.now(timezone.utc).isoformat()

    for ticker_symbol, meta in symbols.items():
        try:
            # Obtiene precio actual
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_symbol}"
            params = {
                "interval": "1d",
                "range":    "7d"
            }
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            result = data["chart"]["result"][0]
            meta_info = result["meta"]
            indicators = result["indicators"]["quote"][0]
            timestamps = result["timestamp"]

            closes  = indicators.get("close",  [])
            opens   = indicators.get("open",   [])
            highs   = indicators.get("high",   [])
            lows    = indicators.get("low",    [])

            # Filtra None
            closes_clean = [c for c in closes if c is not None]
            highs_clean  = [h for h in highs  if h is not None]
            lows_clean   = [l for l in lows   if l is not None]

            if not closes_clean:
                print(f"⚠️ Sin datos para {ticker_symbol}")
                continue

            last_price  = closes_clean[-1]
            open_price  = opens[0] if opens[0] is not None else closes_clean[0]
            high_7d     = max(highs_clean)
            low_7d      = min(lows_clean)
            high_24h    = highs_clean[-1]
            low_24h     = lows_clean[-1]

            price_change_24h     = round(last_price - open_price, 4)
            price_change_pct_24h = round((price_change_24h / open_price) * 100, 4) if open_price else None

            print(f"✅ {ticker_symbol}: ${last_price}")

            record = {
                "SYMBOL":               meta["symbol"],
                "NAME":                 meta["name"],
                "UNIT":                 meta["unit"],
                "CURRENCY":             "USD",
                "PRICE":                last_price,
                "OPEN_PRICE":           open_price,
                "HIGH_24H":             high_24h,
                "LOW_24H":              low_24h,
                "PRICE_CHANGE_24H":     price_change_24h,
                "PRICE_CHANGE_PCT_24H": price_change_pct_24h,
                "HIGH_7D":              high_7d,
                "LOW_7D":               low_7d,
                "HIGH_30D":             None,
                "LOW_30D":              None,
                "HIGH_52W":             None,
                "LOW_52W":              None,
                "LAST_UPDATED":         datetime.now(timezone.utc).isoformat(),
                "INGESTED_AT":          ingested_at
            }

            if meta["type"] == "metal":
                metals_records.append(record)
            else:
                oil_records.append(record)

        except Exception as e:
            print(f"❌ Error extrayendo {ticker_symbol}: {e}")

    results = {}
    if metals_records:
        results["metals"] = upload_to_s3(metals_records, "metals")
    if oil_records:
        results["oil"] = upload_to_s3(oil_records, "oil")

    return results

# ── Handler principal ───────────────────────────────────────
def lambda_handler(event, context):
    results = {}
    errors  = []

    for name, fn in [("crypto",      extract_crypto),
                     ("forex",       extract_forex),
                     ("commodities", extract_commodities)]:
        try:
            results[name] = fn()
        except Exception as e:
            errors.append(f"{name}: {str(e)}")
            print(f"❌ Error en {name}: {e}")

    return {
        "statusCode": 200 if not errors else 207,
        "uploaded":   results,
        "errors":     errors
    }