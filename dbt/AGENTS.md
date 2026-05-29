# dbt Guide Instructions

These rules apply inside the `dbt/` guide.

## Project Direction

- This is a learning project for local `dbt-core` with Snowflake.
- Explain dbt concepts only when they are first used.
- Do not add Snowflake connection details until the project step needs them.

## Data Contracts

- Use only the raw event contracts from `docs/contract.md`.
- Current event types are:
  - `person.v1`
  - `address.v1`
- Do not add new raw event contracts unless the user asks for it.
