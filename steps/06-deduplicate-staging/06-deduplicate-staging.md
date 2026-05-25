# Step 06 - Deduplicate Staging

## Goal

Make `stg_person` contain one row per distinct event data record.

After this step, dbt also checks:

- no duplicate `event_id` remains in staging
- no duplicate `sequence` remains in staging

In this project, `sequence` is the event order/version value from the raw contract.

## Why this step

The raw contract allows duplicate `event_id`.

- Same `event_id` with the same content is an idempotent duplicate.
- Same `event_id` with different content is an error.
- Staging should remove exact duplicate event data.
- Staging tests should still fail when duplicate IDs or duplicate sequence values remain.

`ingest_timestamp` is not part of the event data.

- Two identical events inserted at different times can have different `ingest_timestamp`.
- If `ingest_timestamp` is included in `select distinct`, the rows are still different.
- For this step, keep staging focused on event data only.

## Files

Update `models/mystaging/stg_person.sql`:

- add `distinct` after `select`
- remove `ingest_timestamp` from the selected columns

Full file after the change:

```sql
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
    event.value:data:date_of_birth::date as date_of_birth
from {{ source('raw', 'raw_person') }},
lateral flatten(input => payload:events) event
```

Update `models/mystaging/stg_person.yml`:

- update the model description to say the model contains distinct flattened events
- update the `event_id` description
- add `unique` under `event_id` tests
- update the `sequence` description to mention event order/version
- add `unique` under `sequence` tests

Full file after the change:

```yaml
version: 2

models:
  - name: stg_person
    description: Distinct flattened `person.v1` events from `raw.raw_person`.
    columns:
      - name: event_id
        description: Event identifier from `metadata.event_id`. Exact duplicate event rows are removed in staging.
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
```

## Run

Rebuild the staging view:

```powershell
dbt run
```

After this, the staging view shows exact duplicate events that were sent more than once only once.

Run tests:

```powershell
dbt test
```

Expected result:

- exact duplicate event data is visible only once in `stg_person`
- duplicate `event_id` with different event data fails the `unique` test
- duplicate `sequence` fails the `unique` test

## Navigation

- [Back to README](../../README.md)
- [Previous step: 05 Tests](../05-tests/05-tests.md)
- [Next step: 07 Unit Tests](../07-unit-tests/07-unit-tests.md)
