# Snowflake dbt Learning

Small learning project for dbt with Snowflake as the data warehouse.

The project is built step by step. Each step should be small and focused.

## Goals

- Learn dbt concepts one by one.
- Use local `dbt-core` with the Snowflake adapter.
- Keep examples simple and practical.
- Use only the raw event contracts in `docs/contract.md`.
- Add files only when they are needed by the current step.

## Structure

- `docs/` - general project documents.
- [docs/contract.md](docs/contract.md) - raw event contract for `person.v1` and `address.v1`.
- `steps/` - learning steps.
- [steps/01-init/](steps/01-init/01-init.md) - first dbt project setup.
- [steps/02-debug/](steps/02-debug/02-debug.md) - dbt connection check.
- [steps/03-staging/](steps/03-staging/03-staging.md) - first simple staging model.
- [steps/04-source-clone-vars/](steps/04-source-clone-vars/04-source-clone-vars.md) - dbt vars, source, and raw clone.
- [steps/05-tests/](steps/05-tests/05-tests.md) - source descriptions and basic dbt data tests.
- [steps/06-deduplicate-staging/](steps/06-deduplicate-staging/06-deduplicate-staging.md) - distinct staging rows and uniqueness tests.
- [steps/07-unit-tests/](steps/07-unit-tests/07-unit-tests.md) - mocked inputs and unit test examples.

Step names should be short, for example `01-init` or `03-staging`.

## Step Style

Each step should explain:

- what we build
- which files are used
- which commands are run
- what we learned

The exact step template can change while the project grows.

## Documentation Rules

- Documentation is written in simple English.
- Keep notes short and mostly in bullet points.
- Explain a dbt concept only when it is first used.
- Do not document secrets or real credentials.
- Do not solve future steps too early.
