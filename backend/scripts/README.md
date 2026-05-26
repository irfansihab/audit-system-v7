# backend/scripts — alat dev/ujicoba

## digestion_harness.py — ujicoba pipeline digestion (banyak dokumen)

Menjalankan digest V6 yang sama dengan produksi (`digest_tor`/`digest_rab` per-file,
`digest_pengadaan` folder-level) atas sebuah korpus, **paralel**, lalu mengukur
**kecepatan + kualitas** otomatis — tanpa membaca tiap JSON manual.

### Cara pakai
```bash
# dari root repo
PATH="$PWD/backend/.venv/bin:$PATH" PYTHONPATH="$PWD/backend" \
  backend/.venv/bin/python backend/scripts/digestion_harness.py \
    --corpus /path/ke/korpus [--out folder-output] [--workers 4] [--golden golden.json]
```
`PATH` harus memuat venv (subprocess digest pakai `python3` + butuh deps V6).

### Susun korpus (klasifikasi jenis)
Pilih salah satu — keduanya didukung:
- **Subfolder per jenis** (disarankan untuk korpus besar):
  ```
  korpus/
  ├── tor/   *.pdf
  ├── rab/   *.pdf
  ├── kak/   *.pdf
  ├── hps/   *.pdf
  ├── rfi/   *.pdf
  └── kontrak/ *.pdf
  ```
- **Prefiks nama file** (flat): `TOR-...pdf`, `RAB-...pdf`, `KAK-...pdf`, dst.

`ST/KP/PKP/OTHER` otomatis dilewati (tak punya digest script).

### Output & metrik
- Ringkasan konsol per jenis: jumlah, ok, kosong, waktu rata-rata, **% cakupan field kunci**.
- **Perlu perhatian**: hanya file gagal / kosong (scan→OCR) / field hilang / golden meleset.
- `report.md` + `report.json` di folder output (default `<korpus>/_digest-test/`).

### Golden (akurasi, opsional)
Anotasi nilai-harapan untuk sebagian dokumen → skor akurasi (substring,
case-insensitive, dicocokkan ke isi JSON digest). Lihat `golden.example.json`.

```json
{
  "KAK-Data-Center-DRC-2026.pdf": { "nilai_hps": "8200000000", "obyek": "Data Center" }
}
```

> Catatan: cache lintas-penugasan (`DocumentCache`, dedup sha256) adalah fitur
> jalur APP (upload→auto-digest); harness ini selalu mengukur digest **dingin**
> (murni waktu script), supaya konsisten antar-run.
