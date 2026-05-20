"""
run_batch.py — Orchestrator end-to-end Reviu RKA-K/L (multi-RO).

Menggabungkan 4 fase:
    1. Auto-pair TOR-RAB dari folder penugasan (regex + tie-break tanggal terbaru)
    2. Parallel pipeline per-RO: digest_tor + digest_rab + cross_check (single)
    3. Cross-RO check (batch mode) → anomalies-master.json
    4. Render LHR (multi-RO docx) — opsional via --no-render

Usage:
    python3 run_batch.py \
        --penugasan PATH_FOLDER_PENUGASAN \
        [--tor-dir SUBPATH] [--rab-dir SUBPATH] \
        [--workers N] \
        [--no-render] [--no-raw] \
        [--judul "..."] [--nomor "..."] [--tanggal "..."] [--penerima "..."]

Default:
    --tor-dir : input/objek/TOR (relatif terhadap --penugasan)
    --rab-dir : input/objek/RAB
    --workers : 4
    Output    : <penugasan>/_KKP/  dan  <penugasan>/_LHP/

Backward-compat: jika `input/objek/TOR-RAB` tidak ada, fallback flat
(cari TOR + RAB di akar --penugasan).
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures as cf
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# --------- konfigurasi --------- #

SCRIPT_DIR = Path(__file__).resolve().parent
DIGEST_TOR = SCRIPT_DIR / "digest_tor.py"
DIGEST_RAB = SCRIPT_DIR / "digest_rab.py"
CROSS_CHECK = SCRIPT_DIR / "cross_check.py"
RENDER_LHR = SCRIPT_DIR / "render_lhr.py"

# Regex match nama file: ^[<RO>]<spasi><YYYYMMDD?><...>.pdf
# Group: 1=RO, 2=YYYY, 3=MM, 4=DD (opsional → None bila tak ada)
RE_DATED = re.compile(r"^\[(\d+)\].*?(\d{4})(\d{2})(\d{2}).*\.pdf$", re.IGNORECASE)
RE_NODATE = re.compile(r"^\[(\d+)\].*\.pdf$", re.IGNORECASE)


# --------- AST self-check --------- #

def _self_check_ast() -> None:
    try:
        ast.parse(Path(__file__).read_text(encoding="utf-8"))
    except SyntaxError as e:
        print(f"[FATAL] Self-check AST gagal di {__file__}: {e}", file=sys.stderr)
        sys.exit(2)


def _detect_role(penugasan: Path) -> str:
    """Auto-detect role dari _ROLE.md. Default 'AT' jika tidak ada."""
    role_file = penugasan / "_ROLE.md"
    if not role_file.exists():
        return "AT"  # default to Anggota Tim
    try:
        txt = role_file.read_text(encoding="utf-8")
        import re as _re
        m = _re.search(r"^role_kode:\s*(\S+)", txt, _re.MULTILINE)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return "AT"


def _should_render_lhp(role: str) -> bool:
    """Hanya KT/PT/PM yang generate LHP. AT skip (KKP only)."""
    return role.upper() in ("KT", "PT", "PM")



def _preflight_scripts() -> None:
    """Pre-flight: AST parse dependent scripts."""
    fails: list[str] = []
    for f in (DIGEST_TOR, DIGEST_RAB, CROSS_CHECK, RENDER_LHR):
        if not f.exists():
            fails.append(f"  MISSING: {f}")
            continue
        try:
            ast.parse(f.read_text(encoding="utf-8"))
        except SyntaxError as e:
            fails.append(f"  SYNTAX ERROR: {f.name} -> {e}")
    if fails:
        print("[FATAL] Pre-flight script integrity check gagal:", file=sys.stderr)
        for line in fails:
            print(line, file=sys.stderr)
        print("\nPerbaiki script di atas sebelum menjalankan run_batch.", file=sys.stderr)
        sys.exit(3)


# --------- Phase 1: auto-pair --------- #

@dataclass
class Pair:
    ro_id: int
    tor_path: Path
    rab_path: Path


def _scan_dir(d: Path) -> dict[int, Path]:
    """Scan direktori -> {ro_id: best_path}.

    Aturan:
        - skip file 'Lampiran*' (case-insensitive)
        - skip file di subfolder Backup/
        - jika >1 file untuk RO sama -> pilih tanggal terbaru
          (file tanpa tanggal kalah dari yang ada tanggal,
           kecuali tidak ada kandidat lain)
    """
    candidates: dict[int, list[tuple[Path, str | None]]] = {}
    if not d.exists():
        return {}
    for p in d.iterdir():
        if not p.is_file():
            continue
        name = p.name
        if not name.lower().endswith(".pdf"):
            continue
        if name.lower().startswith("lampiran"):
            continue
        # Skip jika part dari path mengandung 'Backup' (case-insens)
        if any(part.lower() == "backup" for part in p.parts):
            continue
        m = RE_DATED.match(name)
        if m:
            ro_id = int(m.group(1))
            ymd = m.group(2) + m.group(3) + m.group(4)
            candidates.setdefault(ro_id, []).append((p, ymd))
            continue
        m2 = RE_NODATE.match(name)
        if m2:
            ro_id = int(m2.group(1))
            candidates.setdefault(ro_id, []).append((p, None))
    out: dict[int, Path] = {}
    for ro_id, lst in candidates.items():
        # urutkan: yang ada tanggal lebih tinggi prioritasnya, terbaru menang
        with_date = [(p, d) for (p, d) in lst if d is not None]
        without_date = [(p, d) for (p, d) in lst if d is None]
        if with_date:
            with_date.sort(key=lambda x: x[1], reverse=True)
            out[ro_id] = with_date[0][0]
        elif without_date:
            out[ro_id] = without_date[0][0]
    return out


def auto_pair(tor_dir: Path, rab_dir: Path) -> tuple[list[Pair], list[str]]:
    """Pasangkan TOR-RAB by ro_id. Kembalikan (pairs, warnings)."""
    tors = _scan_dir(tor_dir)
    rabs = _scan_dir(rab_dir)
    warnings: list[str] = []
    common = sorted(set(tors.keys()) & set(rabs.keys()))
    only_tor = sorted(set(tors.keys()) - set(rabs.keys()))
    only_rab = sorted(set(rabs.keys()) - set(tors.keys()))
    for r in only_tor:
        warnings.append(f"RO #{r}: TOR ada tetapi RAB tidak ditemukan - skip.")
    for r in only_rab:
        warnings.append(f"RO #{r}: RAB ada tetapi TOR tidak ditemukan - skip.")
    pairs = [Pair(ro_id=r, tor_path=tors[r], rab_path=rabs[r]) for r in common]
    return pairs, warnings


# --------- Phase 2: per-RO worker (subprocess isolated) --------- #

def process_one_ro(args_tuple: tuple) -> dict[str, Any]:
    """Worker per-RO: digest TOR + RAB + cross_check single.

    args_tuple: (ro_id, tor_path, rab_path, kkp_dir, no_raw)
    """
    ro_id, tor_path, rab_path, kkp_dir, no_raw = args_tuple
    kkp_dir = Path(kkp_dir)
    tor_path = Path(tor_path)
    rab_path = Path(rab_path)
    tor_json = kkp_dir / f"tor-{ro_id}.json"
    rab_json = kkp_dir / f"rab-{ro_id}.json"
    anom_json = kkp_dir / f"anomalies-{ro_id}.json"
    t0 = time.time()
    errors: list[str] = []
    py = sys.executable or "python3"

    def _run(cmd: list[str], tag: str) -> bool:
        try:
            r = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=120,
            )
            if r.returncode != 0:
                errors.append(
                    f"{tag} rc={r.returncode}: "
                    f"{(r.stderr or r.stdout or '').strip()[:500]}"
                )
                return False
            return True
        except subprocess.TimeoutExpired:
            errors.append(f"{tag} timeout >120s")
            return False
        except Exception as e:  # noqa: BLE001
            errors.append(f"{tag} exception: {e}")
            return False

    # 1) digest TOR
    cmd_tor = [py, str(DIGEST_TOR), str(tor_path), "-o", str(tor_json)]
    if no_raw:
        cmd_tor.append("--no-raw")
    ok_tor = _run(cmd_tor, "digest_tor")

    # 2) digest RAB
    cmd_rab = [py, str(DIGEST_RAB), str(rab_path), "-o", str(rab_json)]
    if no_raw:
        cmd_rab.append("--no-raw")
    ok_rab = _run(cmd_rab, "digest_rab")

    # 3) cross_check single (hanya jika kedua digest sukses)
    n_anom = 0
    ok_cc = False
    if ok_tor and ok_rab:
        cmd_cc = [
            py,
            str(CROSS_CHECK),
            str(tor_json),
            str(rab_json),
            "-o",
            str(anom_json),
        ]
        ok_cc = _run(cmd_cc, "cross_check")
        if ok_cc and anom_json.exists():
            try:
                data = json.loads(anom_json.read_text(encoding="utf-8"))
                n_anom = len(data.get("anomalies", []))
            except Exception as e:  # noqa: BLE001
                errors.append(f"parse anomalies-{ro_id}.json: {e}")

    duration = time.time() - t0
    status = "ok" if (ok_tor and ok_rab and ok_cc) else "error"
    return {
        "ro_id": ro_id,
        "status": status,
        "duration": duration,
        "tor": str(tor_path),
        "rab": str(rab_path),
        "tor_json": str(tor_json) if ok_tor else None,
        "rab_json": str(rab_json) if ok_rab else None,
        "anomalies_json": str(anom_json) if ok_cc else None,
        "n_anomalies_single": n_anom,
        "errors": errors,
    }


# --------- helpers untuk derive nama RO dari nama file --------- #

_RE_FNAME_LABEL = re.compile(
    r"^\[\d+\]\s*(?:\d{8}\s+)?(?:TOR|RAB)\s*(?:[A-Z]{2,4}\s+)?"
    r"(.*?)\s*(?:2026|2027|_tte|\.pdf)",
    re.IGNORECASE,
)


def _label_from_filename(p: Path) -> str:
    name = p.stem
    m = _RE_FNAME_LABEL.match(name)
    if m:
        lbl = m.group(1).strip(" -_")
        # bersihkan token tambahan
        lbl = re.sub(r"\s+", " ", lbl)
        if lbl:
            return lbl
    return name


# --------- Phase 3: cross-RO batch --------- #

def cross_check_batch(kkp_dir: Path) -> tuple[Path, dict[str, Any]]:
    py = sys.executable or "python3"
    out_path = kkp_dir / "anomalies-master.json"
    cmd = [
        py,
        str(CROSS_CHECK),
        "--batch",
        "--tor-dir",
        str(kkp_dir),
        "--rab-dir",
        str(kkp_dir),
        "-o",
        str(out_path),
    ]
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    info: dict[str, Any] = {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    if r.returncode != 0:
        return out_path, info
    try:
        data = json.loads(out_path.read_text(encoding="utf-8"))
        ring = data.get("ringkasan", {})
        info["total_ro"] = ring.get("total_ro")
        info["total_anomali"] = ring.get("total_anomali")
        info["per_severity"] = ring.get("per_severity", {})
        info["per_aspek"] = ring.get("per_aspek", {})
    except Exception as e:  # noqa: BLE001
        info["parse_error"] = str(e)
    return out_path, info


# --------- Phase 4: render LHR --------- #

def render_lhr(
    kkp_dir: Path,
    lhp_dir: Path,
    judul: str | None,
    nomor: str | None,
    tanggal: str | None,
    penerima: str | None,
) -> tuple[Path, dict[str, Any]]:
    py = sys.executable or "python3"
    lhp_dir.mkdir(parents=True, exist_ok=True)
    out_docx = lhp_dir / "LHR-DRAFT.docx"
    anom_master = kkp_dir / "anomalies-master.json"
    kp_md = kkp_dir / "01-KP-Reviu.md"
    cmd = [py, str(RENDER_LHR), str(anom_master)]
    if kp_md.exists():
        cmd.append(str(kp_md))
    cmd += [
        "--tor-dir",
        str(kkp_dir),
        "--rab-dir",
        str(kkp_dir),
        "-o",
        str(out_docx),
    ]
    for flag, val in (
        ("--judul", judul),
        ("--nomor", nomor),
        ("--tanggal", tanggal),
        ("--penerima", penerima),
    ):
        if val:
            cmd += [flag, val]
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    info = {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    return out_docx, info


# --------- main --------- #

def _resolve_dirs(penugasan: Path, tor_sub: str | None, rab_sub: str | None) -> tuple[Path, Path]:
    """Resolve direktori TOR & RAB dengan fallback flat structure."""
    if tor_sub:
        td = penugasan / tor_sub
    else:
        td = penugasan / "input" / "objek" / "TOR"
    if rab_sub:
        rd = penugasan / rab_sub
    else:
        rd = penugasan / "input" / "objek" / "RAB"
    if td.exists() and rd.exists():
        return td, rd
    # fallback flat: TOR & RAB langsung di --penugasan
    if not td.exists() or not rd.exists():
        if penugasan.exists():
            return penugasan, penugasan
    return td, rd


def main(argv: list[str] | None = None) -> int:
    _self_check_ast()
    _preflight_scripts()

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--penugasan", required=True, help="Path folder penugasan")
    ap.add_argument(
        "--tor-dir",
        default=None,
        help="Subpath TOR relatif --penugasan (default input/objek/TOR)",
    )
    ap.add_argument(
        "--rab-dir",
        default=None,
        help="Subpath RAB relatif --penugasan (default input/objek/RAB)",
    )
    ap.add_argument("--workers", type=int, default=4, help="Jumlah worker (default 4)")
    ap.add_argument("--no-render", action="store_true", help="Skip render LHR")
    ap.add_argument(
        "--no-raw",
        action="store_true",
        help="Pass --no-raw ke digest_tor/digest_rab (hemat storage)",
    )
    ap.add_argument("--judul", default=None)
    ap.add_argument("--nomor", default=None)
    ap.add_argument("--tanggal", default=None)
    ap.add_argument("--penerima", default=None)
    ap.add_argument("--role", default=None, choices=["AT", "KT", "PT", "PM"],
                    help="Role auditor: AT=Anggota Tim (KKP only), KT/PT/PM=Ketua Tim/Pengendali (LHP). "
                         "Default: auto-detect dari _ROLE.md, fallback AT.")

    args = ap.parse_args(argv)

    penugasan = Path(args.penugasan).resolve()
    if not penugasan.exists():
        print(f"[FATAL] Folder penugasan tidak ditemukan: {penugasan}", file=sys.stderr)
        return 4

    tor_dir, rab_dir = _resolve_dirs(penugasan, args.tor_dir, args.rab_dir)
    kkp_dir = penugasan / "_KKP"
    lhp_dir = penugasan / "_LHP"
    kkp_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("RUN BATCH - Reviu RKA-K/L")
    print("=" * 72)
    print(f"  Penugasan : {penugasan}")
    print(f"  TOR dir   : {tor_dir}")
    print(f"  RAB dir   : {rab_dir}")
    print(f"  KKP dir   : {kkp_dir}")
    print(f"  Workers   : {args.workers}")
    print(f"  Render    : {'OFF (--no-render)' if args.no_render else 'ON'}")
    print()
    # ---------- Role-based gating ----------
    role = (args.role or _detect_role(penugasan)).upper()
    print(f"  Role      : {role} ({'KKP only (skip LHP)' if not _should_render_lhp(role) else 'Full pipeline (render LHP)'})")


    # ---------- Phase 1 ---------- #
    print("[Phase 1] Auto-pair TOR-RAB ...")
    t_phase1 = time.time()
    pairs, warns = auto_pair(tor_dir, rab_dir)
    for w in warns:
        print(f"  ! {w}")
    if not pairs:
        print("[FATAL] Tidak ada pasangan TOR-RAB ditemukan.", file=sys.stderr)
        return 5
    pairs.sort(key=lambda p: p.ro_id)
    print(f"  Detected {len(pairs)} pasangan:")
    for p in pairs:
        print(f"    RO #{p.ro_id:>2}: TOR={p.tor_path.name}")
        print(f"            RAB={p.rab_path.name}")
    print(f"  ({time.time()-t_phase1:.2f}s)")
    print()

    # ---------- Phase 2 ---------- #
    n_workers = max(1, min(args.workers, len(pairs)))
    print(f"[Phase 2] Parallel pipeline (digest + single cross-check) - workers={n_workers} ...")
    t_phase2 = time.time()
    job_args = [
        (p.ro_id, str(p.tor_path), str(p.rab_path), str(kkp_dir), args.no_raw)
        for p in pairs
    ]
    results: list[dict[str, Any]] = []
    name_lookup = {p.ro_id: _label_from_filename(p.tor_path) for p in pairs}
    completed = 0
    total = len(pairs)
    # ProcessPoolExecutor untuk isolasi crash
    with cf.ProcessPoolExecutor(max_workers=n_workers) as ex:
        future_map = {ex.submit(process_one_ro, ja): ja[0] for ja in job_args}
        for fut in cf.as_completed(future_map):
            ro_id = future_map[fut]
            completed += 1
            try:
                res = fut.result()
            except Exception as e:  # noqa: BLE001
                res = {
                    "ro_id": ro_id,
                    "status": "error",
                    "duration": 0.0,
                    "errors": [f"future exception: {e}"],
                }
            results.append(res)
            tag = "OK" if res["status"] == "ok" else "ERR"
            label = name_lookup.get(ro_id, "?")
            extra = ""
            if res.get("errors"):
                extra = f" - {res['errors'][0][:120]}"
            print(
                f"  [{completed}/{total}] RO #{ro_id} ({label}) ... "
                f"{res['duration']:.1f}s {tag}{extra}"
            )
    phase2_secs = time.time() - t_phase2
    n_ok = sum(1 for r in results if r["status"] == "ok")
    n_err = total - n_ok
    print(f"  ({phase2_secs:.2f}s - {n_ok}/{total} sukses)")
    print()

    # ---------- Phase 3 ---------- #
    print("[Phase 3] Cross-RO batch check ...")
    t_phase3 = time.time()
    master_path, batch_info = cross_check_batch(kkp_dir)
    if batch_info.get("rc") != 0:
        print("  ! Cross-check batch gagal:", file=sys.stderr)
        print((batch_info.get("stderr") or batch_info.get("stdout") or "")[:1000], file=sys.stderr)
    total_anom = batch_info.get("total_anomali")
    per_sev = batch_info.get("per_severity", {})
    print(f"  master: {master_path}")
    print(f"  total RO  : {batch_info.get('total_ro')}")
    print(f"  total anom: {total_anom}")
    print(f"  per sev   : {per_sev}")
    print(f"  ({time.time()-t_phase3:.2f}s)")
    print()

    # ---------- Phase 4 ---------- #
    render_done = False
    lhr_path: Path | None = None
    if not args.no_render and master_path.exists() and batch_info.get("rc") == 0:
        print("[Phase 4] Render LHR (multi-RO docx) ...")
        t_phase4 = time.time()
        lhr_path, render_info = render_lhr(
            kkp_dir, lhp_dir, args.judul, args.nomor, args.tanggal, args.penerima
        )
        if render_info.get("rc") != 0:
            print("  ! Render LHR gagal:", file=sys.stderr)
            print((render_info.get("stderr") or render_info.get("stdout") or "")[:1000], file=sys.stderr)
        else:
            render_done = True
            print(f"  output: {lhr_path}")
        print(f"  ({time.time()-t_phase4:.2f}s)")
        print()
    elif args.no_render:
        print("[Phase 4] Skipped (--no-render)\n")
    else:
        print("[Phase 4] Skipped (Phase 3 gagal)\n")

    # ---------- Tulis _pipeline_meta.json ---------- #
    wall = time.time() - t_phase1
    meta = {
        "tanggal": time.strftime("%Y-%m-%dT%H:%M:%S%z") or time.strftime("%Y-%m-%dT%H:%M:%S"),
        "penugasan": str(penugasan),
        "tor_dir": str(tor_dir),
        "rab_dir": str(rab_dir),
        "workers": n_workers,
        "ro_processed": total,
        "ro_success": n_ok,
        "ro_failed": n_err,
        "wall_clock_seconds": round(wall, 3),
        "phase2_seconds": round(phase2_secs, 3),
        "warnings": warns,
        "per_ro": [
            {
                "ro_id": r["ro_id"],
                "status": r["status"],
                "duration": round(r.get("duration", 0.0), 3),
                "tor": r.get("tor"),
                "rab": r.get("rab"),
                "n_anomalies_single": r.get("n_anomalies_single", 0),
                "errors": r.get("errors", []),
            }
            for r in sorted(results, key=lambda x: x["ro_id"])
        ],
        "total_anomali": total_anom,
        "per_severity": per_sev,
        "per_aspek": batch_info.get("per_aspek", {}),
        "render_lhr_done": render_done,
        "lhr_path": str(lhr_path) if lhr_path else None,
    }
    meta_path = kkp_dir / "_pipeline_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------- Phase Final: Generate Bukti AI .docx + Submit JSON untuk Integral ----------
    print("[Phase Final] Generate Bukti Cek AI .docx + Submit JSON ...")
    t_final = time.time()
    SCRIPTS_PARENT = SCRIPT_DIR.parent
    BUKTI_AI_GEN = SCRIPTS_PARENT / "generate_bukti_ai_docx.py"
    SUBMIT_GEN = SCRIPTS_PARENT / "generate_submit_json.py"

    if BUKTI_AI_GEN.exists():
        ok, msg = _run([py, str(BUKTI_AI_GEN), "--penugasan", str(penugasan),
                        "--skill", "reviu-rka-kl", "--model", "claude-sonnet-4-6"], "generate_bukti_ai_docx", timeout=120)
        if not ok:
            print(f"  WARN bukti_ai: {msg}", file=sys.stderr)

    if SUBMIT_GEN.exists():
        ok, msg = _run([py, str(SUBMIT_GEN), "--penugasan", str(penugasan),
                        "--skill", "reviu-rka-kl", "--model", "claude-sonnet-4-6"], "generate_submit_json", timeout=60)
        if not ok:
            print(f"  WARN submit_json: {msg}", file=sys.stderr)
        else:
            print(f"  Submit JSON: {penugasan / '_SUBMIT' / 'submit-latest.json'}")
    print(f"  ({time.time()-t_final:.2f}s)\n")


    # ---------- Summary ---------- #
    print("=" * 72)
    sev_str = ""
    if per_sev:
        sev_str = " (" + ", ".join(f"{k}={v}" for k, v in per_sev.items()) + ")"
    status_icon = "OK" if n_err == 0 else "PARTIAL"
    print(
        f"[{status_icon}] Batch selesai: {n_ok}/{total} RO sukses dalam "
        f"{wall:.1f} detik"
    )
    if total_anom is not None:
        print(f"   Total anomali: {total_anom}{sev_str}")
    if render_done and lhr_path:
        print(f"   LHR : {lhr_path}")
    print(f"   KKP : {kkp_dir}")
    print(f"   Meta: {meta_path}")
    print("=" * 72)
    return 0 if n_err == 0 and batch_info.get("rc") == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
