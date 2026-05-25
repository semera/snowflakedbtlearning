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
- Data tests test real model data in the warehouse.
- Data tests include `not_null`, `accepted_values`, and `unique`.
- Data tests can also be custom SQL tests.
- Data tests usually live in model YAML files or in the `tests/` directory.

For this step:

- The unit test proves that `select distinct` removes exact duplicate event rows.
- The unit test also proves that different event rows with the same `sequence` are not collapsed.
- The data test `unique` on `sequence` reports the duplicate sequence problem.

## Files

Create `macros/mock_person_raw.sql`:

```jinja
{% macro mock_person_raw(sequence, surname) %}

{% set event_id_by_surname = {
    'A': '7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41',
    'B': '3f65f416-6a3e-4f65-b6c1-fb0d4f0e74d8'
} %}
{% set event_id = event_id_by_surname.get(surname, '7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41') %}

select parse_json($$
{
  "events": [
    {
      "metadata": {
        "event_id": "{{ event_id }}",
        "type": "person.v1",
        "time": "2026-05-23T12:34:56Z",
        "sequence": {{ sequence }},
        "mutation": "insert"
      },
      "data": {
        "person_id": "db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1",
        "pin": "1234567890",
        "first_name": "John",
        "surname": "{{ surname }}",
        "date_of_birth": "1980-01-15"
      }
    }
  ]
}
$$) as payload

{% endmacro %}
```

Create `macros/mock_person_expected.sql`:

```jinja
{% macro mock_person_expected(sequence, surname) %}

{% set event_id_by_surname = {
    'A': '7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41',
    'B': '3f65f416-6a3e-4f65-b6c1-fb0d4f0e74d8'
} %}
{% set event_id = event_id_by_surname.get(surname, '7b3b31d4-6df8-4e1f-9f7f-6ec22a7d3f41') %}

select
    '{{ event_id }}' as event_id,
    'person.v1' as event_type,
    '2026-05-23T12:34:56'::timestamp_ntz as event_time,
    {{ sequence }} as sequence,
    'insert' as mutation,
    'db2e56e1-54f4-4f8e-91a5-63d02ad8b8a1' as person_id,
    '1234567890' as pin,
    'John' as first_name,
    '{{ surname }}' as surname,
    '1980-01-15'::date as date_of_birth

{% endmacro %}
```

These helpers create one row each.

- Calling `mock_person_raw(1000, 'A')` twice creates an exact duplicate.
- Calling `mock_person_raw(1000, 'A')` and `mock_person_raw(1000, 'B')` creates two different events with the same `sequence`.
- `mock_person_expected` creates matching expected rows for the unit test output.

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
          {{ mock_person_raw(1000, 'A') }}
          union all
          {{ mock_person_raw(1000, 'A') }}
    expect:
      format: sql
      rows: |
        {{ mock_person_expected(1000, 'A') }}

  - name: stg_person_keeps_same_sequence_with_different_data
    model: stg_person
    given:
      - input: source('raw', 'raw_person')
        format: sql
        rows: |
          {{ mock_person_raw(1000, 'A') }}
          union all
          {{ mock_person_raw(1000, 'B') }}
    expect:
      format: sql
      rows: |
        {{ mock_person_expected(1000, 'A') }}
        union all
        {{ mock_person_expected(1000, 'B') }}
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
