---
id: KONTEKS-POLA-BERULANG
kategori: konteks
judul: "9 Pola Temuan Berulang Inspektorat II (2025-2026)"
sumber: "Sintesis 11+ LHP/LHR Inspektorat II TA 2025–2026"
tanggal_update: "2026-04-24"
tags: [pola-berulang, akar-masalah, audit-preventif, cheat-sheet]
---

# 9 Pola Temuan Berulang — Inspektorat II Komdigi

**Tujuan halaman ini**: cheat sheet yang dibaca agen **sebelum** susun KKP/temuan. Pola-pola di bawah adalah akar masalah yang sudah teridentifikasi lintas LHP TA 2025–2026. Bila kondisi dokumen yang sedang dianalisis cocok dengan salah satu pola, gunakan pattern terkait (`RP-XX` atau `RKA-XX`) sebagai referensi formulasi.

**Catatan penting untuk agen**:
- Pola di bawah BUKAN template untuk dipakai *copy-paste*. Setiap temuan tetap wajib didukung bukti dari dokumen yang dianalisis.
- Bila bukti tidak mendukung pola, JANGAN paksakan pola tersebut. Lapor `feedback` jika menemukan pola baru.
- Sitasi peraturan harus diverifikasi ke [[regulasi-kunci]].

---

## Pola 1 — Kontrak Berjalan Tanpa Kontrak (Akibat SOTK Kominfo→Komdigi)

**Akar masalah**: DIPA terbit terlambat pasca perubahan SOTK; belum ada playbook transisi kontrak; vendor tetap bekerja karena layanan continuous.

**Pattern terkait**: [[RP-09]]

**Contoh kasus**:
- LHA TKPPSE 2025: tagihan Desember 2025 tanpa kontrak Rp2,69 M
- LHR Aptika 2025: 3 kontrak (Root CA PSrE Rp2,9 M, Colocation Rp2,2 M, ISP Rp1 M) berjalan tanpa kontrak
- LHP Pengadaan TKPPSE 2026: 6 PJT belum berkontrak awal TA

**Yang harus dicek agen**: tanggal DIPA vs tanggal mulai pekerjaan; dasar Perpres 46/2025 ps. 9(1)f² disebut eksplisit.

---

## Pola 2 — Draft SIRUP Tidak Tuntas di Awal Tahun

**Akar masalah**: perencanaan pengadaan belum matang menjelang akhir TW I.

**Pattern terkait**: [[RP-11]]

**Contoh kasus**:
- LHP Program Prioritas Wasdig: 68,36% pagu (Rp236,7M) masih draft per 27 Januari 2026; 3 paket risiko tinggi Rp95M.

**Yang harus dicek agen**: konsistensi SIRUP vs RKA-K/L; status paket Prioritas Nasional; pagu draft TW > I = red flag.

---

## Pola 3 — Kajian Teknis Belum Diimplementasikan

**Akar masalah**: kajian tertulis tapi tidak diterjemahkan ke rencana aksi konkret dengan milestone.

**Pattern terkait**: [[RP-12]]

**Contoh kasus**:
- Redesain TKPPSE: kajian teknis baru akan dikaji TW II 2026, eksekusi TA 2027.

**Yang harus dicek agen**: tanyakan "kajian ini akan jadi apa di tahun berjalan?"; cek RO turunan kajian di RKA-K/L.

---

## Pola 4 — Pedoman Internal Usang (Regulasi Nomenklatur Lama)

**Akar masalah**: pedoman/SOP masih merujuk regulasi lama, tidak disesuaikan dengan SOTK atau regulasi pengganti.

**Pattern terkait**: [[RKA-07]] (berdekatan), [[RP-15]] (e-katalog tanpa negosiasi)

**Contoh kasus**:
- Pedoman MR masih memakai Permenkominfo 6/2017 (sumber: LHE MR 2026).
- SOP Wasdig masih gunakan nomenklatur Kominfo lama; belum ada Renstra baru.

**Yang harus dicek agen**: cek tanggal terakhir revisi pedoman + nomenklatur regulasi yang dirujuk.

---

## Pola 5 — Sistem Informasi Tidak Terintegrasi / Belum Early Warning

**Akar masalah**: sistem informasi hanya berfungsi sebagai repositori, belum sebagai decision support.

**Pattern terkait**: (umum — bisa di RKA atau pengadaan tergantung konteks)

