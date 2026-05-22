# Pattern Temuan — Reviu RKA-K/L

Index pattern temuan yang berlaku untuk skill `reviu-rka-kl`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| RKA-01 | TOR Tidak Memuat 7 Blok Substansi Wajib | RKA-TOR | HIGH | PMK 107/2024 Pasal 61 |
| RKA-02 | RO Tidak Didukung Parameter Keberhasilan Terukur | RKA-OUTPUT | HIGH | PMK 107/2024 Pasal 61 + Pedoman Renja Bappenas |
| RKA-03 | Komponen/Sub-Komponen Belum Cukup Mendukung Ketercapaian RO | RKA-KOMPONEN | HIGH | PMK 107/2024 Pasal 61 + Lampiran Struktur RKA-K/L |
| RKA-04 | TOR Belum Jelaskan Metode Pengadaan dan Spesifikasi Teknis di Level Sub-Komponen | RKA-TOR | MEDIUM | PMK 107/2024 Pasal 61 + Perpres 16/2018 Pasal 18 |
| RKA-05 | Ketidakselarasan Komponen/Sub-Komponen antara Metode Pelaksanaan dan Tahapan Waktu | RKA-TIMELINE | MEDIUM | PMK 107/2024 Pasal 61 |
| RKA-06 | Cost Analysis Kecukupan Anggaran untuk Mencapai Output Belum Ada | RKA-ANGGARAN | HIGH | PMK 107/2024 Pasal 61 + PMK SBM tahun berjalan |
| RKA-07 | Indikator Kinerja RO OM Tidak Sesuai Prinsip OM | RKA-INDIKATOR | MEDIUM | PMK 107/2024 Pasal 61 + Pedoman OM |

## Kategori yang dipakai

- `RKA-TOR` — kelengkapan & substansi Term of Reference (7 blok wajib, metode pengadaan, spek teknis)
- `RKA-OUTPUT` — definisi & parameter keberhasilan RO
- `RKA-KOMPONEN` — kecukupan komponen/sub-komponen mendukung output
- `RKA-INDIKATOR` — keselarasan indikator kinerja (KPI) dengan jenis RO
- `RKA-ANGGARAN` — cost analysis & kecukupan
- `RKA-TIMELINE` — keselarasan jadwal dengan metode pelaksanaan
- `RKA-RAB` — kewajaran Rencana Anggaran Biaya (per item)
- `RKA-SBM` — kepatuhan terhadap Standar Biaya Masukan tahun anggaran
- `RKA-CASCADING` — konsistensi vertikal Output / RO / Komponen
- `RKA-PENANDAAN` — penandaan output kegiatan (mis. Tematik, Lokus)

## Sumber data pattern

Pattern di folder ini disusun dari LHR/CHR Inspektorat II TA 2025–2026:

- CHR Renja & Data Dukung Renja Ekosistem Digital 2026 (B-247/IJ.3/PW.02.04/08/2025) — sumber utama RKA-02 s.d. RKA-06
- CHR RKA-K/L Wasdig 2026 (B-282/IJ.3/PW.02.04/09/2025) — sumber RKA-07 + konteks pagu vs bare minimum
- LHR RKA BUN LPU 2026 (B-290/IJ.3/PW.04.04/09/2025)
- Berbagai LHR Revisi Anggaran (DBS, antar program, restrukturisasi) Ekdig & Wasdig 2025

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [`../../konteks/pola-temuan-berulang.md`](../../konteks/pola-temuan-berulang.md) — 9 pola berulang lintas LHP/LHR
- [`../../konteks/regulasi-kunci.md`](../../konteks/regulasi-kunci.md) — pasal baku PMK 107/2024 + Perpres 16/2018
- [`../../konteks/glossary-komdigi.md`](../../konteks/glossary-komdigi.md) — definisi istilah (RO, komponen, IKU, dst)
- [`../reviu-pengadaan/README.md`](../reviu-pengadaan/README.md) — pattern reviu Pengadaan
