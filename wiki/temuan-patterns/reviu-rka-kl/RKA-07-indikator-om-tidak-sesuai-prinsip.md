---
id: RKA-07
skill: reviu-rka-kl
kategori: RKA-INDIKATOR
severity: MEDIUM
judul: "Indikator Kinerja RO OM Tidak Sesuai Prinsip OM (Mengukur Peningkatan, Bukan Pemeliharaan)"
kriteria_baku: "PMK 107/2024 Pasal 61 + Pedoman OM (Operation & Maintenance)"
tags: [om, operation-maintenance, indikator, ro, pmk-107]
---

# RKA-07: Indikator Kinerja RO OM Tidak Sesuai Prinsip OM (Mengukur Peningkatan, Bukan Pemeliharaan)

## Pattern Kondisi

RO Operation & Maintenance (OM) — yang seharusnya berorientasi mempertahankan/mengembalikan fungsi — justru memiliki indikator kinerja yang mengukur **peningkatan kapasitas** atau pengembangan teknologi baru. Indikator umum:

- KPI RO OM berbunyi "Peningkatan Kapasitas dan Pengembangan Teknologi/Perangkat..."
- Anggaran OM dialokasikan untuk pengadaan perangkat baru, bukan pemeliharaan
- Tidak ada KPI yang mengukur **uptime/availability/SLA** sistem terkait
- Tidak ada KPI yang mengukur **kapasitas eksisting yang dipertahankan** (mis. trafik 7,3 Tbps)
- Confusion antara RO OM (52xxx) vs RO Pengembangan (53xxx) dalam mata anggaran

## Kriteria

**PMK 107/2024 Pasal 61** + Pedoman OM:
- **Prinsip OM** = mengembalikan/mempertahankan fungsi sistem yang sudah ada (bukan menambah/meningkatkan kapasitas).
- **Indikator OM** seharusnya: uptime, availability, SLA, kapasitas trafik yang dipertahankan, MTTR, jumlah unit yang dioperasikan.
- **Pengembangan baru** seharusnya masuk RO Pengembangan/Pembangunan, bukan OM.

## Akibat

1. **Mata anggaran rancu** — OM (52xxx) dipakai untuk pengembangan (53xxx) yang seharusnya beda akun.
2. **Pelaporan capaian salah arah** — fokus ke "peningkatan" padahal target sebenarnya stabilitas operasional.
3. **Risiko temuan BPK** — penggunaan anggaran tidak sesuai mata anggaran.
4. **Kerancuan strategis** — Direktorat tidak punya gambaran jelas mana yang dipertahankan vs dikembangkan.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| RKA-K/L Matriks RO | Daftar RO OM + indikator |
| TOR RO OM | Definisi pekerjaan + KPI |
| RAB RO OM | Komposisi belanja (52xxx pemeliharaan vs 53xxx modal) |
| Pedoman OM internal | Definisi OM di unit terkait |
| Riwayat capaian TA-1 | Bagaimana KPI OM diukur sebelumnya |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-RKA-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Indikator Kinerja RO OM {nama RO} Tidak Sesuai Prinsip OM (Mengukur Peningkatan, Bukan Pemeliharaan)",
  "kondisi": "RO OM {nama RO} di {satker} TA {YYYY} (anggaran Rp{X.XXX.XXX.XXX}) memiliki KPI: '{Peningkatan Kapasitas/Pengembangan Teknologi...}' — yang merujuk pada peningkatan kapasitas, bukan pemeliharaan fungsi yang sudah ada. KPI ini tidak sesuai prinsip OM yang seharusnya berorientasi mempertahankan/mengembalikan fungsi.",
  "kriteria": "PMK 107/2024 Pasal 61 + Pedoman OM mensyaratkan RO OM memiliki indikator yang berorientasi mempertahankan/mengembalikan fungsi. Indikator standar OM: uptime/availability/SLA, kapasitas trafik yang dipertahankan, MTTR, jumlah unit yang dioperasikan.",
  "akibat": "Mata anggaran OM (52xxx) dipakai untuk pengembangan baru (53xxx) yang seharusnya berbeda akun; pelaporan capaian salah arah; risiko temuan BPK; kerancuan strategis antara pemeliharaan vs pengembangan.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/RKA-KL-{satker}-{YYYY}.pdf", "halaman": "X", "kutipan": "RO {nama OM} KPI: Peningkatan Kapasitas ..."},
    {"file": "03-perencanaan/TOR-{nama-RO}.pdf", "halaman": "Y", "kutipan": "Definisi pekerjaan + KPI"}
  ]
}
```

## Rekomendasi Standar

- Ubah KPI RO OM agar berorientasi **pemeliharaan**: uptime, SLA, kapasitas trafik yang dipertahankan, MTTR.
- Mis. TKPPSE: KPI '1 unit dioperasikan dengan pengukuran kapasitas trafik internet nasional di bawah pengawasan langsung TKPPSE mencapai minimal 7,3 Tbps'.
- Pisahkan kebutuhan pengembangan baru ke RO Pengembangan terpisah dengan mata anggaran modal (53xxx) yang tepat.
- Susun **glossary internal**: "OM = pemeliharaan; Pengembangan = pembangunan baru" untuk menghindari konflasi.

## Contoh Kasus Historis

- **CHR RKA-K/L Wasdig 2026 (B-282/IJ.3/PW.02.04/09/2025)** — RO OM Sistem Pengendalian TKPPSE awalnya memiliki KPI: "Peningkatan Kapasitas dan Pengembangan Teknologi/Perangkat Lembaga (PJT) pada Sistem TKPPSE" + "Operasional/Pemeliharaan diterapkan di Lembaga PJT dengan traffic 7,3 Tbps". Catatan Itjen: **indikator pertama tidak sesuai prinsip OM**. Tindak lanjut sesuai (TOR Rev2): diubah menjadi **"1 unit dioperasikan dengan pengukuran kapasitas trafik internet nasional di bawah pengawasan langsung TKPPSE mencapai minimal 7,3 Tbps"**.

## Catatan

- Pattern ini sering muncul saat ada kebutuhan teknologi baru tapi dikamuflase masuk RO OM untuk kemudahan administratif.
- Solusi: Direktorat susun **roadmap multi-tahun** yang membedakan pemeliharaan dan pengembangan secara eksplisit.
- Lihat juga [[RP-12]] (Kajian tanpa rencana aksi) dan [[pola-temuan-berulang]] poin #4 (Pedoman Internal Usang).
