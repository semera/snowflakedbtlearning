# Step 06 - Params and Variables

## Goal

Use runtime params for one DAG run and an Airflow Variable for shared runtime configuration.

## Knowledge: params vs Variables

Params belong to a DAG run. When you trigger a DAG manually, Airflow can show a form where you change param values for that run.

Variables are stored in Airflow metadata DB and can be read by many DAGs. They are useful for runtime values that are not tied to one specific run.

Use params when the value should be chosen for one run. Use Variables when the value belongs to the Airflow environment.

Keep most configuration in DAG code when it can be versioned. Use Variables only for values that really need to change at runtime. Do not put real secrets in this learning guide.

## Experiment: trigger params and Variable

Create an Airflow Variable in the UI:

- Open Admin.
- Open Variables.
- Add a variable:
  - key: `learning_city`
  - value: `Prague`

Create `params_variables_example.py` in your Airflow DAGs folder:

```python
from datetime import datetime

from airflow.sdk import Param, Variable, dag, get_current_context, task


@dag(
    dag_id="params_variables_example",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    params={
        "name": Param("Airflow learner", type="string"),
        "excited": Param(True, type="boolean"),
    },
    tags=["learning"],
)
def params_variables_example():
    @task
    def print_message():
        context = get_current_context()
        params = context["params"]

        name = params["name"]
        excited = params["excited"]
        city = Variable.get("learning_city", default="Unknown city")

        suffix = "!" if excited else "."

        print(f"Hello, {name} from {city}{suffix}")

    print_message()


params_variables_example()
```

In the Airflow UI:

- Open `params_variables_example`.
- Trigger the DAG.
- Inspect the trigger form.
- Change `name`.
- Keep or change `excited`.
- Start the DAG run.
- Open the task log.

Expected log line shape:

```text
Hello, Airflow learner from Prague!
```

If you changed the trigger form, the printed `name` or punctuation should change.

## Additional info: choosing the right input

Use params for values that describe one run, for example a selected date, mode, customer, or dry-run flag.

Use Variables for environment-level values, for example a default country, feature flag, or non-secret setting shared by multiple DAGs.

Do not use Variables to pass data between tasks. Use task return values and XComs for that.

Read Variables inside tasks, not at the top level of the DAG file. Top-level reads happen while Airflow parses DAG files and can make DAG parsing slower or more fragile.

Official docs:

- https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/params.html
- https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/variables.html
- https://airflow.apache.org/docs/apache-airflow/stable/howto/variable.html

## Navigation

- [Back to Airflow README](../../README.md)
- [Previous step](../05-context/05-context.md)
