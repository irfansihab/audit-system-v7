---
name: kepatuhan-saipi
version: 1.0
jenis: Kepatuhan Standar Audit Intern Pemerintah Indonesia (SAIPI)
dasar-hukum: Peraturan Menteri PANRB & PER-01/AAIPI/DPN/2021 (SAIPI)
model: claude-sonnet-4-6
output: Laporan Quality Assurance + Audit Trail
---

# Skill — Kepatuhan SAIPI (Quality Assurance per-penugasan)

> **Sumber otoritatif**: PER-01/AAIPI/DPN/2021 — Standar Audit Intern Pemerintah Indonesia (SAIPI), terbit DPN AAIPI, 2021. PDF: `wiki/raw/SAIPI-PER-01-AAIPI-DPN-2021.pdf`.

## Tujuan
Memastikan setiap penugasan pengawasan v4 mematuhi SAIPI — terutama Standar Atribut yang per-penugasan (1100, 1200) dan Standar Kinerja yang per-penugasan (2200, 2300, 2400). Cek dijalankan **otomatis** setelah Task 03 (KKP) dan Task 04 (LHP) — sebelum berkas penugasan disubmit ke INTEGRAL — supaya gap kepatuhan bisa dikoreksi lebih dulu.

## Cakupan vs. Tidak

| Dicek per-penugasan (skill ini) | TIDAK dicek (out of scope per-penugasan) |
|---|---|
| 1100 Independensi & Objektivitas (tingkat penugasan) | 1000 Piagam APIP (organisasi) |
| 1200 Kecakapan & Kecermatan Profesional | 1300 Program Penjaminan Kualitas APIP (organisasi) |
| 2200 Perencanaan Penugasan | 2000–2080 Pengelolaan APIP |
| 2300 Pelaksanaan Penugasan | 2100–2130 Sifat Dasar Tata Kelola/Risiko/Pengendalian |
| 2400 Komunikasi Hasil Penugasan | 2500 Pemantauan Tindak Lanjut (akan dicek skill `pemantauan-tindak-lanjut`) |
| | 2600 Komunikasi Penerimaan Risiko (organisasi) |

## Eksekusi Otomatis

Skill ini **tidak dipanggil manual** oleh auditor. Skill dipanggil otomatis oleh:

1. **Akhir Task 03 (KKP)** — Claude memanggil `python3 scripts/qc_saipi.py --penugasan [path] --stage kkp` setelah `temuan.json` final & sebelum minta gate auditor. Cek standar 1100, 1200, 2200, 2300.
2. **Akhir Task 04 (LHP)** — Claude memanggil `python3 scripts/qc_saipi.py --penugasan [path] --stage lhp` setelah LHP-SUBSTANSI.docx final & sebelum minta gate ketua tim. Cek seluruh standar termasuk 2400.

Output:
- `_QA-SAIPI/checklist-[stage].json` — JSON master per standar (status + bukti + gap)
- `_QA-SAIPI/laporan-qa-[stage].md` — narasi yang siap di-tampilkan ke auditor

Jika ada gap **KRITIS** (mis. temuan tanpa dokumen sumber, KP/PKP tidak ada, LHP tidak memuat simpulan), `qc_saipi.py` exit code 2 — Claude WAJIB tampilkan laporan QA ke auditor dan minta koreksi sebelum melanjutkan ke gate.

## Severity

| Severity | Arti | Tindakan |
|----------|------|----------|
| `KRITIS` | Standar wajib SAIPI tidak terpenuhi & dapat dideteksi otomatis. | Blokir gate. Wajib koreksi. |
| `PERINGATAN` | Indikasi ketidaksesuaian, perlu review manual. | Tampilkan ke auditor, boleh override dengan justifikasi. |
| `NEEDS_REVIEW` | Tidak bisa dicek otomatis (mis. independensi pribadi auditor). | Auditor konfirmasi via checklist manual. |
| `OK` | Memenuhi standar. | (informasional) |

## Mapping Singkat: Standar → Apa yang Dicek

### 1100 Independensi & Objektivitas
- **1100/1130** Cek: ada `_QA-SAIPI/deklarasi-independensi.md` ditandatangani semua anggota tim? (NEEDS_REVIEW kalau belum ada — tampilkan template)
- **1130.A1** Cek: ada flag manual auditor "tim pernah jadi PIC area ini di tahun sebelumnya?" (NEEDS_REVIEW)

