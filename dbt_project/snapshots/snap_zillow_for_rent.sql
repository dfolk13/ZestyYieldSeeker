{% snapshot snap_zillow_for_rent %}
{{
  config(
    target_schema='SNAPSHOTS',
    unique_key='zpid',
    strategy='check',
    check_cols=['price'],
  )
}}
with deduped as (
    select
        f.value:zpid::string as zpid,
        f.value:baseRent::float as price,
        f.value as listing,
        s.filename,
        s.ingested_at,
        row_number() over (
            partition by f.value:zpid::string
            order by s.ingested_at desc
        ) as row_num
    from {{ source('raw_zillow', 'RAW_LISTINGS_FOR_RENT') }} s,
    lateral flatten(input => s.raw_data:data.listings) f
)
select zpid, price, listing, filename, ingested_at
from deduped
where row_num = 1
{% endsnapshot %}