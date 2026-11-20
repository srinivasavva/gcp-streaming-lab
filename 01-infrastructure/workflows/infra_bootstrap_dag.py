"""
Stage 01 Workflow DAG: Provisions and verifies BigQuery landing tables.
Mirrors a Google PLX Workflow managing DDL initialization and schema checks.
"""
from datetime import datetime
from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryInsertJobOperator,
    BigQueryTableExistenceSensor,
)

PROJECT_ID = "streaming-lab-515223"
DATASET_ID = "streaming_lab"
TABLE_ID = "windowed_click_metrics"

with DAG(
    dag_id="01_infrastructure_ddl_bootstrap",
    start_date=datetime(2026, 1, 1),
    schedule=None,  # Triggered on deployment / manual bootstrap
    catchup=False,
    tags=["stage-01", "infrastructure", "ddl"],
) as dag:

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

    verify_table_exists = BigQueryTableExistenceSensor(
        task_id="verify_windowed_click_metrics_exists",
        project_id=PROJECT_ID,
        dataset_id=DATASET_ID,
        table_id=TABLE_ID,
        timeout=60,
        poke_interval=10,
    )

    create_landing_table >> verify_table_exists