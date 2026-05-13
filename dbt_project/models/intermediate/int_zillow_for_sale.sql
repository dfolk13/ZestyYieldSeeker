with base as (
    select * from {{ ref('stg_zillow_for_sale') }}
)

select
    listing:zpid::string as zpid,
    listing:address::string as address,
    listing:addressZipcode::string as zipcode,
    COALESCE(
        listing:area::int,
        listing:hdpData.homeInfo.livingArea::int
    ) as sqft_area,
    COALESCE(
        listing:unformattedPrice::float,
        TRY_CAST(REGEXP_REPLACE(listing:units[0].price::string, '[^0-9.]', '') AS FLOAT)
    ) as price,
    COALESCE(
        listing:beds::int,
        listing:factsAndFeatures.beds::int,
        listing:units[0].beds::int
    ) as beds,
    COALESCE(
        listing:baths::float,
        listing:factsAndFeatures.baths::float,
        listing:units[0].bathrooms::float
    ) as baths,
    listing:statusType::string as status_type,
    listing:latLong.latitude::float as latitude,
    listing:latLong.longitude::float as longitude,
    round(
        COALESCE(listing:unformattedPrice::float,
            TRY_CAST(REGEXP_REPLACE(listing:units[0].price::string, '[^0-9.]', '') AS FLOAT))
        / nullif(COALESCE(listing:beds::int,
            listing:factsAndFeatures.beds::int,
            listing:units[0].beds::int), 0)
    , 2) as price_per_bedroom,
    dbt_valid_from,
    dbt_updated_at
from base
where zipcode is not null
