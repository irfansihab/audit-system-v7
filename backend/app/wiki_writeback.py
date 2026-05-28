"""W3 — tulis-balik penugasan selesai (LHP_DONE) ke vault llm-wiki.

Saat sebuah penugasan tutup (LHP terbit), kita rangkum jadi satu catatan Karpathy-
style di vault organisasi, supaya pengetahuan operasional (siapa diaudit, ditemukan
apa, dasar hukum mana) terakumulasi dan bisa di-cite agen pada penugasan berikutnya
(via search_wiki / get_wiki_page yang sudah ada di W1).

Alur:
  1. Auditor (PT/PM/KT) klik "Generate" di tab Knowledge untuk penugasan LHP_DONE.
  2. Modul ini baca DB (Penugasan) + file `_KKP/temuan.json` + `_LHP/rekomendasi.json`,
     bangun draft `pengawasan-{kode}.md` + delta untuk `index.md` & `log.md`. Simpan
     sebagai baris `WikiProposal(status=DRAFT)`.
  3. Auditor (PT/PM) review preview di UI. Dua pilihan apply:
       - **Opsi A (rekomendasi):** "Download .md" → di-paste manual ke vault Obsidian
         supaya curate flow auditor tetap utuh. Status proposal → REVIEWED (opsional).
       - **Opsi B:** "Apply ke vault" → modul ini tulis file + append index/log ke
         folder `<APP_VAULT_PATH>/wiki/`. Status → APPLIED.

V6 read-only — kita tidak menyentuh `backend/v6/`. Generator deterministik; tidak
ada panggilan LLM (data sudah tersedia, kita rapikan). Anti-duplikat: 1 proposal
per penugasan (regenerate mengganti row); apply idempoten (cek file & baris index
sudah ada → skip).
"""
from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(text: str) -> str:
    """Slug aman untuk nama file & wikilink ([[ ... ]])."""
    s = _SLUG_RE.sub("-", (text or "").lower()).strip("-")
    return s or "untitled"


def _safe_read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _stringify_skill(skill: Any) -> str:
    """Skill bisa enum, string, atau None — kembalikan string."""
    if skill is None:
        return ""
    if isinstance(skill, str):
        return skill
    return getattr(skill, "value", str(skill))


def _humanize_skill(skill_value: str) -> str:
    """`reviu-rka-kl` → `Reviu RKA-K/L`. Best-effort, tidak fatal kalau gagal."""
    if not skill_value:
        return ""
    parts = skill_value.split("-")
    out: list[str] = []
    for p in parts:
        if p == "rka":
            out.append("RKA")
        elif p == "kl":
            out.append("K/L")
        elif p in ("ai", "saipi", "spip", "sakip", "rb", "tor", "rab", "kkp", "lhp"):
            out.append(p.upper())
        else:
            out.append(p.capitalize())
    label = " ".join(out)
    # Pola idiomatik di Komdigi: "RKA-K/L" (hyphen), bukan "RKA K/L".
    label = label.replace("RKA K/L", "RKA-K/L")
    return label


def _format_tanggal(value: str | None) -> str:
    """Toleran terhadap '2026-05-22' / '2026-05-22T..Z' / None."""
    if not value:
        return ""
    v = str(value).strip()
    if not v:
        return ""
    # Ambil 10 char depan kalau ISO datetime
    return v[:10]


# ---------------------------------------------------------------------------
# Build proposal (deterministik)
# ---------------------------------------------------------------------------

def _severity_label(jumlah: int) -> str:
    if jumlah == 0:
        return "tanpa temuan"
    if jumlah == 1:
        return "1 temuan"
    return f"{jumlah} temuan"


def _related_wikilinks(skill_value: str) -> list[str]:
    """Tautan "Lihat juga" minimal: pelaksana + kategori skill (best-effort)."""
    out: list[str] = ["[[inspektorat-ii]]"]
    if skill_value:
        # Untuk skill seperti `audit-kinerja`, taut langsung ke kategori induk
        # bila terdapat halaman vault dgn nama itu — agen biarkan menambah
        # tautan lain. Cukup deterministik & non-fatal.
        out.append(f"[[{slugify(skill_value)}]]")
    return out


