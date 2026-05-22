---
id: RP-12
skill: reviu-pengadaan
kategori: PBJ-PERENCANAAN
severity: MEDIUM
judul: "Hasil Kajian Teknis Belum Diturunkan ke Rencana Aksi dengan Milestone"
kriteria_baku: "Perpres 16/2018 Pasal 18 (Perencanaan Pengadaan)"
tags: [kajian, redesain, perencanaan, milestone]
---

# RP-12: Hasil Kajian Teknis Belum Diturunkan ke Rencana Aksi dengan Milestone

## Pattern Kondisi

Satker memiliki dokumen kajian teknis (kajian arsitektur, redesain, *technology refresh*) namun tidak menerjemahkannya menjadi rencana aksi yang spesifik dengan milestone, sehingga eksekusi tertunda hingga TA berikutnya. Indikator umum:

- Dokumen kajian ada (kadang sudah memenuhi kualitas akademis) tetapi tidak ada matriks "kajian → kegiatan pengadaan TA X"
- Rekomendasi kajian masih berbentuk *narrative recommendation* tanpa target tanggal
- Anggaran TA berjalan tidak memuat RO untuk implementasi kajian
- Roadmap multi-tahun belum disusun atau berhenti di slide presentasi
- Tim PJP/operasional belum di-handover rincian temuan kajian

## Kriteria

**Perpres 16/2018 Pasal 18** mengatur perencanaan pengadaan harus didasarkan pada:
1. Identifikasi kebutuhan terukur,
2. Penetapan barang/jasa,
3. Penyusunan spesifikasi teknis & KAK yang konkret,
4. Penyusunan jadwal pelaksanaan.

Kajian teknis yang tidak terhubung ke rencana aksi gagal memenuhi prinsip ini.

## Akibat

1. **Eksekusi tertunda 1–2 TA** — kajian "menggantung" hingga kebutuhan jadi mendesak di TW IV.
2. **Pemborosan biaya kajian** — investasi kajian sudah keluar tapi tidak menghasilkan implementasi.
3. **Risiko obsolesensi** — teknologi yang dikaji sudah tertinggal saat akhirnya diimplementasi.
4. **Sulit di-monitor** — tanpa milestone, Itjen/manajemen tidak dapat mengukur progres.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Dokumen kajian teknis | Tanggal selesai + rekomendasi spesifik |
| Roadmap multi-tahun (jika ada) | Konsistensi dengan rekomendasi kajian |
| RKA-K/L TA berjalan | Apakah ada RO/komponen turunan kajian |
| RUP TA berjalan | Apakah ada paket pengadaan implementasi |
| Berita Acara internal | Status follow-up kajian |
| Roadmap Renstra | Apakah kajian masuk milestone Renstra |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Kajian Teknis {nama kajian} di {satker} Belum Diturunkan ke Rencana Aksi dengan Milestone TA {YYYY}",
  "kondisi": "{satker} telah menyelesaikan kajian teknis '{nama kajian}' (selesai {tanggal kajian}) yang merekomendasikan {ringkasan rekomendasi}. Namun pada RKA-K/L TA {YYYY} dan RUP {YYYY}, tidak ditemukan RO/komponen/paket pengadaan untuk mengimplementasikan rekomendasi tersebut. Pelaksana menyampaikan rencana implementasi pada TA {YYYY+1} atau TA {YYYY+2} tanpa milestone tertulis.",
  "kriteria": "Perpres 16/2018 Pasal 18 mensyaratkan perencanaan pengadaan didasarkan pada identifikasi kebutuhan, spesifikasi, dan jadwal pelaksanaan yang terukur. Kajian teknis tanpa rencana aksi tidak memenuhi prinsip perencanaan yang konkret.",
  "akibat": "Eksekusi rekomendasi kajian tertunda 1–2 TA, berisiko teknologi yang dikaji menjadi obsolet saat akhirnya diimplementasi, dan biaya kajian terbuang tanpa output operasional.",
  "dokumen_sumber": [
    {"file": "03-perencanaan/Kajian-{nama}.pdf", "halaman": 1, "kutipan": "Tanggal selesai: {tanggal}"},
    {"file": "03-perencanaan/RKA-KL-{satker}-{YYYY}.pdf", "halaman": "X", "kutipan": "(tidak ditemukan RO terkait implementasi kajian)"}
  ]
}
```

## Rekomendasi Standar

- Susun **matriks rencana aksi** dari kajian: per rekomendasi → kegiatan pengadaan/non-pengadaan → PJP → milestone (mis. per triwulan) → target output.
- Pasang **gate review** per triwulan untuk monitor progres milestone.
- Kalau anggaran tidak cukup TA berjalan, susun **multi-year roadmap** sampai akhir Renstra dengan urutan prioritas.
- Letakkan kajian dalam **lingkup KAK** RKA-K/L TA berikutnya (lihat juga [[RKA-04]] — TOR belum jelaskan metode pengadaan).

## Contoh Kasus Historis

- **LHP Pengadaan Redesain TKPPSE 2026 (B-34/IJ.3/PW.04.03/01/2026)**: Kajian redesain teknis TKPPSE (proyeksi pertumbuhan trafik, dampak merger operator menjadi IOH/XLSmart/Telkomsel, peninjauan lokasi DC pasca merger) sudah selesai. Namun rencana implementasi: kajian komprehensif TW II 2026 → eksekusi TA 2027. Tidak ada milestone konkret untuk dismantle/relokasi perangkat di TA 2026.

## Catatan

- Bedakan kajian *strategic* (Renstra-level, 5 tahunan) vs *operational* (TA-level): pattern ini fokus operational.
- Bila kajian *strategic*, rekomendasi lebih ke "masukkan ke Renstra periode berikutnya" bukan "implementasikan TA berjalan".
- Severity dapat naik ke HIGH bila kajian terkait risiko HIGH di [[peta-risiko-wasdig-2026]] / [[peta-risiko-ekosistem-digital-2026]].
- Lihat juga [[pola-temuan-berulang]] poin #3.
