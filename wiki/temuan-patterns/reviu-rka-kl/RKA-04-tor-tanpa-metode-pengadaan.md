---
id: RKA-04
skill: reviu-rka-kl
kategori: RKA-TOR
severity: MEDIUM
judul: "TOR Belum Jelaskan Metode Pengadaan dan Spesifikasi Teknis di Level Sub-Komponen"
kriteria_baku: "PMK 107/2024 Pasal 61 + Perpres 16/2018 Pasal 18 (Perencanaan Pengadaan)"
tags: [tor, metode-pengadaan, spesifikasi-teknis, sub-komponen, pmk-107]
---

# RKA-04: TOR Belum Jelaskan Metode Pengadaan dan Spesifikasi Teknis di Level Sub-Komponen

## Pattern Kondisi

TOR untuk RO mencantumkan komponen + sub-komponen, namun tidak menjelaskan **metode pengadaan** (mis. e-katalog, tender, swakelola) maupun **spesifikasi teknis kebutuhan** pada level sub-komponen. Indikator umum:

- TOR hanya menyebut nama sub-komponen tanpa kategori pengadaan
- Tidak ada rujukan ke Peraturan LKPP atau Perpres 16/2018 untuk metode yang dipilih
- Spesifikasi teknis hanya berbentuk daftar nama barang (mis. "1 unit server") tanpa spek minimum
- Anggaran sub-komponen tidak konsisten dengan metode pengadaan yang implicit (mis. nilai > Rp200 jt tapi metode "pengadaan langsung")
- RUP/SIRUP draft tidak konsisten dengan TOR

## Kriteria

**PMK 107/2024 Pasal 61** — TOR adalah gambaran umum + penjelasan keluaran termasuk lingkup pekerjaan + anggaran.

**Perpres 16/2018 Pasal 18** — Perencanaan Pengadaan wajib mencakup:
1. Identifikasi kebutuhan + spesifikasi
2. Pemilihan metode pengadaan
3. Jadwal pelaksanaan

Pengujian pada TOR:
1. Setiap sub-komponen yang melibatkan pengadaan disebut **metode** (tender, e-katalog, langsung, swakelola).
2. Spesifikasi teknis: minimum spek + jumlah unit + satuan.
3. Nilai anggaran sub-komponen konsisten dengan metode (ambang batas LKPP).

## Akibat

1. **RUP/SIRUP sulit disusun konsisten** — tidak ada anchor dari TOR untuk metode.
2. **Risiko pemilihan metode salah** — mis. nilai > Rp200 jt dipilih metode pengadaan langsung yang seharusnya tender.
3. **Penelaahan DJA berisiko dikembalikan** karena TOR tidak operasional.
4. **Pelaksana bingung saat eksekusi** — PPK harus menyusun ulang spek dan metode dari awal.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| TOR per sub-komponen | Metode pengadaan + spesifikasi teknis |
| RAB | Nilai per sub-komponen + kategori belanja (52/53/dst) |
| RUP/SIRUP draft | Konsistensi dengan TOR |
| Rujukan regulasi | Apakah TOR menyebut Peraturan LKPP yang berlaku |
| Daftar barang/jasa eksisting | Spek minimum yang biasa dipakai di Direktorat |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-RKA-XX",
  "assigned_to": "{nama anggota}",
  "judul": "TOR RO {nama RO} Belum Jelaskan Metode Pengadaan dan Spesifikasi Teknis di Level Sub-Komponen",
  "kondisi": "TOR RO {nama RO} di {satker} TA {YYYY} mencantumkan {N} sub-komponen pengadaan dengan total nilai Rp{X.XXX.XXX.XXX}. Pemeriksaan menemukan: (a) {M} dari {N} sub-komponen tidak menyebut metode pengadaan (tender/e-katalog/langsung/swakelola); (b) Spesifikasi teknis hanya berbentuk daftar nama barang tanpa spek minimum (mis. '1 unit server' tanpa CPU/RAM/storage minimum); (c) Beberapa sub-komponen bernilai > Rp200 jt tanpa rujukan ke Peraturan LKPP yang berlaku.",
  "kriteria": "PMK 107/2024 Pasal 61 + Perpres 16/2018 Pasal 18 mensyaratkan TOR memuat metode pengadaan + spesifikasi teknis di level operasional untuk mendukung penyusunan RUP/SIRUP yang konsisten.",
  "akibat": "RUP/SIRUP sulit disusun konsisten dengan TOR; risiko pemilihan metode pengadaan tidak sesuai dengan nilai/karakter belanja; PPK harus menyusun ulang spek/metode saat eksekusi.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/TOR-{nama-RO}.pdf", "halaman": "X", "kutipan": "Sub-komponen tanpa metode pengadaan / spek minimum"},
    {"file": "03-perencanaan/RAB-{nama-RO}.pdf", "halaman": "Y", "kutipan": "Nilai sub-komponen"}
  ]
}
```

## Rekomendasi Standar

- Narasikan **metode pengadaan** untuk setiap sub-komponen di TOR — eksplisit (tender/e-katalog/langsung/swakelola).
- Lampirkan **spesifikasi teknis minimum** per item barang/jasa.
- Pasang **rujukan regulasi** LKPP yang berlaku untuk masing-masing metode.
- Pasang **gate konsistensi**: TOR → RAB → RUP/SIRUP harus sinkron sebelum penayangan.

## Contoh Kasus Historis

- **CHR Renja Ekdig 2026 (B-247/IJ.3/PW.02.04/08/2025)** — Catatan substantif #4: **"TOR belum menjelaskan metode pengadaan dan spesifikasi teknis kebutuhan di level sub-komponen"**. Rekomendasi: narasikan metode pengadaan + spesifikasi teknis di TOR.

## Catatan

- Pattern ini sering muncul di RO baru atau RO dengan banyak sub-komponen pengadaan kecil.
- Severity dapat naik ke HIGH bila ada sub-komponen besar (≥ Rp1 M) yang tidak memiliki metode/spek.
- Lihat juga [[RP-11]] (Pagu SIRUP draft > 50% setelah TW I) — gejala dari pattern ini.
