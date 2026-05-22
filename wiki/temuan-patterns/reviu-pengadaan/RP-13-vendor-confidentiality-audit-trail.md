---
id: RP-13
skill: reviu-pengadaan
kategori: PBJ-KONTRAK
severity: MEDIUM
judul: "Klausul Confidentiality Vendor Menghambat Audit Trail Teknis"
kriteria_baku: "Perpres 16/2018 Pasal 6 huruf g (akuntabel) + UU 15/2004 tentang Pemeriksaan Pengelolaan Keuangan Negara"
tags: [kontrak, vendor, confidentiality, audit-trail, klausul-kontrak]
---

# RP-13: Klausul Confidentiality Vendor Menghambat Audit Trail Teknis

## Pattern Kondisi

Vendor besar (penyedia telekomunikasi, kolokasi DC, ISP) memiliki klausul *confidentiality* atau arsitektur teknis yang menghalangi pengawasan teknis rutin oleh satker maupun auditor internal. Indikator umum:

- Topologi jaringan vendor terenkripsi sehingga sistem milik satker tidak dapat membaca trafik (mis. TCP Reset tidak berfungsi)
- DC vendor di-sub-leased ke pihak ketiga yang membatasi akses (mis. lokasi disewa oleh perusahaan lain dengan klausul rahasia)
- Klausul kontrak vendor membatasi akses log/metadata tertentu
- SOP vendor menutup mekanisme audit teknis langsung
- Vendor menolak permintaan audit-trail dengan dasar perjanjian rahasia korporat (mis. SUFI confidentiality)

## Kriteria

**Perpres 16/2018 Pasal 6 huruf g** — prinsip pengadaan akuntabel: setiap aspek pelaksanaan kontrak harus dapat dipertanggungjawabkan dan ditelusur.

**UU 15/2004 tentang Pemeriksaan Pengelolaan dan Tanggung Jawab Keuangan Negara** Pasal 9 — BPK berwenang mengakses semua dokumen/data terkait pengelolaan keuangan negara, termasuk yang dipegang pihak ketiga.

Pengujian praktik baik:
1. Kontrak vendor wajib memuat klausul *right to audit* (auditor/Itjen).
2. SLA wajib didukung mekanisme pelaporan teknis yang dapat divalidasi.
3. Bila vendor menggunakan sub-vendor/lokasi sewa, kontrak utama wajib menjamin akses tetap dimungkinkan.

## Akibat

1. **Audit teknis tidak dapat dilakukan** — Itjen/BPK tidak bisa memverifikasi capaian SLA secara independen.
2. **Risiko fungsi sistem gagal** — bila sistem milik satker (TKPPSE) tidak dapat membaca trafik vendor, fungsi pemblokiran gagal di titik tersebut.
3. **Sengketa SLA sulit dibuktikan** — saat ada *outage*, satker hanya pegang laporan vendor tanpa data independen.
4. **Lock-in vendor** — sulit menggantikan vendor karena pengetahuan teknis tertutup.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Kontrak utama dengan vendor | Klausul confidentiality, klausul *right to audit*, klausul SLA |
| Lampiran teknis (architecture diagram) | Apakah topologi terbuka untuk inspeksi |
| Log SLA dan capaian | Apakah disampaikan vendor saja, atau ada cross-check |
| Daftar sub-vendor / DC sewa | Identitas pemilik DC + klausul kontrak vendor-sub-vendor |
| Berita Acara Pemeriksaan Lapangan | Apakah ada akses fisik/teknis yang ditolak |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Kontrak {nama pekerjaan} dengan {vendor} Memiliki Hambatan Audit Trail Teknis akibat Klausul Confidentiality/Topologi Tertutup",
  "kondisi": "Kontrak {nama pekerjaan} (nilai Rp{X.XXX.XXX.XXX}, vendor {vendor}) memiliki hambatan audit trail teknis: (a) {topologi terenkripsi sehingga sistem TKPPSE tidak dapat membaca trafik / lokasi DC di-sub-leased ke {pihak ketiga} dengan klausul rahasia}; (b) Klausul kontrak tidak memuat hak akses log/metadata yang eksplisit untuk Itjen. Akibatnya, capaian SLA hanya dapat divalidasi dari laporan vendor.",
  "kriteria": "Perpres 16/2018 Pasal 6 huruf g mensyaratkan kontrak pengadaan akuntabel; UU 15/2004 Pasal 9 menjamin akses audit untuk pemeriksaan keuangan negara. Klausul confidentiality vendor tidak boleh mengeliminasi hak audit pemerintah.",
  "akibat": "Tanpa hak akses teknis yang eksplisit, Itjen/BPK tidak dapat memverifikasi capaian SLA secara independen. Pemfungsian sistem milik satker (mis. TKPPSE) berisiko gagal di titik vendor, dan sengketa SLA sulit dibuktikan.",
  "dokumen_sumber": [
    {"file": "02-kontrak/Kontrak-{vendor}.pdf", "halaman": "X", "kutipan": "Klausul confidentiality: ..."},
    {"file": "02-kontrak/Architecture-{vendor}.pdf", "halaman": "Y", "kutipan": "Topologi terenkripsi"}
  ]
}
```

## Rekomendasi Standar

- Tambahkan klausul *right to audit* eksplisit di kontrak vendor — auditor/Itjen berhak akses log/metadata tertentu untuk verifikasi SLA.
- Untuk vendor dengan klausul tertutup, lakukan **Cost-Benefit Analysis** (CBA): vendor besar dengan lock-in vs vendor alternatif dengan transparansi lebih baik.
- Susun **playbook akses lokasi DC sub-leased** — koordinasi dengan pemilik DC + pemberitahuan resmi.
- Bila tidak ada opsi vendor lain, terapkan **kompensasi audit**: laporan teknis berkala dari vendor + audit pihak ketiga independen.

## Contoh Kasus Historis

- **LHP Pengadaan Redesain TKPPSE 2026 (B-34/IJ.3/PW.04.03/01/2026)**:
  - **PT Moratel**: Perubahan topologi jaringan terenkripsi — perangkat TKPPSE tidak dapat membaca trafik. Usulan pindah ke BDx masih dikaji legalitas + SOP.
  - **PT Lintasarta + iForte**: Lokasi DC berkontrak dengan PT SUFI dengan batasan *confidentiality* yang membatasi akses data.

## Catatan

- Pattern ini sering muncul di pengadaan layanan infrastruktur kritikal (telekomunikasi, DC, ISP) dengan vendor besar.
- Severity dapat naik ke HIGH bila vendor terkait paket Prioritas Nasional.
- Rekomendasi harus realistis — vendor besar punya posisi tawar tinggi, jadi fokus pada *additive safeguards* (klausul tambahan, audit pihak ketiga) bukan pemaksaan akses.
- Lihat juga [[pola-temuan-berulang]] poin #9.
