# ZestyYieldSeeker

Data ETL pipeline focusing on helping an investor find properties where the rental income exceeds the mortgage/maintenance costs

## Architecture
[diagram or description of the pipeline]

## Stack
- **Ingestion**: Python, Snowflake
- **Transformation**: dbt (Snowflake)
- **Orchestration**: GitHub Actions
- **Source**: Zillow via RapidAPI

## Pipeline
fetch_zillow.py → RAW_LISTINGS → dbt snapshot → dbt run → investment_yield

## Models
| Model | Layer | Description |
|---|---|---|
| stg_zillow_for_sale | Staging | Deduped for-sale listings from snapshot |
| stg_zillow_for_rent | Staging | Deduped for-rent listings from snapshot |
| int_zillow_for_sale | Intermediate | Cleaned and structured sale listings |
| int_zillow_for_rent | Intermediate | Cleaned and structured rent listings |
| investment_yield | Mart | Cap rates, GRM, price per sqft per listing |

## Key Metrics Produced
- Cap rate per listing
- Gross Rent Multiplier
- Price per bedroom
- Rent per sqft
- Price-to-rent ratio by zipcode

## Setup
1. Clone the repo
2. Add a `.env` file with Snowflake and RapidAPI credentials
3. Run `pip install -r requirements.txt`
4. Run `python fetch_zillow.py`
5. Run `python bulk_ingestion2.py`
6. Run `dbt snapshot && dbt run && dbt test`

## Automated Pipeline
GitHub Actions runs the full pipeline daily at 6am UTC.
