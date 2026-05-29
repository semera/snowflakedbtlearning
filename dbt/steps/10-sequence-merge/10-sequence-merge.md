# Step 10 - Sequence Merge

## Goal

Make the incremental merge respect `sequence`.

A newly ingested event should update `stg_person` only when it has a higher `sequence` than the current row for the same `person_id`.

## Knowledge: ingest time and sequence

`ingest_timestamp` and `sequence` solve different problems.

- `ingest_timestamp` decides which raw rows dbt should process in this run.
- `sequence` decides which event is the latest business state.
- A new raw row can arrive late with an older `sequence`.
- Late older events should be processed, but they should not overwrite current state.

## Files

Update `models/mystaging/stg_person.sql`:

- keep the incremental filter by `_last_ingest_timestamp`
- keep `select distinct` for the new raw batch
- compare new rows with existing rows from `{{ this }}`
- choose the highest `sequence` per `person_id`

Full file after the change:

```sql
{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='person_id'
    )
}}

with raw_rows as (

    select
        payload,
        ingest_timestamp
    from {{ source('raw', 'raw_person') }}

    {% if is_incremental() %}
        where ingest_timestamp > (
            select coalesce(max(_last_ingest_timestamp), '1900-01-01'::timestamp_ltz)
            from {{ this }}
        )
    {% endif %}

),

distinct_events as (

    select distinct
        event.value:metadata:event_id::string as event_id,
        event.value:metadata:type::string as event_type,
        event.value:metadata:time::timestamp_ntz as event_time,
        event.value:metadata:sequence::integer as sequence,
        event.value:metadata:mutation::string as mutation,

        event.value:data:person_id::string as person_id,
        event.value:data:pin::string as pin,
        event.value:data:first_name::string as first_name,
        event.value:data:surname::string as surname,
        event.value:data:date_of_birth::date as date_of_birth,

        ingest_timestamp
    from raw_rows,
    lateral flatten(input => payload:events) event

),

latest_new_person_events as (

    select
        event_id,
        event_type,
        event_time,
        sequence,
        mutation,
        person_id,
        pin,
        first_name,
        surname,
        date_of_birth,
        ingest_timestamp as _last_ingest_timestamp
    from distinct_events
    qualify row_number() over (
        partition by person_id
        order by sequence desc, ingest_timestamp desc
    ) = 1

),

candidate_current_state as (

    select *
    from latest_new_person_events

    {% if is_incremental() %}
        union all

        select
            event_id,
            event_type,
            event_time,
            sequence,
            mutation,
            person_id,
            pin,
            first_name,
            surname,
            date_of_birth,
            _last_ingest_timestamp
        from {{ this }}
        where person_id in (
            select person_id
            from latest_new_person_events
        )
    {% endif %}

),

final as (

    select *
    from candidate_current_state
    qualify row_number() over (
        partition by person_id
        order by sequence desc, _last_ingest_timestamp desc
    ) = 1

)

select
    event_id,
    event_type,
    event_time,
    sequence,
    mutation,
    person_id,
    pin,
    first_name,
    surname,
    date_of_birth,
    _last_ingest_timestamp
from final
```

No YAML change is needed in this step.

## Test

First insert a newer event for the existing person:

```sql
insert into raw.raw_person (payload)
select parse_json($$
{
  "events": [
    {
      "metadata": {
        "event_id": "5a4f02c2-7f87-4561-8473-b29a5dd0f91d",
        "type": "person.v1",
        "time": "2026-05-23T12:50:56Z",
        "sequence": 1020,
        "mutation": "update"
      },
      "data": {
        "person_id": "db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1",
        "pin": "1234567890",
        "first_name": "John",
        "surname": "Newest",
        "date_of_birth": "1980-01-15"
      }
    }
  ]
}
$$);
```

Run:

```powershell
dbt run --select stg_person
```

Check the current row:

```sql
select
    person_id,
    sequence,
    surname
from staging.stg_person
where person_id = 'db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1';
```

Expected result:

```text
sequence = 1020
surname = Newest
```

Now insert a late-arriving older event:

```sql
insert into raw.raw_person (payload)
select parse_json($$
{
  "events": [
    {
      "metadata": {
        "event_id": "7de94c4c-1f9d-4b7d-9062-1989829fe2fb",
        "type": "person.v1",
        "time": "2026-05-23T12:45:56Z",
        "sequence": 1005,
        "mutation": "update"
      },
      "data": {
        "person_id": "db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1",
        "pin": "1234567890",
        "first_name": "John",
        "surname": "Late",
        "date_of_birth": "1980-01-15"
      }
    }
  ]
}
$$);
```

Run again:

```powershell
dbt run --select stg_person
```

Check the current row again:

```sql
select
    person_id,
    sequence,
    surname
from staging.stg_person
where person_id = 'db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1';
```

Expected result stays:

```text
sequence = 1020
surname = Newest
```

The late event was ingested and processed, but it did not replace the current state.

## Run Tests

Run the normal data tests:

```powershell
dbt test --select stg_person
```

## Navigation

- [Back to README](../../README.md)
- [Previous step: 09 Incremental](../09-incremental/09-incremental.md)
