# SAIPI 2300 — Pelaksanaan Penugasan

> **Sumber**: PER-01/AAIPI/DPN/2021, Standar Kinerja.

## 2300 — Pelaksanaan Penugasan
> Auditor harus mengidentifikasi, menganalisis, mengevaluasi, dan mendokumentasikan informasi yang memadai untuk mencapai tujuan penugasan.

## 2310 — Identifikasi Informasi
> Auditor harus mengidentifikasi informasi yang **cukup, andal, relevan dan bermanfaat** untuk mencapai tujuan penugasan.

**Interpretasi**:
- **Cukup**: faktual, memadai, meyakinkan.
- **Andal**: terbaik, valid, konsisten dengan fakta, diperoleh melalui teknik yang tepat.
- **Relevan**: hubungan logis dengan observasi & rekomendasi.
- **Bermanfaat**: membantu mencapai tujuan penugasan.

**2310.A1** — Auditor harus mengumpulkan informasi sesuai dengan langkah-langkah dalam Program Kerja Penugasan.

**2310.A2** — Indikasi fraud dilaporkan kepada Pimpinan APIP sesuai mekanisme intern.

## 2320 — Analisis dan Evaluasi
> Auditor harus menyusun kesimpulan dan hasil penugasan berdasarkan analisis dan evaluasi yang memadai.

## 2330 — Dokumentasi Informasi
> Auditor harus mendokumentasikan informasi yang cukup, andal, relevan, dan bermanfaat untuk mendukung kesimpulan dan hasil penugasan.

**2330.A1** — Pimpinan APIP mengendalikan akses atas hasil penugasan.
**2330.A2** — Pimpinan APIP mengembangkan kebutuhan retensi penyimpanan hasil penugasan.

## 2340 — Supervisi Penugasan
> Penugasan audit harus disupervisi secara memadai untuk memastikan tercapainya sasaran, terjaminnya kualitas, dan peningkatan kompetensi auditor.

**Interpretasi**: Tingkat supervisi tergantung kemahiran & pengalaman auditor dan kompleksitas penugasan. Bukti supervisi **didokumentasikan dan disimpan**.

## Implikasi untuk qc_saipi

| Rule | Standar | Cek otomatis | Severity default |
|------|---------|--------------|------------------|
| `LAK-001` | 2310 | tiap temuan di temuan.json punya `dokumen_sumber[]` ≥ 1 | KRITIS |
| `LAK-002` | 2310 | tiap file di `dokumen_sumber.file` ada di `00-input/` | KRITIS |
| `LAK-003` | 2310 | tiap temuan punya `dokumen_sumber.halaman` terisi (informasi cukup-andal) | PERINGATAN |
| `LAK-004` | 2320 | tiap temuan: kondisi ≥ 30 char, kriteria ≥ 10 char, akibat ≥ 10 char | KRITIS (sudah enforce di schema, double-check) |
| `LAK-005` | 2320 | (audit) tiap temuan: sebab terisi non-null | KRITIS untuk audit-pengadaan/audit-kinerja |
| `LAK-006` | 2330 | `temuan.json` valid terhadap `schemas/kkp-temuan.schema.json` | KRITIS |
| `LAK-007` | 2330 | `_KKP/KKP-*.docx` exist (view formal Word) | PERINGATAN |
| `LAK-008` | 2340 | ada event audit-trail `GATE_PASSED` task=03 dengan actor.role_kode in {KT,PT,PM} (bukti supervisi) | PERINGATAN kalau belum ada saat stage=lhp |
| `LAK-009` | 2310.A1 | tiap sasaran SELESAI_KKP punya `id_temuan_terkait` non-empty (atau dieksplisitkan "tidak ada temuan") | PERINGATAN |
