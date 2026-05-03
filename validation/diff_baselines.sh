#!/bin/bash
# Mas E Observatory — Baseline Diff Script
# Jalankan SETELAH apply patch v2.3 dan capture baseline baru
# Usage: bash validation/diff_baselines.sh

set -e

VALIDATION_DIR="validation"

# Cari dua folder capture terbaru
CAPTURES=($(ls -dt "$VALIDATION_DIR"/phase0_prepatch_* 2>/dev/null))

if [ ${#CAPTURES[@]} -lt 2 ]; then
  echo ""
  echo "ERROR: Butuh minimal 2 baseline capture untuk membandingkan."
  echo ""
  echo "Langkah:"
  echo "  1. Jalankan capture SEBELUM patch : bash validation/capture_baseline.sh"
  echo "  2. Apply patch v2.3"
  echo "  3. Jalankan capture SESUDAH patch : bash validation/capture_baseline.sh"
  echo "  4. Jalankan script ini kembali"
  echo ""
  exit 1
fi

BEFORE="${CAPTURES[1]}"
AFTER="${CAPTURES[0]}"

echo ""
echo "========================================"
echo "  Mas E Phase 0 — Baseline Diff"
echo "========================================"
echo "  BEFORE : $BEFORE"
echo "  AFTER  : $AFTER"
echo "========================================"
echo ""

# -----------------------------------------------------------
# 1. Memory
# -----------------------------------------------------------
echo "## Memory"
echo ""
MEM_BEFORE=$(grep "RAM used" "$BEFORE/summary.md" 2>/dev/null | awk '{print $4}')
MEM_AFTER=$(grep  "RAM used" "$AFTER/summary.md"  2>/dev/null | awk '{print $4}')
echo "  RAM before : ${MEM_BEFORE} MB"
echo "  RAM after  : ${MEM_AFTER} MB"
echo ""

# -----------------------------------------------------------
# 2. Vectorizer
# -----------------------------------------------------------
echo "## Vectorizer"
echo ""
FEAT_BEFORE=$(grep "max_features" "$BEFORE/summary.md" 2>/dev/null | awk '{print $3}')
FEAT_AFTER=$(grep  "max_features" "$AFTER/summary.md"  2>/dev/null | awk '{print $3}')
echo "  max_features before : $FEAT_BEFORE"
echo "  max_features after  : $FEAT_AFTER"
if [ "$FEAT_AFTER" = "100" ]; then
  echo "  Vectorizer upgrade  : OK (20 -> 100)"
else
  echo "  WARNING: max_features after = $FEAT_AFTER (expected 100)"
fi
echo ""

# -----------------------------------------------------------
# 3. Log Schema
# -----------------------------------------------------------
echo "## Log Schema"
echo ""
if [ -f "$BEFORE/log_schema_sample.json" ] && [ -f "$AFTER/log_schema_sample.json" ]; then
  FIELDS_BEFORE=$(python3 -c "
import json
with open('$BEFORE/log_schema_sample.json') as f:
    r = json.load(f)
print(sorted(r.keys()))
" 2>/dev/null || echo "?")
  FIELDS_AFTER=$(python3 -c "
import json
with open('$AFTER/log_schema_sample.json') as f:
    r = json.load(f)
print(sorted(r.keys()))

# Check new fields
r_keys = set(r.keys())
expected_new = {'node_id', 'session_id'}
found_new = expected_new.intersection(r_keys)
missing_new = expected_new - r_keys
if found_new:
    print('New fields found    :', found_new)
if missing_new:
    print('New fields MISSING  :', missing_new)

# Check lifecycle_phase in decision
if 'decision' in r and 'lifecycle_phase' in r['decision']:
    print('lifecycle_phase     : OK ->', r['decision']['lifecycle_phase'])
else:
    print('lifecycle_phase     : MISSING in decision')
" 2>/dev/null || echo "?")
  echo "  Fields before : $FIELDS_BEFORE"
  echo "  Fields after  :"
  echo "$FIELDS_AFTER" | sed 's/^/    /'
else
  echo "  Log schema samples tidak ditemukan di salah satu capture."
fi
echo ""

# -----------------------------------------------------------
# 4. Health Response
# -----------------------------------------------------------
echo "## Health Endpoint"
echo ""
HEALTH_BEFORE=$(grep "^health" "$BEFORE/summary.md" 2>/dev/null | sed 's/health.*: //')
HEALTH_AFTER=$(grep  "^health" "$AFTER/summary.md"  2>/dev/null | sed 's/health.*: //')
echo "  Before : $HEALTH_BEFORE"
echo "  After  : $HEALTH_AFTER"
if echo "$HEALTH_AFTER" | grep -q '"node"'; then
  echo "  node field : OK"
else
  echo "  WARNING: node field tidak ada di health response"
fi
echo ""

# -----------------------------------------------------------
# 5. Latency
# -----------------------------------------------------------
echo "## Latency"
echo ""
if [ -f "$BEFORE/latency_baseline.txt" ] && [ -f "$AFTER/latency_baseline.txt" ]; then
  LAT_BEFORE=$(grep "Average latency" "$BEFORE/latency_baseline.txt" | awk '{print $3}')
  LAT_AFTER=$(grep  "Average latency" "$AFTER/latency_baseline.txt"  | awk '{print $3}')
  echo "  Avg latency before : ${LAT_BEFORE}s"
  echo "  Avg latency after  : ${LAT_AFTER}s"
  echo ""
  echo "  Note: Latency sedikit naik adalah normal karena YAML loading"
  echo "        dan log schema yang lebih besar."
  echo "        Jika naik > 3x, periksa YAML parsing di engine.py."
fi
echo ""

# -----------------------------------------------------------
# Summary
# -----------------------------------------------------------
echo "========================================"
echo "  Diff selesai."
echo ""
echo "  File capture tersimpan di:"
echo "  BEFORE : $BEFORE"
echo "  AFTER  : $AFTER"
echo "========================================"
echo ""
