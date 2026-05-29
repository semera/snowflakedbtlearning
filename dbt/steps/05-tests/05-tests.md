# Step 05 - Tests

## Move profiles.yml to .dbt

So far, commands used `--profiles-dir .` because `profiles.yml` was in the project folder.

dbt can also use its default profile location:

```text
~/.dbt/profiles.yml
```

On Windows this usually means:

```text
C:\Users\<your-user>\.dbt\profiles.yml
```

Create the `.dbt` folder if it does not exist, then move `profiles.yml` there.

PowerShell example:

```powershell
New-Item -ItemType Directory -Force $HOME\.dbt
Move-Item .\profiles.yml $HOME\.dbt\profiles.yml
```

After this, dbt commands do not need `--profiles-dir .`:

```powershell
dbt test
```

You can still override the profile location from the command line:

```powershell
dbt test --profiles-dir .
```

This is useful when you want to test a temporary local profile or a profile stored with a specific project.

## Goal

Describe the input source and add basic dbt data tests for `stg_person`.

We check:

- required columns are not null
- `event_type` contains only `person.v1`
- `mutation` contains only `insert`, `update`, or `delete`

## Add two raw rows before the test

Run this in Snowflake before running dbt tests.

The first row is an idempotent duplicate of the first `person.v1` event.

```sql
insert into raw.raw_person (payload)
select parse_json($$
{
  "events": [
    {
      "metadata": {
        "event_id": "7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41",
        "type": "person.v1",
        "time": "2026-05-23T12:34:56Z",
        "sequence": 1000,
        "mutation": "insert"
      },
      "data": {
        "person_id": "db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1",
        "pin": "1234567890",
        "first_name": "John",
        "surname": "Doe",
        "date_of_birth": "1980-01-15"
      }
    }
  ]
}
$$);
```

The second row is intentionally invalid for `raw_person`.

- `event_type` is `address.v1`, but `raw_person` should contain only `person.v1`.
- `mutation` is `merge`, but the contract allows only `insert`, `update`, and `delete`.
- `person_id` is missing from `data`.

```sql
insert into raw.raw_person (payload)
select parse_json($$
{
  "events": [
    {
      "metadata": {
        "event_id": "dc6c30f8-77b2-4b10-9da2-2b7dbefbf77b",
        "type": "address.v1",
        "time": "2026-05-23T12:35:56Z",
        "sequence": 1001,
        "mutation": "merge"
      },
      "data": {
        "pin": "9999999999",
        "first_name": "Invalid",
        "surname": "Person"
      }
    }
  ]
}
$$);
```

## Knowledge: dbt test

`dbt test` checks assumptions about your data.

- Tests are usually defined in YAML files.
- dbt compiles each test into a SQL query.
- A test passes when the query returns zero failing rows.
- A test fails when the query returns one or more failing rows.
- Tests do not fix data; they only report data quality problems.

Common generic tests:

- `not_null`: the column must not contain null values.
- `accepted_values`: the column may contain only listed values.
- `unique`: values in the column must not repeat.

We do not add `unique` on `event_id` yet.

- The raw event contract explicitly allows duplicate `event_id`.
- The same `event_id` with the same content is an idempotent duplicate.
- A simple `unique` test would fail on valid idempotent duplicates.
- Detecting "same id, different content" is a later business rule, not this basic test.

## Files

Update `models/mystaging/sources.yml`:

```yaml
version: 2

sources:
  - name: raw
    description: Raw append-only event tables loaded outside dbt.
    schema: "raw{{ var('schema_suffix', '') }}"
    tables:
      - name: raw_person
        description: Raw payloads for `person.v1` events. Each row contains one JSON document with an `events` array.
```

Create `models/mystaging/stg_person.yml`:

```yaml
version: 2

models:
  - name: stg_person
    description: Flattened `person.v1` events from `raw.raw_person`.
    columns:
      - name: event_id
        description: Event identifier from `metadata.event_id`. It may repeat for idempotent duplicates.
        tests:
          - not_null

      - name: event_type
        description: Event type from `metadata.type`.
        tests:
          - not_null
          - accepted_values:
              values: ['person.v1']

      - name: sequence
        description: Event sequence from `metadata.sequence`.
        tests:
          - not_null

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

Run all tests:

```powershell
dbt test
```

Expected result with the invalid row:

- the idempotent duplicate does not fail any current test
- `accepted_values` on `event_type` fails
- `accepted_values` on `mutation` fails
- `not_null` on `person_id` fails

After removing or fixing the invalid raw row

```sql
delete from raw.raw_person where payload::text rlike '^.*Invalid.*$'
```

run again:

```powershell
dbt test
```

Expected result after fixing the invalid row:

```text
Completed successfully
```

## Useful checks in Snowflake

See the rows used by the tests:

```sql
select
    event_id,
    event_type,
    sequence,
    mutation,
    person_id
from staging.stg_person
order by sequence, event_id;
```

Find duplicate event IDs:

```sql
select
    event_id,
    count(*) as row_count
from staging.stg_person
group by event_id
having count(*) > 1;
```

This query can show idempotent duplicates, but it is not a dbt failure in this step.

## Navigation

- [Back to README](../../README.md)
- [Previous step: 04 Source Clone Vars](../04-source-clone-vars/04-source-clone-vars.md)
- [Next step: 06 Deduplicate Staging](../06-deduplicate-staging/06-deduplicate-staging.md)
