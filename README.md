# GCP Real-Time Clickstream Pipeline (Staff Data Engineer Prep)

End-to-end modular streaming data engineering project built on Google Cloud Platform (`streaming-lab-515223`: Pub/Sub, Apache Beam, BigQuery, dbt, Terraform, Airflow) alongside comprehensive architecture documentation and Staff DE interview Q&As.

## Project Stages
- **`01-infrastructure/`** — BigQuery DDL, `Makefile` build targets, and Airflow bootstrap workflow DAG
- **`02-streaming-ingestion/`** *(Next)* — Python clickstream producer & Apache Beam streaming pipeline with DLQ routing
- **`03-warehouse-modeling/`** *(Upcoming)* — `dbt Core` multi-hop transformations (`staging` -> `intermediate` -> `marts`)
- **`04-orchestration/`** *(Upcoming)* — End-to-end Airflow DAGs & automated quality gates

## Documentation Index
- **01 - Developer Tooling**
  - [Homebrew & Python Virtual Environments](docs/01-developer-tooling/homebrew-and-python-venv.md)
  - [Git & GitHub Workflow](docs/01-developer-tooling/git-and-github-workflow.md)
  - [Git Commands Reference Guide](docs/01-developer-tooling/git-commands-reference.md)
  - [Modular Project Layout: Makefiles & Workflow DAGs vs. Google Stack](docs/01-developer-tooling/makefile-and-workflows-vs-google.md)
- **02 - GCP Infrastructure**
  - [What is Cloud Pub/Sub?](docs/02-gcp-infrastructure/what-is-pubsub.md)
  - [Pub/Sub, Subscriptions & Schema Deep Dive](docs/02-gcp-infrastructure/pubsub-and-schema-deep-dive.md)
  - [Retention, Replay (`seek`), Broker Rejections & DE Boundaries](docs/02-gcp-infrastructure/retention-replay-and-broker-rejections.md)
  - [Pub/Sub, ADC & BigQuery Setup](docs/02-gcp-infrastructure/pubsub-and-bigquery-setup.md)
  - [Apache Airflow Workflow Guide: `infra_bootstrap_dag.py`](docs/02-gcp-infrastructure/airflow-infra-bootstrap-dag-guide.md)
- **03 - Streaming Concepts** *(Coming in Stage 02)*
- **04 - Staff DE Interview Prep**
  - [Lab vs. Enterprise Production Gap Analysis](docs/04-staff-de-interview-prep/lab-vs-enterprise-production.md)