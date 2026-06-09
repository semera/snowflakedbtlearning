# Step 05 - Context

## Goal

Print common Airflow context values from a running task.

## Knowledge: task context

Task context is runtime metadata for one task attempt.

It tells the task where it is running in Airflow: which DAG, which task, which run, which logical date, which data interval, and which try number.

Use context when task code needs metadata about the current Airflow run. Do not use it for business data that should come from task inputs, files, APIs, or databases.

In Airflow 3, TaskFlow code can access the current context with:

```python
from airflow.sdk import get_current_context
```

Context is available while the task is running. It is not available when Airflow only parses the DAG file.

## Experiment: print context values

Create `context_example.py` in your Airflow DAGs folder and run it from the UI:

```python
from datetime import datetime

from airflow.sdk import dag, get_current_context, task


@dag(
    dag_id="context_example",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["learning"],
)
def context_example():
    @task
    def print_context():
        context = get_current_context()
        task_instance = context["ti"]
        dag_run = context["dag_run"]

        print(f"dag_id: {task_instance.dag_id}")
        print(f"task_id: {task_instance.task_id}")
        print(f"run_id: {dag_run.run_id}")
        print(f"run_type: {dag_run.run_type}")
        print(f"logical_date: {context['logical_date']}")
        print(f"data_interval_start: {context['data_interval_start']}")
        print(f"data_interval_end: {context['data_interval_end']}")
        print(f"try_number: {task_instance.try_number}")

        raise ValueError("Intentional failure after printing context")

    print_context()


context_example()
```

In the Airflow UI:

- Open `context_example`.
- Trigger it manually.
- Open the DAG run.
- Open the failed task log.
- Inspect the printed context values.

Expected final error:

```text
ValueError: Intentional failure after printing context
```

The task fails on purpose so the log is easy to find as a failed task.

## Additional info: common context values

Useful context values:

- `ti` or `task_instance` - current task instance
- `dag_run` - current DAG run
- `run_id` - unique run identifier
- `run_type` - manual, scheduled, or another run type
- `logical_date` - Airflow's logical date for the run
- `data_interval_start` - start of the data interval
- `data_interval_end` - end of the data interval
- `params` - runtime params for this DAG run

`logical_date` is not always the wall-clock time when the task runs. For scheduled DAGs, it is tied to the data interval.

## Navigation

- [Back to Airflow README](../../README.md)
- [Previous step](../04-retries/04-retries.md)
