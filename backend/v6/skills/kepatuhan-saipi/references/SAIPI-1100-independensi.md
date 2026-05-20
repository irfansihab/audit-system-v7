# SAIPI 1100 — Independensi dan Objektivitas

> **Sumber**: PER-01/AAIPI/DPN/2021, Standar Atribut. Ekstraksi verbatim dari `wiki/raw/SAIPI-PER-01-AAIPI-DPN-2021.pdf`.

## 1100 — Independensi dan Objektivitas
> Aktivitas Pengawasan Intern harus independen dan auditor harus objektif dalam melaksanakan tugasnya.

**Interpretasi**: Independensi adalah kondisi bebas dari situasi yang dapat mengancam kemampuan APIP untuk dapat melaksanakan tanggung jawabnya secara objektif. Objektivitas adalah suatu sikap mental tidak memihak yang memungkinkan auditor melaksanakan tugas sedemikian rupa sehingga mereka memiliki keyakinan terhadap hasil kerja mereka dan tanpa kompromi dalam mutu.

## 1110 — Independensi APIP
> Pimpinan APIP bertanggung jawab kepada Pimpinan K/L/D atas pelaksanaan Pengawasan Intern.

**1110.A1** — Kegiatan asurans harus bebas dari campur tangan dalam penentuan ruang lingkup, pelaksanaan penugasan, dan pelaporan hasilnya.

## 1120 — Objektivitas Auditor
> Auditor harus memiliki sikap netral dan tidak bias, serta senantiasa menghindarkan diri dari kemungkinan timbulnya benturan kepentingan.

## 1130 — Pelemahan terhadap Independensi atau Objektivitas
> Jika terjadi pelemahan terhadap independensi atau objektivitas, baik secara faktual maupun penampilan, maka pelemahan tersebut harus diungkapkan kepada Pimpinan K/L/D dan Komite Audit.

**1130.A1** — Auditor **harus menolak melaksanakan penugasan asurans yang sebelumnya pernah menjadi tanggung jawabnya**. Objektivitas auditor dianggap melemah apabila auditor memberikan jasa asurans atas kegiatan yang pernah menjadi tanggung jawabnya pada tahun sebelumnya.

**1130.A2** — Penugasan asurans yang dilakukan terhadap aktivitas dan/atau unit kerja yang pernah menjadi tanggung jawab Pimpinan APIP, harus diawasi oleh pihak lain di luar APIP.

**1130.A3** — APIP dapat memberikan jasa asurans meskipun sebelumnya telah melaksanakan jasa konsultansi, dengan syarat pelaksanaan kegiatan konsultansi tersebut tidak mengganggu objektivitas.

## Implikasi untuk qc_saipi

| Rule | Standar | Cek otomatis | Severity default |
|------|---------|--------------|------------------|
| `IND-001` | 1100/1130 | ada `_QA-SAIPI/deklarasi-independensi.md` | NEEDS_REVIEW kalau belum ada |
| `IND-002` | 1130.A1 | confirm: tim tidak pernah jadi PIC area diaudit setahun terakhir | NEEDS_REVIEW (manual) |
| `IND-003` | 1130 | jika konflik/pelemahan ditemukan, sudah diungkap di context.md atau LHP | NEEDS_REVIEW (manual) |
