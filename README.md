# ZestyYieldSeeker

A end-to-end real estate investment analytics pipeline that identifies high-yield real estate investments by joining sale listings with rental market proxies.

## Architecture
`Zillow API -> Python -> Snowflake (Bronze) -> dbt (Silver/Gold)`

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
1. Create Snowflake and RapidAPI accounts
2. Add a `.env` file with Snowflake and RapidAPI credentials
3. Run `pip install -r requirements.txt`
4. Run `python fetch_zillow.py`
5. Run `python bulk_ingestion2.py`
6. Run `dbt snapshot && dbt run && dbt test`

## Automated Pipeline
GitHub Actions runs the full pipeline daily at 6am UTC.

### 1. Create Snowflake and RapidAPI accounts

#### Creating a free trial Snowflake account

**Go to below URL:**

https://signup.snowflake.com/

Fill all the required details. You must have an active email account to receive activation email.

- Enter in account information (see screenshots)
- Fill out their questionaire
- Check email for account activation
- Password should include “Your password must be 14 - 256 characters and contain at least 1 number(s), 0 special character(s), 1 uppercase and 1 lowercase letter(s).” (HINT: best to avoid special characters like **`@, #, $, : , /`** as it could break the connection)
- Credentials: Account → Account Details

#### Creating a free trial RapidAPI account

**Go to below URL:**

https://rapidapi.com/auth/sign-up

Fill all the required details. You must have an active email account to receive activation email.

- Create an account with the above link
- Verify the account activation email
- The API endpoint used is https://rapidapi.com/letsscrape/api/real-estate-zillow-com
- “Subscribe to Test” → Basic (125 requests per month) → Subscribe
- Find API Key under Console → Applications → default-application → [Authorization Keys](https://rapidapi.com/console/11930884/applications/8760224/authorizations)

### 2. Add a `.env` file with Snowflake and RapidAPI credentials

### 3. Run `pip install -r requirements.txt`

### 4. Run `python fetch_zillow.py`

### 5. Run `python bulk_ingestion2.py`

### 6. Run `dbt snapshot && dbt run && dbt test`
