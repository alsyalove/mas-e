# Mas E Observatory — Phase 0 Validation Suite
# Version: 1.2 | Status: Active
# Dibaca sebelum: mulai Phase 1, atau setelah major change
# Updated: v2.4 — sync dengan 3-axis bipolar semantic space

---

## Tujuan Dokumen

Dokumen ini adalah **pre-certification suite** untuk Mas E Phase 0.

Sistem dinyatakan **fully alive** hanya jika semua layer pass.

Bukan ketika server running.
Bukan ketika satu endpoint merespons.

Tetapi ketika:

```
infrastruktur → runtime → API contract → semantic engine → observability
```

semuanya berjalan sinkron dan konsisten.

---

## Prinsip Validasi

**Validasi berjalan vertikal, bukan horizontal.**

Jika Layer N gagal:
- Stop
- Fix Layer N
- Ulangi dari Layer N
- Jangan lanjut ke Layer N+1

Karena sistem layered tidak bisa di-debug dari atas.
Debugging di cognitive layer sementara infrastruktur salah adalah ilusi.

---

## Cara Menjalankan

```bash
# Aktifkan environment dulu
source ~/mas_e/venv/bin/activate
cd ~/mas_e
```

Jalankan setiap section secara berurutan.
Catat hasilnya di bagian **Hasil** di bawah setiap test.

---

## Layer 1 — Infrastructure & Memory Habitat

**Tujuan:** Memastikan habitat sistem sehat sebelum menyentuh kode apapun.

```bash
# L1.1 — Swap aktif dan cukup
free -m
```
Target: swap total >= 4096 MB

```bash
# L1.2 — Swappiness benar
cat /proc/sys/vm/swappiness
```
Target: `10`

```bash
# L1.3 — Swap persistent
grep swap /etc/fstab
```
Target: ada baris `/swapfile none swap sw 0 0`

```bash
# L1.4 — Mount valid, tidak ada error
sudo findmnt --verify
```
Target: tidak ada output error

```bash
# L1.5 — Struktur folder lengkap
ls ~/mas_e/
```
Target: `app/ web/ logs/ rules/ glyphs/ models/ data/ anchors/ drift/ archaeology/ venv/`

```bash
# L1.6 — Git initialized dan ada commit pertama
cd ~/mas_e && git log --oneline
```
Target: minimal 1 commit dengan message `feat: initial habitat structure`

```bash
# L1.7 — Port aktif
sudo ss -tlnp | grep -E '80|8000'
```
Target: keduanya listening

**[ ] Layer 1 PASS**

---

## Layer 2 — Python Runtime

**Tujuan:** Memastikan runtime Python dan seluruh dependency berjalan benar.

```bash
# L2.1 — Venv aktif dan Python path benar
which python && python --version
```
Target: path menunjuk ke `~/mas_e/venv/bin/python`, versi >= 3.10

```bash
# L2.2 — Semua package terinstall
pip list | grep -E 'fastapi|uvicorn|numpy|scikit|joblib|yaml|multipart'
```
Target: semua muncul, tidak ada yang missing

```bash
# L2.3 — Corpus ada dan tidak kosong
wc -l ~/mas_e/data/reference_corpus.txt
cat ~/mas_e/data/reference_corpus.txt
```
Target: minimal 5 baris, berisi kata-kata Indonesia

```bash
# L2.4 — Vectorizer fit dari corpus tanpa error
python3 -c "
from app.vectorizer import get_vectorizer
v = get_vectorizer()
n = len(v.get_feature_names_out())
print('Features:', n)
assert n > 0, 'Vectorizer tidak punya features'
assert n <= 100, 'Features melebihi max_features=100'
print('Vectorizer OK')
"
```
Target: `Features: [jumlah kata unik di corpus]`, `Vectorizer OK`
Catatan v2.3: max_features dinaikkan ke 100. Jumlah aktual = ukuran vocabulary corpus
(bukan 20). Jangan hardcode angka ini — ia akan bertumbuh saat corpus diperkaya di Phase 1.

```bash
# L2.5 — Model file tersimpan dengan benar
ls -lh ~/mas_e/models/vectorizer.pkl
```
Target: file ada, ukuran > 0