### 1200 Kecakapan & Kecermatan Profesional
- **1210** Cek: tabel tim di context.md → tiap anggota mencantumkan jabfung auditor (Auditor Madya/Muda/Pertama/Ahli/Penyelia)? (PERINGATAN kalau ada anggota tanpa jabfung)
- **1210.A1** NEEDS_REVIEW: kalau jenis penugasan butuh keahlian khusus (mis. audit-kinerja butuh metodologi statistik), apakah tim punya? (manual confirm)
- **1220** Inheritend dari 2310/2320 — bila informasi kondisi cukup/andal/relevan/bermanfaat dipenuhi → 1220 OK.

### 2200 Perencanaan Penugasan
- **2200** Cek: `00-input/KP-*.{pdf,docx}` exist & `00-input/PKP-*.{pdf,docx}` exist? (KRITIS kalau tidak)
- **2210** Cek: `context.md` punya field "Tujuan" terisi & `sasaran-assignment.json` ≥ 1 sasaran? (KRITIS kalau kosong)
- **2220** Cek: `context.md` punya field "Ruang Lingkup" terisi? (PERINGATAN)
- **2230** Cek: alokasi tim (jumlah anggota di sasaran-assignment.json) wajar terhadap jumlah sasaran? (NEEDS_REVIEW di luar threshold)
- **2240** Inherited — PKP eksternal (manual di INTEGRAL).

### 2300 Pelaksanaan
- **2310** Cek: setiap temuan di `temuan.json` punya `dokumen_sumber[]` non-empty & file di-referensi exist di `00-input/`? (KRITIS)
- **2320** Cek: setiap temuan punya kondisi (≥ 30 char), kriteria (≥ 10 char), akibat (≥ 10 char)? (KRITIS — sudah enforce schema, double-check)
- **2330** Cek: `temuan.json` valid terhadap schema & `KKP-*.docx` exist? (KRITIS)
- **2340** Cek: ada event `GATE_PASSED` task=03 dengan actor role_kode=KT? (PERINGATAN kalau belum) — bukti supervisi.

### 2400 Komunikasi Hasil
- **2410** Cek isi LHP docx: memuat string "Tujuan", "Ruang Lingkup", "Simpulan", "Rekomendasi"? (KRITIS untuk masing-masing yang hilang)
- **2420** Cek: tidak ada placeholder `{{...}}` atau `[CONTOH]` bocor di LHP? (KRITIS) Cek panjang wajar (1500–15000 kata).
- **2421** NEEDS_REVIEW: jika ada koreksi pasca-distribusi, sudah dikomunikasikan?
- **2422** PERINGATAN: cek apakah LHP memuat section "Tanggapan Auditi" — kalau tidak ada, beri reminder (auditi mungkin belum diminta tanggapan).
- **2430** Cek: LHP memuat string "dilaksanakan sesuai dengan Standar Audit Intern Pemerintah Indonesia"? (KRITIS — standar wajib)
- **2431** NEEDS_REVIEW: kalau ada gap SAIPI yang tidak bisa dipenuhi, harus diungkap di LHP.
- **2440** NEEDS_REVIEW: distribusi LHP (manual oleh auditor di INTEGRAL).

## Deklarasi Independensi (template)

`_QA-SAIPI/deklarasi-independensi.md` (template auto-generate kalau belum ada):

```
# Deklarasi Independensi & Objektivitas — SAIPI 1100/1130
Penugasan: [nomor ST]

Tiap anggota tim menyatakan:
1. Tidak memiliki benturan kepentingan personal/keluarga dengan auditi.
2. Tidak pernah menjadi PIC/penanggung jawab area yang diaudit dalam 1 tahun terakhir.
3. Tidak menerima imbalan/hadiah yang dapat melemahkan objektivitas.
4. Bersedia mengungkap jika ada pelemahan independensi/objektivitas yang muncul di tengah penugasan.

Tim:
- [ ] [Nama Ketua Tim] — [TTD/tanggal]
- [ ] [Nama Anggota 1] — [TTD/tanggal]
- [ ] [Nama Anggota 2] — [TTD/tanggal]
```

## Output Audit Trail

Setiap eksekusi qc_saipi mencatat 2 event:
- `VALIDATION_PASSED` atau `VALIDATION_FAILED` di audit-trail (action=`SAIPI_CHECK`).
- Payload: `{stage, total_kritis, total_peringatan, total_needs_review, total_ok}`.

## References Pendukung
- `references/SAIPI-1100-independensi.md`
- `references/SAIPI-1200-kecakapan.md`
- `references/SAIPI-2200-perencanaan.md`
- `references/SAIPI-2300-pelaksanaan.md`
- `references/SAIPI-2400-komunikasi.md`
- `references/checklist-saipi-per-penugasan.json` — schema mapping rule_id → standar SAIPI.

PDF asli: `wiki/raw/SAIPI-PER-01-AAIPI-DPN-2021.pdf`.
