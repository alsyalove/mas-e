#!/bin/bash
# Mas E Observatory — Baseline Capture Script
# Jalankan SEBELUM apply patch v2.3
# Output disimpan ke validation/phase0_prepatch_*/

set -e

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUT="validation/phase0_prepatch_${TIMESTAMP}"
mkdir -p "$OUT"

echo ""
echo "========================================"
echo "  Mas E Phase 0 — Baseline Capture"
echo "  Output: $OUT"
echo "========================================"
echo ""

# -----------------------------------------------------------
# 1. Memory Snapshot
# -----------------------------------------------------------
echo "[1/6] Capturing memory snapshot..."
{
  echo "# Memory Snapshot — $(date)"
  echo ""
  echo "## free -m"
  free -m
  echo ""
  echo "## /proc/meminfo (ringkas)"
  grep -E 'MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree' /proc/meminfo
  echo ""
  echo "## Swappiness"
  echo "vm.swappiness = $(cat /proc/sys/vm/swappiness)"
} > "$OUT/memory_snapshot.txt"
echo "   -> $OUT/memory_snapshot.txt"

# -----------------------------------------------------------
# 2. Endpoint Samples
# -----------------------------------------------------------
echo "[2/6] Capturing endpoint samples..."

# Pastikan service running
if ! curl -s http://localhost/health > /dev/null 2>&1; then
  echo "   ERROR: Service tidak merespons di http://localhost"
  echo "   Pastikan mas-e service running sebelum menjalankan script ini."
  exit 1
fi

