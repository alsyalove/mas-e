# Mas E Phase 0 — Pre-Patch Baseline
# Captured: Fri May  8 07:55:10 UTC 2026
# Purpose : Comparison point before applying patch v2.3

---

## System

RAM used       : 451 MB / 969 MB
Swap used      : 27 MB
Swappiness     : 10

## Vectorizer

max_features   : 67
model size     : 3.4K

## Log

session lines  : 86
log fields     : ['node_id', 'session_id', 'input', 'metrics', 'decision', 'drift', 'timestamp']

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
| RAM used       | 451 MB     | ?                         |
| max_features   | 67              | 100 (expected)            |
| log fields     | ['node_id', 'session_id', 'input', 'metrics', 'decision', 'drift', 'timestamp']        | + node_id, session_id     |
| lifecycle_phase| absent             | present (expected)        |
| health.node    | absent             | cell-0 (expected)         |
