# Checklist Dokumen — Reviu Rencana Kerja dan Anggaran (RKA/KL)

**Skill:** reviu-rka-kl
**Lingkup:** Kesesuaian dan kualitas perencanaan anggaran sebelum diajukan ke DPR
**Timing:** Oktober–November (sebelum RKA/KL T+1 diajukan)

---

## Dokumen WAJIB

| No | Dokumen | Sumber/Folder | Keterangan |
|----|---------|---------------|------------|
| W1 | Surat Tugas (ST) | `00-surat-tugas/` | Dasar penugasan |
| W2 | Draft RKA/KL yang akan direviu | `03-perencanaan/` atau via chat | Dokumen utama — bisa berupa file Excel SAKTI/SATU ANGGARAN |
| W3 | Perjanjian Kinerja (PK) atau Rencana Kinerja Tahunan (RKT) | `03-perencanaan/` | Dasar pengujian keselarasan program-anggaran |

---

## Dokumen PENTING (reviu terbatas jika tidak ada)

| No | Dokumen | Sumber | Dampak jika tidak ada |
|----|---------|--------|-----------------------|
| P1 | Renstra unit kerja (5 tahunan) yang berlaku | `03-perencanaan/` | Keselarasan jangka menengah tidak dapat diverifikasi |
| P2 | RKP (Rencana Kerja Pemerintah) tahun berjalan | via chat | Kesesuaian dengan prioritas nasional tidak dapat dinilai |
| P3 | Standar Biaya Masukan (SBM) PMK tahun berjalan | `01-peraturan-internal/` atau via chat | Kewajaran komponen biaya tidak dapat diverifikasi |
| P4 | Standar Biaya Keluaran (SBK) jika tersedia | `01-peraturan-internal/` | Kewajaran target output tidak dapat dikonfirmasi |
| P5 | DIPA/RKA/KL tahun berjalan (untuk perbandingan) | `03-perencanaan/` | Perubahan signifikan dari tahun sebelumnya tidak dapat diidentifikasi |

---

## Dokumen OPSIONAL

| No | Dokumen | Manfaat |
|----|---------|---------|
| O1 | TOR/KAK per kegiatan | Pengujian rincian justifikasi anggaran |
| O2 | RAB per kegiatan | Pengujian kewajaran rincian biaya |
| O3 | Nota Dinas permintaan reviu dari unit perencanaan | Konteks fokus yang diminta |
| O4 | Laporan kinerja tahun sebelumnya | Pertimbangan kelayakan target T+1 |

---

## Aturan Validasi

```
KRITIS:
  → W1 (Surat Tugas)
  → W2 (Draft RKA/KL)

PERINGATAN:
  → W3 tidak ada → kesesuaian program-anggaran dengan PK/RKT tidak dapat dinilai
  → P3 tidak ada → kewajaran komponen biaya (SBM) tidak dapat diverifikasi — catat sebagai keterbatasan

INFORMASI:
  → P1, P2, P4, P5, O1–O4 tidak ada → reviu tetap berjalan dengan keterbatasan yang dicatat
```

---

## Pesan Notifikasi

Jika W2 (RKA/KL) tidak ada:
> ❌ **Reviu tidak dapat dimulai.** Draft RKA/KL yang akan direviu tidak ditemukan. Mohon upload file RKA/KL (Excel SATU ANGGARAN/SAKTI) atau kirim via chat.

Jika P3 (SBM) tidak ada:
> ⚠️ **SBM tidak tersedia.** Kewajaran komponen biaya per satuan tidak dapat diverifikasi terhadap standar resmi. Reviu akan menggunakan penilaian kewajaran umum. Ketik **LANJUT** atau upload PMK SBM terlebih dahulu.

Jika dokumen lengkap:
> ✅ **Dokumen siap.** Ketik **LANJUT** untuk memulai reviu.
