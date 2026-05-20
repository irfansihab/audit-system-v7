# SAIPI 2200 — Perencanaan Penugasan Pengawasan Intern

> **Sumber**: PER-01/AAIPI/DPN/2021, Standar Kinerja.

## 2200 — Perencanaan Penugasan
> Auditor harus menyusun dan mendokumentasikan rencana untuk setiap penugasan, termasuk **tujuan, ruang lingkup, waktu, dan alokasi sumber daya** penugasan. Rencana penugasan harus mempertimbangkan strategi, tujuan, dan risiko organisasi yang relevan dengan penugasan.

## 2201 — Pertimbangan Perencanaan
Dalam merencanakan penugasan, Auditor harus mempertimbangkan:
- Strategi dan sasaran kegiatan serta pengendalian atas kinerjanya;
- Risiko signifikan atas sasaran, sumber daya, dan operasi;
- Kecukupan dan efektivitas proses tata kelola, manajemen risiko dan pengendalian intern kegiatan;
- Peluang untuk perbaikan yang signifikan.

## 2210 — Tujuan Penugasan
> Tujuan harus ditetapkan untuk setiap penugasan.

**2210.A1** — Auditor harus melakukan penilaian terhadap risiko kegiatan. Hasil penilaian atas risiko tersebut harus tercermin dalam tujuan penugasan.

**2210.A3** — Kriteria yang memadai diperlukan untuk mengevaluasi tata kelola, manajemen risiko, dan pengendalian intern. Jenis kriteria: intern (kebijakan/prosedur organisasi), ekstern (hukum/peraturan), praktik terdepan.

## 2220 — Ruang Lingkup Penugasan
> Ruang lingkup penugasan yang ditetapkan harus memadai untuk mencapai tujuan penugasan.

**2220.A1** — Ruang lingkup harus mempertimbangkan sistem, dokumen, sumber daya manusia, dan aset yang relevan, termasuk yang berada di bawah pengelolaan pihak ketiga.

## 2230 — Alokasi Sumber Daya Penugasan
> Auditor harus menentukan sumber daya yang **memadai dan cukup** untuk mencapai tujuan penugasan, berdasarkan evaluasi atas karakteristik dan tingkat kompleksitas setiap penugasan, keterbatasan waktu, dan sumber daya yang tersedia.

**Interpretasi**: *Memadai* = secara kolektif kecakapan terpenuhi. *Cukup* = kuantitas sumber daya cukup.

## 2240 — Program Kerja Penugasan
> Auditor harus menyusun dan mendokumentasikan program kerja untuk mencapai tujuan penugasan.

## Implikasi untuk qc_saipi (di v4 KP+PKP berasal dari INTEGRAL — di-upload ke 00-input/)

| Rule | Standar | Cek otomatis | Severity default |
|------|---------|--------------|------------------|
| `REN-001` | 2200/2240 | `00-input/KP-*.{pdf,docx}` exist | KRITIS |
| `REN-002` | 2200/2240 | `00-input/PKP-*.{pdf,docx}` exist | KRITIS |
| `REN-003` | 2210 | `context.md` punya field "Tujuan" terisi non-empty | KRITIS |
| `REN-004` | 2210 | `_PKP/sasaran-assignment.json` ≥ 1 sasaran | KRITIS |
| `REN-005` | 2220 | `context.md` punya field "Ruang Lingkup" terisi | PERINGATAN |
| `REN-006` | 2230 | rasio sasaran:anggota wajar (mis. ≥ 1 anggota tiap sasaran) | NEEDS_REVIEW kalau ekstrem |
| `REN-007` | 2210.A3 | tiap sasaran punya `langkah_kerja[]` non-empty (kriteria operasional) | PERINGATAN |
