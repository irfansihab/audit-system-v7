---
id: RP-09
skill: reviu-pengadaan
kategori: PBJ-KONTRAK
severity: HIGH
judul: "Pekerjaan Berjalan Tanpa Kontrak Akibat DIPA Terlambat (Transisi SOTK)"
kriteria_baku: "Perpres 46/2025 Pasal 9 ayat (1) huruf f angka 2"
tags: [kontrak, sotk, dipa, transisi, perpres-46]
---

# RP-09: Pekerjaan Berjalan Tanpa Kontrak Akibat DIPA Terlambat (Transisi SOTK)

## Pattern Kondisi

Pekerjaan/layanan terus berjalan namun kontrak periode TA berjalan belum ditandatangani karena DIPA terbit terlambat akibat perubahan SOTK kementerian/lembaga (mis. Kominfo → Komdigi). Indikator umum:

- Vendor tetap menyediakan layanan *continuous* (telekomunikasi, kolokasi, ISP, OM TKPPSE) selama 3–6 bulan tanpa kontrak periode TA berjalan
- Tagihan vendor masuk ke unit pemilik tapi tidak ada SPK/SPPBJ untuk periode tagihan tersebut
- Justifikasi yuridis baru disusun *setelah* pekerjaan berjalan
- DIPA satker direvisi/baru terbit pada TW II atau TW III TA berjalan

## Kriteria

**Perpres 46/2025 Pasal 9 ayat (1) huruf f angka 2** — membenarkan pekerjaan yang sudah berjalan sebelum anggaran ditetapkan dapat diproses pembayarannya sepanjang justifikasi terpenuhi.

Pengujian wajar:
1. **Justifikasi terpenuhi** — ada dasar keterlambatan DIPA yang sah (mis. perubahan SOTK terdokumentasi).
2. **Harga wajar** — nilai kontrak konsisten dengan periode sebelumnya (tidak markup).
3. **SLA tercapai** — capaian SLA ≥95% selama periode berjalan tanpa kontrak.

## Akibat

1. **Risiko temuan BPK** — pembayaran tanpa kontrak periode TA berjalan dapat di-flag sebagai pengeluaran tidak didukung dokumen kontrak yang sah.
2. **Sengketa vendor** — bila salah satu syarat (harga/SLA) tidak terpenuhi, vendor dapat menggugat dasar penundaan pembayaran.
3. **Audit trail tidak lengkap** — adendum/SPK kontinuitas yang baru disusun belakangan sulit diaudit secara linier.
4. **Preseden buruk** — pola ini berulang setiap kali ada transisi kelembagaan.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| DIPA satker TA berjalan | Tanggal terbit DIPA (revisi terakhir) |
| Kontrak periode sebelumnya | Tanggal berakhir kontrak TA-1 |
| Tagihan vendor | Tanggal mulai layanan vs tanggal kontrak baru |
| Surat permintaan justifikasi | Apakah dasar Perpres 46/2025 ps. 9(1)f² disebut eksplisit |
| Laporan SLA periode tanpa kontrak | Capaian SLA bulanan |
| Daftar harga vs kontrak TA sebelumnya | Apakah nilai per item konsisten |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Pekerjaan {nama pekerjaan} Berjalan Tanpa Kontrak Periode {bulan-bulan} TA {YYYY} akibat Keterlambatan DIPA Pasca Perubahan SOTK",
  "kondisi": "Pekerjaan {nama} dengan vendor {vendor} bernilai Rp{X.XXX.XXX.XXX} berjalan terus dari {tanggal-mulai} sampai {tanggal-akhir} tanpa kontrak TA berjalan. DIPA satker baru terbit/revisi pada {tanggal-DIPA} karena proses transisi SOTK {Kominfo→Komdigi}. Vendor terus menyediakan layanan continuous (telekomunikasi/kolokasi/ISP) dengan capaian SLA {X}%.",
  "kriteria": "Perpres 46/2025 Pasal 9 ayat (1) huruf f angka 2 membenarkan pekerjaan yang berjalan sebelum anggaran ditetapkan dapat diproses pembayarannya sepanjang justifikasi terpenuhi, harga wajar, dan SLA tercapai.",
  "akibat": "Tanpa dokumen kontrak periode TA berjalan, pembayaran berisiko menjadi temuan BPK atau menimbulkan sengketa kontrak. Pola transisi tanpa kontrak yang berulang juga mencerminkan absennya SOP transisi kontrak lintas unit.",
  "dokumen_sumber": [
    {"file": "02-kontrak/Tagihan-{vendor}.pdf", "halaman": 1, "kutipan": "Periode layanan: {bulan} {YYYY}"},
    {"file": "03-perencanaan/DIPA-{satker}.pdf", "halaman": 1, "kutipan": "Tanggal terbit: {tanggal}"}
  ]
}
```

## Rekomendasi Standar

- Susun SOP transisi kontrak lintas Ditjen sebelum cut-off SOTK berikutnya.
- Setiap audit pengadaan di TA transisi wajib bandingkan tanggal DIPA vs tanggal mulai pekerjaan.
- Pastikan landasan Perpres 46/2025 ps. 9(1)f² disebut eksplisit di Nota Dinas justifikasi.
- Rekomendasikan early-flag DIPA: bila DIPA belum terbit per akhir TW I, satker pemilik pekerjaan kontinu wajib lapor ke Itjen.

## Contoh Kasus Historis

- **LHR Aptika 2025 (B-66/IJ.3/PW.04.04/02/2026)**: 3 kontrak ex-Aptika (Root CA PSrE Rp2,90M, Colocation Rp2,18M, ISP Paket 1 Rp1,03M) berjalan Januari–Mei 2025 tanpa kontrak; disimpulkan dapat diproses dengan dasar Perpres 46/2025 ps. 9(1)f².
- **LHA OM TKPPSE 2025**: tagihan Desember 2025 tanpa kontrak senilai Rp2,69M.
- **LHP Pengadaan Redesain TKPPSE 2026**: 6 PJT belum berkontrak per 26 Januari 2026.

## Catatan

- Pola ini lintas-LHP — lihat juga [[pola-temuan-berulang]] poin #1.
- Jangan rekomendasikan pembatalan tagihan kecuali ada indikasi nyata mark-up atau SLA gagal.
- Untuk kasus *continuous service*, justifikasi yuridis biasanya terpenuhi — fokus rekomendasi ke SOP preventif, bukan ke "salah pemberi pekerjaan".
