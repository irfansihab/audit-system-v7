---
id: RP-08
skill: reviu-pengadaan
kategori: PBJ-HPS
severity: CRITICAL
judul: "HPS Tidak Didukung Minimum 2 Sumber Harga Independen"
kriteria_baku: "Perpres 16/2018 jo. Perpres 12/2021 Pasal 26 ayat (5)"
tags: [hps, rfi, perpres-16, kewajaran-harga]
---

# RP-08: HPS Tidak Didukung Minimum 2 Sumber Harga Independen

## Pattern Kondisi

HPS hanya didukung satu sumber harga formal (RFI) atau kurang, padahal regulasi mensyaratkan minimum dua sumber harga independen. Indikator umum:

- Salah satu dari tiga RFI ternyata adalah **surat penolakan** (vendor menyatakan tidak dapat berpartisipasi), bukan penawaran harga
- RFI yang ada **tidak menyebutkan harga total atau rincian unit** — hanya pernyataan kapasitas
- Dokumen "Rekap RFI" memuat harga dari vendor yang **tidak ada lampiran RFI formal**-nya
- Tahun anggaran di RFI **berbeda** dengan TA pengadaan yang sedang dinilai

## Kriteria

Perpres 16/2018 tentang Pengadaan Barang/Jasa Pemerintah jo. Perpres 12/2021 (perubahan), **Pasal 26 ayat (5)**:

> "Penyusunan HPS didasarkan pada hasil survei pasar yang dilakukan dengan cara mengumpulkan informasi harga dari sekurang-kurangnya 2 (dua) penyedia atau sumber informasi harga lainnya."

PMK 39/2024 atau SBM yang berlaku TA terkait juga menjadi rujukan pelengkap.

## Akibat

1. **HPS tidak wajar** — tidak ada validasi silang harga pasar, berpotensi mark-up atau under-budget
2. **Sengketa kontrak** — vendor pemenang dapat menggugat dasar HPS bila harga ternyata tidak realistis
3. **Temuan BPK** — auditor eksternal akan kembali menemukan ketidakwajaran HPS
4. **Audit trail tidak lengkap** — bila pertanyaan due diligence dari pengawas eksternal datang, tidak ada bukti penjajakan harga yang memadai

## Bukti Yang Harus Dicari

| Dokumen | Section / Field | Yang dicari |
|---------|-----------------|-------------|
| HPS PDF | "Sumber Penjajakan Harga" atau "Rincian RFI" | Daftar nama vendor + status penawaran |
| RFI per vendor | Body surat | Apakah berisi tabel harga + total, atau surat penolakan |
| RFI per vendor | Header / tanggal | Apakah tanggal & TA sesuai dengan pengadaan saat ini |
| Surat penjajakan | Lampiran | Apakah jumlah vendor yang dikirimi penjajakan ≥ 3 (untuk antisipasi 1-2 menolak) |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PBJ-02",
  "assigned_to": "{nama anggota}",
  "judul": "HPS Hanya Didukung 1 Sumber Harga Independen Valid",
  "kondisi": "HPS senilai Rp X.XXX.XXX.XXX dirujuk dari 4 vendor (Vendor A, B, C, D). Pemeriksaan dokumen menemukan: (1) RFI Vendor A adalah surat penolakan partisipasi; (2) RFI Vendor B & C tidak melampirkan dokumen RFI formal, hanya tertulis di Rekap; (3) Hanya Vendor D yang memberikan penawaran harga formal lengkap dengan rincian unit. Dengan demikian HPS hanya disokong 1 sumber harga independen.",
  "kriteria": "Perpres 16/2018 jo. Perpres 12/2021 Pasal 26 ayat (5) mensyaratkan minimum 2 (dua) sumber informasi harga independen sebagai dasar HPS.",
  "akibat": "Penetapan HPS tidak memiliki validasi silang harga pasar yang memadai, berpotensi tidak wajar dan menimbulkan sengketa kontrak.",
  "dokumen_sumber": [
    {"file": "02-kontrak/HPS-XXX.pdf", "halaman": 3, "kutipan": "Rekap RFI: Vendor A — menolak; Vendor B — Rp ..."},
    {"file": "02-kontrak/RFI-VendorA-XXX.pdf", "halaman": 1, "kutipan": "tidak dapat berpartisipasi..."}
  ]
}
```

## Contoh Kasus Historis

- **2026 Reviu Pengadaan Cloud PSrE** — RFI Telkom Sigma menolak; HPS Rp 5,57 M hanya disokong RFI CNI. Kondisi terverifikasi pada halaman 3 HPS + halaman 1 RFI Telkom Sigma.

## Catatan

- Jangan rekomendasikan pembatalan paket pengadaan kecuali nilai signifikan dan tidak ada jalur perbaikan
- Rekomendasi standar: "Lakukan penjajakan harga ulang ke minimum 2 vendor lain dan dokumentasikan secara formal sebelum proses pemilihan dilanjutkan"
