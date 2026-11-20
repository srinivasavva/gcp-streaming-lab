PROJECT_ID ?= streaming-lab-515223
DATASET ?= streaming_lab

.PHONY: validate-ddl deploy-ddl verify-table

validate-ddl:
	bq query --use_legacy_sql=false --dry_run < ddl/create_windowed_click_metrics.sql

deploy-ddl:
	bq query --use_legacy_sql=false < ddl/create_windowed_click_metrics.sql

verify-table:
	bq show --schema --format=prettyjson $(PROJECT_ID):$(DATASET).windowed_click_metrics