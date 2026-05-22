---
id: RP-16
skill: reviu-pengadaan
kategori: PBJ-KONTRAK
severity: HIGH
judul: "Vendor/PJT Belum Berkontrak Padahal Layanan Sudah Berjalan / Wajib Tersedia"
kriteria_baku: "Perpres 16/2018 Pasal 1 angka 18 (Kontrak) + Pasal 18 (Perencanaan Pengadaan)"
tags: [pjt, vendor, kontrak, kontinuitas-layanan, perpres-16]
---

# RP-16: Vendor/PJT Belum Berkontrak Padahal Layanan Sudah Berjalan / Wajib Tersedia

## Pattern Kondisi

Pada awal/pertengahan TA, ditemukan sejumlah vendor/PJT (Penyedia Jasa Telekomunikasi) belum berkontrak walaupun layanan mereka sudah berjalan atau wajib tersedia. Kendala bersifat administratif, teknis, atau legalitas. Indikator umum:

- Pada TA-1 ada N vendor berkontrak, namun TA berjalan hanya M < N vendor yang berkontrak
- Sisanya (N – M) belum berkontrak karena alasan:
  - **Administratif**: persyaratan email INAPROC, status NAP belum diperbarui
  - **Teknis**: layanan vendor mengalami perubahan teknis yang tidak kompatibel (mis. topologi terenkripsi)
  - **Lokasi**: DC vendor di-sub-leased ke pihak ketiga dengan klausul rahasia
  - **Legalitas**: ada hambatan hukum (mis. confidentiality SUFI) yang perlu kajian terlebih dahulu
- Tidak ada checklist/timeline penyelesaian masalah per vendor
- Tidak ada CBA atas opsi penyelesaian (mis. pindah ke alternatif vs tetap dengan vendor lama)

## Kriteria

**Perpres 16/2018 Pasal 1 angka 18** — Kontrak adalah perjanjian tertulis antara Pejabat Penandatangan Kontrak dengan Penyedia.

**Perpres 16/2018 Pasal 18** — Perencanaan Pengadaan harus mencakup identifikasi penyedia + jadwal pelaksanaan yang terukur.

Pengujian dasar:
1. Daftar vendor TA berjalan vs TA-1 → identifikasi yang belum berkontrak.
2. Klasifikasi kendala per vendor (administratif/teknis/lokasi/legalitas).
3. Timeline penyelesaian per kendala.
4. Bila layanan vendor wajib tersedia (cakupan TKPPSE nasional, infrastruktur kritikal), kendala = risiko HIGH.

## Akibat

