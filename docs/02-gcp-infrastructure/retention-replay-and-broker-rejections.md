# Message Retention, Replay (`seek`), Broker Rejections & DE Role Boundaries

## 1. Data Engineers vs. Application Microservices (Ownership Boundaries)
1. **Application Microservices (Owned by Backend SWEs):**
   - Customer-facing services (`CheckoutService`, `PaymentService`, `MobileGateway`) handle user traffic and publish domain events to Pub/Sub or Kafka.
   - **Staff DE Role:** Co-own the event schema contract (`.proto` / Avro) with SWE teams so upstream deployments cannot silently break downstream analytics.
2. **Streaming & Batch Pipelines (Owned by Data Engineers):**
   - Apache Beam, Spark, Flink, and `dbt` pipelines that ingest from Pub/Sub/Kafka, enforce business-level data quality, compute windowed aggregations, and load BigQuery/Snowflake.
3. **Data-Plane Ingestion Connectors (Owned by Staff/Senior DEs):**
   - Lightweight Python/Go services written by Data Engineers to poll external third-party REST APIs (e.g., Salesforce, Stripe, vendor webhooks), manage rate limits/pagination, and publish standardized events into Pub/Sub.
4. **Why We Build `producer.py` in This Lab:**
   - Simulates an upstream backend microservice emitting realistic traffic—including intentional edge cases (out-of-order late timestamps, duplicate `event_id`s, and malformed JSON payloads) so we can verify pipeline resilience end-to-end.

---

## 2. Pub/Sub Message Retention & Point-in-Time Replay (`seek`)

### Retention Limits & Cost (`7d` Subscription vs. `31d` Topic)
- **Subscription Retention (`7d` maximum):** Configuring `--retain-acked-messages --message-retention-duration=7d` preserves both acknowledged and unacknowledged messages for 7 full days at `$0.00` lab cost (inside the 10 GiB/month Always-Free tier).
- **Topic Retention (`31d` maximum):** For longer compliance or monthly financial reconciliation replay windows, retention can be enabled at the **Topic** level (`gcloud pubsub topics update clickstream-events --message-retention-duration=31d`).

### Incident Response Replay Workflow
1. Stop the buggy subscriber pipeline so it stops writing bad metrics.
2. Deploy the fixed pipeline code.
3. Rewind the subscription's acknowledgement cursor back to a timestamp prior to the bug (or to a pre-deployment **Pub/Sub Snapshot**) using `seek`:
   ```bash
   gcloud pubsub subscriptions seek clickstream-sub --time="2026-11-19T17:00:00Z"
   ```
4. Pub/Sub marks all messages published after that timestamp as unacknowledged again and redelivers them automatically to the fixed pipeline.

### How Our BigQuery Data Model Handles Replays Without Double-Counting (Idempotency)
1. **Event-Level Deduplication (`event_id`):** Deduplicating incoming events by UUID `event_id` protects against Pub/Sub at-least-once redeliveries.
2. **Window-Level Idempotent `MERGE` (Composite Grain Key):** Our destination table uses the natural grain **`(window_start, window_end, event_type)`**. Replayed or late-updated window results execute an atomic BigQuery **`MERGE`** on `(window_start, window_end, event_type)` that overwrites metrics cleanly in place instead of appending duplicate rows.

---

## 3. What Happens When Pub/Sub Rejects a Payload (`HTTP 400 INVALID_ARGUMENT`)?
When a Pub/Sub topic has a **Schema (Protobuf or Avro)** attached, Pub/Sub validates every incoming message **synchronously inside the `Publish` API call** before persisting anything:
1. A schema violation (e.g., `"cart_value": "FREE"` instead of `double`) triggers an immediate **`INVALID_ARGUMENT` (HTTP 400)** error back to the producer.
2. The rejected payload **never enters the topic**, **never enters any subscription**, and **never reaches Apache Beam**.
3. **How Production Producers Handle `HTTP 400` Rejections (So Data Is Not Lost):**
   - **Producer-Side Fallback DLQ:** Catch `google.api_core.exceptions.InvalidArgument` in the producer's publish wrapper and route the raw payload + exception stack trace to a schema-free `raw-unvalidated-dlq` topic or GCS quarantine bucket.
   - **Fail-Fast in CI / Canary:** Surface the `400` exception immediately during automated integration tests or canary rollouts so broken app releases are blocked before 100% production traffic.
   - **Observability & Alerting:** Increment `pubsub_schema_rejection_total` metrics to trigger an on-call alert to the upstream producer team.

---

## 4. Staff Data Engineer Interview Questions & Model Answers

### Q1: *"You discover a bug in your streaming aggregation logic that ran all weekend. Pub/Sub already ACKed 20 million messages. How do you recover without losing data or double-counting?"*
- **Model Answer:**
  1. Ensure **acknowledged message retention** is enabled on the subscription (up to 7 days) or topic (up to 31 days), or take regular **Pub/Sub Snapshots** prior to deployments.
  2. Halt the faulty pipeline, deploy the patched code, and execute **`gcloud pubsub subscriptions seek`** to rewind the cursor to a timestamp before the bad deployment.
  3. Guarantee **end-to-end idempotency** in BigQuery so replayed windows do not double-count: deduplicate raw events by `event_id` and write window aggregates using an atomic BigQuery **`MERGE`** keyed on `(window_start, window_end, event_type)` (or partition-level `WRITE_TRUNCATE` for batch backfills).

### Q2: *"Why validate schemas in both the message broker (Pub/Sub/Kafka Schema Registry) AND inside your streaming pipeline (Beam/Spark)?"*
- **Model Answer:**
  - **Defense in depth:** Broker schemas enforce **structural/syntactic contracts** (field types, required fields, wire compatibility) at the ingestion boundary, rejecting bad producer deployments immediately with `HTTP 400 INVALID_ARGUMENT` before dirty bytes pollute downstream consumers.
  - However, broker schemas cannot express **semantic business rules** (e.g., negative `cart_value`, impossible future timestamps, invalid country codes). Pipeline-level validation `DoFn`s catch semantic anomalies and divert them to a **Dead-Letter Queue (DLQ)** without stalling valid traffic.

### Q3: *"If a Pub/Sub topic rejects a message with `INVALID_ARGUMENT`, where does that message go? Does Pub/Sub send it to a Dead-Letter Queue?"*
- **Model Answer:**
  - **No.** Pub/Sub's built-in Dead-Letter Topic feature only applies to *undeliverable messages sitting inside a subscription* (e.g., when a consumer repeatedly fails to `ACK` after `max-delivery-attempts`).
  - When a topic's Schema rejects a message during `Publish()`, the message never enters the topic—the producer receives an immediate `INVALID_ARGUMENT (400)` exception and must catch it in producer-side error handling (routing the raw bytes to a schema-free fallback DLQ topic or GCS bucket).

### Q4: *"How do you handle duplicate events in a streaming pipeline when Pub/Sub only guarantees at-least-once delivery?"*
- **Model Answer:**
  - Pub/Sub guarantees **at-least-once** delivery, meaning network timeouts between a worker and Pub/Sub can cause a message to be redelivered even after processing.
  - We handle this at three levels: (1) use **Dataflow's built-in Pub/Sub deduplication** via a custom `id_label` (`event_id`) attribute within a short window, (2) maintain stateful deduplication by `event_id` in Beam if longer windows are needed, and (3) design the BigQuery sink around **idempotent `MERGE` upserts** keyed on the natural aggregate grain `(window_start, window_end, event_type)`.