# Step 03 - Scheduling

## Goal

Create a scheduled DAG and understand how `schedule`, `start_date`, and `catchup` work together.

## Knowledge: scheduling

`schedule=None` means manual runs only.

`schedule="@daily"` means Airflow should create one DAG run per day.

Important details:

- `start_date` is the start of the first scheduled data interval.
- A scheduled run is created after its interval is complete.
- `catchup=False` skips old missing intervals.
- `catchup=True` creates runs for old missing intervals from `start_date`.
- A new scheduled DAG may need to be unpaused in the UI before automatic runs happen.

Use `catchup=False` while learning unless you explicitly want historical runs.

Do not set `catchup=True` with an old `start_date` unless you want many historical DAG runs.

## Experiment: scheduled DAG

Create `daily_schedule.py` in your Airflow DAGs folder and run it from the UI:

```python
from datetime import datetime

from airflow.sdk import dag, task


@dag(
    dag_id="daily_schedule",
    start_date=datetime(2026, 5, 30),
    schedule="@daily",
    catchup=False,
    tags=["learning"],
)
def daily_schedule():
    @task
    def show_context():
        print("This DAG is scheduled daily.")

    show_context()


daily_schedule()
```

In the Airflow UI:

- Open DAGs.
- Find `daily_schedule`.
- Open the DAG detail.
- Check the schedule value.
- Check the next run value.
- Unpause the DAG if it is paused.
- Trigger it manually once.
- Open the DAG run log.

Expected log line:

```text
This DAG is scheduled daily.
```

Use the UI to inspect these values:

- manual run
- scheduled run
- next run
- paused vs unpaused DAG

## Additional info: scheduling options

Airflow supports several scheduling styles:

- `schedule=None` - manual or externally triggered runs only.
- `schedule="@once"` - one scheduled run.
- `schedule="@hourly"` - once per hour.
- `schedule="@daily"` - once per day.
- `schedule="@weekly"` - once per week.
- `schedule="@monthly"` - once per month.
- `schedule="@quarterly"` - once per quarter.
- `schedule="@yearly"` - once per year.
- `schedule="@continuous"` - start a new run as soon as the previous run finishes.
- `schedule="0 6 * * *"` - cron expression, here daily at 06:00.
- `schedule=datetime.timedelta(hours=6)` - fixed time delta interval.

Advanced scheduling options:

- custom timetables for schedules that cron or timedelta cannot express well
- asset-aware scheduling for DAGs triggered by asset updates
- event-driven scheduling for DAGs triggered by supported external events

Official docs:

- https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/cron.html
- https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/timetable.html
- https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/asset-scheduling.html

## Navigation

- [Back to Airflow README](../../README.md)
- [Previous step](../02-tasks/02-tasks.md)
