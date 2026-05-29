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

## What We Learned

- Airflow runs as local WSL processes when started manually.
- The scheduler parses DAG files from the `dags` folder.
- A DAG file defines structure.
- A task contains work.
- Logs are the first place to check task behavior.

## Stop Airflow

In the terminal running Airflow:

```bash
Ctrl+C
```

Airflow is not a Windows service in this step. It runs only while you start it.

## Navigation

- [Back to Airflow README](../../README.md)
