# Wiki — Audit AI v7

Knowledge base yang dapat diakses agen Anggota Tim (AT) dan Ketua Tim (KT) saat menjalankan reviu. Folder ini ditujukan untuk **diisi & dikelola oleh auditor manusia** sebagai pengetahuan kumulatif tim Inspektorat II.

## Dua jenis isi

1. **Pattern temuan** (`temuan-patterns/`) — "rumus" temuan yang sudah pernah teruji. Tiap pattern memuat format judul, kondisi, kriteria peraturan, akibat, dan bukti yang harus dicari.
2. **Konteks pendukung** (`konteks/`) — pola temuan berulang, glossary istilah Komdigi, regulasi & pasal kunci. Tujuannya **mengurangi halusinasi agen** (cegah salah definisi istilah, ngarang sitasi pasal, atau memaksakan pola).

## Cara agen pakai wiki

Saat agen menjalankan analisis, dia akan (urutan disarankan):

1. **`list_konteks()` + `get_konteks(kategori)`** — wajib di awal, baca pola-berulang + glossary + regulasi untuk re-orientasi.
2. **`list_temuan_patterns(skill)`** — dapat daftar pattern untuk skill (reviu-pengadaan / reviu-rka-kl).
3. **`get_temuan_pattern(pattern_id)`** — baca pattern spesifik yang relevan, pakai sebagai **referensi format & checklist** (bukan template copy-paste).

## Struktur folder

```
wiki/
├── README.md                          # file ini
├── temuan-patterns/
│   ├── reviu-pengadaan/
│   │   ├── README.md                  # index pattern reviu-pengadaan
│   │   ├── RP-08-hps-rfi-minimum.md
│   │   ├── RP-09-kontrak-tanpa-kontrak-sotk.md
│   │   ├── RP-10-adendum-nomor-ganda.md
│   │   ├── RP-11-pagu-sirup-draft-akhir-tw1.md
│   │   ├── RP-12-kajian-tanpa-rencana-aksi.md
│   │   ├── RP-13-vendor-confidentiality-audit-trail.md
│   │   ├── RP-14-perpanjangan-lisensi-tanggal-awal.md
│   │   ├── RP-15-e-katalog-tanpa-negosiasi.md
│   │   └── RP-16-vendor-pjt-belum-berkontrak.md
│   └── reviu-rka-kl/
│       ├── README.md
│       ├── RKA-01-tor-7-blok.md
│       ├── RKA-02-ro-tanpa-parameter-keberhasilan.md
│       ├── RKA-03-komponen-belum-cukup.md
│       ├── RKA-04-tor-tanpa-metode-pengadaan.md
│       ├── RKA-05-ketidakselarasan-metode-tahapan.md
│       ├── RKA-06-cost-analysis-belum-ada.md
│       └── RKA-07-indikator-om-tidak-sesuai-prinsip.md
└── konteks/
    ├── README.md
    ├── pola-temuan-berulang.md        # 9 akar masalah lintas LHP/LHR 2025-2026
    ├── glossary-komdigi.md            # akronim + profil vendor mitra
    └── regulasi-kunci.md              # pasal baku + kutipan inti
```

## Format file pattern

Setiap pattern adalah file `.md` dengan YAML frontmatter di atas, lalu konten markdown. Skema minimal:

```markdown
---
id: RP-08
skill: reviu-pengadaan
kategori: PBJ-HPS
severity: CRITICAL
judul: "HPS Tidak Didukung Minimum 2 Sumber Harga Independen"
kriteria_baku: "Perpres 16/2018 jo. Perpres 12/2021 Pasal 26 ayat (5)"
tags: [hps, rfi, perpres-16]
---

# RP-08: HPS Tidak Didukung Minimum 2 Sumber Harga Independen

## Pattern Kondisi
Deskripsi pola kondisi yang menjadi indikator temuan...

## Kriteria
Peraturan yang dilanggar, lengkap dengan pasal & ayat...

## Akibat
Risiko yang muncul bila kondisi tidak diperbaiki...

## Bukti Yang Harus Dicari
- Dokumen HPS: section "Sumber Penjajakan Harga"
- Dokumen RFI per vendor: pastikan berisi penawaran harga, bukan surat penolakan
- ...

## Contoh Kasus Sebelumnya
(opsional) Anonimkan kasus historis untuk konteks
```

**Field wajib** di frontmatter:
- `id` — unique identifier (mis. `RP-08`, `RKA-15`)
- `skill` — `reviu-pengadaan` | `reviu-rka-kl`
- `kategori` — bebas (PBJ-HPS, RKA-TOR, dll)
- `severity` — `CRITICAL` | `HIGH` | `MEDIUM` | `LOW` | `INFO`
- `judul` — string

**Field opsional:**
- `kriteria_baku` — peraturan inti yang dilanggar
- `tags` — array string untuk pencarian

## Penamaan file

Pola: `{ID}-{slug-judul-pendek}.md`

Contoh:
- `RP-08-hps-rfi-minimum.md` ✓
- `RKA-15-sbm-tahun-anggaran.md` ✓
- `pattern-hps.md` ✗ (tidak ada ID prefix, sulit dilacak)

## Cara menambahkan pattern baru

1. Tentukan ID yang belum dipakai (cek README.md per skill)
2. Buat file `.md` di subfolder skill yang sesuai
3. Isi frontmatter + konten
4. Update README.md per skill (tambah baris di tabel index)
5. Commit ke git supaya tim lain bisa pakai

## Diakses oleh

- Agen Anggota Tim (`anggota_tim`) saat susun KKP
- Agen Ketua Tim (`ketua_tim`) saat susun LHR + rekomendasi

Path resolusi via env var `APP_WIKI_PATH` di `.env`.

## Lihat juga

- `backend/app/tools/wiki_tools.py` — implementasi bridge agen → wiki
- `../README.md` § "Wiki / Pattern Library"
