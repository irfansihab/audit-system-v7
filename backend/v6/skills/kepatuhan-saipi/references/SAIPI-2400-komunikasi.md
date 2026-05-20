# SAIPI 2400 — Komunikasi Hasil Penugasan

> **Sumber**: PER-01/AAIPI/DPN/2021, Standar Kinerja.

## 2400 — Komunikasi Hasil Penugasan
> Auditor harus mengomunikasikan hasil penugasan.

## 2410 — Kriteria Komunikasi
> Komunikasi harus mencakup **sasaran, ruang lingkup penugasan, dan hasil penugasan**.

**2410.A1** — Komunikasi akhir hasil penugasan harus memuat **simpulan**, sebagaimana **rekomendasi** dan/atau tindak perbaikan yang dapat diterapkan. Apabila memungkinkan, **opini auditor** dapat diberikan.

## 2420 — Kualitas Komunikasi
> Komunikasi harus **akurat, objektif, jelas, ringkas, konstruktif, lengkap, dan tepat waktu**.

**Interpretasi**:
- *Akurat*: bebas dari kesalahan dan distorsi, didasarkan atas fakta.
- *Objektif*: wajar, tidak memihak, tidak bias.
- *Jelas*: mudah dipahami dan logis, terhindar dari istilah teknis tidak penting.
- *Ringkas*: langsung pada masalah, hindari uraian tidak perlu.
- *Konstruktif*: membantu klien, tertuju pada upaya perbaikan.
- *Lengkap*: tidak meninggalkan hal-hal penting bagi pengguna hasil penugasan.
- *Tepat waktu*: sesuai kebutuhan baik waktu maupun substansi.

## 2421 — Kesalahan dan Kelalaian
> Jika komunikasi hasil akhir mengandung kesalahan atau kelalaian yang signifikan, Pimpinan APIP harus mengomunikasikan informasi yang telah diperbaiki kepada semua pihak yang menerima komunikasi aslinya.

## 2422 — Tanggapan Klien
> Auditor harus meminta tanggapan dari pejabat klien yang bertanggung jawab atas simpulan dan rekomendasi hasil penugasan, termasuk meminta tindakan perbaikan yang direncanakan.

**2422.A1** — Tanggapan klien dan rencana tindakan perbaikan harus dicantumkan dalam laporan hasil penugasan.

## 2430 — Pengungkapan atas Kesesuaian dengan Standar
> Auditor harus menyatakan dalam setiap laporan hasil penugasan bahwa Pengawasan Intern **"dilaksanakan sesuai dengan Standar Audit Intern Pemerintah Indonesia"**.

## 2431 — Pengungkapan atas Ketidaksesuaian
Apabila terdapat ketidaksesuaian terhadap Kode Etik atau Standar yang mempengaruhi penugasan, harus diungkapkan: prinsip/aturan yang tidak sepenuhnya dilaksanakan, alasan ketidaksesuaian, dampak ketidaksesuaian.

## 2440 — Penyampaian Hasil Penugasan
> Pimpinan APIP harus mengomunikasikan hasil penugasan kepada pihak yang tepat.

**2440.A1** — Pimpinan APIP bertanggung jawab mengomunikasikan hasil akhir penugasan kepada pihak-pihak yang terkait dan memastikan hasil penugasan akan ditindaklanjuti.

## 2450 — Opini Makro
Apabila APIP memberikan opini makro, Pimpinan APIP harus memperhatikan strategi, sasaran, dan risiko-risiko organisasi.

## Implikasi untuk qc_saipi (stage=lhp)

| Rule | Standar | Cek otomatis | Severity default |
|------|---------|--------------|------------------|
| `KOM-001` | 2410 | LHP docx mengandung heading/string "Tujuan" (atau "Sasaran") | KRITIS |
| `KOM-002` | 2410 | LHP docx mengandung heading/string "Ruang Lingkup" | KRITIS |
| `KOM-003` | 2410.A1 | LHP docx mengandung heading/string "Simpulan" | KRITIS |
| `KOM-004` | 2410.A1 | LHP docx mengandung heading/string "Rekomendasi" | KRITIS |
| `KOM-005` | 2420 | LHP docx tidak mengandung placeholder bocor (`{{`, `[CONTOH]`, `[XXXX]`, `[TBD]`) — kecuali whitelist `[DIISI AUDITOR]` di blok administratif | KRITIS |
| `KOM-006` | 2420 | panjang LHP wajar (1500–15000 kata, kelas penugasan) | PERINGATAN di luar rentang |
| `KOM-007` | 2422 | LHP docx mengandung section "Tanggapan Auditi" (atau "Tanggapan Manajemen", "Tanggapan Klien") | PERINGATAN kalau tidak ada |
| `KOM-008` | 2430 | LHP docx mengandung kutipan: "dilaksanakan sesuai dengan Standar Audit Intern Pemerintah Indonesia" (case insensitive, fleksibel) | KRITIS |
| `KOM-009` | 2421 | NEEDS_REVIEW: kalau ada koreksi pasca-distribusi, sudah dikomunikasikan? | (manual) |
| `KOM-010` | 2431 | NEEDS_REVIEW: kalau ada gap SAIPI yang tak terpenuhi, harus diungkap di LHP | (auto-trigger kalau ada KRITIS lain) |
| `KOM-011` | 2440 | NEEDS_REVIEW: distribusi LHP (manual oleh auditor di INTEGRAL/Word) | (manual) |
