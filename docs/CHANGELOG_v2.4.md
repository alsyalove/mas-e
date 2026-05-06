## v2.4 — 3-Axis Bipolar Semantic Space

**Tipe:** Semantic layer upgrade — bukan rewrite, bukan breaking change arsitektur

---

### Filosofi Patch Ini

v2.3 memastikan fondasi berbicara dalam bahasa arsitektur yang benar.
v2.4 memperdalam cara sistem melihat ruang makna.

Yang berubah: cara sistem mengukur input.
Yang tidak berubah: arsitektur, governance, identity layer, log schema.

---

### File Dimodifikasi

| File | Perubahan |
|---|---|
| `app/semantic_metrics.py` | 2 metric flat → 3 axis bipolar dalam ruang (-0.99, 0.99) |
| `app/engine.py` | Collapse logic 3D + 4 Seal, tambah `seal` dan `dominant_axis` di output |
| `rules/thresholds.yaml` | v0.1 → v0.2: tambah threshold 3-axis, `seal_map`, state `POTENTIAL` |
| `app/main.py` | `np.sum() == 0` → `np.any()`, `mkdir` dipindah ke startup |

---

### Yang Tidak Berubah

- `vectorizer.py` — TF-IDF tetap fondasi yang valid
- `node_id`, `session_id` — identity layer v2.3 dipertahankan
- `lifecycle_phase` — affordance Phase 1 dipertahankan
- `drift: null` — kontrak Phase 2 dipertahankan
- `ARCHITECTURE.md` — tidak ada hukum yang dilanggar
- Nginx, systemd, git structure — tetap

---

### Perubahan Schema Metrics

**v2.3:**
```json
"metrics": {
  "ambiguity": 0.9238,
  "coherence": 0.9592,
  "variance": 0.0408,
  "mean": 0.0825
}
```

**v2.4:**
```json
"metrics": {
  "axes": {
    "clarity_ambiguity": 0.365,
    "stillness_motion": -0.99,
    "value_order": 0.0
  },
  "magnitude": 1.038,
  "active_features": 3,
  "raw": {
    "mean": 0.577,
    "variance": 0.0,
    "density": 0.143
  }
}
```

---

### Perubahan Schema Decision

**v2.3:**
```json
"decision": {
  "state": "HOLD",
  "glyph": "clarity_ambiguity",
  "reason": "Ambiguity terlalu tinggi",
  "lifecycle_phase": "generation"
}
```

**v2.4:**
```json
"decision": {
  "state": "POTENTIAL",
  "seal": "paradox",
  "glyph": "stillness_motion",
  "reason": "Gerak potensial terdeteksi — makna bergerak ke dalam",
  "dominant_axis": "stillness_motion",
  "lifecycle_phase": "incubation"
}
```

---

### Bug yang Diperbaiki

| Bug | File | Status |
|---|---|---|
| Metric bias sparse vector (mean/var dari full vector) | `semantic_metrics.py` | Fixed |
| Division by zero pada `value_order` saat n_active=1 | `semantic_metrics.py` | Fixed |
| `stillness_motion` formula arbitrer dan bias negatif | `semantic_metrics.py` | Fixed |
| Threshold hardcoded di engine (pelanggaran Rule 4) | `engine.py` | Fixed |
| `node_id`, `session_id` tidak ada (regresi dari v2.3) | `main.py` | Fixed |
| `lifecycle_phase` tidak ada di decision | `engine.py` | Fixed |
| `np.sum() == 0` float equality | `main.py` | Fixed |
| `mkdir` dipanggil setiap request | `main.py` | Fixed |

---

### State Baru: POTENTIAL

State keempat ditambahkan untuk menangkap kondisi gerak potensial:

```
HOLD      → generation     → cipher    (ambiguity dominan)
OBSERVE   → refinement     → reflection (sinyal lemah / paradox aktif)
POTENTIAL → incubation     → paradox   (gerak potensial, distribusi merata)
COLLAPSE  → crystallization → ascend   (makna jelas dan terstruktur)
```

---

### Catatan Teknis: Batas Axis clarity_ambiguity

Dengan TF-IDF murni, nilai aktif selalu positif sehingga
`clarity_ambiguity` selalu positif di Phase 0.
Sisi negatif baru bermakna setelah Anchor aktif di Phase 1
(jarak dari anchor menghasilkan clarity relatif yang bisa negatif).
Ini bukan bug — ini batas yang disengaja dan terdokumentasi.

---

### Breaking Change

**Satu:** schema `metrics` berubah total. Log lama pre-v2.4 punya
schema flat (`ambiguity`, `coherence`, dll). Archaeology Layer di Phase 2
harus mempertimbangkan log pre-v2.4 sebagai "generasi metrics lama."

Log tetap valid JSON dan tetap kompatibel di level top-level fields
(`node_id`, `session_id`, `input`, `decision`, `drift`, `timestamp`).

---

### Perintah Setelah Patch

```bash
# Tidak perlu hapus vectorizer — vectorizer tidak berubah

# Restart service
sudo systemctl restart mas-e

# Verifikasi health
curl http://localhost/health

# Test dengan input yang seharusnya COLLAPSE
curl -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "kebenaran logika pengetahuan kepastian"}'

# Test dengan input yang seharusnya POTENTIAL (distribusi merata)
curl -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "kebenaran makna observasi refleksi"}'

# Verifikasi log schema
tail -n 1 logs/session.jsonl | python3 -m json.tool
```
