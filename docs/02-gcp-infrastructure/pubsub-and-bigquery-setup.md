# GCP Infrastructure Setup: Pub/Sub, ADC & BigQuery

## 1. Project, ADC & Billing Guardrails
- **Project ID:** `streaming-lab-515223` (created under `No organization` for personal isolation).
- **ADC Quota Sync:** Running `gcloud auth application-default set-quota-project streaming-lab-515223` aligns local Python SDK credentials with the active CLI project.
- **Budget Alert:** `$5.00` target alert protects a Paid billing account while staying inside Always-Free quotas (Pub/Sub: 10 GiB/month free; BigQuery: 1 TiB queries + 10 GiB storage/month free).

## 2. Cloud Pub/Sub Resources
- **Topic (`clickstream-events`):** Main ingestion endpoint for JSON clickstream events.
- **Dead-Letter Queue (`clickstream-dlq`):** Quarantine topic for malformed JSON or schema violations.
- **Pull Subscription (`clickstream-sub`):** Durable cursor configured with `--retain-acked-messages --message-retention-duration=7d` for point-in-time replay via `gcloud pubsub subscriptions seek`.

## 3. BigQuery Destination Table Design (`01-infrastructure/ddl/create_windowed_click_metrics.sql`)
```sql
CREATE TABLE IF NOT EXISTS `streaming-lab-515223.streaming_lab.windowed_click_metrics` (
  window_start TIMESTAMP,
  window_end TIMESTAMP,
  event_type STRING,
  event_count INT64,
  unique_users INT64,
  total_cart_value FLOAT64,
  processed_at TIMESTAMP
)
PARTITION BY DATE(window_start)
CLUSTER BY event_type;
```
- **Event-Time Partitioning (`DATE(window_start)`):** Places late-arriving data into the historical date partition of the user's action rather than ingestion time.
- **Clustering (`event_type`):** Co-locates rows by event type inside Capacitor storage blocks to minimize scanned bytes.
- **Google Internal Mapping:** External managed version of Dremel / Capacitor tables normally populated by PLX SQL workflows.

## 4. Staff Data Engineer Interview Questions & Model Answers

### Q1: *"Why partition a streaming BigQuery table on `DATE(window_start)` (event time) instead of `DATE(processed_at)` (ingestion time)?"*
- **Model Answer:** Downstream analysts query business metrics by when the user action occurred (`window_start`), not when the pipeline processed it. Event-time partitioning enables partition pruning on business date filters and ensures late-arriving records or historical replays land in their true historical partition.

### Q2: *"How do partitioning and clustering work together in BigQuery?"*
- **Model Answer:** Partitioning divides the table into coarse time-based segments (`DATE(window_start)`) so BigQuery skips entire days before scanning. Clustering (`CLUSTER BY event_type`) sorts rows *within* each partition so Capacitor block metadata pruning skips irrelevant blocks inside a single day.