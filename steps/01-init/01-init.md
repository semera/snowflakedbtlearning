# Step 01 - Init

## Prerequisites

- Windows with PowerShell.
- Python 3.12 or newer.
- Snowflake account.
- Snowflake database where your role can create schemas and tables.

## Install dbt locally

Run in PowerShell:

```powershell
pip install dbt-core dbt-snowflake
```

## Create raw tables

- Open Snowflake worksheet.
- Use your existing database, or create a new one:

```sql
create database dbtest;
use database dbtest;
```

- In this guide, `dbtest` is the default database name.
- Run:

```sql
create schema if not exists raw;

create table if not exists raw.raw_person (
    payload variant not null,
    ingest_timestamp timestamp_ltz not null default current_timestamp()
);
```

## Insert raw person data

The raw storage format is defined in [../../docs/contract.md](../../docs/contract.md).

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

## Navigation

- [Back to README](../../README.md)
- [Next step: 02 Debug](../02-debug/02-debug.md)
