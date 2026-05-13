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
2. Rename and update the `.env.example` to `.env` file with Snowflake and RapidAPI credentials
3. Run `pip install -r requirements.txt`
4. Run `python fetch_zillow.py`
5. Run `python bulk_ingestion2.py`
6. Run `dbt snapshot && dbt run && dbt test`

### 1. Create Snowflake and RapidAPI accounts

#### Creating a free trial Snowflake account

**Go to below URL:**

https://signup.snowflake.com/

Fill all the required details. You must have an active email account to receive activation email.

- Enter in account information (see screenshots below)
- Fill out their questionaire
- Check email for account activation
- Credentials: Account → Account Details

#### Creating a free trial RapidAPI account

**Go to below URL:**

https://rapidapi.com/auth/sign-up

Fill all the required details. You must have an active email account to receive activation email.

- Create an account with the above link (see screenshots below)
- Verify the account activation email
- The API endpoint used is https://rapidapi.com/letsscrape/api/real-estate-zillow-com
- “Subscribe to Test” → Basic (125 requests per month) → Subscribe
- Find API Key under Console → Applications → default-application → [Authorization Keys](https://rapidapi.com/console/11930884/applications/8760224/authorizations)

#### Screenshots

**Snowflake**

Snowflake Account Creation
![Snowflake Account Creation](Assets/RapidAPI%20Account%20Creation.png)

Snowflake Cloud Provider
![Snowflake Cloud Provider](Assets/Snowflake%20Cloud%20Provider.png)

Snowflake Dashboard
![Snowflake Dashboard](Assets/Snowflake%20Dashboard.png)

Snowflake Account
![Snowflake Account](Assets/Snowflake%20Account.png)

Snowflake Account Details
![Snowflake Account Details](Assets/Snowflake%20Account%20Details.png)

**RapidAPI**

RapidAPI Account Creation
![RapidAPI Account Creation](Assets/RapidAPI%20Account%20Creation.png)

RapidAPI Key
![RapidAPI Key](Assets/RapidAPI%20Key.png)

RapidAPI Application
![RapidAPI Application](Assets/RapidAPI%20Applications.png)

RapidAPI App Key
![RapidAPI App Key](Assets/RapidAPI%20App%20Key.png)


### 2. Rename and update the `.env.example` to `.env` file with Snowflake and RapidAPI credentials

#### Rename the `.env.example` file
Rename this file like you would an other file. Simply remove the `.example` part and save the name as `.env`.

#### Update the `.env` file
In the .env file is where you will enter in the credentials from Snowflake and RapidAPI. Leave the variables (RAPIDAPI_KEY, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT, etc.) alone but replace the string (information between the quotation marks) with your own information. Please see [screenshots](https://github.com/dfolk13/ZestyYieldSeeker/blob/main/README.md#screenshots) for more details about what this information might look like.

### 3. Run `pip install -r requirements.txt`

### 4. Run `python fetch_zillow.py`

### 5. Run `python bulk_ingestion2.py`

### 6. Run `dbt snapshot && dbt run && dbt test`

## Automated Pipeline
GitHub Actions runs the full pipeline daily at 6am UTC.
