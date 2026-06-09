# Airflow Learning

Small learning guide for Apache Airflow.

The guide starts with local WSL usage. Docker and dbt integration are not used in the first steps.

## Goals

- Understand Airflow concepts step by step.
- Run Airflow only when needed during learning.
- Start with simple local DAGs.
- Add integrations only after the basics are clear.

## Structure

- `steps/` - Airflow learning steps.
- [steps/01-local-wsl/](steps/01-local-wsl/01-local-wsl.md) - install Airflow in WSL and run the first DAG.
- [steps/02-tasks/](steps/02-tasks/02-tasks.md) - build a DAG with multiple tasks and dependencies.
- [steps/03-scheduling/](steps/03-scheduling/03-scheduling.md) - schedule a DAG and understand catchup.
- [steps/04-retries/](steps/04-retries/04-retries.md) - retry a failed task and inspect task states.
- [steps/05-context/](steps/05-context/05-context.md) - print common task context values.
- [steps/06-params-variables/](steps/06-params-variables/06-params-variables.md) - use DAG params and Airflow Variables.

## TODO

- Step 07 - Working with files.
- Step 08 - Python project layout for DAGs.
- Step 09 - First external API.
- Step 10 - Database hooks.
- Step 11 - dbt from Airflow.
