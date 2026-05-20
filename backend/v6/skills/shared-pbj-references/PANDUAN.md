# Panduan Referensi Bersama — Pengawasan Pengadaan Barang/Jasa

**Berlaku untuk:** audit-pengadaan, reviu-pengadaan, pemantauan-pengadaan, konsultasi-pengadaan

---

## Sumber Regulasi Bersama

Keempat jenis pengawasan pengadaan menggunakan dasar hukum yang sama. Yang membedakan adalah **kedalaman pengujian**, **tujuan**, dan **format output**.

### Regulasi Utama:

| No | Regulasi | Topik Utama |
|----|----------|-------------|
| 1 | **Perpres 16/2018** jo. **Perpres 12/2021** | Prinsip, pelaku, metode, prosedur pengadaan |
| 2 | **Perlem LKPP 12/2021** | Prosedur teknis pemilihan penyedia secara rinci |
| 3 | **Perlem LKPP 4/2024** | Pengadaan konstruksi metode Design & Build |
| 4 | **Perpres 46/2025** | Ketentuan kontrak dan pembayaran terbaru |

### File Referensi (lokasi):
```
skills/audit-pengadaan/references/
  01-perpres-16-2018.md           ← Pasal-pasal utama Perpres 16/2018
  02-perpres-12-2021.md           ← Perubahan penting Perpres 12/2021
  03-perlem-lkpp-12-2021.md       ← Prosedur teknis pemilihan
  04-perlem-lkpp-4-2024.md        ← Konstruksi Design & Build
  05-perpres-46-2025.md           ← Kontrak dan pembayaran
  06-checklist-audit-pengadaan.md ← Checklist + red flags per tahap
```

> Semua skill PBJ dapat merujuk ke referensi di atas. Ketika SKILL.md masing-masing menyebut "baca references/", yang dimaksud adalah file-file tersebut.

---

## Perbandingan 4 Jenis Pengawasan Pengadaan

### Ringkasan Satu Halaman

| Aspek | Audit | Reviu | Pemantauan | Konsultasi |
|-------|-------|-------|------------|------------|
| **Tujuan** | Memberikan keyakinan memadai atas seluruh siklus pengadaan | Memberikan keyakinan terbatas atas kesesuaian dokumen perencanaan dan pemilihan | Memantau progres pelaksanaan dan menyampaikan isu aktif sebagai peringatan dini | Memberikan pendapat teknis atas isu yang dihadapi dalam proses pengadaan |
| **Tingkat Keyakinan** | **Memadai** (reasonable assurance) | **Terbatas** (limited assurance) | Tidak ada keyakinan — hanya pelaporan status | Tidak ada keyakinan — advisory/pendapat |
| **Kapan Dilakukan** | Setelah pekerjaan selesai atau pada isu strategis | Sebelum kontrak ditandatangani atau saat perencanaan | Selama kontrak berjalan | Kapan saja — atas permintaan unit kerja |
| **Ruang Lingkup** | Perencanaan → pemilihan → kontrak → pelaksanaan → pembayaran (seluruh siklus) | Perencanaan → pemilihan saja | Pelaksanaan kontrak saja | Sesuai isu yang ditanyakan |
| **Fokus Pengujian** | Kesesuaian + kewajaran + legalitas + output vs kontrak | Kesesuaian administratif dokumen terhadap ketentuan | Progres fisik vs jadwal, progres keuangan, kepatuhan penyedia | Analisis regulasi terhadap situasi spesifik |
| **Pengujian Bukti** | **Sangat mendalam** — sampai dokumen sumber, verifikasi silang | **Terbatas** — hanya memeriksa dokumen yang tersedia | **Deskriptif** — melaporkan apa yang ada, bukan memverifikasi kebenaran | **Regulasi** — tidak menguji bukti fisik |
| **Elemen Temuan** | Kondisi + Kriteria + **Sebab** + Akibat + Rekomendasi | Kondisi + Kriteria + Akibat + Rekomendasi *(tanpa Sebab)* | Kondisi + Kriteria + Potensi Risiko + Rekomendasi | Pertanyaan + Dasar Hukum + Analisis + Pendapat |
| **Sebab** | ✅ Wajib — analisis akar masalah | ❌ Tidak digunakan | ⚠️ Opsional — hanya jika sudah jelas | ❌ Tidak relevan |
| **Kerugian Negara** | ✅ Dihitung jika ada | ❌ Tidak dihitung | ❌ Tidak dihitung | ❌ Tidak dihitung |
| **Format Output** | KKP (tabel Word) → LHP Audit | KKP (tabel Word) → LHR (Laporan Hasil Reviu) | KKP (tabel Word) → LHP Pemantauan + Dashboard | Memo Konsultasi |
| **Format KKP** | No \| Judul \| Kondisi \| Kriteria \| **Sebab** \| Akibat | No \| Judul \| Kondisi \| Kriteria \| Akibat | No \| Kondisi Terkini \| Target/Kriteria \| Isu/Risiko | Tidak ada KKP formal — analisis langsung |
| **Kode Nomor Surat** | PW.04.04 | PW.04.04 | PW.04.06 | Tidak ada kode khusus / memo internal |

