#!/usr/bin/env python3
"""
qc_saipi.py — Quality Assurance otomatis terhadap Standar Audit Intern
Pemerintah Indonesia (PER-01/AAIPI/DPN/2021), per-penugasan.

Dipanggil otomatis di akhir Task 03 (stage=kkp) dan Task 04 (stage=lhp).

Output:
- penugasan/[nama]/_QA-SAIPI/checklist-{stage}.json
- penugasan/[nama]/_QA-SAIPI/laporan-qa-{stage}.md
- 1 event audit-trail (action=SAIPI_CHECK)
- exit code: 0 (PASS), 2 (ada KRITIS), 1 (error eksekusi)

Usage:
    python3 scripts/qc_saipi.py --penugasan penugasan/2026-05-001-xxx --stage kkp
    python3 scripts/qc_saipi.py --penugasan penugasan/2026-05-001-xxx --stage lhp

Sumber otoritatif: skills/kepatuhan-saipi/references/checklist-saipi-per-penugasan.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CHECKLIST_PATH = ROOT / "skills" / "kepatuhan-saipi" / "references" / "checklist-saipi-per-penugasan.json"

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
from audit_trail import log_event  # noqa: E402

WIB = timezone(timedelta(hours=7))

PLACEHOLDER_BAD = re.compile(r"(\{\{[^}]+\}\}|\[XXXX+\]|\[TBD\]|\[CONTOH\])", re.IGNORECASE)
PLACEHOLDER_OK = "[DIISI AUDITOR]"  # whitelist


def _now_iso() -> str:
    return datetime.now(WIB).isoformat(timespec="seconds")


def _read_text_file(path: Path) -> str:
    if not path.exists():
        return ""
    if path.suffix.lower() == ".docx":
        return _read_docx(path)
    if path.suffix.lower() == ".pdf":
        return ""  # opsi lanjut: pakai pdftotext
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def _read_docx(path: Path) -> str:
    """Ekstraksi teks docx tanpa external lib (parse XML word/document.xml)."""
    import zipfile
    from xml.etree import ElementTree as ET
    try:
        with zipfile.ZipFile(path) as z:
            with z.open("word/document.xml") as f:
                tree = ET.parse(f)
        ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
        texts = [t.text or "" for t in tree.iter(f"{{{ns['w']}}}t")]
        return "\n".join(texts)
    except Exception:
        return ""


def _load_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# ---- helper individual rule check ----

def _result(rule: dict, status: str, severity: str, bukti: str, gap: str = "") -> dict:
    return {
        "rule_id": rule["rule_id"],
        "saipi_standar": rule["saipi_standar"],
        "kelompok": rule["kelompok"],
        "deskripsi": rule["deskripsi"],
        "status": status,            # OK | GAP | NEEDS_REVIEW | NOT_APPLICABLE
        "severity": severity,        # OK | KRITIS | PERINGATAN | NEEDS_REVIEW
        "bukti": bukti,
        "gap": gap,
    }


def check_IND_001(rule, ctx) -> dict:
    p = ctx["penugasan"] / "_QA-SAIPI" / "deklarasi-independensi.md"
    if p.exists():
        return _result(rule, "OK", "OK", f"File ada: {p.name}")
    return _result(rule, "GAP", rule["default_severity"],
                   "deklarasi-independensi.md belum ada",
                   "Buat _QA-SAIPI/deklarasi-independensi.md (template auto-generated)")


def check_KEC_001(rule, ctx) -> dict:
    text = ctx["context_md"]
    if not text:
        return _result(rule, "GAP", rule["default_severity"], "context.md tidak ada", "Jalankan Task 01")
    # Cari kata jabfung di sekitar daftar Tim
    jabfung_kw = re.compile(r"(Auditor (Madya|Muda|Pertama|Ahli|Penyelia|Utama)|Auditor Ahli (Madya|Muda|Pertama|Utama))",
                            re.IGNORECASE)
    hits = jabfung_kw.findall(text)
    if hits:
        return _result(rule, "OK", "OK", f"{len(hits)} indikasi jabfung tercantum di context.md")
    return _result(rule, "GAP", rule["default_severity"],
                   "Tidak ditemukan jabfung auditor di context.md",
                   "Tambahkan jabfung tiap anggota tim di section Tim context.md")


def check_REN_001(rule, ctx) -> dict:
    files = list(ctx["input_dir"].glob("KP-*.*"))
    if files:
        return _result(rule, "OK", "OK", f"Ditemukan: {[f.name for f in files]}")
    return _result(rule, "GAP", rule["default_severity"],
                   "Tidak ada file KP-*.* di 00-input/",
                   "Auditor unduh Kartu Penugasan dari INTEGRAL dan taruh di 00-input/")


def check_REN_002(rule, ctx) -> dict:
    files = list(ctx["input_dir"].glob("PKP-*.*"))
    if files:
        return _result(rule, "OK", "OK", f"Ditemukan: {[f.name for f in files]}")
    return _result(rule, "GAP", rule["default_severity"],
                   "Tidak ada file PKP-*.* di 00-input/",
                   "Auditor unduh Program Kerja Pengawasan dari INTEGRAL dan taruh di 00-input/")


def check_REN_003(rule, ctx) -> dict:
    text = ctx["context_md"]
    if not text:
        return _result(rule, "GAP", rule["default_severity"], "context.md tidak ada", "Jalankan Task 01")
    m = re.search(r"^Tujuan(?:\s*\(.*?\))?\s*:\s*(.+)$", text, re.MULTILINE)
    if m and len(m.group(1).strip()) >= 10:
        return _result(rule, "OK", "OK", f"Tujuan terisi: {m.group(1)[:60]}...")
    return _result(rule, "GAP", rule["default_severity"],
                   "Field 'Tujuan' di context.md kosong atau terlalu pendek",
                   "Lengkapi field Tujuan di context.md (salin dari ST/KP)")


def check_REN_004(rule, ctx) -> dict:
    sa = ctx["sasaran"]
    if sa and len(sa.get("sasaran", [])) >= 1:
        return _result(rule, "OK", "OK", f"{len(sa['sasaran'])} sasaran")
    return _result(rule, "GAP", rule["default_severity"],
                   "_PKP/sasaran-assignment.json tidak ada atau 0 sasaran",
                   "Jalankan Task 01 untuk ekstrak sasaran dari PKP")


def check_REN_005(rule, ctx) -> dict:
    text = ctx["context_md"]
    m = re.search(r"^Ruang Lingkup\s*:\s*(.+)$", text, re.MULTILINE) if text else None
    if m and len(m.group(1).strip()) >= 5:
        return _result(rule, "OK", "OK", f"Terisi: {m.group(1)[:60]}...")
    return _result(rule, "GAP", rule["default_severity"],
                   "Field 'Ruang Lingkup' di context.md kosong",
                   "Lengkapi Ruang Lingkup di context.md")


def check_REN_006(rule, ctx) -> dict:
    sa = ctx["sasaran"]
    if not sa:
        return _result(rule, "GAP", rule["default_severity"], "sasaran-assignment.json tidak ada", "Jalankan Task 01")
    bad = [s["sasaran_id"] for s in sa.get("sasaran", []) if not s.get("assigned_to")]
    if bad:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} sasaran tanpa anggota: {bad}",
                       "Tambahkan assigned_to di sasaran tsb (sumber: PKP)")
    return _result(rule, "OK", "OK", "Semua sasaran punya anggota assigned")


def check_REN_007(rule, ctx) -> dict:
    sa = ctx["sasaran"]
    if not sa:
        return _result(rule, "GAP", rule["default_severity"], "sasaran-assignment.json tidak ada", "Jalankan Task 01")
    bad = [s["sasaran_id"] for s in sa.get("sasaran", []) if not s.get("langkah_kerja")]
    if bad:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} sasaran tanpa langkah_kerja: {bad}",
                       "Tambahkan langkah_kerja[] (operasionalisasi kriteria 2210.A3)")
    return _result(rule, "OK", "OK", "Semua sasaran memiliki langkah_kerja")


def check_LAK_001(rule, ctx) -> dict:
    t = ctx["temuan"]
    if not t:
        return _result(rule, "GAP", rule["default_severity"], "_KKP/temuan.json tidak ada", "Jalankan Task 03")
    bad = [x["id_temuan"] for x in t.get("temuan", []) if not x.get("dokumen_sumber")]
    if bad:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} temuan tanpa dokumen_sumber: {bad}",
                       "Setiap temuan WAJIB sebut sumber dokumen (anti-halusinasi 2310)")
    return _result(rule, "OK", "OK", f"Semua {len(t.get('temuan', []))} temuan punya dokumen_sumber")


def check_LAK_002(rule, ctx) -> dict:
    t = ctx["temuan"]
    if not t:
        return _result(rule, "NOT_APPLICABLE", "OK", "temuan.json belum ada (skip)")
    # Cari file di seluruh folder penugasan (rglob), bukan hanya 00-input/
    # Ini mengakomodasi penugasan yang mengorganisasi bukti di subfolder (mis. 02-kontrak/)
    pen_dir: Path = ctx["penugasan"]
    all_files_by_name: dict[str, Path] = {}
    for p in pen_dir.rglob("*"):
        if p.is_file() and not any(part.startswith("_") for part in p.relative_to(pen_dir).parts):
            all_files_by_name[p.name] = p
    missing = []
    for x in t.get("temuan", []):
        for d in x.get("dokumen_sumber", []):
            f = d.get("file", "")
            if not f:
                continue
            fname = Path(f).name
            # Cek path relatif langsung, atau nama file di mana saja
            full_path = pen_dir / f
            if not full_path.exists() and fname not in all_files_by_name:
                missing.append(f"{x['id_temuan']}: {f}")
    if missing:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(missing)} referensi file tidak ditemukan di folder penugasan",
                       "File yang disebut harus ada di folder penugasan (mis. 02-kontrak/). Daftar: " + "; ".join(missing[:5]))
    return _result(rule, "OK", "OK", "Semua referensi file dapat ditemukan di folder penugasan")


def check_LAK_003(rule, ctx) -> dict:
    t = ctx["temuan"]
    if not t:
        return _result(rule, "NOT_APPLICABLE", "OK", "temuan.json belum ada")
    bad = []
    for x in t.get("temuan", []):
        for d in x.get("dokumen_sumber", []):
            if not d.get("halaman"):
                bad.append(f"{x['id_temuan']}/{d.get('file','?')}")
    if bad:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} dokumen_sumber tanpa halaman",
                       "Cantumkan halaman/pasal supaya informasi cukup-andal (SAIPI 2310)")
    return _result(rule, "OK", "OK", "Semua dokumen_sumber memiliki halaman")


def check_LAK_004(rule, ctx) -> dict:
    t = ctx["temuan"]
    if not t:
        return _result(rule, "NOT_APPLICABLE", "OK", "temuan.json belum ada")
    bad = []
    for x in t.get("temuan", []):
        if len(x.get("kondisi", "")) < 30: bad.append(f"{x['id_temuan']}: kondisi<30")
        if len(x.get("kriteria", "")) < 10: bad.append(f"{x['id_temuan']}: kriteria<10")
        if len(x.get("akibat", "")) < 10: bad.append(f"{x['id_temuan']}: akibat<10")
    if bad:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} field di bawah panjang minimum",
                       "Lengkapi kondisi/kriteria/akibat: " + "; ".join(bad[:5]))
    return _result(rule, "OK", "OK", "Semua kondisi/kriteria/akibat memenuhi panjang minimum")


def check_LAK_005(rule, ctx) -> dict:
    t = ctx["temuan"]
    if not t:
        return _result(rule, "NOT_APPLICABLE", "OK", "temuan.json belum ada")
    jp = t.get("penugasan", {}).get("jenis_pengawasan", "")
    if jp not in ("audit-pengadaan", "audit-kinerja"):
        return _result(rule, "NOT_APPLICABLE", "OK", f"jenis_pengawasan={jp}, tidak butuh sebab")
    bad = [x["id_temuan"] for x in t.get("temuan", []) if not x.get("sebab")]
    if bad:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} temuan audit tanpa sebab: {bad}",
                       "Audit (keyakinan memadai) wajib sebab — analisis akar masalah")
    return _result(rule, "OK", "OK", "Semua temuan audit memiliki sebab")


def check_LAK_006(rule, ctx) -> dict:
    t = ctx["temuan"]
    if not t:
        return _result(rule, "GAP", rule["default_severity"], "_KKP/temuan.json tidak ada", "Jalankan Task 03")
    if t.get("schema_version") != "v4.0.0":
        return _result(rule, "GAP", rule["default_severity"],
                       f"schema_version={t.get('schema_version')!r}, harus 'v4.0.0'", "Update schema_version")
    return _result(rule, "OK", "OK", "schema_version OK; full-validation: scripts/validate_kkp_json.py")


def check_LAK_007(rule, ctx) -> dict:
    files = list((ctx["penugasan"] / "_KKP").glob("KKP-*.docx")) if (ctx["penugasan"] / "_KKP").exists() else []
    if files:
        return _result(rule, "OK", "OK", f"{len(files)} file KKP-*.docx ditemukan")
    return _result(rule, "GAP", rule["default_severity"], "Tidak ada KKP-*.docx",
                   "Generate view per-anggota di Task 03 langkah 6c")


def check_LAK_008(rule, ctx) -> dict:
    log = ctx["audit_trail_events"]
    for evt in log:
        if (evt.get("action") == "GATE_PASSED"
                and evt.get("task") == "03"
                and evt.get("actor", {}).get("role_kode") in ("KT", "PT", "PM")):
            return _result(rule, "OK", "OK", f"Gate KKP disetujui ketua tim: {evt['timestamp']}")
    return _result(rule, "GAP", rule["default_severity"],
                   "Belum ada GATE_PASSED task=03 oleh KT/PT/PM",
                   "Ketua tim harus review & passed gate KKP sebelum LHP (SAIPI 2340)")


def check_LAK_009(rule, ctx) -> dict:
    sa = ctx["sasaran"]
    if not sa: return _result(rule, "NOT_APPLICABLE", "OK", "sasaran-assignment belum ada")
    bad = [s["sasaran_id"] for s in sa.get("sasaran", [])
           if s.get("status") in ("SELESAI_KKP", "DIREVIU_KT", "FINAL")
           and not s.get("id_temuan_terkait")]
    if bad:
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} sasaran SELESAI tanpa id_temuan_terkait: {bad}",
                       "Update id_temuan_terkait, atau kalau memang tidak ada temuan, beri catatan eksplisit")
    return _result(rule, "OK", "OK", "Semua sasaran SELESAI punya id_temuan_terkait (atau status belum)")


# ---- LHP-specific checks ----

def _lhp_text(ctx) -> str:
    if "lhp_text" in ctx:
        return ctx["lhp_text"]
    lhp_dir = ctx["penugasan"] / "_LHP"
    if not lhp_dir.exists():
        ctx["lhp_text"] = ""
        return ""
    docs = list(lhp_dir.glob("LHP*.docx"))
    if not docs:
        ctx["lhp_text"] = ""
        return ""
    # ambil yang terbaru
    docs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    ctx["lhp_text"] = _read_docx(docs[0])
    ctx["lhp_file"] = docs[0].name
    return ctx["lhp_text"]


def _heading_present(text: str, *needles: str) -> bool:
    text_l = text.lower()
    return any(n.lower() in text_l for n in needles)


def check_KOM_001(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    if _heading_present(t, "Tujuan", "Sasaran"):
        return _result(rule, "OK", "OK", "Heading Tujuan/Sasaran ditemukan")
    return _result(rule, "GAP", rule["default_severity"], "Tidak ditemukan heading Tujuan/Sasaran",
                   "LHP wajib memuat tujuan penugasan (SAIPI 2410)")


def check_KOM_002(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    if _heading_present(t, "Ruang Lingkup", "Lingkup"):
        return _result(rule, "OK", "OK", "Heading Ruang Lingkup ditemukan")
    return _result(rule, "GAP", rule["default_severity"], "Tidak ada heading Ruang Lingkup",
                   "LHP wajib memuat ruang lingkup (SAIPI 2410)")


def check_KOM_003(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    if _heading_present(t, "Simpulan", "Kesimpulan"):
        return _result(rule, "OK", "OK", "Heading Simpulan ditemukan")
    return _result(rule, "GAP", rule["default_severity"], "Tidak ada heading Simpulan",
                   "LHP wajib memuat simpulan (SAIPI 2410.A1)")


def check_KOM_004(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    if _heading_present(t, "Rekomendasi", "Saran"):
        return _result(rule, "OK", "OK", "Heading Rekomendasi/Saran ditemukan")
    return _result(rule, "GAP", rule["default_severity"], "Tidak ada heading Rekomendasi",
                   "LHP wajib memuat rekomendasi (SAIPI 2410.A1)")


def check_KOM_005(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    bad = []
    for m in PLACEHOLDER_BAD.finditer(t):
        token = m.group(1)
        if PLACEHOLDER_OK.upper() in token.upper():
            continue
        bad.append(token)
    if bad:
        sample = list(set(bad))[:5]
        return _result(rule, "GAP", rule["default_severity"],
                       f"{len(bad)} placeholder bocor terdeteksi (sample: {sample})",
                       "Ganti semua placeholder kecuali [DIISI AUDITOR]")
    return _result(rule, "OK", "OK", "Tidak ada placeholder bocor")


def check_KOM_006(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    n = len(t.split())
    if 1500 <= n <= 15000:
        return _result(rule, "OK", "OK", f"{n} kata (dalam rentang wajar)")
    return _result(rule, "GAP", rule["default_severity"],
                   f"{n} kata di luar rentang 1500–15000",
                   "Periksa apakah LHP terlalu pendek (kurang detail) atau terlalu panjang (verbose)")


def check_KOM_007(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    if _heading_present(t, "Tanggapan Auditi", "Tanggapan Manajemen", "Tanggapan Klien", "Tanggapan Obyek"):
        return _result(rule, "OK", "OK", "Section Tanggapan ditemukan")
    return _result(rule, "GAP", rule["default_severity"],
                   "Tidak ada section 'Tanggapan Auditi/Manajemen/Klien'",
                   "Mintakan tanggapan ke auditi (SAIPI 2422.A1)")


def check_KOM_008(rule, ctx) -> dict:
    t = _lhp_text(ctx)
    if not t: return _result(rule, "GAP", rule["default_severity"], "LHP belum ada", "Jalankan Task 04")
    pattern = re.compile(r"sesuai\s+dengan\s+Standar\s+Audit\s+Intern\s+Pemerintah\s+Indonesia",
                         re.IGNORECASE)
    if pattern.search(t):
        return _result(rule, "OK", "OK", "Pernyataan kesesuaian SAIPI ditemukan")
    return _result(rule, "GAP", rule["default_severity"],
                   "Pernyataan kesesuaian SAIPI tidak ditemukan",
                   "Tambahkan kalimat: '...dilaksanakan sesuai dengan Standar Audit Intern Pemerintah Indonesia' (SAIPI 2430)")


def check_KOM_009(rule, ctx) -> dict:
    return _result(rule, "NEEDS_REVIEW", "NEEDS_REVIEW",
                   "Tidak dicek otomatis",
                   "Auditor konfirmasi: jika ada koreksi pasca-distribusi, sudah dikomunikasikan ulang? (SAIPI 2421)")


def check_KOM_010(rule, ctx) -> dict:
    return _result(rule, "NEEDS_REVIEW", "NEEDS_REVIEW",
                   "Tidak dicek otomatis (auto-trigger kalau ada KRITIS lain)",
                   "Jika ada gap SAIPI yg tidak terpenuhi, ungkap di LHP (SAIPI 2431)")


def check_IND_002(rule, ctx) -> dict:
    return _result(rule, "NEEDS_REVIEW", "NEEDS_REVIEW",
                   "Tidak dicek otomatis",
                   "Auditor konfirmasi: tim pernah jadi PIC area ini setahun terakhir? (SAIPI 1130.A1)")


def check_KEC_002(rule, ctx) -> dict:
    return _result(rule, "NEEDS_REVIEW", "NEEDS_REVIEW",
                   "Tidak dicek otomatis",
                   "Auditor konfirmasi: jika butuh keahlian khusus, tim memiliki/didampingi? (SAIPI 1210.A1)")


CHECKERS = {
    "IND-001": check_IND_001, "IND-002": check_IND_002,
    "KEC-001": check_KEC_001, "KEC-002": check_KEC_002,
    "REN-001": check_REN_001, "REN-002": check_REN_002, "REN-003": check_REN_003,
    "REN-004": check_REN_004, "REN-005": check_REN_005, "REN-006": check_REN_006,
    "REN-007": check_REN_007,
    "LAK-001": check_LAK_001, "LAK-002": check_LAK_002, "LAK-003": check_LAK_003,
    "LAK-004": check_LAK_004, "LAK-005": check_LAK_005, "LAK-006": check_LAK_006,
    "LAK-007": check_LAK_007, "LAK-008": check_LAK_008, "LAK-009": check_LAK_009,
    "KOM-001": check_KOM_001, "KOM-002": check_KOM_002, "KOM-003": check_KOM_003,
    "KOM-004": check_KOM_004, "KOM-005": check_KOM_005, "KOM-006": check_KOM_006,
    "KOM-007": check_KOM_007, "KOM-008": check_KOM_008, "KOM-009": check_KOM_009,
    "KOM-010": check_KOM_010,
}


def build_context(pen_dir: Path) -> dict:
    return {
        "penugasan": pen_dir,
        "input_dir": pen_dir / "00-input",
        "context_md": _read_text_file(pen_dir / "context.md"),
        "sasaran": _load_json(pen_dir / "_PKP" / "sasaran-assignment.json"),
        "temuan": _load_json(pen_dir / "_KKP" / "temuan.json"),
        "audit_trail_events": _load_jsonl(pen_dir / "_AUDIT-TRAIL" / "events.jsonl"),
    }


def _load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return out


def render_markdown(checklist: list[dict], stage: str, pen_name: str, summary: dict) -> str:
    lines = [
        f"# Laporan QA Kepatuhan SAIPI — Stage {stage.upper()}",
        f"_Penugasan: {pen_name}_  ",
        f"_Generated: {_now_iso()}_  ",
        f"_Sumber: PER-01/AAIPI/DPN/2021_",
        "",
        f"## Ringkasan",
        f"- ✅ OK: **{summary['ok']}**",
        f"- 🔴 KRITIS: **{summary['kritis']}**",
        f"- 🟡 PERINGATAN: **{summary['peringatan']}**",
        f"- 🔵 NEEDS_REVIEW: **{summary['needs_review']}**",
        f"- ◾ NOT_APPLICABLE: **{summary['not_applicable']}**",
        "",
    ]
    if summary["kritis"] > 0:
        lines += [
            "## ⛔ Status: BLOKIR",
            "",
            f"Ada **{summary['kritis']} gap KRITIS** yang harus dikoreksi sebelum berkas penugasan disubmit ke INTEGRAL.",
            "",
        ]
    else:
        lines += [
            "## ✅ Status: PASS (atau ada PERINGATAN/NEEDS_REVIEW yang dapat di-override dengan justifikasi)",
            "",
        ]

    grouped = {}
    for r in checklist:
        grouped.setdefault(r["kelompok"], []).append(r)

    for kel, items in grouped.items():
        lines += [f"## {kel}", ""]
        for r in items:
            icon = {"OK": "✅", "KRITIS": "🔴", "PERINGATAN": "🟡", "NEEDS_REVIEW": "🔵"}.get(r["severity"], "◾")
            lines += [
                f"### {icon} {r['rule_id']} — SAIPI {r['saipi_standar']}",
                f"_{r['deskripsi']}_",
                "",
                f"- **Status**: {r['status']}",
                f"- **Severity**: {r['severity']}",
                f"- **Bukti**: {r['bukti']}",
            ]
            if r.get("gap"):
                lines += [f"- **Gap / Tindak lanjut**: {r['gap']}"]
            lines.append("")

    lines += [
        "---",
        "## Cara Memperbaiki",
        "",
        "1. Untuk gap **KRITIS**: koreksi sumber datanya (mis. tambahkan dokumen_sumber di temuan.json, lengkapi field di context.md, taruh KP/PKP di 00-input/).",
        "2. Untuk **PERINGATAN**: review apakah relevan; jika dianggap sesuai konteks, beri catatan justifikasi di `_QA-SAIPI/justifikasi.md`.",
        "3. Untuk **NEEDS_REVIEW**: konfirmasi manual oleh auditor dengan menambah jawaban di `_QA-SAIPI/jawaban-needs-review.md`.",
        "4. Setelah koreksi, jalankan ulang `python3 scripts/qc_saipi.py --penugasan [path] --stage {stage}`.",
        "",
        "Sumber rujukan lengkap: `skills/kepatuhan-saipi/SKILL.md` & `wiki/raw/SAIPI-PER-01-AAIPI-DPN-2021.pdf`.",
    ]
    return "\n".join(lines)


def _preflight_context(args) -> int:
    """v4.0.4 — Lightweight preflight cek hanya context.md + sasaran-assignment.json.
    Subset rules: REN-003 (Tujuan terisi), REN-005 (Ruang Lingkup terisi),
    REN-001/002 (KP/PKP ada di 00-input/), REN-004 (>=1 sasaran), REN-006/007.
    Tidak menulis checklist.json, tidak log audit-trail. Exit 2 kalau ada KRITIS.
    Dipakai sebelum Task 03 mulai analisis temuan, supaya context.md sudah benar
    sebelum auditor invest waktu reviu temuan."""
    pen_dir = Path(args.penugasan)
    if not pen_dir.exists():
        sys.stderr.write(f"Folder penugasan tidak ditemukan: {pen_dir}\n")
        return 1
    if not CHECKLIST_PATH.exists():
        sys.stderr.write(f"Checklist mapping tidak ditemukan: {CHECKLIST_PATH}\n")
        return 1
    checklist_meta = json.loads(CHECKLIST_PATH.read_text(encoding="utf-8"))
    preflight_rule_ids = {"REN-001", "REN-002", "REN-003", "REN-004", "REN-005", "REN-006", "REN-007"}
    rules = [r for r in checklist_meta["rules"] if r["rule_id"] in preflight_rule_ids]
    ctx = build_context(pen_dir)
    results = []
    for rule in rules:
        checker = CHECKERS.get(rule["rule_id"])
        if checker is None:
            continue
        try:
            results.append(checker(rule, ctx))
        except Exception as e:
            results.append(_result(rule, "GAP", rule["default_severity"],
                                   f"Error checker: {e}", "Investigate"))
    kritis = [r for r in results if r["severity"] == "KRITIS"]
    peringatan = [r for r in results if r["severity"] == "PERINGATAN"]
    ok = [r for r in results if r["severity"] == "OK"]
    print(f"qc_saipi PREFLIGHT (context only): OK={len(ok)} KRITIS={len(kritis)} PERINGATAN={len(peringatan)}")
    if kritis:
        print("\nGap KRITIS yang harus diperbaiki sebelum Task 03:")
        for r in kritis:
            print(f"  - {r['rule_id']} ({r.get('saipi_standar','?')}): {r.get('deskripsi','?')}")
            print(f"    Bukti: {r.get('bukti','-')}")
            if r.get('gap'):
                print(f"    Tindak lanjut: {r['gap']}")
    if peringatan:
        print("\nPERINGATAN (boleh lanjut, tapi sebaiknya diperbaiki):")
        for r in peringatan:
            print(f"  - {r['rule_id']}: {r.get('deskripsi','?')}")
            if r.get('gap'):
                print(f"    Tindak lanjut: {r['gap']}")
    return 2 if kritis else 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--penugasan", required=True, help="Path folder penugasan.")
    ap.add_argument("--stage", required=False, choices=["kkp", "lhp"],
                    help="kkp atau lhp (wajib kecuali --preflight-context)")
    ap.add_argument("--no-audit-trail", action="store_true", help="Skip log ke audit-trail (untuk testing).")
    ap.add_argument(
        "--preflight-context",
        action="store_true",
        help=(
            "v4.0.4 — Mode preflight: hanya jalankan rules yang BISA dievaluasi sebelum "
            "ada temuan/LHP (yaitu rules grup Perencanaan REN-001..REN-007). Output ringkas "
            "ke stdout (tidak menulis checklist .json), exit 2 kalau ada KRITIS. Dipakai "
            "Task 01 untuk early-fix gap context.md sebelum analisis Task 03."
        ),
    )
    args = ap.parse_args()

    if args.preflight_context:
        return _preflight_context(args)
    if not args.stage:
        sys.stderr.write("--stage wajib (kkp|lhp) kecuali bersama --preflight-context\n")
        return 1

    pen_dir = Path(args.penugasan)
    if not pen_dir.exists():
        sys.stderr.write(f"Folder penugasan tidak ditemukan: {pen_dir}\n")
        return 1

    if not CHECKLIST_PATH.exists():
        sys.stderr.write(f"Checklist mapping tidak ditemukan: {CHECKLIST_PATH}\n")
        return 1
    checklist_meta = json.loads(CHECKLIST_PATH.read_text(encoding="utf-8"))

    rules_for_stage = [r for r in checklist_meta["rules"] if args.stage in r.get("stages", [])]

    ctx = build_context(pen_dir)
    results = []
    for rule in rules_for_stage:
        checker = CHECKERS.get(rule["rule_id"])
        if checker is None:
            results.append(_result(rule, "NOT_APPLICABLE", "OK", "(checker belum diimplementasikan)"))
            continue
        try:
            results.append(checker(rule, ctx))
        except Exception as e:
            results.append(_result(rule, "GAP", rule["default_severity"],
                                   f"Error eksekusi checker: {e}",
                                   "Laporkan ke pemelihara skill kepatuhan-saipi"))

    summary = {
        "ok": sum(1 for r in results if r["severity"] == "OK"),
        "kritis": sum(1 for r in results if r["severity"] == "KRITIS"),
        "peringatan": sum(1 for r in results if r["severity"] == "PERINGATAN"),
        "needs_review": sum(1 for r in results if r["severity"] == "NEEDS_REVIEW"),
        "not_applicable": sum(1 for r in results if r["status"] == "NOT_APPLICABLE"),
    }

    out_dir = pen_dir / "_QA-SAIPI"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / f"checklist-{args.stage}.json"
    md_path = out_dir / f"laporan-qa-{args.stage}.md"

    payload = {
        "stage": args.stage,
        "penugasan": pen_dir.name,
        "generated_at": _now_iso(),
        "schema_version": "v4.0.0",
        "sumber": "PER-01/AAIPI/DPN/2021",
        "summary": summary,
        "checklist": results,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md = render_markdown(results, args.stage, pen_dir.name, summary)
    md_path.write_text(md, encoding="utf-8")

    if not args.no_audit_trail:
        action = "VALIDATION_FAILED" if summary["kritis"] > 0 else "VALIDATION_PASSED"
        log_event(
            pen_dir,
            action=action,
            target=str(json_path.relative_to(pen_dir)),
            payload={"stage": args.stage, **summary, "rule_set": "SAIPI per-penugasan"},
            task=("03" if args.stage == "kkp" else "04"),
        )

    print(f"qc_saipi stage={args.stage}: OK={summary['ok']} KRITIS={summary['kritis']} "
          f"PERINGATAN={summary['peringatan']} NEEDS_REVIEW={summary['needs_review']} "
          f"NOT_APPLICABLE={summary['not_applicable']}")
    print(f"  -> {json_path}")
    print(f"  -> {md_path}")

    return 2 if summary["kritis"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