**Contoh kasus**:
- SIMR Kemkomdigi: belum memiliki fitur early warning, belum terintegrasi lintas unit.

**Yang harus dicek agen**: apakah sistem digunakan untuk memicu tindakan (action), bukan hanya pelaporan; interoperabilitas dengan sistem lain.

---

## Pola 6 — Data Kinerja Tidak Dapat Diverifikasi Sumbernya

**Akar masalah**: capaian dilaporkan tinggi tapi sumber data tidak traceable.

**Pattern terkait**: [[RKA-02]] (RO tanpa parameter keberhasilan)

**Contoh kasus**:
- LKj Kemkomdigi 2025: data tidak dapat diverifikasi sumbernya, belum ada analisis efisiensi SDM.

**Yang harus dicek agen**: minta source of truth setiap indikator (aplikasi, spreadsheet, BA); flag indikator yang sumber datanya "olahan internal tanpa referensi".

---

## Pola 7 — Kelemahan Tata Kelola Sistem Layanan Baru

**Akar masalah**: sistem baru diluncurkan dengan kelemahan di hulu (klasifikasi/verifikasi) dan hilir (keamanan, data sensitif).

**Pattern terkait**: (umum — layanan baru lintas skill)

**Contoh kasus**:
- IGRS: inkonsistensi rating, status RC tidak transparan, kebocoran data developer.

**Yang harus dicek agen**: 5 area sasaran kerangka audit layanan baru — kesiapan sistem, akurasi klasifikasi, mekanisme review, keamanan, tata kelola kemitraan.

---

## Pola 8 — Anomali Administrasi Kontrak

**Akar masalah**: inkonsistensi nomor adendum, tanggal, atau versi dokumen kontrak.

**Pattern terkait**: [[RP-10]]

**Contoh kasus**:
- Server crawling CSE: adendum ganda bernomor sama (AD01) dengan isi berbeda.

**Yang harus dicek agen**: konsistensi nomor adendum, tanggal berurutan, versi dokumen.

---

## Pola 9 — Hambatan Teknis pada Vendor Besar (Topologi/Kontrak Tertutup)

**Akar masalah**: vendor besar punya klausul atau arsitektur yang menghalangi pengawasan teknis rutin.

**Pattern terkait**: [[RP-13]], [[RP-16]]

**Contoh kasus**:
- Moratel: topologi terenkripsi — TCP Reset tidak dapat baca trafik.
- Lintasarta: confidentiality SUFI.

**Yang harus dicek agen**: clause audit trail di kontrak; opsi alternatif via CBA.

---

## Ringkasan: Pola → Area Audit Preventif

| Pola | Pattern | Area Audit Preventif |
|------|---------|----------------------|
| 1 — Kontrak tanpa kontrak (SOTK) | [[RP-09]] | SOP transisi kontrak; monitoring DIPA awal TA |
| 2 — Pagu draft SIRUP tinggi | [[RP-11]] | Sinkronisasi RKA-K/L → SIRUP; early flag TW I |
| 3 — Kajian tanpa implementasi | [[RP-12]] | Milestone tracking; roadmap multi-tahun |
| 4 — Pedoman usang | [[RKA-07]] | Reguler policy refresh per 3 tahun |
| 5 — Sistem belum early warning | (umum) | Audit IT fokus fungsionalitas |
| 6 — Data kinerja tidak traceable | [[RKA-02]] | Reviu LKj dengan uji traceability |
| 7 — Layanan baru: tata kelola | (umum) | Framework 5-area IGRS |
| 8 — Administrasi kontrak inkonsisten | [[RP-10]] | Sistem nomenklatur adendum terpusat |
| 9 — Vendor besar klausul tertutup | [[RP-13]], [[RP-16]] | Klausul right to audit; CBA vendor |

---

## Cara Pakai untuk Agen

1. **Sebelum susun KKP**: baca halaman ini secara penuh untuk re-orientasi.
2. **Saat menemukan kondisi**: cocokkan dengan pola di atas. Bila cocok, panggil `get_temuan_pattern("RP-XX" / "RKA-XX")` untuk dapat format detail.
3. **Bila tidak cocok dengan pola manapun**: tetap susun temuan dengan format generik (kondisi-kriteria-akibat); kirim `submit_feedback` untuk menandai pola baru yang perlu di-curate auditor.
4. **JANGAN paksakan pola** ke kondisi yang tidak didukung bukti. Bukti dokumen > pola.
