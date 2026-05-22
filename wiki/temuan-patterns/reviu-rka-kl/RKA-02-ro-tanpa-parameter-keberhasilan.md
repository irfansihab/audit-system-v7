---
id: RKA-02
skill: reviu-rka-kl
kategori: RKA-OUTPUT
severity: HIGH
judul: "RO Tidak Didukung Parameter Keberhasilan Terukur"
kriteria_baku: "PMK 107/2024 tentang Petunjuk Penyusunan dan Penelaahan RKA-K/L Pasal 61 + Pedoman Renja Bappenas"
tags: [ro, rincian-output, parameter-keberhasilan, indikator-smart, pmk-107]
---

# RKA-02: RO Tidak Didukung Parameter Keberhasilan Terukur

## Pattern Kondisi

Rincian Output (RO) di RKA-K/L dinyatakan dengan jumlah (mis. "150 Startup", "1 Layanan", "1 Unit") tetapi tidak memiliki **parameter keberhasilan** yang terukur untuk memastikan output benar-benar tercapai sesuai mutu yang diharapkan. Indikator umum:

- RO hanya berupa angka + satuan, tanpa definisi "tercapai bila ...?"
- Indikator yang ada justru mengukur **proses/aktivitas**, bukan **output** (mis. "jumlah startup difasilitasi")
- Parameter yang diberikan adalah parameter **indikator**, bukan parameter **output** (level salah)
- TOR hanya menjelaskan strategi + dampak jika tidak berjalan, tetapi tidak parameter pengukuran tercapainya output
- Definisi istilah kunci di nama RO tidak ada (mis. "terakselerasi", "tertangani", "terlayani") — tidak ada di TOR maupun glossary internal

## Kriteria

**PMK 107/2024 Pasal 61** + Pedoman Renja Bappenas mensyaratkan setiap RO memiliki:
1. **Definisi output** yang jelas (apa yang dianggap "tercapai")
2. **Parameter keberhasilan** terukur (angka, persentase, kualitas, periode)
3. **Indikator kinerja** SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
4. **Sumber verifikasi** (cara mengukur, dokumen pendukung)

## Akibat

1. **Sulit dilakukan evaluasi capaian** — tanpa parameter, tidak ada baseline untuk menilai "sudah tercapai atau belum".
2. **Penelaahan DJA/Bappenas berisiko dikembalikan** — RKA-K/L tidak memenuhi prinsip *evidence-based budgeting*.
3. **Risiko klaim capaian palsu** — bila tidak ada definisi tercapai, pelaksana dapat mengklaim capaian dengan dasar yang lemah.
4. **Selaras dengan rekomendasi AKIP PAN-RB** — indikator SMART adalah salah satu kriteria penilaian AKIP yang turun bila kualitas perencanaan rendah.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| RKA-K/L (Matriks RO) | Daftar RO + indikator output + parameter |
| TOR per RO | Definisi output + cara pengukuran + sumber verifikasi |
| Pedoman/Glossary Direktorat | Definisi istilah kunci di RO |
| Renja Bappenas | Konsistensi RO dengan IKU/IKSP unit |
| LKj TA-1 | Bagaimana RO yang serupa diukur capaiannya |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-RKA-XX",
  "assigned_to": "{nama anggota}",
  "judul": "RO {nama RO} Tidak Didukung Parameter Keberhasilan Terukur",
  "kondisi": "RO {nama RO} pada {satker} TA {YYYY} ditetapkan dengan output '{X} {satuan}' (mis. 150 Startup, 1 Layanan, 1 Unit). Pemeriksaan TOR menemukan: (a) Tidak ada definisi/parameter '{istilah kunci}' (mis. 'terakselerasi', 'beroperasi') yang menjadi syarat tercapainya output; (b) Indikator yang dilampirkan adalah parameter untuk mengukur indikator kegiatan (mis. revenue, traction, pendanaan), bukan parameter ketercapaian output; (c) Sumber verifikasi tidak disebutkan. Konfirmasi dengan {direktorat pelaksana} menegaskan parameter tersebut bukan parameter output.",
  "kriteria": "PMK 107/2024 Pasal 61 + Pedoman Renja Bappenas mensyaratkan setiap RO memiliki definisi output yang jelas, parameter keberhasilan terukur, dan sumber verifikasi.",
  "akibat": "Capaian RO sulit dievaluasi karena tidak ada baseline pengukuran; RKA-K/L berisiko dikembalikan saat penelaahan DJA/Bappenas; capaian dapat diklaim dengan dasar yang lemah.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/RKA-KL-{satker}-{YYYY}.pdf", "halaman": "X", "kutipan": "RO {nama RO}: 150 Startup"},
    {"file": "03-perencanaan/TOR-{nama-RO}.pdf", "halaman": "Y", "kutipan": "Indikator: ..."}
  ]
}
```

## Rekomendasi Standar

- Narasikan **parameter keberhasilan output** secara eksplisit di TOR — bedakan dari parameter indikator kegiatan.
- Susun **definisi istilah kunci** di TOR atau referensi ke glossary direktorat (mis. "Terakselerasi: startup yang lolos seleksi + telah menerima pendanaan minimum Rp X dalam periode TA").
- Pasang **sumber verifikasi** untuk setiap parameter (sertifikat, BA, laporan pihak ketiga).
- Konsisten dengan rekomendasi AKIP: indikator SMART di setiap RO.

## Contoh Kasus Historis

- **CHR Renja Ekdig 2026 (B-247/IJ.3/PW.02.04/08/2025)** — Pagu TA 2026 Rp597,64M dengan 6 catatan substantif, salah satunya: **RO "Startup Digital Terakselerasi" (output 150 Startup) tidak memiliki definisi/parameter "Terakselerasi"**. Direktorat Pengembangan Ekosistem Digital menjelaskan parameter (revenue, traction, pendanaan) adalah **parameter untuk mengukur indikator**, bukan parameter output. Contoh kedua: **RO "Layanan Publik Bidang Penyiaran" (output 1 Layanan)** — TOR hanya menjelaskan strategi dan dampak jika program tidak berjalan, **tidak ada parameter atau indikator untuk mengukur tercapainya '1 Layanan'**.

## Catatan

- Pattern ini sering muncul di Direktorat dengan output berbasis layanan atau program akselerasi.
- Pertanyaan kunci agen: "Bagaimana cara mengetahui bahwa RO ini SUDAH tercapai? Apa indikatornya?"
- Lihat juga [[RKA-03]] (Komponen belum cukup) dan [[RKA-04]] (TOR belum jelaskan metode).
- Lihat juga [[pola-temuan-berulang]] poin #6 (Data Kinerja Tidak Dapat Diverifikasi Sumbernya).
