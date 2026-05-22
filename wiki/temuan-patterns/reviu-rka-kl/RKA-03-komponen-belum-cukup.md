---
id: RKA-03
skill: reviu-rka-kl
kategori: RKA-KOMPONEN
severity: HIGH
judul: "Komponen/Sub-Komponen Belum Cukup Mendukung Ketercapaian RO"
kriteria_baku: "PMK 107/2024 Pasal 61 + Lampiran tentang Struktur RKA-K/L"
tags: [komponen, sub-komponen, ro, ketercapaian-output, pmk-107]
---

# RKA-03: Komponen/Sub-Komponen Belum Cukup Mendukung Ketercapaian RO

## Pattern Kondisi

Komponen atau sub-komponen yang dialokasikan untuk satu Rincian Output (RO) tidak cukup secara substansi untuk menjamin ketercapaian output tersebut. Indikator umum:

- Daftar komponen di RO hanya menyebut aktivitas administratif (rapat, perjalanan dinas) tanpa kegiatan substantif
- Komponen utama yang biasanya wajib hadir (mis. pengadaan barang, pelatihan, pengembangan sistem) tidak ditemukan
- Sub-komponen tidak menjelaskan **deliverable** masing-masing — hanya berupa nama aktivitas
- Bila dijumlahkan, output dari semua komponen tidak ekuivalen dengan output RO (mis. 5 sub-komponen rapat → tidak menghasilkan 150 startup terakselerasi)
- TOR memuat daftar komponen tapi tidak narasi "bagaimana komponen ini menghasilkan output X"

## Kriteria

**PMK 107/2024 Pasal 61** + Lampiran Struktur RKA-K/L:
- Setiap RO didukung oleh **komponen** yang merupakan aktivitas spesifik untuk mewujudkan output.
- Setiap komponen didukung oleh **sub-komponen** yang lebih rinci (mis. tahap-tahap kegiatan).
- Komponen + sub-komponen harus **cukup** secara substansi untuk menjamin output.

Pengujian kecukupan:
1. **Mapping komponen → output**: setiap komponen jelas menghasilkan apa.
2. **Mapping sub-komponen → komponen**: setiap sub-komponen jelas mendukung komponen mana.
3. **Tes "subtraction"**: bila komponen X dihapus, apakah output tetap dapat tercapai? Bila ya = komponen tidak esensial; bila tidak = komponen esensial.

## Akibat

1. **Eksekusi tidak optimal** — pelaksana mengeksekusi komponen yang ada, tetapi output tidak tercapai karena ada gap aktivitas.
2. **Pelaporan capaian terdistorsi** — capaian per komponen tinggi (rapat 100% terlaksana), tetapi RO sebenarnya tidak tercapai.
3. **Risiko temuan AKIP PAN-RB** — perencanaan kausalitas anggaran-output tidak terbukti.
4. **Penelaahan DJA/Bappenas berisiko dikembalikan**.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| RKA-K/L Matriks RO–Komponen–Sub-Komponen | Daftar lengkap struktur |
| TOR per komponen | Deliverable + cara berkontribusi ke output RO |
| RAB | Komposisi anggaran per komponen — apakah ada yang anomali |
| Renja sebelumnya | Bagaimana RO serupa dipecah komponennya |
| Pedoman internal direktorat | SOP per jenis kegiatan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-RKA-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Komponen/Sub-Komponen RO {nama RO} Belum Cukup Mendukung Ketercapaian Output",
  "kondisi": "RO {nama RO} dengan target output '{X} {satuan}' didukung oleh {N} komponen: {list komponen}. Pemeriksaan menemukan: (a) Komponen substantif yang biasanya wajib hadir untuk output sejenis (mis. {jenis kegiatan utama}) tidak ditemukan; (b) {N-K} dari {N} komponen hanya berupa aktivitas administratif (rapat, perjalanan dinas) tanpa narasi deliverable; (c) Sub-komponen di komponen {nama komponen} hanya menyebut nama aktivitas tanpa deliverable atau target. Bila seluruh komponen dieksekusi 100%, agregasi output tidak ekuivalen dengan output RO.",
  "kriteria": "PMK 107/2024 Pasal 61 + Lampiran Struktur RKA-K/L mensyaratkan komponen + sub-komponen cukup secara substansi untuk menjamin ketercapaian RO. Setiap komponen wajib memiliki deliverable yang jelas berkontribusi ke output.",
  "akibat": "Eksekusi anggaran berisiko menghasilkan capaian komponen tinggi tapi RO tidak tercapai; pelaporan capaian akan terdistorsi; perencanaan kausalitas anggaran-output tidak terbukti, berdampak ke penilaian AKIP.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/RKA-KL-{satker}-{YYYY}.pdf", "halaman": "X", "kutipan": "RO {nama}: Komponen 1 = ..., Komponen 2 = ..."},
    {"file": "03-perencanaan/TOR-{nama-RO}.pdf", "halaman": "Y", "kutipan": "Komponen administratif tanpa deliverable substantif"}
  ]
}
```

## Rekomendasi Standar

- Narasikan **deliverable/output setiap komponen** secara eksplisit di TOR.
- Pasang **mapping komponen → output RO** dalam bentuk tabel: komponen → kontribusi spesifik → bukti ketercapaian.
- Tambahkan komponen substantif yang hilang (mis. pengadaan, pelatihan, pengembangan sistem) bila relevan.
- Pasang **tes substraction** sebagai gate review internal: bila komponen dihapus, output gagal tercapai = komponen esensial.

## Contoh Kasus Historis

- **CHR Renja Ekdig 2026 (B-247/IJ.3/PW.02.04/08/2025)** — Catatan substantif #2: **"Komponen belum cukup dalam mendukung ketercapaian output"**, dan Catatan #3: **"Sub-Komponen belum cukup dalam mendukung ketercapaian komponen"**. Rekomendasi: narasikan deliverable/output dari setiap komponen dan sub-komponen untuk menilai kecukupan.

## Catatan

- Pattern ini sering muncul bersamaan dengan [[RKA-02]] (RO tanpa parameter keberhasilan) — sama-sama mengindikasikan kausalitas anggaran-output belum matang.
- Lihat juga [[RKA-04]] (TOR belum jelaskan metode pengadaan & spek teknis).
- Untuk RO dengan banyak komponen administratif (rapat, koordinasi), nilai dengan hati-hati — kadang komponen administratif memang substantif (mis. forum lintas K/L untuk regulasi).
