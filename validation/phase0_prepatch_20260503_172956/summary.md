# Mas E Phase 0 — Pre-Patch Baseline
# Captured: Sun May  3 17:29:58 UTC 2026
# Purpose : Comparison point before applying patch v2.3

---

## System

RAM used       : 471 MB / 969 MB
Swap used      : 12 MB
Swappiness     : 10

## Vectorizer

max_features   : 21
model size     : 1.7K

## Log

session lines  : 12
log fields     : ['input', 'metrics', 'decision', 'drift', 'timestamp']

## API

health         : <html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx/1.22.1</center>
</body>
</html>

## Files in this capture

endpoint_samples.json
latency_baseline.txt
log_schema_sample.json
log_schema_sample_pretty.json
memory_snapshot.txt
summary.md
vectorizer_info.txt

---

## What to compare after patch v2.3

| Metric         | Before (this file) | After (run capture again) |
|----------------|--------------------|---------------------------|
| RAM used       | 471 MB     | ?                         |
| max_features   | 21              | 100 (expected)            |
| log fields     | ['input', 'metrics', 'decision', 'drift', 'timestamp']        | + node_id, session_id     |
| lifecycle_phase| absent             | present (expected)        |
| health.node    | absent             | cell-0 (expected)         |