def build_proposal(
    *,
    penugasan: dict,
    temuan: dict | None,
    rekomendasi_map: dict | None,
    ketua_tim_nama: str | None = None,
    lhp_filename: str | None = None,
) -> dict:
    """Bangun draft catatan vault dari data penugasan selesai.

    Argumen `penugasan` cukup berupa dict (bukan ORM) untuk memudahkan test:
        {kode, obyek, skill, nomor_st, tanggal_st, created_at (datetime|str)}

    Return dict siap pakai untuk dimasukkan ke `WikiProposal`:
        {nama_file, konten_md, delta_index, delta_log, ringkasan}
    """
    kode = str(penugasan.get("kode") or "").strip()
    obyek = str(penugasan.get("obyek") or "").strip() or "(obyek tidak tercatat)"
    skill_value = _stringify_skill(penugasan.get("skill"))
    skill_label = _humanize_skill(skill_value)
    nomor_st = str(penugasan.get("nomor_st") or "").strip()
    tanggal_st = _format_tanggal(penugasan.get("tanggal_st"))
    created_at = penugasan.get("created_at")
    if isinstance(created_at, datetime):
        tahun = created_at.year
        tanggal_buat = created_at.date().isoformat()
    elif isinstance(created_at, str) and created_at:
        tanggal_buat = created_at[:10]
        tahun = int(tanggal_buat[:4]) if tanggal_buat[:4].isdigit() else date.today().year
    else:
        tanggal_buat = date.today().isoformat()
        tahun = date.today().year

    nama_file = f"pengawasan-{slugify(kode)}.md"
    nama_slug = nama_file[:-3]  # tanpa .md, dipakai [[wikilink]]

    temuan_list = list((temuan or {}).get("temuan") or [])
    n_temuan = len(temuan_list)
    rekomendasi_map = dict(rekomendasi_map or {})

    # Sumber dokumen unik (untuk Sources line)
    sumber_files: list[str] = []
    seen = set()
    for t in temuan_list:
        for ds in t.get("dokumen_sumber") or []:
            f = str(ds.get("file") or "").strip()
            if f and f not in seen:
                seen.add(f)
                sumber_files.append(f)

    # ------------- HEAD: Summary + Sources + Last updated -------------
    summary = (
        f"Penugasan {skill_label or skill_value} atas {obyek} oleh [[inspektorat-ii]] "
        f"(ST {nomor_st or '—'}{', ' + tanggal_st if tanggal_st else ''}). "
        f"Status: LHP_DONE; {_severity_label(n_temuan)}."
    )

    sources_parts: list[str] = []
    if nomor_st:
        sources_parts.append(f"Surat Tugas {nomor_st}{(' tanggal ' + tanggal_st) if tanggal_st else ''}")
    if lhp_filename:
        sources_parts.append(f"LHP: {lhp_filename}")
    sources_parts.append(f"KKP `_KKP/temuan.json` ({n_temuan} temuan)")
    sources_line = "; ".join(sources_parts)

    last_updated = date.today().isoformat()

    lines: list[str] = [
        f"# Penugasan: {obyek}",
        "",
        f"**Summary**: {summary}",
        "",
        f"**Sources**: {sources_line}",
        "",
        f"**Last updated**: {last_updated} (auto-generated W3 wiki write-back)",
        "",
        "---",
        "",
        "## Identitas Penugasan",
        "",
        "| Field | Nilai |",
        "|---|---|",
        f"| Kode | `{kode}` |",
        f"| Jenis pengawasan | {skill_label or skill_value or '—'} |",
        f"| Obyek | {obyek} |",
        f"| Nomor ST | {nomor_st or '—'} |",
        f"| Tanggal ST | {tanggal_st or '—'} |",
        f"| Ketua Tim | {ketua_tim_nama or '—'} |",
        f"| Status | LHP_DONE |",
        f"| Tanggal mulai | {tanggal_buat} |",
        "",
    ]

    # ------------- Temuan & Rekomendasi -------------
    if n_temuan:
        lines.extend(["## Temuan & Rekomendasi", ""])
        for t in temuan_list:
            tid = str(t.get("id_temuan") or "").strip() or "(no-id)"
            judul = str(t.get("judul_temuan") or "").strip() or "(tanpa judul)"
            kondisi = str(t.get("kondisi") or "").strip()
            kriteria = str(t.get("kriteria") or "").strip()
            akibat = str(t.get("akibat") or "").strip()
            anggota = str(((t.get("anggota_tim") or {}).get("nama_lengkap")) or "").strip()
            rekom = str(rekomendasi_map.get(tid) or "").strip()

            lines.append(f"### {tid} — {judul}")
            lines.append("")
            if kondisi:
                lines.append(f"**Kondisi.** {kondisi}")
                lines.append("")
            if kriteria:
                lines.append(f"**Kriteria.** {kriteria}")
                lines.append("")
            if akibat:
                lines.append(f"**Akibat.** {akibat}")
                lines.append("")
            if rekom:
                lines.append(f"**Rekomendasi.** {rekom}")
                lines.append("")
            srcs = t.get("dokumen_sumber") or []
            if srcs:
                lines.append("**Sumber bukti**:")
                for ds in srcs:
                    f = str(ds.get("file") or "").strip()
                    h = ds.get("halaman")
                    if not f:
                        continue
                    if h is not None and str(h).strip():
                        lines.append(f"- {f}, hal. {h}")
                    else:
                        lines.append(f"- {f}")
                lines.append("")
            if anggota:
                lines.append(f"*(Anggota tim: {anggota})*")
                lines.append("")
    else:
        lines.extend([
            "## Temuan & Rekomendasi",
            "",
            "_Tidak ada temuan tercatat pada `_KKP/temuan.json` saat catatan ini dibuat._",
            "",
        ])

    # ------------- Lihat juga -------------
    lines.append("## Lihat juga")
    lines.append("")
    for link in _related_wikilinks(skill_value):
        lines.append(f"- {link}")
    lines.append("")

    konten_md = "\n".join(lines)

    # ------------- Delta index.md & log.md -------------
    obyek_short = obyek if len(obyek) <= 120 else obyek[:117] + "..."
    delta_index = f"- [[{nama_slug}]] — {obyek_short} ({skill_label or skill_value}, LHP_DONE)"

    log_block_lines = [
        f"## {last_updated} — {kode} ({skill_label or skill_value}) — LHP_DONE",
        "",
        f"Penugasan {skill_label or skill_value} atas **{obyek}** selesai (LHP terbit). "
        f"{_severity_label(n_temuan).capitalize()}.",
        "",
        f"Catatan: [[{nama_slug}]]",
        "",
    ]
    delta_log = "\n".join(log_block_lines)

    ringkasan = (
        f"{skill_label or skill_value} · {n_temuan} temuan · ST {nomor_st or '—'} · "
        f"file {nama_file}"
    )

    return {
        "nama_file": nama_file,
        "nama_slug": nama_slug,
        "konten_md": konten_md,
        "delta_index": delta_index,
        "delta_log": delta_log,
        "ringkasan": ringkasan,
        "jumlah_temuan": n_temuan,
        "sumber_files": sumber_files,
    }


