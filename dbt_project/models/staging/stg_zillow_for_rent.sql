with source as (
    select * from {{ ref('snap_zillow_for_rent') }}
    where dbt_valid_to is null
),

deduped as (
    select *,
        row_number() over (
            partition by zpid
            order by dbt_updated_at desc
        ) as row_num
    from source
)

select * from deduped where row_num = 1