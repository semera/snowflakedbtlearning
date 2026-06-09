# Step 02 - Tasks

## Goal

Create a DAG with multiple tasks and run it in Airflow UI.

## Knowledge: task dependencies

A DAG is a graph of tasks.

- `@dag` defines the workflow.
- `@task` defines each task.
- A task is one unit of work.
- A task call creates a task in the DAG.
- Dependencies define task order.
- Airflow shows dependencies in Graph view.
- TaskFlow can pass return values between tasks.
- Passing task output into another task creates a dependency.
- Airflow stores passed values as XComs.

This step uses a simple chain:

```text
get_name -> build_message -> print_message
```

The data flow is:

```text
"Airflow learner" -> "Good morning, Airflow learner!" -> log output
```

## Files

Create `daily_greeting.py` in your Airflow DAGs folder:

```python
from datetime import datetime

from airflow.sdk import dag, task


@dag(
    dag_id="daily_greeting",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["learning"],
)
def daily_greeting():
    @task
    def get_name():
        return "Airflow learner"

    @task
    def build_message(name):
        return f"Good morning, {name}!"

    @task
    def print_message(message):
        print(message)

    print_message(build_message(get_name()))


daily_greeting()
```

This line creates the dependencies:

```python
print_message(build_message(get_name()))
```

## Run

In the Airflow UI:

- Open `daily_greeting`.
- Trigger it manually.
- Open the DAG run.
- Open Graph view.
- Check the task order:

```text
get_name -> build_message -> print_message
```

Open the `print_message` task log.

Expected log line:

```text
Good morning, Airflow learner!
```

## Navigation

- [Back to Airflow README](../../README.md)
- [Previous step](../01-local-wsl/01-local-wsl.md)
