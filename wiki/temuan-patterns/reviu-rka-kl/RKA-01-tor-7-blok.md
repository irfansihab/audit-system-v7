---
id: RKA-01
skill: reviu-rka-kl
kategori: RKA-TOR
severity: HIGH
judul: "TOR Tidak Memuat 7 Blok Substansi Wajib"
kriteria_baku: "PMK 107/2024 tentang Petunjuk Penyusunan dan Penelaahan RKA-K/L Pasal 61"
tags: [tor, kelengkapan, pmk-107]
---

# RKA-01: TOR Tidak Memuat 7 Blok Substansi Wajib

## Pattern Kondisi

TOR (Term of Reference) tidak memuat satu atau lebih dari **7 blok substansi wajib** sesuai PMK 107/2024. Indikator umum:

- Tidak ada section "Latar Belakang" atau hanya 1-2 kalimat formalitas
- "Maksud & Tujuan" digabung jadi satu paragraf umum
- "Ruang Lingkup" tidak menyebutkan keluaran (output) spesifik
- "Strategi Pelaksanaan" tidak ada — langsung lompat ke anggaran
- "Indikator Kinerja" tidak terukur / hanya kualitatif tanpa target

## 7 Blok Substansi Wajib (PMK 107/2024)

1. **Latar belakang** — kebutuhan, urgensi, dasar hukum
2. **Maksud dan tujuan** — eksplisit dipisah
3. **Sasaran, output, dan indikator kinerja** — terukur
4. **Ruang lingkup** — lingkup pekerjaan & batasan
5. **Strategi pelaksanaan** — pendekatan, mekanisme
6. **Anggaran** — pagu + rincian akun
7. **Jadwal** — milestone per bulan / triwulan

## Kriteria

PMK 107/2024 tentang Petunjuk Penyusunan dan Penelaahan RKA-K/L **Pasal 61**:

> "Kerangka Acuan Kerja (KAK)/Term of Reference (TOR) merupakan gambaran umum dan penjelasan mengenai keluaran kegiatan yang akan dilaksanakan, antara lain memuat latar belakang, dasar hukum, gambaran umum, tujuan, sasaran, indikator kinerja, lingkup pekerjaan, anggaran, dan jadwal pelaksanaan."

## Akibat

1. **Penelaahan oleh DJA/Bappenas terhambat** — TOR yang tidak lengkap akan dikembalikan untuk diperbaiki, mundur dari jadwal
2. **Sulit dilakukan pemantauan & evaluasi** — tanpa indikator yang terukur, tidak ada baseline untuk evaluasi capaian
3. **Risiko ketidaksesuaian eksekusi vs perencanaan** — strategi tidak jelas = pelaksana bisa menafsirkan berbeda

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| TOR PDF | Heading section — apakah ke-7 blok ada |
| TOR PDF | "Indikator Kinerja" — apakah dilengkapi target angka & satuan |
| TOR PDF | "Anggaran" — apakah ada rincian per akun atau hanya total |
| TOR PDF | "Jadwal" — apakah per bulan/triwulan, atau hanya "tahun X" |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-RKA-01",
  "assigned_to": "{nama anggota}",
  "judul": "TOR Kegiatan {nama_kegiatan} Tidak Memuat Strategi Pelaksanaan dan Indikator Kinerja Terukur",
  "kondisi": "TOR kegiatan {nama} TA 2026 tidak memuat 2 dari 7 blok wajib: (1) Strategi Pelaksanaan tidak ada; (2) Indikator Kinerja hanya disebut 'capaian output ≥ 95%' tanpa unit pengukuran atau cara verifikasi.",
  "kriteria": "PMK 107/2024 Pasal 61 mensyaratkan TOR memuat 7 blok substansi termasuk indikator kinerja yang terukur dan strategi pelaksanaan.",
  "akibat": "TOR yang tidak lengkap berisiko dikembalikan saat penelaahan DJA dan menyulitkan monitoring capaian output.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/TOR-XXX.pdf", "halaman": 2, "kutipan": "Section 'Indikator Kinerja': 'Persentase capaian output ≥ 95%'"}
  ]
}
```

## Rekomendasi Standar

- Lengkapi 2-3 blok yang hilang sebelum diserahkan ke DJA
- Pasang indikator kinerja yang terukur (angka, %, jumlah, tanggal)
- Pasang milestone pelaksanaan per triwulan
