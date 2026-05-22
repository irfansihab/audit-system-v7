---
id: RP-14
skill: reviu-pengadaan
kategori: PBJ-HPS
severity: MEDIUM
judul: "Perpanjangan Lisensi Dihitung dari Tanggal Awal Kontrak, Bukan dari Masa Berakhir Lisensi"
kriteria_baku: "Perpres 16/2018 Pasal 26 (Penyusunan HPS) + Prinsip kewajaran harga"
tags: [hps, lisensi, perpanjangan, periode-kontrak, kewajaran-harga]
---

# RP-14: Perpanjangan Lisensi Dihitung dari Tanggal Awal Kontrak, Bukan dari Masa Berakhir Lisensi

## Pattern Kondisi

HPS perpanjangan lisensi (mis. lisensi forensik, perangkat lunak berlangganan) menghitung periode dari **tanggal awal kontrak baru** sehingga durasi layanan efektif menjadi lebih pendek dari yang dibayar. Indikator umum:

- Lisensi lama berakhir di bulan tertentu (mis. 28 Agustus 2025) → kontrak perpanjangan baru ditandatangani di bulan lebih awal (mis. Juli 2025)
- HPS dihitung "12 bulan × harga tahunan" dari tanggal kontrak baru
- Akibatnya, ada *overlap* periode antara lisensi lama (masih aktif) dengan lisensi baru → satker membayar 12 bulan tapi menerima hanya 10–11 bulan layanan baru
- Atau sebaliknya: kontrak baru baru ditandatangani setelah lisensi lama berakhir → ada *gap* yang juga tidak diperhitungkan

## Kriteria

**Perpres 16/2018 Pasal 26** — HPS disusun berdasarkan harga pasar yang wajar dan terkait dengan ruang lingkup pekerjaan.

Prinsip kewajaran harga:
1. **Periode efektif layanan** harus dihitung dari masa berakhir lisensi sebelumnya, bukan dari tanggal awal kontrak baru.
2. HPS perpanjangan = harga per bulan × jumlah bulan layanan efektif yang diterima.
3. Bila ada gap/overlap, perlu penyesuaian harga sesuai durasi layanan yang benar-benar diterima.

## Akibat

1. **Pemborosan biaya** — satker membayar lebih dari layanan yang benar-benar diterima.
2. **HPS tidak wajar** — temuan BPK saat reviu eksternal.
3. **Salah praktik administrasi** — terulang setiap kali ada perpanjangan tahunan.
4. **Tidak konsisten dengan prinsip *value for money***.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| HPS perpanjangan | Periode layanan + harga per unit waktu |
| Kontrak/lisensi sebelumnya | Tanggal akhir lisensi yang akan diperpanjang |
| Surat penawaran vendor | Apakah berbasis tanggal mulai layanan atau tanggal kontrak |
| Daftar item perpanjangan | Apakah ada item yang tanggal mulainya berbeda (multiple expirations) |
| Berita Acara serah terima lisensi | Tanggal aktivasi license key |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "HPS Perpanjangan Lisensi {nama lisensi} Dihitung dari Tanggal Kontrak, Bukan Tanggal Berakhir Lisensi",
  "kondisi": "HPS perpanjangan lisensi {nama lisensi} senilai Rp{X.XXX.XXX.XXX} dihitung untuk 12 bulan terhitung dari {tanggal kontrak baru, mis. 1 Juli 2025}. Padahal lisensi sebelumnya baru berakhir {tanggal akhir lisensi, mis. 28 Agustus 2025} sehingga ada *overlap* {X} bulan layanan ganda yang dibayar. Periode layanan efektif perpanjangan seharusnya {periode yang benar, mis. 29 Agustus 2025 – 28 Agustus 2026}.",
  "kriteria": "Perpres 16/2018 Pasal 26 mensyaratkan HPS disusun berdasarkan harga pasar yang wajar dan terkait ruang lingkup pekerjaan. Periode efektif layanan perpanjangan harus dihitung dari masa berakhir lisensi sebelumnya, bukan dari tanggal kontrak baru.",
  "akibat": "Pemborosan biaya senilai (estimasi) Rp{X.XXX.XXX.XXX} karena satker membayar 12 bulan tapi menerima hanya {Y} bulan layanan baru. HPS yang tidak konsisten dengan prinsip *value for money* berisiko menjadi temuan BPK saat reviu eksternal.",
  "dokumen_sumber": [
    {"file": "02-kontrak/HPS-Lisensi-{nama}.pdf", "halaman": "X", "kutipan": "Periode: 12 bulan terhitung dari tanggal kontrak"},
    {"file": "02-kontrak/Lisensi-Lama-{nama}.pdf", "halaman": "Y", "kutipan": "Tanggal berakhir: {tanggal}"}
  ]
}
```

## Rekomendasi Standar

- Susun ulang HPS dengan periode efektif dimulai dari tanggal berakhir lisensi lama.
- Lakukan **penyesuaian harga** sesuai durasi yang dikoreksi sebelum proses pemilihan.
- Untuk daftar lisensi dengan tanggal berakhir berbeda (multiple expirations), buat tabel rinci: lisensi → tanggal akhir lama → tanggal mulai baru → bulan layanan efektif → harga proporsional.
- Pasang *checklist* di KAK perpanjangan lisensi: "Periode efektif = (tanggal akhir lisensi lama + 1 hari) sampai (tanggal akhir + 12 bulan)".

## Contoh Kasus Historis

- **LHR Pengadaan Lisensi Forensik 2025 (B-278/IJ.3/PW.04.04/09/2025)**: Total pengadaan Rp4,73 M untuk 17 item lisensi forensik (Cellebrite UFED, Magnet Axiom, Oxygen Forensic, Magnet Verify). Item lisensi memiliki tanggal expired bervariasi (Jul–Des 2025). Rekomendasi reviu Itjen ke-2: **"Periode perpanjangan dihitung dari masa berakhir lisensi sebelumnya, bukan dari tanggal awal kontrak — perlu penyesuaian harga sesuai durasi layanan yang diterima."**

## Catatan

- Pattern ini sering muncul di lisensi *yearly* yang harus diperpanjang tiap TA.
- Untuk pengadaan dengan banyak item (≥ 10 lisensi), buat **tabel periode efektif per item** sebelum susun HPS.
- Lihat juga [[RP-08]] untuk pattern HPS yang lebih umum (sumber harga).
