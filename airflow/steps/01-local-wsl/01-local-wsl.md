# Step 01 - Local WSL

Install Airflow in WSL and run a first simple DAG.

This step does not use Docker and does not integrate with dbt.

## What We Build

- Local Airflow installation in WSL.
- One simple DAG called `hello_airflow`.
- A manual DAG run from the Airflow UI.

## Concepts

- Airflow is an orchestrator.
- A DAG is a workflow definition.
- A task is one unit of work inside a DAG.
- The scheduler decides when DAG runs should be created.
- The UI lets you inspect DAGs, runs, tasks, and logs.

Airflow decides when and how tasks run.

## Knowledge: DAG file refresh

Airflow does not load every new DAG file immediately.

- The DAG processor scans the DAG folder repeatedly.
- In Airflow 3, the refresh interval can be configured.
- A shorter interval makes new DAG files appear faster during local learning.
- This setting is useful for development, not required for production.

Use this local setting before starting Airflow:

```bash
export AIRFLOW__DAG_PROCESSOR__REFRESH_INTERVAL=30
```

This asks Airflow to refresh DAG files every 30 seconds.

## Install System Packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

## Create Python Environment

```bash
mkdir -p ~/airflow-learning
cd ~/airflow-learning

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

## Install Airflow

Use the official Airflow constraint file for repeatable installation.

```bash
AIRFLOW_VERSION=3.2.1
PYTHON_VERSION="$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

pip install "apache-airflow==${AIRFLOW_VERSION}" --constraint "${CONSTRAINT_URL}"
```

Check the command:

```bash
airflow version
```

Official docs:

- https://airflow.apache.org/docs/apache-airflow/stable/start.html
- https://airflow.apache.org/docs/apache-airflow/stable/installation/index.html

## Start Airflow

Set a local Airflow home:

```bash
export AIRFLOW_HOME=~/airflow-learning/airflow-home
```

Start local standalone Airflow:

```bash
cd ~/airflow-learning
source ~/airflow-learning/.venv/bin/activate

export AIRFLOW_HOME=~/airflow-learning/airflow-home
export AIRFLOW__DAG_PROCESSOR__REFRESH_INTERVAL=30
airflow standalone
```

Airflow prints:

- UI URL, usually `http://localhost:8080`
- username, usually `admin`
- generated password - check ```cat $AIRFLOW_HOME/simple_auth_manager_passwords.json.generated```

## Add First DAG

Open a second Ubuntu/WSL terminal:

```bash
cd ~/airflow-learning
source .venv/bin/activate
export AIRFLOW_HOME=~/airflow-learning/airflow-home

mkdir -p "$AIRFLOW_HOME/dags"
```

Copy this file into:

```text
~/airflow-learning/airflow-home/dags/hello_airflow.py
```

Use the example from this repository:

- [hello_airflow.py](hello_airflow.py)

## Run the DAG

In the Airflow UI:

- Open DAGs.
- Find `hello_airflow`.
- Trigger the DAG manually.
- Open the DAG run.
- Open the task log.

Expected log line:

```text
Hello from Airflow
```



## Navigation

- [Back to Airflow README](../../README.md)
