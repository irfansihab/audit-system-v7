---
id: RP-11
skill: reviu-pengadaan
kategori: PBJ-SIRUP
severity: HIGH
judul: "Pagu SIRUP Status Draft > 50% Setelah Akhir Triwulan I"
kriteria_baku: "Perpres 16/2018 Pasal 22 + Peraturan LKPP tentang RUP"
tags: [sirup, rup, perencanaan-pengadaan, draft, perpres-16]
---

# RP-11: Pagu SIRUP Status Draft > 50% Setelah Akhir Triwulan I

## Pattern Kondisi

Persentase pagu pengadaan satker masih berstatus *draft* (belum diumumkan) di SIRUP melampaui ambang risiko (mis. > 50%) menjelang akhir TW I — indikator perencanaan pengadaan belum matang. Indikator umum:

- Total pagu di SIRUP per akhir Januari/Februari masih > 50% draft
- Paket-paket Prioritas Nasional (PN) belum diumumkan
- Paket besar (≥ Rp10 M) tertahan di draft
- Swakelola 100% masih draft (mengisyaratkan unit teknis belum menyusun KAK)
- Riwayat paket draft memuat isu PJP/SLA dari TA sebelumnya yang belum tuntas

## Kriteria

**Perpres 16/2018 Pasal 22** — RUP wajib diumumkan paling lambat 31 Maret TA berjalan untuk paket yang anggarannya berasal dari APBN.

Peraturan LKPP terkait penayangan SIRUP:
- Paket yang sudah memiliki pagu wajib diumumkan setelah DIPA disahkan.
- Status draft yang bertahan > TW I mencerminkan ketidaksiapan rencana pengadaan.

## Akibat

1. **Pelanggaran timeline pengumuman RUP** — Perpres 16/2018 Pasal 22 mensyaratkan paling lambat 31 Maret.
2. **Risiko eksekusi mundur ke TW III/IV** — paket besar yang baru diumumkan TW II umumnya selesai di TW IV (*crunch time*), menimbulkan risiko kualitas + sengketa kontrak.
3. **Daya serap anggaran rendah** — realisasi TW I–TW II tertahan, target serapan akhir TA gagal.
4. **Risiko paket Prioritas Nasional gagal** — PN biasanya target serapan ≥ 90%; draft yang bertahan = risiko paket dipotong saat revisi DIPA.

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Export SIRUP per akhir Januari/Februari/Maret | Daftar paket + status (draft/terumumkan) + nilai pagu |
| DIPA satker | Tanggal terbit + nilai per program/RO |
| Daftar Prioritas Nasional Kemkomdigi TA berjalan | Mapping paket PN dengan kode RUP |
| Riwayat paket pengadaan TA sebelumnya | Apakah ada isu yang belum tuntas (SLA, sengketa, kontrak tanpa kontrak) |
| Berita Acara rapat satker | Pembahasan paket pengadaan yang berisiko terlambat |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-XX",
  "assigned_to": "{nama anggota}",
  "judul": "Pagu Pengadaan {satker} TA {YYYY} Masih {X}% Berstatus Draft di SIRUP per {tanggal}",
  "kondisi": "Per {tanggal monitoring}, total pagu pengadaan {satker} di SIRUP senilai Rp{X.XXX.XXX.XXX} (100%) — dengan rincian: (a) Final/terumumkan Rp{X.XXX.XXX.XXX} ({Y}%); (b) Draft Rp{X.XXX.XXX.XXX} ({Z}%). Dari paket draft tersebut, {N} paket bernilai > Rp{Y M} merupakan Prioritas Nasional dengan riwayat isu pengadaan {sebutkan: SLA gagal / tagihan tanpa kontrak / sengketa vendor}. Swakelola {100/X}% masih berstatus draft.",
  "kriteria": "Perpres 16/2018 Pasal 22 mensyaratkan RUP diumumkan paling lambat 31 Maret TA berjalan. Status draft > 50% setelah akhir TW I mencerminkan perencanaan pengadaan belum matang dan berisiko eksekusi mundur ke TW III/IV.",
  "akibat": "Eksekusi paket besar mundur ke TW III/IV menimbulkan risiko kualitas (crunch time), serapan anggaran rendah, dan potensi pemotongan pagu PN saat revisi DIPA. Paket dengan isu historis PJP/SLA berpotensi melanjutkan masalah lama.",
  "dokumen_sumber": [
    {"file": "01-sirup/Export-SIRUP-{satker}-{tanggal}.xlsx", "halaman": 1, "kutipan": "Total pagu: Rp{X}; Draft: Rp{Y} ({Z}%)"},
    {"file": "01-sirup/Daftar-Paket-PN-{YYYY}.pdf", "halaman": 2, "kutipan": "{Nama paket} - Status: Draft"}
  ]
}
```

## Rekomendasi Standar

- Segera finalisasi paket draft yang berstatus PN — target umumkan dalam {N} hari kerja.
- Susun *early-flag risk register* per paket besar (≥ Rp10 M) dengan isu historis — identifikasi mitigasi sebelum penayangan SIRUP.
- Untuk paket risiko tinggi: minta pendampingan LKPP sebelum eksekusi.
- Reviu RKA-K/L → SIRUP wajib sinkron — pasang gate konsistensi di awal TW I.

## Contoh Kasus Historis

- **LHP Pengadaan Program Prioritas Wasdig 2026 (B-33/IJ.3/PW.04.03/01/2026)**: Per 27 Januari 2026, **68,36% pagu (Rp236,7M)** masih draft di SIRUP dari total Rp346,27M. 3 paket risiko tinggi senilai **Rp95M**: Sewa Kolokasi & Metro-E TKPPSE (Rp76,12M, riwayat SLA + tagihan tanpa kontrak), Pemeliharaan CSE (Rp6,91M, riwayat keterlambatan), Sewa Kolokasi & ISP TKPPSE (Rp12M). Seluruh swakelola Rp5,49M masih draft 100%.

## Catatan

- Pattern ini sering muncul di TA transisi SOTK atau pasca-perubahan struktur Ditjen.
- Lihat juga [[pola-temuan-berulang]] poin #2.
- Format ekspor SIRUP biasanya `.xlsx` — agen wajib gunakan pengukuran ulang untuk validasi persentase.
