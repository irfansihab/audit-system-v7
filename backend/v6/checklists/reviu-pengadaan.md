# Checklist Dokumen — Reviu Perencanaan dan Pemilihan Pengadaan

**Skill:** reviu-pengadaan (v1.2)
**Lingkup default:** Perencanaan (KAK + HPS) — lihat Scope Switch di SKILL.md
**Dokumen yang tidak diperlukan:** RUP/SiRUP (untuk scope perencanaan), SPPBJ (untuk scope perencanaan), laporan pelaksanaan fisik, SPM/SP2D, BAST

---

## Scope Perencanaan (DEFAULT)

### Dokumen WAJIB

| No | Dokumen | Folder | Keterangan |
|----|---------|--------|------------|
| W1 | Surat Tugas (ST) | `00-surat-tugas/` | Dasar penugasan — jika tidak ada, tandai uji coba dan lanjutkan |
| W2 | KAK / TOR / Spesifikasi Teknis | `03-perencanaan/` | Dokumen utama yang akan direviu |
| W3 | Harga Perkiraan Sendiri (HPS) | `03-perencanaan/` | Wajib untuk menilai kewajaran estimasi biaya |
| W4 | Data dukung HPS (survei harga / RFI / e-katalog / harga referensi) | `03-perencanaan/` | Wajib untuk verifikasi metodologi HPS |

### Dokumen PENTING (scope perencanaan)

| No | Dokumen | Folder | Dampak jika tidak ada |
|----|---------|--------|-----------------------|
| P1 | Kontrak periode sebelumnya / pembanding harga | `02-kontrak/` | Tidak ada data pembanding — kelemahan analisis HPS |
| P2 | Rancangan Kontrak | `03-perencanaan/` atau `02-kontrak/` | Aspek klausul kontrak tidak dapat dinilai |

### Dokumen OPSIONAL (scope perencanaan)

| No | Dokumen | Folder | Manfaat |
|----|---------|--------|---------|
| O1 | SOP / Peraturan Internal instansi | `01-peraturan-internal/` | Kriteria tambahan di luar Perpres |
| O2 | DPA / DIPA / RKA | `03-perencanaan/` | Verifikasi kesesuaian pagu anggaran |
| O3 | ND Permintaan (jika ada) | `00-surat-tugas/` | Konteks latar belakang penugasan |

> ❌ **RUP/SiRUP tidak masuk checklist scope perencanaan** — tidak efisien (portal tidak bisa diakses AI, dokumen jarang ada di berkas)
> ❌ **SPPBJ, BAHP, Dokumen Pemilihan tidak masuk checklist scope perencanaan** — aktifkan jika scope pemilihan

---

## Tambahan jika Scope Pemilihan (aktifkan jika ST mencakup pemilihan)

| No | Dokumen | Folder | Dampak jika tidak ada |
|----|---------|--------|-----------------------|
| P3 | Dokumen Pemilihan (RFP/dok. tender) | folder penugasan atau `02-kontrak/` | Aspek pemilihan tidak dapat dinilai |
| P4 | BAHP / BA Evaluasi | folder penugasan atau `02-kontrak/` | Proses evaluasi penyedia tidak dapat dinilai |
| P5 | SPPBJ (Surat Penunjukan Penyedia) | `02-kontrak/` | Tahap penetapan pemenang tidak dapat dinilai |
| O4 | Dokumen sanggah (jika ada) | folder penugasan | Memahami kontroversi di tahap pemilihan |

---

## Aturan Validasi

```
KRITIS (harus ada, reviu TIDAK DAPAT dilanjutkan):
  → W2 (KAK/TOR/Spesifikasi) — ini adalah dokumen utama yang direviu

PERINGATAN (reviu terbatas, catat sebagai keterbatasan):
  → W1 tidak ada → catat sebagai uji coba / tanpa dasar ST resmi, lanjutkan
  → W3 tidak ada → aspek HPS tidak dapat dinilai
  → W4 tidak ada → kewajaran metodologi pembentukan harga tidak dapat diverifikasi
                 → catat "Data dukung HPS tidak tersedia — kewajaran harga tidak dapat dikonfirmasi"
  → P1 tidak ada → tidak ada data pembanding — analisis proporsionalitas HPS terbatas
  → P3, P4 tidak ada (scope pemilihan) → aspek pemilihan tidak dapat dinilai

INFORMASI (catat, lanjutkan tanpa hambatan):
  → O1–O4 tidak ada → reviu tetap berjalan dengan kriteria Perpres
```

---

## Pesan Notifikasi untuk Auditor

Jika dokumen kritis tidak ada:
> ❌ **Reviu tidak dapat dimulai.** Dokumen wajib berikut tidak ditemukan: [daftar]. Mohon upload dokumen tersebut ke folder yang sesuai, kemudian ketik **ULANG** untuk memeriksa ulang.

Jika ada dokumen penting yang tidak ada:
> ⚠️ **Reviu dapat dilanjutkan dengan keterbatasan.** Dokumen berikut tidak ditemukan: [daftar]. Aspek yang terkait tidak akan dapat dinilai dan akan dicatat sebagai keterbatasan reviu. Ketik **LANJUT** untuk melanjutkan atau upload dokumen tambahan terlebih dahulu.

Jika semua dokumen wajib tersedia:
> ✅ **Dokumen lengkap.** Semua dokumen wajib tersedia. Ketik **LANJUT** untuk memulai analisis.
