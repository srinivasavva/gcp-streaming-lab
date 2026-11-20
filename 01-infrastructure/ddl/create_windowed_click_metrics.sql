-- BigQuery Destination Table: 1-Minute Windowed Clickstream Aggregates
-- Partitioned by event time (window_start) for accurate late-data backfills
-- Clustered by event_type for Capacitor block pruning

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