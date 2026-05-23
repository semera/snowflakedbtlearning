# Agent Instructions

These rules apply to all current and future agents working in this repository.

## Communication

- Talk with the user in Czech by default.
- If the user uses another language, follow the user's language.
- Write project documentation in simple English.
- Keep documentation short and mostly in bullet points.

## Repository Boundaries

- Work only inside this repository directory.
- Do not read or write files outside this repository.
- Do not create commits.
- Do not create branches.
- Do not open pull requests.
- Do not run git write operations.
- Allowed git commands are read-only commands, for example:
  - `git status`
  - `git diff`
  - `git log`
  - `git show`

## Project Direction

- This is a learning project for local `dbt-core` with Snowflake.
- Build the project in small steps.
- Use short step directory names, for example:
  - `steps/01-init`
  - `steps/02-staging`
- Each step should contain a short markdown guide and any files needed for that step.
- Do not overbuild future steps.
- Explain dbt concepts only when they are first used.

## Data Contracts

- Use only the raw event contracts from `docs/contract.md`.
- Current event types are:
  - `person.v1`
  - `address.v1`
- Do not add new raw event contracts unless the user asks for it.

## Secrets

- Never write real secrets or credentials.
- Use placeholders only when secrets become needed.
- Do not add Snowflake connection details until the project step needs them.