# ---------------------------------------------------------------------------
# Build dari folder penugasan (helper untuk route)
# ---------------------------------------------------------------------------

def build_proposal_from_folder(
    *,
    penugasan_dict: dict,
    folder: Path,
    ketua_tim_nama: str | None = None,
) -> dict:
    """Convenience: cari file _KKP/temuan.json + _LHP/rekomendasi.json + LHP-*.docx
    di `folder`, lalu panggil `build_proposal`."""
    temuan = _safe_read_json(folder / "_KKP" / "temuan.json")
    rekom = _safe_read_json(folder / "_LHP" / "rekomendasi.json")
    rekomendasi_map = rekom if isinstance(rekom, dict) else {}

    lhp_filename: str | None = None
    lhp_dir = folder / "_LHP"
    if lhp_dir.is_dir():
        for ext in ("*.docx", "*.pdf"):
            for p in sorted(lhp_dir.glob(ext)):
                if p.name.lower().startswith(("lhp", "lhr")):
                    lhp_filename = p.name
                    break
            if lhp_filename:
                break

    return build_proposal(
        penugasan=penugasan_dict,
        temuan=temuan,
        rekomendasi_map=rekomendasi_map,
        ketua_tim_nama=ketua_tim_nama,
        lhp_filename=lhp_filename,
    )


# ---------------------------------------------------------------------------
# Apply ke vault (opsi B)
# ---------------------------------------------------------------------------

class WikiWriteBackError(Exception):
    """Error apply ke vault — diumpan ke HTTP 400."""


def _ensure_under(parent: Path, child: Path) -> Path:
    """Path traversal guard: child harus berada di dalam parent."""
    parent_r = parent.resolve()
    try:
        child_r = (parent / child).resolve() if not child.is_absolute() else child.resolve()
    except Exception as exc:
        raise WikiWriteBackError(f"path invalid: {exc}") from exc
    try:
        child_r.relative_to(parent_r)
    except ValueError as exc:
        raise WikiWriteBackError("path keluar dari vault tidak diizinkan") from exc
    return child_r


