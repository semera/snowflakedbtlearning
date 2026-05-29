# Step 09 - Incremental

## Goal

Make `stg_person` an incremental table.

We want to avoid:

- reading all raw rows on every run
- creating a view that recalculates current state from a huge event history

The result is still current person state:

- one row per `person_id`
- latest row selected by highest `sequence`

## Knowledge: incremental current state

An incremental model stores its result in a table.

- First run reads all raw rows.
- Next runs read only new raw rows.
- dbt merges the new result into the existing table.
- `--full-refresh` rebuilds the table from scratch.

For current state, the merge key is `person_id`.

- New raw rows are flattened and deduplicated.
- Only changed `person_id` values are recalculated.
- Existing rows for unchanged people stay in the incremental table.

## Design

Use one materialized model:

```text
raw.raw_person
  -> stg_person
```

`stg_person` becomes an incremental table.

- It reads only raw rows with a new `ingest_timestamp`.
- It creates distinct event rows from that small raw batch.
- It finds the latest new event per `person_id`.
- It merges the result back into `stg_person` by `person_id`.

## Files

Update `models/mystaging/stg_person.sql`:

- change materialization to `incremental`
- use `person_id` as `unique_key`
- filter raw rows by `_last_ingest_timestamp` on incremental runs
- keep `_last_ingest_timestamp` as a technical watermark column
- use `select distinct` for exact duplicate raw events

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
from latest_new_person_events
```

Update `models/mystaging/stg_person.yml`:

- keep current-state tests
- add the technical watermark column

Full file after the change:

```yaml
version: 2

models:
  - name: stg_person
    description: Incremental current person state built from the latest distinct `person.v1` event per `person_id`.
    columns:
      - name: event_id
        description: Event identifier from the latest event for this person.
        tests:
          - not_null
          - unique

      - name: event_type
        description: Event type from `metadata.type`.
        tests:
          - not_null
          - accepted_values:
              values: ['person.v1']

      - name: sequence
        description: Event order/version value from `metadata.sequence`.
        tests:
          - not_null
          - unique

      - name: mutation
        description: Event mutation from `metadata.mutation`.
        tests:
          - not_null
          - accepted_values:
              values: ['insert', 'update', 'delete']

      - name: person_id
        description: Stable person identifier from `data.person_id`.
        tests:
          - not_null
          - unique

      - name: _last_ingest_timestamp
        description: Technical watermark used to read only new raw rows on incremental runs.
        tests:
          - not_null
```

## Run

First run:

```powershell
dbt run --select stg_person
```

This reads all raw rows and creates the incremental table.

Next run:

```powershell
dbt run --select stg_person
```

This reads only raw rows with `ingest_timestamp` greater than the maximum `_last_ingest_timestamp` already stored in `stg_person`.

## Check Materialized Behavior

`stg_person` is now a table.

After inserting a new raw event, check `stg_person` before running dbt again:

```sql
select
    person_id,
    sequence,
    surname,
    _last_ingest_timestamp
from staging.stg_person;
```

The row should not change yet.

Then run:

```powershell
dbt run --select stg_person
```

Check the table again:

```sql
select
    person_id,
    sequence,
    surname,
    _last_ingest_timestamp
from staging.stg_person;
```

Now the new raw event should be reflected in `stg_person`.

Run tests:

```powershell
dbt test --select stg_person
```

Full rebuild:

```powershell
dbt run --select stg_person --full-refresh
```

Use full refresh when:

- you changed the incremental model logic
- the target table got corrupted
- you want to rebuild from all raw rows

## Expected Result

`stg_person` is now a table, not a view.

- It does not recalculate from all raw rows on every query.
- It does not scan the full raw table on every incremental run.
- It keeps one row per `person_id`.
- It merges people affected by new raw events.

## Warning

This is still a learning version.

- `_last_ingest_timestamp` is a technical column.
- `ingest_timestamp > max(_last_ingest_timestamp)` is simple.
- If the target table is empty, the watermark starts at `1900-01-01`.
- This simple merge assumes newly ingested events should replace the existing row for the same `person_id`.
- Real pipelines often use a stronger raw load ID or batch ID.
- If two raw rows get the exact same timestamp, a simple timestamp watermark can be risky.
- Late-arriving older events need stricter logic than this step shows.
- Always keep `--full-refresh` available.

## Navigation

- [Back to README](../../README.md)
- [Previous step: 08 Current Person](../08-current-person/08-current-person.md)
- [Next step: 10 Sequence Merge](../10-sequence-merge/10-sequence-merge.md)
