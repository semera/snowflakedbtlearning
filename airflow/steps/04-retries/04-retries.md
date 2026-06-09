# Step 04 - Retries

## Goal

Create a task that fails and watch how Airflow retries it.

## Knowledge: task failures

Retries belong to tasks, not to the whole DAG.

- `retries=2` means one first attempt plus two retries, so the task can run up to three times.
- `retry_delay` controls how long Airflow waits before the next attempt.
- A task can be `failed` while the DAG run is still waiting for retries.
- `up_for_retry` means the task failed but Airflow will try it again.
- If all retries fail, the task becomes `failed`.
- The DAG run fails when a required task stays failed.
- A failed task can be cleared manually from the UI and run again later.

Airflow does not repair the error. It only runs the same task again.

## Experiment: failed task with retries

Create `retry_example.py` in your Airflow DAGs folder and run it from the UI:

```python
from datetime import datetime, timedelta

from airflow.sdk import dag, task


@dag(
    dag_id="retry_example",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["learning"],
)
def retry_example():
    @task(retries=2, retry_delay=timedelta(seconds=30))
    def unstable_task():
        print("This task will fail on purpose.")
        raise ValueError("Intentional failure")

    unstable_task()


retry_example()
```

In the Airflow UI:

- Open `retry_example`.
- Trigger it manually.
- Open the DAG run.
- Open Graph view.
- Inspect the task state.
- Open the task logs.
- Wait for retry attempts.
- Inspect the task state again after retries are exhausted.

Expected log line:

```text
This task will fail on purpose.
```

Expected final error:

```text
ValueError: Intentional failure
```

Inspect these values in the UI:

- task state
- try number
- next retry time
- logs for each attempt
- final DAG run state

## Experiment: manual restart

After the task is finally failed:

- Open the failed DAG run.
- Select `unstable_task`.
- Clear the task.
- Confirm the clear action.
- Wait for Airflow to schedule the task again.
- Open the new task log.

Clearing a task removes the task state for the selected DAG run. It does not clear the whole workflow unless you select additional tasks or runs in the clear dialog.

Common clear scopes include:

- only the selected task
- downstream tasks
- upstream tasks
- past or future DAG runs

The task fails again because the Python code still raises the same error.

Manual clear is useful after you change the code or fix the external reason for the failure.

## Additional info: retry options

Useful task retry settings:

- `retries` - how many retries Airflow can run after the first failure
- `retry_delay` - delay before the next retry
- `retry_exponential_backoff` - increase retry delay after repeated failures
- `max_retry_delay` - cap for exponential backoff
- `execution_timeout` - maximum allowed runtime for one task attempt

Airflow does not know whether a failure is temporary. This is why task design matters: split work into clear tasks and add retries only where running the same code later may reasonably succeed, for example when an API is temporarily unavailable, a database connection is briefly broken, or a rate limit clears after a delay.

Retries do not help when the code always fails the same way.

## Navigation

- [Back to Airflow README](../../README.md)
- [Previous step](../03-scheduling/03-scheduling.md)