1. **Cakupan layanan tidak utuh** — bila vendor menyediakan jalur trafik nasional, ketidakhadiran kontrak = lubang cakupan.
2. **Risiko sengketa** — vendor yang sudah menyediakan layanan tanpa kontrak dapat menuntut pembayaran.
3. **Risiko fungsi sistem gagal** — TKPPSE/CSE/dll. tidak dapat berfungsi penuh tanpa vendor terkait.
4. **Tidak ada akuntabilitas** — pelaksana tidak tahu kapan kendala akan tuntas.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Daftar vendor/PJT berkontrak TA-1 | Total vendor + jenis layanan |
| Daftar vendor/PJT berkontrak TA berjalan | Subset dari TA-1 yang sudah ditandatangani |
| Berita Acara Internal | Status kendala per vendor yang belum kontrak |
| Surat menyurat dengan vendor | Riwayat negosiasi/penolakan |
| Kajian CBA (jika ada) | Opsi penyelesaian + biaya |
| Email/disposisi internal | Timeline penyelesaian yang dijanjikan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "{N} Vendor/PJT Belum Berkontrak di {satker} TA {YYYY} per {tanggal monitoring}",
  "kondisi": "Pada TA {YYYY-1} terdapat {N} vendor/PJT yang berkontrak. Pada TA {YYYY} per {tanggal monitoring}, hanya {M} vendor yang sudah berkontrak ({list vendor}). {N-M} vendor belum berkontrak karena kendala: (a) {vendor 1} — administratif: {detail}; (b) {vendor 2} — teknis: {detail topologi terenkripsi atau lainnya}; (c) {vendor 3} — legalitas: {detail confidentiality / lokasi sub-leased}. Tidak ditemukan checklist/timeline penyelesaian per vendor dan tidak ada CBA atas opsi alternatif.",
  "kriteria": "Perpres 16/2018 Pasal 18 mensyaratkan perencanaan pengadaan mencakup identifikasi penyedia + jadwal pelaksanaan yang terukur. Vendor yang menyediakan layanan kritikal (TKPPSE, infrastruktur ruang digital) wajib berkontrak sebelum atau bersamaan dengan dimulainya layanan.",
  "akibat": "Cakupan layanan {sistem terkait, mis. TKPPSE} tidak utuh di lokasi vendor terkait; risiko sengketa pembayaran untuk layanan yang sudah berjalan tanpa kontrak; ketidakpastian fungsi sistem milik satker di titik tersebut.",
  "dokumen_sumber": [
    {"file": "02-kontrak/Daftar-PJT-TA{YYYY-1}.pdf", "halaman": 1, "kutipan": "{N} PJT berkontrak"},
    {"file": "02-kontrak/Daftar-PJT-TA{YYYY}.pdf", "halaman": 1, "kutipan": "{M} PJT berkontrak"},
    {"file": "03-perencanaan/BA-Internal-Kendala.pdf", "halaman": 2, "kutipan": "{vendor}: kendala {jenis}"}
  ]
}
```

## Rekomendasi Standar

- Susun **checklist penyelesaian per vendor** dengan PJP, target tanggal, dan langkah-langkah administratif/teknis/legal.
- Lakukan **Cost-Benefit Analysis** untuk setiap kendala signifikan (mis. teknis Moratel, legalitas Lintasarta-SUFI).
- Pasang **timeline akhir** untuk masing-masing vendor — bila melewati TW II tanpa kontrak, eskalasi ke pimpinan Ditjen.
- Untuk vendor dengan kendala teknis fundamental (mis. tidak dapat dibaca trafik), siapkan **opsi alternatif** sejak awal.
- Susun **roadmap multi-tahun** (mis. roadmap TKPPSE 5 tahun) supaya kendala vendor masuk dalam rencana jangka panjang.

## Contoh Kasus Historis

- **LHP Pengadaan Redesain TKPPSE 2026 (B-34/IJ.3/PW.04.03/01/2026)**: TA 2025 ada 16 PJT berkontrak; TA 2026 per 26 Januari 2026 hanya **6 PJT yang sudah berkontrak** (Indosat, Telkomsel, XLSmart, Telkom, Telkomsat, Kreatif Pacific). Sisanya **6 PJT belum berkontrak**: PT NTT (administratif + status NAP), PT Trans Hybrid Communication (teknis), PT Dinamika (lokasi disewa PT SUFI), PT Moratel (teknis signifikan — topologi terenkripsi), PT Lintasarta + iForte (legalitas signifikan — confidentiality SUFI). Rekomendasi LHP: checklist Lintasarta + CBA Moratel + timeline 2026 + roadmap 5 tahun.

## Catatan

- Pattern ini lazim di pengadaan layanan infrastruktur terdistribusi (TKPPSE multi-PJT, ISP, kolokasi multi-DC).
- Severity dapat dipertahankan HIGH bila vendor terkait paket Prioritas Nasional atau layanan kritikal.
- Lihat juga [[RP-09]] (kontrak tanpa kontrak akibat SOTK) dan [[RP-13]] (klausul confidentiality vendor).
- Untuk Itjen: pertimbangkan masukan ke peta risiko Ditjen ([[peta-risiko-wasdig-2026]]) bila pola berulang antar TA.