{
  echo "{"
  echo "  \"captured_at\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\","
  echo ""
  
  # Health endpoint
  HEALTH=$(curl -s http://localhost/health)
  echo "  \"health\": $HEALTH,"
  echo ""

  # Process — sample 1
  R1=$(curl -s -X POST http://localhost/process \
    -H "Content-Type: application/json" \
    -d '{"text": "kebenaran logika pengetahuan"}')
  echo "  \"sample_clarity\": $R1,"
  echo ""

  # Process — sample 2
  R2=$(curl -s -X POST http://localhost/process \
    -H "Content-Type: application/json" \
    -d '{"text": "emosi intuisi perasaan persepsi"}')
  echo "  \"sample_ambiguous\": $R2,"
  echo ""

  # Process — sample 3
  R3=$(curl -s -X POST http://localhost/process \
    -H "Content-Type: application/json" \
    -d '{"text": "analisis observasi struktur penalaran"}')
  echo "  \"sample_coherent\": $R3"
  echo "}"
} > "$OUT/endpoint_samples.json"
echo "   -> $OUT/endpoint_samples.json"

# -----------------------------------------------------------
# 3. Log Schema Sample
# -----------------------------------------------------------
echo "[3/6] Capturing log schema sample..."
if [ -f ~/mas_e/logs/session.jsonl ]; then
  tail -n 1 ~/mas_e/logs/session.jsonl > "$OUT/log_schema_sample.json"
  # Pretty print jika bisa
  python3 -m json.tool "$OUT/log_schema_sample.json" > "$OUT/log_schema_sample_pretty.json" 2>/dev/null || true
  echo "   -> $OUT/log_schema_sample.json"
  echo "   -> $OUT/log_schema_sample_pretty.json"
else
  echo "   WARNING: logs/session.jsonl tidak ditemukan"
fi

# -----------------------------------------------------------
# 4. Vectorizer Info
# -----------------------------------------------------------
echo "[4/6] Capturing vectorizer metadata..."
{
  echo "# Vectorizer Metadata — $(date)"
  echo ""
  source ~/mas_e/venv/bin/activate 2>/dev/null || true
  cd ~/mas_e 2>/dev/null || true
  python3 -c "
from app.vectorizer import get_vectorizer
v = get_vectorizer()
features = v.get_feature_names_out()
print('max_features:', len(features))
print('features:', list(features))
print('params:', v.get_params())
" 2>/dev/null || echo "ERROR: Tidak bisa load vectorizer"
  echo ""
  echo "## Model file"
  ls -lh ~/mas_e/models/vectorizer.pkl 2>/dev/null || echo "Model file tidak ditemukan"
} > "$OUT/vectorizer_info.txt"
echo "   -> $OUT/vectorizer_info.txt"

# -----------------------------------------------------------
# 5. Latency Baseline
# -----------------------------------------------------------
echo "[5/6] Measuring response latency (10 requests)..."
{
  echo "# Latency Baseline — $(date)"
  echo ""
  TOTAL=0
  for i in $(seq 1 10); do
    T=$(curl -s -o /dev/null -w "%{time_total}" \
      -X POST http://localhost/process \
      -H "Content-Type: application/json" \
      -d '{"text": "kebenaran logika observasi"}')
    echo "  Request $i: ${T}s"
    TOTAL=$(python3 -c "print(round($TOTAL + $T, 4))")
  done
  AVG=$(python3 -c "print(round($TOTAL / 10, 4))")
  echo ""
  echo "Average latency: ${AVG}s"
  echo "Total (10 req) : ${TOTAL}s"
} > "$OUT/latency_baseline.txt"
echo "   -> $OUT/latency_baseline.txt"

# -----------------------------------------------------------
# 6. Summary Report
# -----------------------------------------------------------
echo "[6/6] Writing summary report..."
{
  echo "# Mas E Phase 0 — Pre-Patch Baseline"
  echo "# Captured: $(date)"
  echo "# Purpose : Comparison point before applying patch v2.3"
  echo ""
  echo "---"
  echo ""
  echo "## System"
  echo ""
  MEM_USED=$(free -m | awk '/^Mem:/ {print $3}')
  MEM_TOTAL=$(free -m | awk '/^Mem:/ {print $2}')
  SWAP_USED=$(free -m | awk '/^Swap:/ {print $3}')
  echo "RAM used       : ${MEM_USED} MB / ${MEM_TOTAL} MB"
  echo "Swap used      : ${SWAP_USED} MB"
  echo "Swappiness     : $(cat /proc/sys/vm/swappiness)"
  echo ""
  echo "## Vectorizer"
  echo ""
  FEAT=$(cd ~/mas_e 2>/dev/null && source venv/bin/activate 2>/dev/null && \
    python3 -c "from app.vectorizer import get_vectorizer; print(len(get_vectorizer().get_feature_names_out()))" 2>/dev/null || echo "?")
  echo "max_features   : $FEAT"
  MODEL_SIZE=$(ls -lh ~/mas_e/models/vectorizer.pkl 2>/dev/null | awk '{print $5}' || echo "?")
  echo "model size     : $MODEL_SIZE"
  echo ""
  echo "## Log"
  echo ""
  LOG_LINES=$(wc -l < ~/mas_e/logs/session.jsonl 2>/dev/null || echo "0")
  echo "session lines  : $LOG_LINES"
  LOG_FIELDS=$(tail -n 1 ~/mas_e/logs/session.jsonl 2>/dev/null | \
    python3 -c "import json,sys; r=json.load(sys.stdin); print(list(r.keys()))" 2>/dev/null || echo "?")
  echo "log fields     : $LOG_FIELDS"
  echo ""
  echo "## API"
  echo ""
  HEALTH=$(curl -s http://localhost/health 2>/dev/null || echo '{"status":"unreachable"}')
  echo "health         : $HEALTH"
  echo ""
  echo "## Files in this capture"
  echo ""
  ls "$OUT/"
  echo ""
  echo "---"
  echo ""
  echo "## What to compare after patch v2.3"
  echo ""
  echo "| Metric         | Before (this file) | After (run capture again) |"
  echo "|----------------|--------------------|---------------------------|"
  echo "| RAM used       | ${MEM_USED} MB     | ?                         |"
  echo "| max_features   | $FEAT              | 100 (expected)            |"
  echo "| log fields     | $LOG_FIELDS        | + node_id, session_id     |"
  echo "| lifecycle_phase| absent             | present (expected)        |"
  echo "| health.node    | absent             | cell-0 (expected)         |"
} > "$OUT/summary.md"
echo "   -> $OUT/summary.md"

# -----------------------------------------------------------
# Done
# -----------------------------------------------------------
echo ""
echo "========================================"
echo "  Baseline capture selesai."
echo "  Semua file tersimpan di: $OUT"
echo ""
echo "  Langkah berikutnya:"
echo "  1. Baca $OUT/summary.md untuk confirm baseline"
echo "  2. Apply patch v2.3"
echo "  3. Jalankan: bash validation/capture_baseline.sh"
echo "     untuk capture post-patch dan bandingkan"
echo "========================================"
echo ""
