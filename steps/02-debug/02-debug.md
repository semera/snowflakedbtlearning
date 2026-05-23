# Step 02 - Debug

## Goal

Connect dbt to Snowflake with `dbt debug`.

`dbt init` can create starter files for you, but here we create the files manually to understand what they do.

## Knowledge: Data Layers

Data usually moves through layers from source data to a user or consumer layer.

## Layer Overview

- Source (Raw, Landing): Use this layer to keep data as close to the original source as possible.
- Staging (Clean, Standardized): Use this layer to make source data easier to work with.
- Warehouse (Core, Intermediate): Use this layer to apply business rules and build stable internal models.
- Consumption (Marts, Presentation): Use this layer to serve data to users, reports, dashboards, or applications.

## Source Layer

Use this layer to keep data as close to the original source as possible.

- Minimal transformations.
- Stores original source records.
- Often includes technical ingestion metadata.
- Useful for audit and reprocessing.

## Staging Layer

Use this layer to make source data easier to work with.

- Standard column names.
- Correct data types.
- Simple filtering.
- Simple structure flattening.
- Usually still close to the source shape.

### Staging Notes

Staging prepares ingested data for the next layer.

- Keeps data close to the source, often one model per source object.
- Extracts or flattens raw structures into columns.
- Converts data types.
- Cleans simple quality issues.
- Standardizes formats and naming.
- Filters only clearly invalid or unwanted records.
- Can deduplicate technical duplicates.
- Reduces load on source systems by processing copied data.
- Can keep audit fields such as load time or source file.

Staging can be temporary or persistent.

- Temporary staging is overwritten or cleared after processing.
- Persistent staging keeps raw or lightly cleaned history for audit and reprocessing.

In ETL, staging may live outside the warehouse before loading. In ELT, staging usually lives inside the warehouse and transformations happen there.

dbt is the `T` in ELT. It does not extract or load source data; it transforms data that already exists in the warehouse.

## Knowledge: dbt debug

`dbt debug` checks that dbt can run in the current project.

- Checks the dbt project file.
- Checks the selected profile.
- Checks required connection settings.
- Tests the database connection.
- Useful before running models for the first time.

## Files

Create these files in the project root:

- `dbt_project.yml`
- `profiles.yml`
- `dbt.env.ps1`

`dbt_project.yml` tells dbt where the project starts and which profile to use.

```yaml
name: snowflake_dbt_learning
version: 1.0.0
config-version: 2

profile: snowflake_dbt_learning
```

`profiles.yml` tells dbt how to connect to Snowflake.

```yaml
snowflake_dbt_learning:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('DBT_SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('DBT_SNOWFLAKE_USER') }}"
      password: "{{ env_var('DBT_SNOWFLAKE_PASSWORD') }}"
      role: "{{ env_var('DBT_SNOWFLAKE_ROLE') }}"
      warehouse: "{{ env_var('DBT_SNOWFLAKE_WAREHOUSE') }}"
      database: "{{ env_var('DBT_SNOWFLAKE_DATABASE', 'DBTEST') }}"
      schema: "{{ env_var('DBT_SNOWFLAKE_SCHEMA', 'STAGING') }}"
      threads: 4
```

`dbt.env.ps1` stores local environment variables. Do not commit this file.

```powershell
$env:DBT_SNOWFLAKE_ACCOUNT = "<account>"
$env:DBT_SNOWFLAKE_USER = "<user>"
$env:DBT_SNOWFLAKE_PASSWORD = "<password>"
$env:DBT_SNOWFLAKE_ROLE = "<role>"
$env:DBT_SNOWFLAKE_WAREHOUSE = "<warehouse>"
$env:DBT_SNOWFLAKE_DATABASE = "DBTEST"
$env:DBT_SNOWFLAKE_SCHEMA = "STAGING"
```

## Run dbt debug

You can set these values as persistent local environment variables on your computer.

For repeated work, or if you use more Snowflake environments such as dev and production, use a local env file.

Create `dbt.env.ps1` and edit it with your Snowflake values. This file is ignored by git.

Load environment variables in PowerShell:

```powershell
. .\dbt.env.ps1
```

Run dbt debug:

```powershell
dbt debug --profiles-dir .
```

The goal is to see a successful Snowflake connection.

## Alternative Authentication

The default setup in this guide uses password authentication.

Browser authentication:

```yaml
authenticator: externalbrowser
```

Use browser authentication only when SSO is configured for the Snowflake account.

Key pair authentication:

```yaml
private_key_path: "{{ env_var('DBT_SNOWFLAKE_PRIVATE_KEY_PATH') }}"
private_key_passphrase: "{{ env_var('DBT_SNOWFLAKE_PRIVATE_KEY_PASSPHRASE') }}"
```

```powershell
$env:DBT_SNOWFLAKE_PRIVATE_KEY_PATH = "C:\path\to\rsa_key.p8"
$env:DBT_SNOWFLAKE_PRIVATE_KEY_PASSPHRASE = "<passphrase>"
```

Add the public key to the Snowflake user:

```sql
alter user <user_name>
set rsa_public_key = '<public_key_without_begin_end_lines>';
```

Use password authentication for local learning. Use key pair authentication for service users or automation.
