# Step 07 - Unit Tests

## Goal

Add examples for dbt unit tests with mocked raw input.

We want to test:

- exact duplicate raw events become one row in `stg_person`
- same `sequence` with different data stays as two rows
- the existing `unique` data test on `sequence` catches the duplicate sequence

## Knowledge: unit tests and data tests

dbt has two useful test types here.

- Unit tests test model SQL logic with small mocked inputs.
- Unit tests are defined in YAML files under `models/`.
- Unit test mock data is defined in `given`.
- Unit test expected output is defined in `expect`.
- Unit test mock data must be literal data.
- Jinja macros are not supported inside unit test `rows` or fixture files.
- Data tests test real model data in the warehouse.
- Data tests include `not_null`, `accepted_values`, and `unique`.
- Data tests can also be custom SQL tests.
- Data tests usually live in model YAML files or in the `tests/` directory.

For this step:

- The unit test proves that `select distinct` removes exact duplicate event rows.
- The unit test also proves that different event rows with the same `sequence` are not collapsed.
- The data test `unique` on `sequence` reports the duplicate sequence problem.

## Files

Do not use helper macros inside `unit_tests.rows`.

- dbt does not render Jinja macros there.
- If you write `{{ mock_person_raw(...) }}`, dbt reports `mock_person_raw is undefined`.
- For this step, keep the unit test data inline.

Create `models/mystaging/stg_person_unit_tests.yml`:

```yaml
version: 2

unit_tests:
  - name: stg_person_removes_exact_duplicate_event
    model: stg_person
    given:
      - input: source('raw', 'raw_person')
        format: sql
        rows: |
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
                  "surname": "A",
                  "date_of_birth": "1980-01-15"
                }
              }
            ]
          }
          $$) as payload
          union all
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
                  "surname": "A",
                  "date_of_birth": "1980-01-15"
                }
              }
            ]
          }
          $$) as payload
    expect:
      format: sql
      rows: |
        select
            '7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41' as event_id,
            'person.v1' as event_type,
            '2026-05-23T12:34:56'::timestamp_ntz as event_time,
            1000 as sequence,
            'insert' as mutation,
            'db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1' as person_id,
            '1234567890' as pin,
            'John' as first_name,
            'A' as surname,
            '1980-01-15'::date as date_of_birth

  - name: stg_person_keeps_same_sequence_with_different_data
    model: stg_person
    given:
      - input: source('raw', 'raw_person')
        format: sql
        rows: |
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
                  "surname": "A",
                  "date_of_birth": "1980-01-15"
                }
              }
            ]
          }
          $$) as payload
          union all
          select parse_json($$
          {
            "events": [
              {
                "metadata": {
                  "event_id": "3f65f416-6a3e-4f65-b6c1-fb0d4f0e74d8",
                  "type": "person.v1",
                  "time": "2026-05-23T12:34:56Z",
                  "sequence": 1000,
                  "mutation": "insert"
                },
                "data": {
                  "person_id": "db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1",
                  "pin": "1234567890",
                  "first_name": "John",
                  "surname": "B",
                  "date_of_birth": "1980-01-15"
                }
              }
            ]
          }
          $$) as payload
    expect:
      format: sql
      rows: |
        select
            '7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41' as event_id,
            'person.v1' as event_type,
            '2026-05-23T12:34:56'::timestamp_ntz as event_time,
            1000 as sequence,
            'insert' as mutation,
            'db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1' as person_id,
            '1234567890' as pin,
            'John' as first_name,
            'A' as surname,
            '1980-01-15'::date as date_of_birth
        union all
        select
            '3f65f416-6a3e-4f65-b6c1-fb0d4f0e74d8' as event_id,
            'person.v1' as event_type,
            '2026-05-23T12:34:56'::timestamp_ntz as event_time,
            1000 as sequence,
            'insert' as mutation,
            'db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1' as person_id,
            '1234567890' as pin,
            'John' as first_name,
            'B' as surname,
            '1980-01-15'::date as date_of_birth
```

## Run

Run only unit tests:

```powershell
dbt test --select "test_type:unit"
```

Run only unit tests for `stg_person`:

```powershell
dbt test --select "stg_person,test_type:unit"
```

Run all tests:

```powershell
dbt test
```

Expected result:

- both unit tests pass
- the second unit test returns two rows because the data is different
- `dbt test` can still fail on the `unique` data test for `sequence` when real `stg_person` contains duplicate sequence values

## Notes

- Unit tests mock only the direct inputs listed in `given`.
- The mocked source table still needs to match the columns used by the model.
- Here the mocked source needs only `payload`, because `stg_person` no longer selects `ingest_timestamp`.
- Keep unit test inputs small.
- Use data tests for warehouse data quality rules.

## Navigation

- [Back to README](../../README.md)
- [Previous step: 06 Deduplicate Staging](../06-deduplicate-staging/06-deduplicate-staging.md)
- [Next step: 08 Current Person](../08-current-person/08-current-person.md)
