# SAIPI 1200 — Kecakapan dan Kecermatan Profesional

> **Sumber**: PER-01/AAIPI/DPN/2021, Standar Atribut.

## 1200 — Kecakapan dan Kecermatan Profesional
> Penugasan harus dilaksanakan dengan menggunakan kecakapan dan kecermatan profesional (due professional care).

## 1210 — Kecakapan
> Auditor harus memiliki pengetahuan, keterampilan, dan kompetensi lain yang dibutuhkan dalam melaksanakan tugas dan tanggung jawabnya. Pimpinan APIP harus memastikan bahwa setiap tim yang melaksanakan kegiatan Pengawasan Intern secara kolektif memiliki kecakapan dibutuhkan.

**1210.A1** — Dalam hal Auditor tidak memiliki kecakapan yang memadai untuk melaksanakan seluruh atau sebagian penugasan, Pimpinan APIP harus memperoleh saran dan asistensi dari pihak yang cakap.

**1210.A2** — Auditor harus memiliki pengetahuan dan keterampilan yang memadai untuk mengevaluasi risiko fraud.

**1210.A3** — Auditor harus memiliki pengetahuan memadai mengenai risiko dan pengendalian utama serta teknik audit berbasis teknologi informasi.

## 1220 — Kecermatan Profesional (Due Professional Care)
> Auditor harus menggunakan kecermatan professional dan kecakapan dalam setiap penugasan.

**1220.A1** — Auditor harus mempertimbangkan:
- Ruang lingkup yang diperlukan dalam mencapai tujuan penugasan asurans;
- Kompleksitas, materialitas, atau signifikansi permasalahan;
- Kecukupan dan efektivitas proses tata kelola, pengelolaan risiko, dan pengendalian;
- Kemungkinan terjadinya kesalahan, fraud, atau ketidakpatuhan yang signifikan; dan
- Biaya penugasan asurans dibandingkan dengan potensi manfaat (value for money).

## 1230 — Pengembangan Profesi Berkelanjutan
> Auditor harus meningkatkan kecakapan melalui pengembangan profesi berkelanjutan.

## Implikasi untuk qc_saipi

| Rule | Standar | Cek otomatis | Severity default |
|------|---------|--------------|------------------|
| `KEC-001` | 1210 | tabel tim di context.md → tiap anggota mencantumkan jabfung auditor | PERINGATAN kalau ada anggota tanpa jabfung |
| `KEC-002` | 1210.A1 | jenis penugasan butuh keahlian khusus → tim punya? | NEEDS_REVIEW |
| `KEC-003` | 1220 | inherited dari 2310 (kecukupan informasi) — tidak dicek terpisah | inherited |
| `KEC-004` | 1230 | CPD tahunan auditor (di luar scope penugasan) | (tidak dicek per-penugasan) |