```bash
# L2.6 — Semua modul dapat diimport
python3 -c "
from app.semantic_metrics import compute_metrics
from app.engine import evaluate_collapse
from app.vectorizer import get_vectorizer
print('All imports OK')
"
```
Target: `All imports OK`, tidak ada traceback

**[ ] Layer 2 PASS**

---

## Layer 3 — API Contract

**Tujuan:** Memastikan endpoint berperilaku sesuai kontrak — bukan hanya merespons, tetapi merespons dengan benar di semua kondisi.

```bash
# L3.1 — Service running
sudo systemctl status mas-e
```
Target: `active (running)`

```bash
# L3.2 — Health check direct (bypass nginx)
curl -s http://127.0.0.1:8000/health
```
Target: `{"status":"alive","node":"cell-0"}`
Catatan v2.3: field `node` ditambahkan. Target lama `{"status":"alive"}` akan false-fail.

```bash
# L3.3 — Health check via nginx
curl -s http://localhost/health
```
Target: `{"status":"alive","node":"cell-0"}`

```bash
# L3.4 — Happy path: input valid
curl -s -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "kebenaran logika pengetahuan"}' | python3 -m json.tool
```
Target: JSON lengkap dengan `node_id`, `session_id`, `input`, `metrics`, `decision`, `drift`, `timestamp`

```bash
# L3.5 — Input kosong: harus validation error, bukan crash
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": ""}'
```
Target: `422` (bukan `500`)

```bash
# L3.6 — Input melebihi 500 karakter: harus validation error
LONG=$(python3 -c "print('a ' * 260)")
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"$LONG\"}"
```
Target: `422`

```bash
# L3.7 — Input tidak dikenal corpus: error informatif, bukan crash
curl -s -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "xyzxyz qqqqqq zzzzz"}'
```
Target: `{"error": "Input tidak dikenali corpus", "hint": "..."}`

```bash
# L3.8 — Request tanpa body: validation error
curl -s -o /dev/null -w "%{http_code}" -X POST http://localhost/process \
  -H "Content-Type: application/json"
```
Target: `422`

**[ ] Layer 3 PASS**

---

## Layer 4 — Semantic Engine

**Tujuan:** Memastikan collapse logic benar, konsisten, dan tidak menghasilkan output di luar kontrak.

```bash
# L4.1 — Metrics struktur valid dan semua nilai dalam range (v2.4)
curl -s -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "makna refleksi pemahaman memori"}' \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
m = r['metrics']

# Cek struktur top-level metrics (v2.4)
assert 'axes'            in m, 'Missing: axes'
assert 'magnitude'       in m, 'Missing: magnitude'
assert 'active_features' in m, 'Missing: active_features'
assert 'raw'             in m, 'Missing: raw'

# Cek axis keys
axes = m['axes']
assert 'clarity_ambiguity' in axes, 'Missing axis: clarity_ambiguity'
assert 'stillness_motion'  in axes, 'Missing axis: stillness_motion'
assert 'value_order'       in axes, 'Missing axis: value_order'

# Cek range: semua axis dalam (-0.99, 0.99)
for name, val in axes.items():
    assert -0.99 <= val <= 0.99, f'{name} out of range: {val}'

# Cek magnitude selalu >= 0
assert m['magnitude'] >= 0, 'Magnitude negatif: ' + str(m['magnitude'])

# Cek active_features > 0 (input dikenali corpus)
assert m['active_features'] > 0, 'active_features = 0'

print('Metrics structure: OK')
print('  clarity_ambiguity :', axes['clarity_ambiguity'])
print('  stillness_motion  :', axes['stillness_motion'])
print('  value_order       :', axes['value_order'])
print('  magnitude         :', m['magnitude'])
print('  active_features   :', m['active_features'])
"
```

