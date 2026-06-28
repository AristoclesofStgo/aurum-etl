# Aurum ETL Pipeline

Pipeline de datos automatizado que extrae precios de criptomonedas, 
divisas, metales preciosos y petróleo en tiempo real.

## Arquitectura
EventBridge (cada 6h) → Lambda Extract → S3 → Lambda Load → Snowflake → Tableau

## Fuentes de datos
- **Crypto**: CoinGecko API (BTC, ETH, SOL, ADA, XRP)
- **Forex**: ExchangeRate API (EUR, GBP, JPY, CAD, CHF, MXN, BRL)
- **Metales**: Yahoo Finance (XAU, XAG, XPT, XPD)
- **Petróleo**: Yahoo Finance (WTI, Brent)

## Stack tecnológico
- **AWS Lambda** — extracción y carga serverless
- **AWS S3** — staging de datos raw
- **AWS EventBridge** — orquestación y scheduling
- **Snowflake** — data warehouse
- **Tableau** — visualización

## Estructura
- `lambdas/extract/` — extracción de APIs a S3
- `lambdas/load/` — carga de S3 a Snowflake
- `snowflake/` — DDL de tablas y configuración
- `infra/` — configuración de EventBridge

## Setup
1. Clona el repositorio
2. Copia `.env.example` a `.env` y completa las variables
3. Crea el bucket S3 y ejecuta `snowflake/setup.sql`
4. Despliega las Lambdas a AWS
5. Configura el trigger de S3 y EventBridge