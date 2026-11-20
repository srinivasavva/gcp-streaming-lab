# Apache Airflow Workflow Guide: `01-infrastructure/workflows/infra_bootstrap_dag.py`

## 1. What This Workflow File Does (Google PLX Workflow Mapping)
In Google’s internal stack, a **PLX Workflow** defines a dependency graph of SQL scripts and verification checks (e.g., running a DDL/DML query and verifying the resulting Dremel table exists before downstream consumers read it).

In external GCP/open-source environments, **Apache Airflow** (managed on GCP as **Cloud Composer**) performs that exact orchestration role using Python **DAGs (Directed Acyclic Graphs)**:
- **`infra_bootstrap_dag.py`** executes our BigQuery landing table DDL (`01-infrastructure/ddl/create_windowed_click_metrics.sql`) and runs a sensor check to confirm the table exists before any streaming or transformation pipeline starts.

---

## 2. Line-by-Line Explanation of `infra_bootstrap_dag.py`

### Lines 1–4: Module Docstring
```python
"""
Stage 01 Workflow DAG: Provisions and verifies BigQuery landing tables.
Mirrors a Google PLX Workflow managing DDL initialization and schema checks.
"""
```
- **What it does:** Documents the purpose of the DAG in Python and appears as the DAG description inside the Airflow Web UI.

---

### Lines 5–10: Standard & Google Cloud Provider Imports
```python
from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
    BigQueryTableExistenceSensor,
)
```
- **`from datetime import datetime`:** Provides the `start_date` timestamp required by Airflow's scheduler to anchor the DAG's timeline.
- **`from airflow import DAG`:** Imports the core `DAG` context manager used to define the workflow container and its scheduling rules.
- **`BigQueryInsertJobOperator`:** An Airflow **Operator** (an action task) that submits a SQL query or DDL job to BigQuery's `jobs.insert` API and waits for it to finish.
- **`BigQueryTableExistenceSensor`:** An Airflow **Sensor** (a polling gatekeeper task) that repeatedly checks BigQuery metadata until a target table exists (or times out).

---

### Lines 12–14: Environment & Table Configuration Constants
```python
PROJECT_ID = "streaming-lab-515223"
DATASET_ID = "streaming_lab"
TABLE_ID = "windowed_click_metrics"
```
- **What it does:** Centralizes GCP project, dataset, and table identifiers at the top of the file so you never hardcode resource names inside multiple tasks.
- **Enterprise Production Upgrade:** In multi-environment (`dev`/`stage`/`prod`) deployments, these values are pulled dynamically from Airflow Variables or environment variables (`os.getenv("GCP_PROJECT_ID", "streaming-lab-515223")`).

---

### Lines 16–22: DAG Definition Block (`with DAG(...) as dag:`)
```python
with DAG(
    dag_id="01_infrastructure_ddl_bootstrap",
    start_date=datetime(2026, 1, 1),
    schedule=None,  # Triggered on deployment / manual bootstrap
    catchup=False,
    tags=["stage-01", "infrastructure", "ddl"],
) as dag:
```
- **`dag_id="01_infrastructure_ddl_bootstrap"`:** The unique identifier for this workflow in Airflow (equivalent to a PLX Workflow ID). Prefixed with `01_` so stages sort cleanly in the Airflow UI.
- **`start_date=datetime(2026, 1, 1)`:** The logical date from which Airflow considers the DAG valid to run.
- **`schedule=None`:** Tells Airflow **not** to run this on a recurring cron timer (like `@hourly` or `@daily`). Infrastructure DDL bootstrap workflows run **on demand** during deployment or CI/CD releases.
- **`catchup=False`:** Prevents Airflow from backfilling historical runs between `start_date` and today when the DAG is first turned on.
- **`tags=[...]`:** Adds searchable filter pills in the Airflow UI so teams can filter all `stage-01` or `ddl` workflows instantly.

---

### Lines 24–33: Task 1 — Execute the BigQuery DDL File (`BigQueryInsertJobOperator`)
```python
    create_landing_table = BigQueryInsertJobOperator(
        task_id="create_windowed_click_metrics_table",
        configuration={
            "query": {
                "query": "{% include '../ddl/create_windowed_click_metrics.sql' %}",
                "useLegacySql": False,
            }
        },
        project_id=PROJECT_ID,
    )
```
- **`task_id="create_windowed_click_metrics_table"`:** Unique name of this step inside the DAG graph.
- **`configuration={"query": {...}}`:** Mirrors the exact JSON payload of BigQuery's REST API `jobs.insert` endpoint.
- **`"{% include '../ddl/create_windowed_click_metrics.sql' %}"`:** Uses Airflow's **Jinja templating engine** to read your external `.sql` file at runtime and inject its SQL text directly into the job—keeping SQL cleanly separated from Python orchestration code.
- **`"useLegacySql": False`:** Enforces **GoogleSQL (Standard SQL)** syntax (required for `PARTITION BY`, `CLUSTER BY`, and `CREATE TABLE IF NOT EXISTS`).
- **`project_id=PROJECT_ID`:** Tells BigQuery which GCP project executes and bills the job (`streaming-lab-515223`).

