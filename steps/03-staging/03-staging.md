# Step 03 - Staging

## Goal

Create the first staging model and run it with `dbt run`.

## Knowledge: dbt run

`dbt run` executes dbt models.

- dbt reads the project files on your computer.
- dbt compiles model SQL from SQL files and Jinja.
- dbt sends the final SQL to the data warehouse.
- The data warehouse runs the SQL and creates the result objects.
- Source data is not downloaded to your computer.

dbt is the control layer. Snowflake does the data processing.

```text
local dbt project
  -> compile SQL
  -> send SQL to Snowflake
  -> Snowflake runs transformations
  -> Snowflake creates views or tables
```

Use `dbt run` after `dbt debug` works.

## Files

Update `dbt_project.yml`:

```yaml
name: snowflake_dbt_learning
version: 1.0.0
config-version: 2

profile: snowflake_dbt_learning

models:
  snowflake_dbt_learning:
    mystaging:
      +materialized: view
```

This config means:

- `models` is a dbt keyword for model configuration.
- `snowflake_dbt_learning` is the project/package level.
- Here, `snowflake_dbt_learning` matches `name: snowflake_dbt_learning`.
- Later, this same level can also configure models from dbt packages.
- `mystaging` is the directory path level.
- `mystaging` must match the folder `models/mystaging`.
- `+materialized: view` makes dbt create models inside `models/mystaging` as views.

Create `models/mystaging/stg_person.sql`:

```sql
select
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
from raw.raw_person,
lateral flatten(input => payload:events) event
```

`lateral flatten(input => payload:events) event` expands the `events` JSON array.

- `payload:events` selects the `events` array from the raw JSON.
- `flatten` creates one row per event in the array.
- `lateral` runs the flatten operation for each raw row.
- `event` is the alias used to read fields with `event.value`.

Notes:

- The target schema comes from `schema` in `profiles.yml`.
- In this guide, it is set by `DBT_SNOWFLAKE_SCHEMA` and defaults to `STAGING`.
- The target object name comes from the file name.
- `models/mystaging/stg_person.sql` creates `stg_person`.
- The object name can be changed with an alias, but we do not need that now.
- Because this model is a view, new rows in `raw.raw_person` are visible when the view is queried without a new `dbt run`.

## Run

Run:

```powershell
dbt run --profiles-dir .
```

Expected output should include something like:

```text
Found 1 model
1 of 1 OK created sql view model STAGING.stg_person
Completed successfully
Done. PASS=1 WARN=0 ERROR=0 SKIP=0 NO-OP=0 TOTAL=1
```

Check the created view in Snowflake:

```sql
select *
from staging.stg_person;
```

## Navigation

- [Back to README](../../README.md)
- [Previous step: 02 Debug](../02-debug/02-debug.md)
- [Next step: 04 Source Clone Vars](../04-source-clone-vars/04-source-clone-vars.md)
