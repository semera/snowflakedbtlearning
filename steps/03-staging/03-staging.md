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