def _append_index_line(index_path: Path, baris: str) -> tuple[bool, str]:
    """Sisip 1 baris ke `index.md` dgn anti-duplikat sederhana.

    Strategi: bila berkas memuat sub-section `## Penugasan / Audit`, tempel baris di
    BAWAH heading itu (sebelum sub-section berikutnya). Bila tidak, append ke akhir
    file (bersama heading baru). Return (changed, alasan).
    """
    if not index_path.exists():
        # Bikin baru dengan struktur minimal
        index_path.write_text(
            "# Wiki Index\n\n## Penugasan / Audit\n\n" + baris + "\n",
            encoding="utf-8",
        )
        return True, "index.md dibuat baru"

    text = index_path.read_text(encoding="utf-8")
    if baris.strip() and baris.strip() in text:
        return False, "baris sudah ada di index.md (idempoten)"

    heading = "## Penugasan / Audit"
    if heading in text:
        # Sisip tepat setelah heading (atau setelah blank line pertama setelah heading)
        idx = text.index(heading)
        # Cari posisi end-of-section (heading H2 berikutnya atau EOF)
        after_heading = text[idx + len(heading) :]
        m = re.search(r"\n##\s", after_heading)
        if m:
            insert_pos = idx + len(heading) + m.start()
        else:
            insert_pos = len(text)
        # Tambah newline jika perlu
        prefix = text[:insert_pos]
        suffix = text[insert_pos:]
        if not prefix.endswith("\n"):
            prefix += "\n"
        new_text = prefix + baris + "\n" + suffix
    else:
        new_text = text.rstrip() + "\n\n## Penugasan / Audit\n\n" + baris + "\n"

    index_path.write_text(new_text, encoding="utf-8")
    return True, "baris ditambah di index.md"


def _prepend_log_block(log_path: Path, blok: str) -> tuple[bool, str]:
    """Tempel blok kronologis di ATAS log.md (paling baru di atas), anti-dup."""
    blok = blok.rstrip() + "\n"
    header = "# Wiki Log\n\nCatatan kronologis perubahan wiki.\n\n"
    if not log_path.exists():
        log_path.write_text(header + blok, encoding="utf-8")
        return True, "log.md dibuat baru"

    text = log_path.read_text(encoding="utf-8")
    first_line = blok.splitlines()[0].strip() if blok.strip() else ""
    if first_line and first_line in text:
        return False, "blok log sudah ada (idempoten)"

    if text.startswith("# Wiki Log"):
        # Sisip setelah preamble (cari heading H2 pertama, sisipkan tepat sebelumnya)
        m = re.search(r"\n##\s", text)
        if m:
            insert_pos = m.start() + 1  # tepat di awal baris H2 berikutnya
            new_text = text[:insert_pos] + blok + "\n" + text[insert_pos:]
        else:
            new_text = text.rstrip() + "\n\n" + blok
    else:
        new_text = header + blok + "\n" + text

    log_path.write_text(new_text, encoding="utf-8")
    return True, "blok log ditambah"


def apply_to_vault(
    *,
    vault_root: Path,
    nama_file: str,
    konten_md: str,
    delta_index: str,
    delta_log: str,
) -> dict:
    """Tulis file pengawasan-*.md + sisip delta index/log di `<vault>/wiki/`.

    Idempoten: rewrite file pengawasan (overwrite), tapi index/log skip kalau baris
    sudah ada.
    """
    notes_dir = vault_root / "wiki"
    if not notes_dir.exists() or not notes_dir.is_dir():
        raise WikiWriteBackError(
            f"folder vault tidak ditemukan: {notes_dir} — set APP_VAULT_PATH dgn benar"
        )

    # Path traversal guard
    target_md = _ensure_under(notes_dir, Path(nama_file))
    target_md.write_text(konten_md, encoding="utf-8")

    index_changed, index_reason = _append_index_line(notes_dir / "index.md", delta_index)
    log_changed, log_reason = _prepend_log_block(notes_dir / "log.md", delta_log)

    return {
        "ok": True,
        "path": str(target_md),
        "index": {"changed": index_changed, "reason": index_reason},
        "log": {"changed": log_changed, "reason": log_reason},
    }
