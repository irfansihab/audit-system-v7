---
id: RKA-06
skill: reviu-rka-kl
kategori: RKA-ANGGARAN
severity: HIGH
judul: "Cost Analysis Kecukupan Anggaran untuk Mencapai Output Belum Ada"
kriteria_baku: "PMK 107/2024 Pasal 61 + PMK SBM (Standar Biaya Masukan) tahun berjalan"
tags: [cost-analysis, kecukupan-anggaran, sbm, rab, pmk-107]
---

# RKA-06: Cost Analysis Kecukupan Anggaran untuk Mencapai Output Belum Ada

## Pattern Kondisi

RKA-K/L mencantumkan total anggaran per RO + RAB rinci, namun tidak ada **cost analysis** yang membuktikan kecukupan anggaran untuk mencapai output yang ditargetkan. Indikator umum:

- RAB hanya berbentuk daftar belanja (harga × jumlah) tanpa pembanding output
- Tidak ada perhitungan "unit cost per output" (mis. biaya per startup, biaya per kantor LPU)
- Tidak ada benchmarking dengan TA-1 atau K/L lain
- Total anggaran terlihat "muat" output secara administratif tapi tidak ada justifikasi substansial
- Bila terjadi *cut* dari pagu indikatif ke pagu definitif, RAB tidak direvisi proporsional dengan target output

## Kriteria

**PMK 107/2024 Pasal 61** + Pedoman Renja Bappenas mensyaratkan RKA-K/L memuat:
1. **Komposisi anggaran** per komponen/sub-komponen yang dijustifikasi.
2. **Kecukupan anggaran** terhadap target output.

Pengujian:
1. **Unit cost analysis**: total anggaran ÷ target output = unit cost. Bandingkan dengan TA-1 atau benchmark sejenis.
2. **Bottom-up vs top-down**: cek apakah RAB disusun dari bawah (per kegiatan riil) atau dipaksa pas dengan pagu.
3. **Sensitivity analysis**: bila pagu di-cut X%, output target seharusnya disesuaikan.

## Akibat

1. **Anggaran tidak realistis** — output gagal tercapai karena anggaran kurang, atau anggaran berlebih (pemborosan).
2. **Pelaksana menambah/mengurangi item tanpa dasar** saat eksekusi.
3. **Tidak ada *value for money* terukur**.
4. **Pelanggaran prinsip *evidence-based budgeting*** yang menjadi kriteria AKIP PAN-RB.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| RAB rinci per RO | Komposisi belanja + asumsi |
| Dokumen pembentuk harga | RFI, kuotasi, e-katalog reference |
| Riwayat realisasi TA-1 | Unit cost output sebelumnya |
| Benchmarking eksternal | Unit cost di K/L lain |
| SBM PMK tahun berjalan | Acuan harga satuan |
| Skenario sensitivity (kalau ada) | Bila pagu dipangkas, output disesuaikan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-RKA-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Cost Analysis Kecukupan Anggaran RO {nama RO} Belum Tersedia di RKA-K/L TA {YYYY}",
  "kondisi": "RO {nama RO} di {satker} TA {YYYY} mengalokasikan anggaran Rp{X.XXX.XXX.XXX} untuk target output '{Y} {satuan}'. Pemeriksaan menemukan: (a) RAB hanya berbentuk daftar belanja (harga × jumlah) tanpa perhitungan unit cost per output; (b) Tidak ada pembanding TA-1 maupun benchmark K/L lain untuk menilai kewajaran; (c) Bila pagu indikatif ({Rp pagu indikatif}) di-cut menjadi pagu definitif ({Rp pagu definitif}), tidak ditemukan dokumen sensitivity analysis yang menyesuaikan target output dengan pagu baru.",
  "kriteria": "PMK 107/2024 Pasal 61 + Pedoman Renja Bappenas mensyaratkan kecukupan anggaran terhadap output dijustifikasi melalui cost analysis. RAB tidak cukup hanya berbentuk daftar belanja.",
  "akibat": "Risiko output gagal tercapai karena anggaran kurang, atau pemborosan karena anggaran berlebih; pelaksana berpotensi menambah/mengurangi item tanpa dasar; tidak ada value for money yang terukur.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/RAB-{nama-RO}.pdf", "halaman": "X", "kutipan": "Daftar belanja tanpa unit cost analysis"},
    {"file": "03-perencanaan/RKA-KL-{satker}-{YYYY}.pdf", "halaman": "Y", "kutipan": "RO {nama}: Anggaran Rp{X}, Output {Y}"}
  ]
}
```

## Rekomendasi Standar

- Lampirkan **cost analysis** per RO: unit cost output + perbandingan TA-1 + benchmark eksternal.
- Susun **RAB bottom-up** dari kegiatan riil, bukan dipaksa pas dengan pagu.
- Bila ada *cut* pagu, lakukan **sensitivity analysis**: target output disesuaikan dengan pagu baru, atau scope dikurangi.
- Pasang **gate kecukupan** sebelum pengusulan: matriks "Anggaran cukup untuk mencapai output? (Ya/Tidak/Catatan)".

## Contoh Kasus Historis

- **CHR Renja Ekdig 2026 (B-247/IJ.3/PW.02.04/08/2025)** — Catatan substantif #6: **"Cost analysis kecukupan anggaran dalam mencapai output belum ada"**. Rekomendasi: pastikan kembali komposisi anggaran dalam mencapai output.
- **CHR RKA-K/L Wasdig 2026 (B-282/IJ.3/PW.02.04/09/2025)** — Pagu Rp134,82M vs bare minimum Rp542,02M = **gap ~75%**. Tanpa cost analysis yang jelas, dampak pemangkasan ke 6 fungsi inti Wasdig (TKPPSE, Penyidikan, PSrE Induk, Moderasi PSE, Lembaga PDP, Pengelolaan Domain) tidak terkuantifikasi.

## Catatan

- Pattern ini lebih berat di RO yang melibatkan banyak komponen dan target output kuantitatif.
- Cost analysis tidak perlu rumit — minimal: unit cost output + benchmark + sensitivity.
- Severity HIGH karena dampak langsung ke akuntabilitas anggaran.
- Lihat juga [[RKA-02]] (RO tanpa parameter keberhasilan) — dua-duanya hulu dari kausalitas anggaran-output yang lemah.