```bash
# L4.2 — Decision selalu punya semua key wajib dan state valid (v2.4)
curl -s -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "emosi intuisi perasaan persepsi"}' \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)

# Cek identity fields (v2.3)
assert 'node_id'    in r, 'Missing: node_id'
assert 'session_id' in r, 'Missing: session_id'
assert r['node_id'] == 'cell-0', 'node_id salah: ' + str(r['node_id'])

# Cek decision fields (v2.4)
d = r['decision']
assert 'state'          in d, 'Missing: state'
assert 'seal'           in d, 'Missing: seal (v2.4)'
assert 'glyph'          in d, 'Missing: glyph'
assert 'reason'         in d, 'Missing: reason'
assert 'dominant_axis'  in d, 'Missing: dominant_axis (v2.4)'
assert 'lifecycle_phase' in d, 'Missing: lifecycle_phase'

valid_states = ['HOLD', 'OBSERVE', 'COLLAPSE', 'POTENTIAL']
assert d['state'] in valid_states, 'Unknown state: ' + d['state']

valid_seals = ['cipher', 'reflection', 'ascend', 'paradox']
assert d['seal'] in valid_seals, 'Unknown seal: ' + d['seal']

valid_phases = ['generation', 'refinement', 'crystallization', 'incubation']
assert d['lifecycle_phase'] in valid_phases, 'Unknown lifecycle_phase: ' + d['lifecycle_phase']

valid_axes = ['clarity_ambiguity', 'stillness_motion', 'value_order']
assert d['dominant_axis'] in valid_axes, 'Unknown dominant_axis: ' + d['dominant_axis']

print('Decision structure: OK')
print('  state          :', d['state'])
print('  seal           :', d['seal'])
print('  glyph          :', d['glyph'])
print('  dominant_axis  :', d['dominant_axis'])
print('  lifecycle_phase:', d['lifecycle_phase'])
print('  node_id        :', r['node_id'])
"
```

```bash
# L4.3 — Drift field ada dan null (kontrak Phase 0)
curl -s -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "kebenaran logika"}' \
  | python3 -c "
import json, sys
r = json.load(sys.stdin)
assert 'drift' in r, 'Missing: drift field'
assert r['drift'] is None, 'Drift harus null di Phase 0, dapat: ' + str(r['drift'])
print('Drift placeholder: OK')
"
```

```bash
# L4.4 — Repeatability: input sama harus menghasilkan state yang sama
echo "Testing repeatability (5x)..."
STATES=""
for i in {1..5}; do
  STATE=$(curl -s -X POST http://localhost/process \
    -H "Content-Type: application/json" \
    -d '{"text":"kebenaran logika observasi"}' \
    | python3 -c "import json,sys; print(json.load(sys.stdin)['decision']['state'])")
  STATES="$STATES $STATE"
  echo "  Run $i: $STATE"
done
echo "Hasil: $STATES"
```
Target: semua 5 run menampilkan state yang sama

**[ ] Layer 4 PASS**

---

## Layer 5 — Observability

**Tujuan:** Memastikan sistem dapat diamati — log valid, resource dalam batas, dan proxy berjalan.

```bash
# L5.1 — Log file terbuat setelah request
ls -lh ~/mas_e/logs/session.jsonl
```
Target: file ada, ukuran > 0

```bash
# L5.2 — Setiap request menulis tepat 1 baris log
BEFORE=$(wc -l < ~/mas_e/logs/session.jsonl)
curl -s -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "uji log growth"}' > /dev/null
AFTER=$(wc -l < ~/mas_e/logs/session.jsonl)
echo "Log lines: $BEFORE -> $AFTER (delta: $((AFTER - BEFORE)))"
```
Target: delta = 1

```bash
# L5.3 — Format log valid JSON per baris
tail -n 5 ~/mas_e/logs/session.jsonl | while IFS= read -r line; do
  echo "$line" | python3 -m json.tool > /dev/null \
    && echo "  Line: VALID JSON" \
    || echo "  Line: INVALID JSON"
done
```
Target: semua `VALID JSON`

```bash
# L5.4 — Log punya semua field wajib (termasuk field baru v2.3)
tail -n 1 ~/mas_e/logs/session.jsonl | python3 -c "
import json, sys
r = json.load(sys.stdin)

# Field wajib Phase 0 original
required_base = ['input', 'metrics', 'decision', 'drift', 'timestamp']
# Field tambahan v2.3
required_v23  = ['node_id', 'session_id']
# Field wajib di dalam decision (v2.3)
required_decision = ['state', 'glyph', 'reason', 'lifecycle_phase']

all_required = required_base + required_v23
missing = [k for k in all_required if k not in r]
missing_decision = [k for k in required_decision if k not in r.get('decision', {})]

if missing:
    print('MISSING top-level fields:', missing)
elif missing_decision:
    print('MISSING decision fields:', missing_decision)
else:
    print('Log schema: OK')
    print('Fields found:', list(r.keys()))
    print('lifecycle_phase:', r['decision'].get('lifecycle_phase'))
"
```