---

### Lines 35–42: Task 2 — Verify Table Creation (`BigQueryTableExistenceSensor`)
```python
    verify_table_exists = BigQueryTableExistenceSensor(
        task_id="verify_windowed_click_metrics_exists",
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        table_id=TABLE_ID,
        timeout=60,
        poke_interval=10,
    )
```
- **Why this task exists:** Even after a DDL statement returns, metadata propagation or cross-stage handoffs benefit from an explicit verification gate before downstream streaming pipelines start writing rows.
- **`poke_interval=10`:** Checks BigQuery every **10 seconds** to see if `streaming_lab.windowed_click_metrics` is live.
- **`timeout=60`:** Fails the task cleanly after **60 seconds** if the table still hasn't appeared, preventing stuck worker slots.

---

### Line 44: Dependency Wiring (`>>` Bitshift Operator)
```python
    create_landing_table >> verify_table_exists
```
- **What it does:** Declares the directed edge in the DAG: `verify_table_exists` will **only** start after `create_landing_table` finishes with state `SUCCESS` (equivalent to defining upstream/downstream node dependencies in a PLX Workflow).

---

## 3. How to Maintain & Extend This Workflow

### Scenario A: Updating Existing SQL (`create_windowed_click_metrics.sql`)
- **Do you need to edit `infra_bootstrap_dag.py`?** **No.**
- Because the DAG loads `../ddl/create_windowed_click_metrics.sql` dynamically via `{% include %}`, editing the `.sql` file (for example, adding a new column or updating `OPTIONS(...)`) automatically updates what Airflow executes on the next run.
- **Note on BigQuery `CREATE TABLE IF NOT EXISTS`:** If a table already exists in BigQuery, `CREATE TABLE IF NOT EXISTS` is a no-op. To add columns to an existing production table, either write an idempotent `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` DDL file or manage schema evolution via Terraform.

### Scenario B: Adding a Second DDL File (e.g., `create_dlq_audit_log.sql`)
When you add a new `.sql` file inside `01-infrastructure/ddl/`, update three places:
1. **`01-infrastructure/Makefile`:** Add `validate-dlq-ddl` and `deploy-dlq-ddl` targets (or loop over `ddl/*.sql`).
2. **`01-infrastructure/workflows/infra_bootstrap_dag.py`:** Add a new `BigQueryInsertJobOperator` + `BigQueryTableExistenceSensor` pair and wire them in parallel (so both tables deploy concurrently):
   ```python
   create_dlq_table = BigQueryInsertJobOperator(
       task_id="create_dlq_audit_log_table",
       configuration={
           "query": {
               "query": "{% include '../ddl/create_dlq_audit_log.sql' %}",
               "useLegacySql": False,
           }
       },
       project_id=PROJECT_ID,
   )

   verify_dlq_table = BigQueryTableExistenceSensor(
       task_id="verify_dlq_audit_log_exists",
       project_id=PROJECT_ID,
       dataset_id=DATASET_ID,
       table_id="dlq_audit_log",
       timeout=60,
       poke_interval=10,
   )

   # Run both table creations in parallel:
   create_landing_table >> verify_table_exists
   create_dlq_table >> verify_dlq_table
   ```
3. **`README.md`:** Add the new guide link under the Documentation Index.

---

## 4. Lead / Staff Data Engineer Interview Questions & Model Answers

### Q1: *"What is the difference between an Airflow Operator and an Airflow Sensor, and when can Sensors become an anti-pattern at scale?"*
- **Model Answer:** An **Operator** performs an action (such as submitting a BigQuery job or triggering a Dataflow pipeline), whereas a **Sensor** polls an external condition until it becomes true (such as waiting for a BigQuery table or GCS file to arrive). In standard `poke` mode, a Sensor occupies a worker slot continuously while sleeping; at scale with hundreds of concurrent sensors, this causes **worker slot starvation**. Production Airflow DAGs avoid this by setting **`mode="reschedule"`** (releasing the worker slot between checks) or using **Deferrable Operators/Sensors** (asyncio triggers).

### Q2: *"Why keep SQL logic inside standalone `.sql` files loaded via Jinja `{% include %}` rather than embedding multi-line SQL strings inside Python DAG files?"*
- **Model Answer:** Separating `.sql` files from Python orchestration enables native SQL syntax highlighting, dry-run validation (`bq query --dry_run` in `Makefile`/CI), isolated code reviews, and reusability across CLI tools, CI checks, and Airflow without touching orchestration logic.