---

## Panduan Pemilihan Jenis Pengawasan

### Flowchart Keputusan

```
Apakah pekerjaan sedang berjalan (kontrak aktif)?
  → YA → Gunakan PEMANTAUAN (monitor progres + isu)
  → TIDAK ↓

Apakah pekerjaan sudah selesai/dibayar, atau ada isu serius (kerugian, penyimpangan)?
  → YA → Gunakan AUDIT (verifikasi mendalam sampai dokumen sumber)
  → TIDAK ↓

Apakah dokumen perencanaan/pemilihan perlu diperiksa sebelum kontrak ditandatangani?
  → YA → Gunakan REVIU (cek kesesuaian administratif)
  → TIDAK ↓

Apakah ada pertanyaan teknis atau isu yang perlu pendapat APIP?
  → YA → Gunakan KONSULTASI (advisory, tidak mengikat)
```

### Contoh Kasus Nyata

| Situasi | Jenis yang Tepat | Alasan |
|---------|-----------------|--------|
| PPK meminta pendapat apakah boleh menunjuk langsung vendor IT Rp 400 juta | Konsultasi | Pertanyaan regulasi, belum ada proses |
| KAK dan HPS untuk server Rp 2 M sudah selesai, hendak dilelang | Reviu | Cek kesesuaian dokumen sebelum tender berjalan |
| Kontraktor pembangunan gedung sudah 40% tapi laporan progres 70% | Pemantauan | Isu aktif selama pelaksanaan |
| Proyek selesai, ada indikasi nilai pekerjaan tidak sesuai kontrak | Audit | Verifikasi mendalam output vs kontrak |
| Pejabat pengadaan bertanya tentang cara menangani sanggah | Konsultasi | Pertanyaan prosedural |
| Evaluasi pengadaan yang baru selesai lelang untuk meyakinkan pimpinan | Reviu | Memberikan keyakinan terbatas atas proses |

---

## Batasan Lintas Skill — Yang Boleh dan Tidak Boleh

| Hal | Audit | Reviu | Pemantauan | Konsultasi |
|-----|-------|-------|------------|------------|
| Menghitung kerugian negara | ✅ | ❌ | ❌ | ❌ |
| Menganalisis sebab (root cause) | ✅ | ❌ | Opsional | ❌ |
| Menilai kewajaran harga | ✅ | Terbatas (HPS saja) | ❌ | Pendapat umum |
| Menilai kualitas fisik pekerjaan | ✅ | ❌ | Dari laporan saja | ❌ |
| Menyimpulkan pelanggaran | ✅ | Terbatas | ❌ (gunakan "isu") | ❌ |
| Memberikan rekomendasi | ✅ | ✅ | ✅ | ✅ |
| Bersifat mengikat secara hukum | ❌ | ❌ | ❌ | ❌ |

---

## Catatan Penting

> **Sumber referensi yang sama ≠ perlakuan yang sama.**
>
> Keempat skill menggunakan Perpres PBJ dan Peraturan LKPP yang sama sebagai kriteria pengujian. Namun:
> - **Audit** menggunakan regulasi tersebut untuk **membuktikan** apakah terjadi penyimpangan, seberapa besar, dan apa penyebabnya.
> - **Reviu** menggunakan regulasi tersebut untuk **memverifikasi** apakah dokumen telah memenuhi ketentuan secara administratif.
> - **Pemantauan** menggunakan regulasi tersebut sebagai **tolok ukur** dalam melaporkan deviasi kondisi aktual.
> - **Konsultasi** menggunakan regulasi tersebut untuk **menjelaskan** apa yang seharusnya dilakukan sesuai ketentuan.
