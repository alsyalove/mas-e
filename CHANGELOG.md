# Mas E Observatory — Patch Changelog

---

## v2.3 — Ontology Alignment Patch

**Tanggal:** 2025
**Tipe:** Architectural patch — bukan rewrite, bukan breaking change

### Filosofi Patch Ini

v2.2 benar sebagai fondasi teknis.
v2.3 menyelaraskan fondasi itu dengan identitas sistem yang kini sudah jelas.

Yang diperbaiki bukan error code.
Yang diperbaiki adalah jarak antara identitas Mas E dan source-nya.

---

### File Baru

| File | Fungsi |
|---|---|
| `ARCHITECTURE.md` | Kontrak ontologis sistem — wajib dibaca sebelum Phase berikutnya |
| `anchors/cell0_anchor.yaml` | Anchor schema formal — inactive, aktif di Phase 1 |
| `rules/thresholds.yaml` | Threshold dipindah dari hardcode ke policy file |

---

### File Dimodifikasi

| File | Perubahan |
|---|---|
| `app/engine.py` | Baca threshold dari YAML, tambah `lifecycle_phase` di output |
| `app/main.py` | Tambah `node_id`, `session_id` di log schema |
| `app/vectorizer.py` | `max_features` 20 → 100, tambah `sublinear_tf=True` |

---

### Yang Tidak Berubah

- Runtime FastAPI tetap sama
- Collapse logic tidak berubah
- Semantic metrics tidak berubah
- Nginx config tidak berubah
- Systemd service tidak berubah
- RAM target tetap < 250MB

---

### Breaking Change

**Satu:** vectorizer model lama (`models/vectorizer.pkl`) harus dihapus agar
vectorizer baru di-fit ulang dengan `max_features=100`.

```bash
rm models/vectorizer.pkl
```

Model baru akan dibuat otomatis saat startup berikutnya.

---

### Migration Notes untuk Log Lama

Log lama (`session.jsonl`) tidak punya `node_id` dan `session_id`.
Ini bukan masalah — sistem bisa membaca keduanya dengan toleransi field opsional.
Archaeology Layer di Phase 2 harus mempertimbangkan log pre-v2.3 sebagai
"generasi 0" tanpa identity metadata.

---

### Apa yang Belum Dibangun (Intentional)

| Konsep | Status | Target |
|---|---|---|
| Anchor aktif | Schema ada, belum aktif | Phase 1 |
| Drift Engine | `drift: null` tetap | Phase 2 |
| Context Router | Belum ada | Phase 3 |
| RCL | Terdokumentasi di ARCHITECTURE.md | Phase 2 |
| Economy Layer | North Star only | Phase 4+ |

---

### Perintah Setelah Patch

```bash
# 1. Hapus vectorizer lama
rm models/vectorizer.pkl

# 2. Restart service
sudo systemctl restart mas-e

# 3. Verifikasi health
curl http://localhost/health

# 4. Test proses
curl -X POST http://localhost/process \
  -H "Content-Type: application/json" \
  -d '{"text": "kebenaran struktur makna"}'

# 5. Verifikasi log schema baru
tail -n 1 logs/session.jsonl | python3 -m json.tool
```

Output yang diharapkan dari log entry baru:
```json
{
  "node_id": "cell-0",
  "session_id": "uuid-...",
  "input": "...",
  "metrics": {...},
  "decision": {
    "state": "COLLAPSE",
    "glyph": "pure_knowledge",
    "reason": "...",
    "lifecycle_phase": "crystallization"
  },
  "drift": null,
  "timestamp": "..."
}
```
