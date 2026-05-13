with for_sale as (
    select * from {{ ref('int_zillow_for_sale') }}
),

for_rent as (
    select * from {{ ref('int_zillow_for_rent') }}
),

rent_proxies as (
    select
        zipcode,
        beds,
        median(price) as median_rent
    from for_rent
    group by 1, 2
)

select
    s.zpid,
    s.address,
    s.zipcode,
    s.price as purchase_price,
    s.beds,
    s.baths,
    s.sqft_area,
    s.latitude,
    s.longitude,
    s.price_per_bedroom,
    r.median_rent as est_monthly_rent,
    (r.median_rent * 12) as est_annual_rent,
    round(((r.median_rent * 12) / nullif(s.price, 0)) * 100, 2) as cap_rate,
    round(r.median_rent / nullif(s.sqft_area, 0), 2) as rent_per_sqft
from for_sale s
join rent_proxies r
    on s.zipcode = r.zipcode and s.beds = r.beds
