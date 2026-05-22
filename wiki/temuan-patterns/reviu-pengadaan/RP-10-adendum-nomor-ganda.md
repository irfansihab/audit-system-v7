---
id: RP-10
skill: reviu-pengadaan
kategori: PBJ-KONTRAK
severity: HIGH
judul: "Adendum Bernomor Sama dengan Isi Berbeda (Pelanggaran Prinsip Akuntabel)"
kriteria_baku: "Perpres 16/2018 jo. Perpres 12/2021 Pasal 6 huruf g"
tags: [adendum, kontrak, akuntabilitas, perpres-16]
---

# RP-10: Adendum Bernomor Sama dengan Isi Berbeda (Pelanggaran Prinsip Akuntabel)

## Pattern Kondisi

Ditemukan dua atau lebih adendum kontrak yang menggunakan **nomor yang sama** (mis. AD01) namun memuat isi (klausul, durasi, nilai) yang berbeda. Indikator umum:

- Dua versi adendum AD01 dengan tanggal berbeda; isi tentang perpanjangan waktu yang tidak konsisten (mis. 50 hari vs 90 hari)
- Salah satu adendum tidak melalui paraf/tandatangan resmi pejabat berwenang
- Dokumen kontrak terlampir di KKP/LHR menampilkan adendum yang sudah diperbarui tanpa pembatalan adendum lama
- Sistem nomenklatur adendum tidak terpusat — masing-masing PPK menerbitkan nomor sendiri

## Kriteria

**Perpres 16/2018 jo. Perpres 12/2021 Pasal 6 huruf g** — prinsip pengadaan yang **akuntabel**: setiap dokumen pengadaan harus dapat dipertanggungjawabkan dan ditelusur jejaknya.

Pengujian dasar:
1. **Konsistensi nomor adendum** — setiap nomor unik untuk satu perubahan kontrak.
2. **Pembatalan eksplisit** — bila ada perubahan, adendum lama wajib dibatalkan secara resmi sebelum adendum baru diterbitkan.
3. **Audit trail** — semua adendum tercatat dalam log dokumen kontrak terpusat.

## Akibat

1. **Ambiguitas hukum** — saat sengketa, tidak jelas mana adendum yang berlaku.
2. **Pelanggaran prinsip akuntabel Perpres 16/2018** — temuan formal akan muncul di reviu BPK/BPKP.
3. **Risiko penyalahgunaan** — adendum ganda dapat dimanfaatkan untuk memodifikasi durasi/nilai sepihak.
4. **Audit trail rusak** — sulit melakukan rekonstruksi sejarah perubahan kontrak.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Kontrak utama | Daftar adendum yang dirujuk + nomor adendum |
| Setiap file adendum | Nomor + tanggal + isi perubahan + tanda tangan |
| Log dokumen kontrak (jika ada) | Apakah ada catatan pembatalan adendum |
| Berita Acara/SPK terkait perubahan kontrak | Apakah memuat referensi yang konsisten ke nomor adendum |
| Email/disposisi internal | Sequence persetujuan adendum |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Kontrak {nama pekerjaan} Memiliki 2 Adendum Bernomor Sama (AD{nn}) dengan Isi Berbeda",
  "kondisi": "Ditemukan 2 adendum dengan nomor sama AD{nn} pada kontrak {nama pekerjaan} (nilai Rp{X.XXX.XXX.XXX}, vendor {vendor}): (1) Adendum AD{nn} tanggal {tanggal-1} berisi perpanjangan waktu {X1} hari; (2) Adendum AD{nn} tanggal {tanggal-2} berisi perpanjangan waktu {X2} hari. Tidak ditemukan dokumen pembatalan resmi atas salah satu adendum sehingga keduanya beredar bersamaan di lampiran kontrak.",
  "kriteria": "Perpres 16/2018 jo. Perpres 12/2021 Pasal 6 huruf g mensyaratkan setiap dokumen pengadaan akuntabel dan dapat dipertanggungjawabkan. Adendum bernomor sama dengan isi berbeda melanggar prinsip akuntabel karena menciptakan ambiguitas dokumen.",
  "akibat": "Tanpa pembatalan resmi, kedua adendum berpotensi dianggap sah dan menimbulkan sengketa interpretasi durasi/nilai kontrak. Audit trail kontrak menjadi rusak dan sulit direkonstruksi.",
  "dokumen_sumber": [
    {"file": "02-kontrak/Adendum-AD{nn}-v1.pdf", "halaman": 1, "kutipan": "Perpanjangan waktu {X1} hari, tanggal {tanggal-1}"},
    {"file": "02-kontrak/Adendum-AD{nn}-v2.pdf", "halaman": 1, "kutipan": "Perpanjangan waktu {X2} hari, tanggal {tanggal-2}"}
  ]
}
```

## Rekomendasi Standar

- Batalkan secara resmi salah satu adendum yang tidak berlaku — terbitkan Berita Acara Pembatalan oleh PPK + paraf KPA.
- Susun sistem nomenklatur adendum terpusat di tingkat satker/Ditjen (mis. log spreadsheet sequential).
- Sebelum BAST, lakukan rekonsiliasi dokumen kontrak — pastikan semua adendum yang dirujuk konsisten antara kontrak utama, log internal, dan dokumen pencairan.

## Contoh Kasus Historis

- **LHR Server Crawling CSE 2025 (B-41/IJ.3/PW.04.04/02/2026)**: Pengadaan peremajaan server crawling konten negatif Rp40,11M dengan PT Persada Artha Selaras. Ditemukan 2 adendum AD01 dengan perpanjangan waktu 50 hari dan 90 hari — keduanya beredar tanpa pembatalan resmi. Rekomendasi: batalkan satu adendum secara formal.

## Catatan

- Adendum ganda umumnya **bukan** indikasi fraud — lebih sering disebabkan administrasi PPK yang buru-buru.
- Tetap masuk temuan HIGH karena pelanggaran prinsip akuntabel adalah temuan formal yang akan diangkat BPK.
- Lihat juga [[pola-temuan-berulang]] poin #8 (Anomali Administrasi Kontrak).
