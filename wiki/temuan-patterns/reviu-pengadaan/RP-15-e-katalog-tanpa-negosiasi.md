---
id: RP-15
skill: reviu-pengadaan
kategori: PBJ-PEMILIHAN
severity: MEDIUM
judul: "Pemilihan via E-Katalog/E-Purchasing Tanpa Negosiasi atau Mini Kompetisi"
kriteria_baku: "Peraturan LKPP 9/2021 + Peraturan LKPP 4/2024 tentang Pengadaan Barang/Jasa Melalui Penyedia"
tags: [e-katalog, e-purchasing, negosiasi, mini-kompetisi, lkpp]
---

# RP-15: Pemilihan via E-Katalog/E-Purchasing Tanpa Negosiasi atau Mini Kompetisi

## Pattern Kondisi

Pengadaan dilakukan melalui E-Katalog atau E-Purchasing dengan satu atau lebih penyedia, namun tidak ada bukti dilakukan negosiasi (untuk 1 penyedia) atau mini kompetisi (untuk > 1 penyedia). Indikator umum:

- Berita Acara Pemilihan hanya memuat satu penyedia + harga tunggal tanpa catatan negosiasi
- Untuk paket dengan beberapa penyedia tersedia di e-katalog: PPK langsung pilih satu vendor tanpa undangan mini kompetisi
- Tidak ditemukan dokumen pernyataan negosiasi harga (BA Negosiasi) atau undangan mini kompetisi (Surat Undangan + Tabulasi Penawaran)
- Lisensi/produk reseller asing: PPK tidak melakukan benchmark dengan principal/agen lain
- Efisiensi yang dilaporkan = 0% atau nominal kecil (mis. < 2%) yang menyiratkan tidak ada negosiasi serius

## Kriteria

**Peraturan LKPP 9/2021** tentang Toko Daring dan Katalog Elektronik, **Peraturan LKPP 4/2024** tentang Pengadaan Barang/Jasa Melalui Penyedia:
- Bila tersedia **1 penyedia** di e-katalog → wajib dilakukan **negosiasi harga**.
- Bila tersedia **> 1 penyedia** di e-katalog → wajib dilakukan **mini kompetisi** atau prosedur kompetitif setara.

Pengujian dasar:
1. Berita Acara Negosiasi tersedia dan ditandatangani PPK + vendor.
2. Bila mini kompetisi: undangan kepada minimum 2 vendor + tabulasi penawaran + simpulan pemilihan.
3. Efisiensi negosiasi terdokumentasi (selisih harga awal vs harga sepakat).

## Akibat

1. **Harga tidak optimal** — peluang efisiensi anggaran hilang.
2. **Pelanggaran formal Peraturan LKPP** — temuan administratif yang berulang.
3. **Risiko sengketa** — vendor lain yang merasa dirugikan dapat mengajukan keberatan.
4. **Tidak konsisten dengan prinsip kompetisi yang sehat** dalam Perpres 16/2018.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Berita Acara Pemilihan/Pemenang | Daftar penyedia yang tersedia di e-katalog + pemenang |
| BA Negosiasi (jika 1 penyedia) | Harga awal + harga negosiasi + tanda tangan |
| Surat Undangan Mini Kompetisi (jika > 1) | Daftar vendor yang diundang + tabulasi penawaran |
| Screenshot e-katalog | Jumlah penyedia yang tersedia untuk komoditas tersebut |
| Riwayat email/disposisi | Komunikasi PPK ↔ vendor terkait negosiasi |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Pengadaan {nama pekerjaan} via E-Katalog Tidak Disertai Berita Acara Negosiasi/Mini Kompetisi",
  "kondisi": "Pengadaan {nama pekerjaan} senilai Rp{X.XXX.XXX.XXX} dilakukan melalui E-Katalog/E-Purchasing dengan penyedia {vendor}. Pada saat pemilihan, di e-katalog tersedia {jumlah} penyedia untuk komoditas serupa. Namun PPK {tidak melakukan negosiasi harga / tidak menyelenggarakan mini kompetisi} dan langsung memilih satu penyedia. Tidak ditemukan {BA Negosiasi / Surat Undangan Mini Kompetisi + Tabulasi Penawaran} di file pengadaan.",
  "kriteria": "Peraturan LKPP 9/2021 + Peraturan LKPP 4/2024 mengatur: bila tersedia 1 penyedia → wajib negosiasi harga; bila > 1 penyedia → wajib mini kompetisi.",
  "akibat": "Peluang efisiensi anggaran hilang; berisiko temuan administratif berulang serta sengketa dari vendor lain yang merasa tidak diberi kesempatan kompetisi.",
  "dokumen_sumber": [
    {"file": "02-kontrak/BA-Pemilihan-{nama}.pdf", "halaman": "X", "kutipan": "Pemenang: {vendor}; harga: Rp{X}"},
    {"file": "01-rup-sirup/Screenshot-Ekatalog.png", "halaman": 1, "kutipan": "{jumlah} penyedia tersedia"}
  ]
}
```

## Rekomendasi Standar

- Lakukan **negosiasi harga ulang** atau **mini kompetisi terbatas** sebelum SPK ditandatangani (kalau masih memungkinkan).
- Susun checklist e-katalog/e-purchasing untuk PPK:
  1. Cek jumlah penyedia di e-katalog
  2. Bila 1 → wajib BA Negosiasi
  3. Bila > 1 → undang minimum 2 vendor, dokumentasikan tabulasi
- Pasang **gate audit internal** sebelum SPPBJ: file pengadaan wajib lampirkan BA Negosiasi atau BA Mini Kompetisi.

## Contoh Kasus Historis

- **LHR Pengadaan Lisensi Forensik 2025 (B-278/IJ.3/PW.04.04/09/2025)**: Pengadaan via reseller resmi untuk 17 item lisensi forensik. Rekomendasi reviu Itjen ke-1: **"Karena tidak didapatkan harga principal dari agen resmi → pemilihan via e-katalog perlu negosiasi jika hanya 1 penyedia, atau mini kompetisi jika lebih dari 1 penyedia."**

## Catatan

- Untuk paket dengan principal asing (lisensi software, alat lab), umumnya hanya tersedia 1–2 reseller resmi di Indonesia — negosiasi wajib tetap dilakukan.
- Bila benar-benar hanya 1 penyedia di e-katalog dan tidak ada principal alternatif, terapkan **benchmark harga internasional** sebagai dasar negosiasi.
- Severity dapat naik ke HIGH bila nilai paket ≥ Rp10 M dan tidak ada bukti negosiasi sama sekali.
