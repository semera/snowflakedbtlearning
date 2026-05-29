from datetime import datetime

from airflow.sdk import dag, task


@dag(
    dag_id="hello_airflow",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["learning"],
)
def hello_airflow():
    @task
    def say_hello():
        print("Hello from Airflow")

    say_hello()


hello_airflow()
