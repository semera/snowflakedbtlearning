# Step 08 - Current Person

## Goal

Change `stg_person` so it shows only the latest record for each `person_id`.

The latest record is selected by the highest `sequence`.

## Knowledge: current state

Raw events are history.

- One `person_id` can have many events.
- Each new event has a higher `sequence`.
- To show the current person state, keep only the latest event per `person_id`.
- In SQL, use `row_number()` with `partition by person_id`.

## Files

Update `models/mystaging/stg_person.sql`:

- keep the first `select distinct` step
- add `row_number()` per `person_id`
- order by `sequence desc`
- return only `row_number = 1`

Full file after the change:

```sql
with distinct_events as (

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

),

ranked_events as (

    select
        *,
        row_number() over (
            partition by person_id
            order by sequence desc
        ) as person_event_rank
    from distinct_events

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
    date_of_birth
from ranked_events
where person_event_rank = 1
```

Update `models/mystaging/stg_person.yml`:

- update the model description
- add `unique` test for `person_id`
- keep `unique` on `event_id`
- keep `unique` on `sequence`

Full file after the change:

```yaml
version: 2

models:
  - name: stg_person
    description: Current person state built from the latest distinct `person.v1` event per `person_id`.
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
```

## Warning

This step can hide some source data problems.

- `stg_person` now shows only the latest row per `person_id`.
- Older raw events are no longer visible in this view.
- Duplicate or invalid raw events can be harder to see here.
- A better long-term design is to add an intermediate layer for testing source data before this model.
- For this learning step, this simpler approach is enough.

## Add an update event

Run this in Snowflake before rebuilding the view.

This event updates the valid person from the first step.

```sql
insert into raw.raw_person (payload)
select parse_json($$
{
  "events": [
    {
      "metadata": {
        "event_id": "8a1779b1-0b38-4cf0-a7c0-4fda585f9e4c",
        "type": "person.v1",
        "time": "2026-05-23T12:40:56Z",
        "sequence": 1010,
        "mutation": "update"
      },
      "data": {
        "person_id": "db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1",
        "pin": "1234567890",
        "first_name": "John",
        "surname": "Updated",
        "date_of_birth": "1980-01-15"
      }
    }
  ]
}
$$);
```

After `dbt run`, `stg_person` should show only the row with `sequence = 1010` for this `person_id`.

## Run

Rebuild the staging view:

```powershell
dbt run
```

After this, `stg_person` shows only the latest event for each `person_id`.

Run tests:

```powershell
dbt test
```

Expected result:

- one row per `person_id`
- the row has the highest `sequence` for that `person_id`
- exact duplicate events are still collapsed before picking the latest row

## Navigation

- [Back to README](../../README.md)
- [Previous step: 07 Unit Tests](../07-unit-tests/07-unit-tests.md)
