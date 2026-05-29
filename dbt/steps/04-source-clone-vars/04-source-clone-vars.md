# Step 04 - Source

## Goal

Define the first dbt source and use it in the staging model.

## Knowledge: dbt vars

dbt vars are values that can be inserted into dbt files with Jinja.

- Use vars for values like schema names, suffixes, flags, or small options.
- Do not use vars for secrets, users, accounts, or connection credentials.
- Vars can be used in SQL, YAML, and model config.
- A var is read with `var('name')`.
- A default value can be added with `var('name', 'default_value')`.

Example:

```jinja
{{ var('schema_suffix', '') }}
```

If `schema_suffix` is not defined, dbt uses the default value `''`.

Define a var in `dbt_project.yml`:

```yaml
vars:
  schema_suffix: ""
```

Override a var from the command line:

```powershell
dbt run --profiles-dir . --vars "{schema_suffix: _CLONED}"
```

Var priority:

1. command line `--vars`
2. `vars:` in `dbt_project.yml`
3. default value in `var('name', 'default_value')`

## Knowledge: dbt source

A dbt source describes a table that already exists outside dbt.

- dbt does not create source tables.
- dbt uses sources as named inputs for models.
- Source names make model SQL easier to read.
- Source definitions live in YAML files.
- Source YAML can use Jinja, so the schema can include `var('schema_suffix', '')`.

The source schema and the model output schema are configured in different places.

- `sources.yml` controls where the model reads from.
- `profiles.yml` controls where dbt creates model output.
- `profiles.yml` should stay focused on connection settings.
- To use the same suffix for model output, use a dbt macro with `var('schema_suffix', '')`.

Using `source()` is better than hardcoding `raw.raw_person` in SQL.

- The real schema and table are defined in one YAML file.
- Model SQL uses a logical name instead of a physical table path.
- If the raw schema changes later, update the source definition, not every model.
- dbt can show that the model depends on a source table.

## Files

Create `models/mystaging/sources.yml`:

```yaml
version: 2

sources:
  - name: raw
    schema: "raw{{ var('schema_suffix', '') }}"
    tables:
      - name: raw_person
```

Update `models/mystaging/stg_person.sql`.

Before:

```sql
from raw.raw_person,
lateral flatten(input => payload:events) event
```

After:

```sql
from {{ source('raw', 'raw_person') }},
lateral flatten(input => payload:events) event
```

## Knowledge: macros

dbt macros are reusable Jinja blocks.

- Macros live in the `macros` folder.
- A macro can generate SQL or run SQL.
- A macro can use `var()`, `target`, and dbt metadata.
- Normal macros run only when we call them.
- Some macro names are special because dbt calls them automatically.

Create `macros/clone_raw.sql`:

```jinja
{% macro clone_raw() %}

    {% set schema_suffix = var('schema_suffix', '') %}

    {% if schema_suffix == '' %}
        {{ exceptions.raise_compiler_error("Set schema_suffix before cloning raw sources.") }}
    {% endif %}

    {% set source_schema = 'raw' %}
    {% set target_schema = 'raw' ~ schema_suffix %}

    {% do run_query('create schema if not exists ' ~ target_schema) %}

    {% for source in graph.sources.values() %}
        {% if source.source_name == 'raw' %}
            {% set sql %}
                create or replace table {{ target_schema }}.{{ source.identifier }}
                clone {{ source_schema }}.{{ source.identifier }}
            {% endset %}

            {% do log(sql, info=true) %}
            {% do run_query(sql) %}
        {% endif %}
    {% endfor %}

{% endmacro %}
```

This macro:

- reads all tables defined under `sources:` with `name: raw`
- clones them from `raw`
- writes them into `raw{{ var('schema_suffix') }}`
- does not run during `dbt run`

Run the clone manually:

```powershell
dbt run-operation clone_raw --profiles-dir . --vars "{schema_suffix: _CLONED}"
```

Now `raw_CLONED.raw_person` exists.

## Knowledge: special macro

`generate_schema_name` is a special dbt macro.

- dbt calls it when it decides where to create model output.
- We can override it to add `schema_suffix` to the target schema.
- Without this macro, `--vars "{schema_suffix: _CLONED}"` changes the source schema only.
- With this macro, the output schema gets the same suffix too.
- This is needed because the profile is evaluated before dbt vars are available, so `var('schema_suffix')` cannot be used inside `profiles.yml`.
- We can still change the target schema through environment variables, for example `DBT_SNOWFLAKE_SCHEMA`.

Create `macros/generate_schema_name.sql`:

```jinja
{% macro generate_schema_name(custom_schema_name, node) -%}

    {%- set schema_suffix = var('schema_suffix', '') -%}

    {%- if custom_schema_name is none -%}
        {{ target.schema }}{{ schema_suffix }}
    {%- else -%}
        {{ custom_schema_name | trim }}{{ schema_suffix }}
    {%- endif -%}

{%- endmacro %}
```

This macro changes where dbt creates model output.

- Without suffix: `STAGING`
- With `--vars "{schema_suffix: _CLONED}"`: `STAGING_CLONED`

Now both input raw schema and target model schema can be remapped with the same suffix.

```powershell
dbt run --profiles-dir .
```

This reads from the original source and writes to the original staging schema.

```powershell
dbt run --profiles-dir . --vars "{schema_suffix: _CLONED}"
```

This reads from cloned raw tables and writes to cloned staging schema.

## Navigation

- [Back to README](../../README.md)
- [Previous step: 03 Staging](../03-staging/03-staging.md)
- [Next step: 05 Tests](../05-tests/05-tests.md)