```bash
# L5.5 — RAM usage dalam batas aman
free -m | python3 -c "
import sys
lines = sys.stdin.readlines()
mem = lines[1].split()
used = int(mem[2])
total = int(mem[1])
pct = round(used / total * 100, 1)
print(f'RAM used: {used} MB / {total} MB ({pct}%)')
if used < 300:
    print('RAM usage: OK')
elif used < 400:
    print('RAM usage: ACCEPTABLE (monitor di Phase 1)')
else:
    print('RAM usage: WARNING — terlalu tinggi')
"
```
Target: < 400 MB

```bash
# L5.6 — Nginx melayani UI
curl -s -o /dev/null -w "HTTP status: %{http_code}\n" http://localhost/
```
Target: `HTTP status: 200`

```bash
# L5.7 — Restart persistence: model tidak hilang setelah restart
sudo systemctl restart mas-e
sleep 4
curl -s http://localhost/health
ls -lh ~/mas_e/models/vectorizer.pkl
```
Target: health `{"status":"alive"}`, model pkl masih ada

**[ ] Layer 5 PASS**

---

## Layer 6 — Load Stability (Opsional tapi Direkomendasikan)

**Tujuan:** Memastikan sistem stabil di bawah request berturut-turut sebelum apply patch.

```bash
# L6.1 — 20 request berturut-turut, hitung success rate
SUCCESS=0
FAIL=0
for i in $(seq 1 20); do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost/process \
    -H "Content-Type: application/json" \
    -d '{"text": "kebenaran logika observasi"}')
  if [ "$STATUS" = "200" ]; then
    SUCCESS=$((SUCCESS+1))
  else
    FAIL=$((FAIL+1))
    echo "  FAIL pada request $i: HTTP $STATUS"
  fi
done
echo "Hasil: $SUCCESS/20 sukses, $FAIL gagal"
```
Target: 20/20

```bash
# L6.2 — RAM setelah load masih aman
free -m | grep Mem
```
Target: masih < 400 MB

**[ ] Layer 6 PASS**

---

## Definisi Fully Alive

| Layer | Nama | Critical? |
|---|---|---|
| Layer 1 | Infrastructure & Memory | Wajib |
| Layer 2 | Python Runtime | Wajib |
| Layer 3 | API Contract | Wajib |
| Layer 4 | Semantic Engine | Wajib |
| Layer 5 | Observability | Wajib |
| Layer 6 | Load Stability | Direkomendasikan |

Sistem dinyatakan **Fully Alive** jika Layer 1–5 semua PASS.

---

## Hasil Validasi

Isi bagian ini setiap kali validasi dijalankan.

```
Tanggal        :
Versi          : Phase 0 v2.4
Dijalankan oleh:

Layer 1 : [ ] PASS  [ ] FAIL — Catatan:
Layer 2 : [ ] PASS  [ ] FAIL — Catatan:
Layer 3 : [ ] PASS  [ ] FAIL — Catatan:
Layer 4 : [ ] PASS  [ ] FAIL — Catatan:
Layer 5 : [ ] PASS  [ ] FAIL — Catatan:
Layer 6 : [ ] PASS  [ ] FAIL — Catatan:

Status  : [ ] FULLY ALIVE — siap mulai Phase 1
          [ ] NOT READY  — lihat catatan di atas
```

---

## Catatan Untuk Phase Berikutnya

Dokumen ini berlaku sebagai standar validasi untuk **semua phase Mas E**.

Saat Phase 1 selesai dibangun, buat file baru:

```
tests/phase1_validation.md
```

Dengan layer tambahan yang sesuai dengan komponen yang ditambahkan di Phase 1:
- Anchor active layer
- Threshold YAML loading
- Lifecycle mapping
- Extended log schema (node_id, session_id)

Phase 0 validation tetap dijalankan sebagai **regression check** di Phase 1.
Karena layer baru tidak boleh merusak layer yang sudah ada.
