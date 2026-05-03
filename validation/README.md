# validation/

Folder ini menyimpan baseline captures dan perbandingan antar phase.

---

## Cara Kerja

Setiap kali sistem melewati perubahan besar (patch, phase baru),
jalankan `capture_baseline.sh`. Script akan membuat subfolder baru:

```
validation/
├── phase0_prepatch_20250101_143022/   ← sebelum patch v2.3
│   ├── summary.md
│   ├── memory_snapshot.txt
│   ├── endpoint_samples.json
│   ├── log_schema_sample.json
│   ├── log_schema_sample_pretty.json
│   ├── vectorizer_info.txt
│   └── latency_baseline.txt
├── phase0_prepatch_20250101_160511/   ← sesudah patch v2.3
│   └── ...
├── capture_baseline.sh
├── diff_baselines.sh
└── README.md
```

---

## Workflow Standar

### Sebelum Apply Patch

```bash
cd ~/mas_e
bash validation/capture_baseline.sh
```

### Apply Patch

```bash
cp -r /path/to/patch/app ~/mas_e/
cp /path/to/patch/rules/thresholds.yaml ~/mas_e/rules/
cp /path/to/patch/anchors/cell0_anchor.yaml ~/mas_e/anchors/
cp /path/to/patch/ARCHITECTURE.md ~/mas_e/
rm ~/mas_e/models/vectorizer.pkl
sudo systemctl restart mas-e
sleep 4
```

### Sesudah Apply Patch

```bash
bash validation/capture_baseline.sh
bash validation/diff_baselines.sh
```

### Commit Semuanya

```bash
git add validation/ ARCHITECTURE.md CHANGELOG.md
git commit -m "patch: v2.3 ontology alignment — baseline captured"
```

---

## Prinsip

Folder ini adalah bentuk observasi diri sistem.

Mas E mengamati makna.
Folder ini mengamati transformasi dirinya sendiri.

Setiap capture adalah satu frame dalam lineage arsitektural Mas E.
