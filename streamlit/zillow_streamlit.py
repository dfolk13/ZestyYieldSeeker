# Import standard libraries

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import seaborn as sns
import plotly.express as px
import snowflake.connector
import os

from dotenv import load_dotenv

load_dotenv()

# 1. Setup Page Config
st.set_page_config(page_title="Zillow Investment Yield", layout="wide")
st.title("🏠 Real Estate Investment Yield Dashboard")
st.markdown("Analyzing potential yields by matching 'For Sale' listings with 'Median Rent' proxies.")

# 2. Snowflake Connection
@st.cache_resource # Keeps connection alive
def get_snowflake_conn():
    return snowflake.connector.connect(
        user=os.getenv('SNOWFLAKE_USER'),
        password=os.getenv('SNOWFLAKE_PASSWORD'),
        account=os.getenv('SNOWFLAKE_ACCOUNT'),
        warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
        database=os.getenv('SNOWFLAKE_DATABASE'),
        schema='ANALYTICAL_DATA'
    )

conn = get_snowflake_conn()

# 3. Load Data
@st.cache_data(ttl=600) # Caches data for 10 mins so it's faster
def load_gold_data():
    query = "SELECT * FROM ZILLOW_YIELD_DB.ANALYTICAL_DATA.INVESTMENT_YIELD"
    return pd.read_sql(query, conn)

df = load_gold_data()

# 4. Sidebar Filters
st.sidebar.header("Filters")
selected_zip = st.sidebar.multiselect("Select Zip Codes", options=df['ZIPCODE'].unique(), default=df['ZIPCODE'].unique())
min_yield = st.sidebar.slider("Minimum Yield (%)", 0.0, float(df['CAP_RATE'].max()), 5.0)
selected_price = st.sidebar.slider("Minimum Purchase Price", 0.0, float(df['PURCHASE_PRICE'].max()), 50000.0)

filtered_df = df[(df['ZIPCODE'].isin(selected_zip)) & (df['CAP_RATE'] >= min_yield) & (df['RENT_PER_SQFT'] == df['RENT_PER_SQFT'].fillna(0))]  

# 5. Key Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Opportunities", len(filtered_df))
col2.metric("Avg Rent per Sq Ft", f"${filtered_df['RENT_PER_SQFT'].mean():.2f}")
col3.metric("Avg Yield", f"{filtered_df['CAP_RATE'].mean():.2f}%")
col4.metric("Highest Yield", f"{filtered_df['CAP_RATE'].max():.2f}%")

# 6.A Visualizations
st.subheader("Yield Analysis")
fig = px.scatter(
    filtered_df, 
    x="PURCHASE_PRICE", 
    y="EST_MONTHLY_RENT", 
    color="CAP_RATE",
    size="CAP_RATE",
    hover_name="ADDRESS",
    title="Price vs. Rent (Color-coded by Yield)"
)
st.plotly_chart(fig, use_container_width=True)

# 6.B Visualizations
st.subheader("Yield Analysis")
fig = px.scatter(
    filtered_df, 
    x="SQFT_AREA", 
    y="EST_MONTHLY_RENT", 
    color="RENT_PER_SQFT",
    size="RENT_PER_SQFT",
    hover_name="ADDRESS",
    title="Price vs. Rent (Color-coded by Yield)"
)
st.plotly_chart(fig, use_container_width=True)

# 7. Data Table
st.subheader("Top Investment Properties")
st.dataframe(filtered_df.sort_values(by='CAP_RATE', ascending=False), use_container_width=True)

# 8. Map Visualization
st.subheader("Investment Property Locations")
st.map(filtered_df[['LATITUDE', 'LONGITUDE']].dropna())