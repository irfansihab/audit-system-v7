---
id: RKA-05
skill: reviu-rka-kl
kategori: RKA-TIMELINE
severity: MEDIUM
judul: "Ketidakselarasan Komponen/Sub-Komponen antara Metode Pelaksanaan dan Tahapan Waktu"
kriteria_baku: "PMK 107/2024 Pasal 61 + Lampiran Petunjuk Penyusunan Jadwal Kegiatan"
tags: [komponen, sub-komponen, jadwal, metode-pelaksanaan, timeline, pmk-107]
---

# RKA-05: Ketidakselarasan Komponen/Sub-Komponen antara Metode Pelaksanaan dan Tahapan Waktu

## Pattern Kondisi

Narasi metode pelaksanaan di komponen/sub-komponen tidak selaras dengan tahapan/waktu pelaksanaan yang dijadwalkan. Indikator umum:

- Komponen menyebut metode "swakelola tipe I 6 bulan" tetapi jadwal hanya TW IV (3 bulan)
- Pengadaan via tender (lead time 2–3 bulan) dijadwalkan dieksekusi mulai TW I, padahal proses pemilihan baru bisa selesai TW II
- Sub-komponen pelatihan internal direncanakan TW III, tetapi metode menyatakan dilaksanakan oleh penyedia eksternal yang belum di-RFI
- Jadwal kegiatan menumpuk di TW IV (> 60% kegiatan) — indikasi metode tidak realistis di awal TA
- Sub-komponen yang saling berurutan (output sub-komponen 1 = input sub-komponen 2) dijadwalkan paralel

## Kriteria

**PMK 107/2024 Pasal 61** — TOR memuat jadwal pelaksanaan yang **selaras** dengan metode + komponen.

Pengujian:
1. **Lead time per metode** sesuai durasi (mis. tender ≥ 2 bulan, e-katalog 2–4 minggu, swakelola tipe I berkelanjutan).
2. **Dependency antar sub-komponen** terpetakan — sub-komponen A → B → C tidak boleh paralel.
3. **Distribusi triwulan**: idealnya merata; > 60% kegiatan di TW IV = red flag.

## Akibat

1. **Risiko eksekusi gagal** — kegiatan tertunda atau dibatalkan karena waktu tidak cukup.
2. **Daya serap anggaran rendah** — TW IV crunch time → serapan akhir TA gagal target.
3. **Kualitas pelaksanaan menurun** — vendor/pelaksana terburu-buru.
4. **Pelanggaran prinsip perencanaan operasional**.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| TOR per sub-komponen | Metode + waktu pelaksanaan |
| Gantt chart / Jadwal Kegiatan TA | Distribusi per triwulan |
| RUP/SIRUP draft | Tanggal mulai dan akhir paket pengadaan |
| Riwayat eksekusi TA-1 | Berapa % kegiatan terserap di TW IV |
| Lead time standar metode (LKPP) | Acuan durasi proses pemilihan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-RKA-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Ketidakselarasan Metode Pelaksanaan dan Tahapan Waktu pada {N} Sub-Komponen RO {nama RO}",
  "kondisi": "RO {nama RO} di {satker} TA {YYYY} memiliki {N} sub-komponen dengan ketidakselarasan jadwal-metode: (a) Sub-komponen {nama} menyebut metode '{metode, mis. tender}' tetapi jadwal {detail jadwal, mis. mulai 1 Februari} — lead time minimum {durasi} membuat eksekusi tidak realistis; (b) Sub-komponen {nama lain} dijadwalkan paralel dengan sub-komponen {dependent} padahal sub-komponen tersebut menjadi input untuk pelaksanaannya; (c) {X}% kegiatan menumpuk di TW IV.",
  "kriteria": "PMK 107/2024 Pasal 61 mensyaratkan TOR memuat jadwal pelaksanaan yang selaras dengan metode + komponen. Lead time setiap metode pengadaan harus konsisten dengan tahapan TA.",
  "akibat": "Risiko eksekusi gagal atau tertunda karena waktu tidak cukup; daya serap akhir TA tertekan; kualitas pelaksanaan menurun karena crunch time TW IV.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/TOR-{nama-RO}.pdf", "halaman": "X", "kutipan": "Metode: ...; Jadwal: ..."},
    {"file": "03-perencanaan/Gantt-{nama-RO}.pdf", "halaman": 1, "kutipan": "Distribusi triwulan"}
  ]
}
```

## Rekomendasi Standar

- Selaraskan **narasi metode** dan **jadwal pelaksanaan** per sub-komponen.
- Susun **Gantt chart** dengan dependency antar sub-komponen.
- Tetapkan **distribusi triwulan target** (mis. 25–25–25–25 atau 20–30–30–20) — hindari > 50% di TW IV.
- Pakai **lead time baku LKPP** sebagai acuan: tender 60–90 hari, e-katalog 14–30 hari, swakelola tipe I/II/III sesuai sifatnya.

## Contoh Kasus Historis

- **CHR Renja Ekdig 2026 (B-247/IJ.3/PW.02.04/08/2025)** — Catatan substantif #5: **"Ketidakselarasan komponen/sub-komponen antara metode pelaksanaan dan tahapan/waktu pelaksanaan"**. Rekomendasi: selaraskan narasi komponen/sub-komponen dalam metode pelaksanaan dengan timeline.

## Catatan

- Pola ini sering merupakan akar penyebab dari [[RP-11]] (Pagu SIRUP draft tinggi di akhir TW I).
- Severity dapat naik ke HIGH bila Quattro paket besar (≥ Rp1 M) terjadwal di TW IV.
