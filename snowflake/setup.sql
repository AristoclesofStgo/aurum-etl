
--Create table for crypto data, verify the table structure with the data from the API
CREATE TABLE IF NOT EXISTS CRYPTO_PRICES (
    ID                      VARCHAR(100),
    SYMBOL                  VARCHAR(20),
    NAME                    VARCHAR(100),
    CURRENT_PRICE           FLOAT,
    HIGH_24H                FLOAT,
    LOW_24H                 FLOAT,
    PRICE_CHANGE_24H        FLOAT,
    PRICE_CHANGE_PCT_24H    FLOAT,
    MARKET_CAP              FLOAT,
    MARKET_CAP_RANK         INT,
    TOTAL_VOLUME_24H        FLOAT,
    CIRCULATING_SUPPLY      FLOAT,
    TOTAL_SUPPLY            FLOAT,
    ATH                     FLOAT,
    ATH_DATE                TIMESTAMP_NTZ,
    ATL                     FLOAT,
    ATL_DATE                TIMESTAMP_NTZ,
    LAST_UPDATED            TIMESTAMP_NTZ,
    INGESTED_AT             TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS FX_PRICES (
    BASE_CURRENCY           VARCHAR(10),
    QUOTE_CURRENCY          VARCHAR(10),
    PAIR                    VARCHAR(20),
    RATE                    FLOAT,
    BID                     FLOAT,
    ASK                     FLOAT,
    OPEN_PRICE              FLOAT,
    HIGH_24H                FLOAT,
    LOW_24H                 FLOAT,
    PRICE_CHANGE_24H        FLOAT,
    PRICE_CHANGE_PCT_24H    FLOAT,
    HIGH_7D                 FLOAT,
    LOW_7D                  FLOAT,
    HIGH_30D                FLOAT,
    LOW_30D                 FLOAT,
    LAST_UPDATED            TIMESTAMP_NTZ,
    INGESTED_AT             TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS METALS_PRICES (
    SYMBOL                  VARCHAR(10),
    NAME                    VARCHAR(50),
    UNIT                    VARCHAR(20),
    CURRENCY                VARCHAR(10),
    PRICE                   FLOAT,
    OPEN_PRICE              FLOAT,
    HIGH_24H                FLOAT,
    LOW_24H                 FLOAT,
    PRICE_CHANGE_24H        FLOAT,
    PRICE_CHANGE_PCT_24H    FLOAT,
    HIGH_7D                 FLOAT,
    LOW_7D                  FLOAT,
    HIGH_30D                FLOAT,
    LOW_30D                 FLOAT,
    HIGH_52W                FLOAT,
    LOW_52W                 FLOAT,
    LAST_UPDATED            TIMESTAMP_NTZ,
    INGESTED_AT             TIMESTAMP_NTZ
);

CREATE TABLE IF NOT EXISTS OIL_PRICES (
    SYMBOL                  VARCHAR(10),
    NAME                    VARCHAR(50),
    UNIT                    VARCHAR(20),
    CURRENCY                VARCHAR(10),
    PRICE                   FLOAT,
    OPEN_PRICE              FLOAT,
    HIGH_24H                FLOAT,
    LOW_24H                 FLOAT,
    PRICE_CHANGE_24H        FLOAT,
    PRICE_CHANGE_PCT_24H    FLOAT,
    HIGH_7D                 FLOAT,
    LOW_7D                  FLOAT,
    HIGH_30D                FLOAT,
    LOW_30D                 FLOAT,
    LAST_UPDATED            TIMESTAMP_NTZ,
    INGESTED_AT             TIMESTAMP_NTZ
);