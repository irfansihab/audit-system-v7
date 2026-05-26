# Template Workflow Reviu RKA-K/L

Tiga template + skeleton untuk mempercepat penugasan reviu RKA-K/L
ke depan. Tujuan: auditor / skill `reviu-rka-kl` tidak perlu generate
struktur dari nol — cukup duplikasi, ganti placeholder, isi konten.

## Daftar File

| File | Tujuan | Tool generate |
|------|--------|----------------|
| `PKP-Reviu-RKA-KL-template.xlsx` | Program Kerja Pengawasan: 18 baris pengujian (Aspek A-F) + status per RO | openpyxl |
| `KKR-Reviu-RKA-KL-template.xlsx` | Kertas Kerja Reviu: catatan reviu detail + rekap per RO + rekap per aspek | openpyxl |
| `LHR-Reviu-RKA-KL-skeleton.docx` | Skeleton Laporan Hasil Reviu: KOP + bagian A-H + lampiran matriks | python-docx |

## Kapan Pakai Template vs Generate dari Script

- **Pakai template (manual / via skill duplikasi)** untuk:
  - Penugasan ad-hoc dengan jumlah RO < 5
  - Kasus khusus yang butuh tweak struktur (tambah aspek, ganti rule mapping)
  - Workshop / latihan auditor

- **Generate dari script `scripts/render_lhr.py`** untuk:
  - Penugasan reguler dengan output JSON KKR sudah siap
  - Otomasi mass-render multi-direktorat
  - Catatan: `render_lhr.py` saat ini belum multi-RO sempurna (lihat
    `feedback_pipeline_reviu_rkakl.md`); template ini sebagai fallback
    sampai render_lhr v2 selesai.

## Variable Replacement Convention

Semua placeholder pakai format **double curly braces**:

```
{{NAMA_FIELD}}
{{NAMA_FIELD — petunjuk pengisian opsional setelah em-dash}}
```

Contoh field umum:

| Placeholder | Diisi dengan |
|-------------|--------------|
| `{{NOMOR_LHR}}` | Nomor LHR final |
| `{{TANGGAL_LHR}}` | Tanggal LHR (DD Bulan YYYY) |
| `{{NAMA_DIREKTORAT}}` | Nama direktorat auditan |
| `{{TAHUN}}` | TA RKA-K/L (mis. 2027) |
| `{{N}}` | Jumlah RO |
| `{{LIST_RO}}` | Daftar RO (1 baris per RO) |
| `{{HASIL_A}}` ... `{{HASIL_F}}` | Narasi hasil per aspek |
| `{{REKOMENDASI_LIST}}` | Top 5 rekomendasi PERINGATAN |
| `{{SIMPULAN}}` | Kalimat keyakinan terbatas |
| `{{NAMA_INSPEKTUR}}` / `{{NIP_INSPEKTUR}}` | Penanda tangan |
| `{{RO_ID}}` / `{{RO_NAMA}}` | Identitas RO di Excel |

## Reminder Kualitas

Setelah replace placeholder, **tidak boleh ada `{{...}}` tersisa** di
output final. Cek cepat:

```bash
# .docx
unzip -p LHR-Reviu-RKA-KL-XXXX.docx word/document.xml | grep -o '{{[^}]*}}' | sort -u

# .xlsx
unzip -p PKP-Reviu-RKA-KL-XXXX.xlsx 'xl/worksheets/*.xml' | grep -o '{{[^}]*}}' | sort -u
```

Hasil harus kosong sebelum dikirim ke auditan/Inspektur.

## Penggunaan dalam Skill `reviu-rka-kl`

Skill akan:
1. Copy 3 file template ke `audit-system-v4/penugasan/<ID>/output/`
2. Untuk PKP: duplikasi kolom RO sesuai jumlah aktual (cell comment di
   header RO #1 mengingatkan ini)
3. Untuk KKR: append baris ke sheet `Catatan Reviu` dari JSON pipeline
4. Untuk LHR: replace placeholder `{{...}}` dengan konten dari KKR

## Regenerate Template

Bila struktur perlu diubah:

```bash
cd audit-system-v4/templates/
python3 _generate_reviu_rkakl_templates.py
```

File akan di-overwrite. Commit perubahan template + script bersamaan.

---

**Versi:** v1.0 (2026-05-06)
**Pembuat:** audit-system-v4 generator
**Lokasi:** `audit-system-v4/templates/`
