# Pattern Temuan — Reviu Pengadaan

Index pattern temuan yang berlaku untuk skill `reviu-pengadaan`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| RP-08 | HPS Tidak Didukung Minimum 2 Sumber Harga Independen | PBJ-HPS | CRITICAL | Perpres 16/2018 jo. Perpres 12/2021 Pasal 26 ayat (5) |
| RP-09 | Pekerjaan Berjalan Tanpa Kontrak Akibat DIPA Terlambat (Transisi SOTK) | PBJ-KONTRAK | HIGH | Perpres 46/2025 Pasal 9 ayat (1) huruf f angka 2 |
| RP-10 | Adendum Bernomor Sama dengan Isi Berbeda (Pelanggaran Prinsip Akuntabel) | PBJ-KONTRAK | HIGH | Perpres 16/2018 jo. Perpres 12/2021 Pasal 6 huruf g |
| RP-11 | Pagu SIRUP Status Draft > 50% Setelah Akhir Triwulan I | PBJ-SIRUP | HIGH | Perpres 16/2018 Pasal 22 + Peraturan LKPP RUP |
| RP-12 | Hasil Kajian Teknis Belum Diturunkan ke Rencana Aksi dengan Milestone | PBJ-PERENCANAAN | MEDIUM | Perpres 16/2018 Pasal 18 |
| RP-13 | Klausul Confidentiality Vendor Menghambat Audit Trail Teknis | PBJ-KONTRAK | MEDIUM | Perpres 16/2018 Pasal 6 huruf g + UU 15/2004 |
| RP-14 | Perpanjangan Lisensi Dihitung dari Tanggal Awal Kontrak, Bukan dari Masa Berakhir Lisensi | PBJ-HPS | MEDIUM | Perpres 16/2018 Pasal 26 |
| RP-15 | Pemilihan via E-Katalog/E-Purchasing Tanpa Negosiasi atau Mini Kompetisi | PBJ-PEMILIHAN | MEDIUM | Peraturan LKPP 9/2021 + 4/2024 |
| RP-16 | Vendor/PJT Belum Berkontrak Padahal Layanan Sudah Berjalan / Wajib Tersedia | PBJ-KONTRAK | HIGH | Perpres 16/2018 Pasal 1 angka 18 + Pasal 18 |

## Kategori yang dipakai

- `PBJ-KAK` — kelengkapan & substansi Kerangka Acuan Kerja
- `PBJ-HPS` — kewajaran Harga Perkiraan Sendiri
- `PBJ-RFI` — kelengkapan & validitas Request for Information
- `PBJ-KONTRAK` — substansi kontrak (SLA, denda, pasal-pasal, adendum)
- `PBJ-SIRUP` — perencanaan pengadaan & status RUP
- `PBJ-PERENCANAAN` — kelengkapan dokumen perencanaan (kajian, roadmap)
- `PBJ-PEMILIHAN` — kewajaran metode pemilihan (Tender, E-Purchasing, Langsung)
- `PBJ-TRACEABILITY` — konsistensi antar dokumen (KAK ↔ HPS ↔ Kontrak)

## Sumber data pattern

Pattern di folder ini disusun dari LHR/LHP Inspektorat II TA 2025–2026:

- LHA OM TKPPSE 2025
- LHR Kontrak Aptika 2025 (B-66/IJ.3/PW.04.04/02/2026)
- LHR Server Crawling CSE 2025 (B-41/IJ.3/PW.04.04/02/2026)
- LHR Pengadaan Lisensi Forensik 2025 (B-278/IJ.3/PW.04.04/09/2025)
- LHP Pengadaan Program Prioritas Wasdig 2026 (B-33/IJ.3/PW.04.03/01/2026)
- LHP Pengadaan Redesain TKPPSE 2026 (B-34/IJ.3/PW.04.03/01/2026)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [`../../konteks/pola-temuan-berulang.md`](../../konteks/pola-temuan-berulang.md) — 9 pola berulang lintas LHP/LHR
- [`../../konteks/regulasi-kunci.md`](../../konteks/regulasi-kunci.md) — pasal baku regulasi
- [`../reviu-rka-kl/README.md`](../reviu-rka-kl/README.md) — pattern reviu RKA-K/L
