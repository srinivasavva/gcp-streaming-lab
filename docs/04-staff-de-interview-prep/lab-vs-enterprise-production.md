# Staff Data Engineer Prep: $0 GCP Lab vs. Enterprise Production

## 1. Six Real-World Workplace Production Gaps & How to Bridge Them
1. **Distributed Cluster Operations & Skew Tuning (Dataflow / Spark):** Lab runs locally via `DirectRunner`; production runs on distributed workers with network shuffles, stragglers, and OOM risks. Bridge by running one brief Dataflow validation job (~$0.05) and practicing **key salting**.
2. **Orchestration & Hybrid Batch/Streaming (Airflow / Cloud Composer):** Lab runs CLI scripts; production orchestrates backfills, `dbt` runs, and SLAs via Airflow DAGs. Bridge via local Docker Airflow (`docker compose up`).
3. **CI/CD, Automated Testing & IaC (Terraform + GitHub Actions):** Lab uses imperative `gcloud`/`bq` commands; production uses declarative Terraform + `pytest` (`TestStream`) in CI/CD. Bridge by translating CLI setup to `main.tf` and GitHub Actions.
4. **Production IAM, Service Accounts & VPC Security:** Lab uses personal ADC credentials; production uses least-privilege Service Accounts, VPC Service Controls, and CMEK.
5. **Real Upstream CDC & Schema Governance:** Lab emits controlled Python events; production enforces Pub/Sub/Confluent Schema Registries and handles breaking changes + late data.
6. **Open-Source & Multi-Cloud Equivalents:** Map Pub/Sub -> Kafka, Beam/Dataflow -> Spark/Flink, BigQuery -> Iceberg/Snowflake, and run `dbt Core` locally.

---

## 2. Stage 01 Comparison Matrix: Foundation & Ingestion

| Layer | $0 Lab Implementation | Enterprise Production Setup | Staff DE Interview Talking Point |
| :--- | :--- | :--- | :--- |
| **Repo & Build Structure** | Modular `01-infrastructure/` with `Makefile`, `ddl/`, and `workflows/` DAG. | Declarative **Terraform** + **GitHub Actions** CI/CD + **Airflow**. | Separate deploy-time infra automation from runtime data orchestration. |
| **Org & Project Hierarchy** | Single project (`streaming-lab-515223`) under `No organization` with $5 budget alert. | Corporate **Organization + Folders** (`dev`/`stage`/`prod`) with cascading org policies & FinOps labels. | Isolate blast radius by environment and enforce programmatic cost governance. |
| **Auth & IAM** | Personal ADC user credentials (`gcloud auth`). | Least-privilege **Service Accounts** + VPC Service Controls. | Follow principle of least privilege; separate producer and consumer identities. |
| **Message Bus & Retention** | Pub/Sub topics + subscription with `7d` retained acked messages + DLQ topic. | **Pub/Sub Schema Registry** (Avro/Protobuf) + `7d` subscription retention + fallback DLQ. | Reject breaking structural changes at the broker edge and enable point-in-time replay. |
| **Warehouse Table** | BigQuery partitioned by `DATE(window_start)`, clustered by `event_type`. | Same + `require_partition_filter = true` + idempotent `MERGE` upserts. | Partition on event time for accurate late-data backfills and prevent replay duplicates. |