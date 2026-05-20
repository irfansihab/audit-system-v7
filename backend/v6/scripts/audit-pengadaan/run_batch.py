"""
run_batch.py — Orchestrator end-to-end Audit Pengadaan.

Pipeline 3 fase:
    1. digest_pengadaan(folder)        → _KKP/pengadaan-digest.json
    2. cross_check(digest)             → _KKP/anomalies.json
    3. render_lha(anomalies, context)  → _LHP/LHA-DRAFT.docx (opsional --no-render)

Usage:
    python3 run_batch.py \
        --penugasan PATH_FOLDER_PENUGASAN \
        [--input-dir SUBPATH] \
        [--context PATH_CONTEXT_MD] \
        [--no-render]

Default:
    --input-dir : seluruh folder --penugasan (rglob)
    --context   : <penugasan>/context.md
    Output      : <penugasan>/_KKP/  dan  <penugasan>/_LHP/
"""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
DIGEST_PENGADAAN = SCRIPT_DIR / "digest_pengadaan.py"
CROSS_CHECK = SCRIPT_DIR / "cross_check.py"
RENDER_LHA = SCRIPT_DIR / "render_lha.py"


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
    fails: list[str] = []
    for f in (DIGEST_PENGADAAN, CROSS_CHECK, RENDER_LHA):
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
        sys.exit(3)


def _run(cmd: list[str], tag: str, timeout: int = 300) -> tuple[bool, str]:
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        if r.returncode != 0:
            err = (r.stderr or r.stdout or "").strip()[:1000]
            return False, f"{tag} rc={r.returncode}: {err}"
        return True, (r.stdout or "").strip()[:500]
    except subprocess.TimeoutExpired:
        return False, f"{tag} timeout >{timeout}s"
    except Exception as e:  # noqa: BLE001
        return False, f"{tag} exception: {e}"


def main(argv: list[str] | None = None) -> int:
    _self_check_ast()
    _preflight_scripts()

    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--penugasan", required=True, help="Path folder penugasan")
    ap.add_argument(
        "--input-dir",
        default=None,
        help="Subpath folder pengadaan relatif --penugasan (default: seluruh folder penugasan)",
    )
    ap.add_argument(
        "--context",
        default=None,
        help="Path context.md (default: <penugasan>/context.md)",
    )
    ap.add_argument("--no-render", action="store_true", help="Skip Phase 3 render LHA")
    ap.add_argument("--role", default=None, choices=["AT", "KT", "PT", "PM"],
                    help="Role auditor: AT=Anggota Tim (KKP only), KT/PT/PM=Ketua Tim/Pengendali (LHP). "
                         "Default: auto-detect dari _ROLE.md, fallback AT.")

    args = ap.parse_args(argv)

    penugasan = Path(args.penugasan).resolve()
    if not penugasan.exists():
        print(f"[FATAL] Folder penugasan tidak ditemukan: {penugasan}", file=sys.stderr)
        return 4

    input_dir = (penugasan / args.input_dir).resolve() if args.input_dir else penugasan
    context_path = Path(args.context).resolve() if args.context else penugasan / "context.md"
    kkp_dir = penugasan / "_KKP"
    lhp_dir = penugasan / "_LHP"
    kkp_dir.mkdir(parents=True, exist_ok=True)

    digest_json = kkp_dir / "pengadaan-digest.json"
    anom_json = kkp_dir / "anomalies.json"
    lha_docx = lhp_dir / "LHA-DRAFT.docx"

    py = sys.executable or "python3"

    print("=" * 72)
    print("RUN BATCH - Audit Pengadaan")
    print("=" * 72)
    print(f"  Penugasan : {penugasan}")
    print(f"  Input dir : {input_dir}")
    print(f"  KKP dir   : {kkp_dir}")
    print(f"  Render    : {'OFF (--no-render)' if args.no_render else 'ON'}")
    print()
    # ---------- Role-based gating ----------
    role = (args.role or _detect_role(penugasan)).upper()
    print(f"  Role      : {role} ({'KKP only (skip LHP)' if not _should_render_lhp(role) else 'Full pipeline (render LHP)'})")


    t_start = time.time()
    errors: list[str] = []

    # ---------- Phase 1: digest ----------
    print("[Phase 1] digest_pengadaan ...")
    t1 = time.time()
    ok, msg = _run(
        [py, str(DIGEST_PENGADAAN), str(input_dir), "-o", str(digest_json)],
        "digest_pengadaan",
    )
    if not ok:
        print(f"  FAIL: {msg}", file=sys.stderr)
        errors.append(msg)
        return 5
    print(f"  output: {digest_json}")
    print(f"  ({time.time()-t1:.2f}s)")
    print()

    # ---------- Phase 2: cross_check ----------
    print("[Phase 2] cross_check ...")
    t2 = time.time()
    ok, msg = _run(
        [py, str(CROSS_CHECK), str(digest_json), "-o", str(anom_json)],
        "cross_check",
    )
    if not ok:
        print(f"  FAIL: {msg}", file=sys.stderr)
        errors.append(msg)
        return 6
    n_anom = 0
    per_sev: dict[str, int] = {}
    if anom_json.exists():
        try:
            data = json.loads(anom_json.read_text(encoding="utf-8"))
            anomalies = data.get("anomalies", [])
            n_anom = len(anomalies)
            for a in anomalies:
                sev = a.get("severity", "INFO")
                per_sev[sev] = per_sev.get(sev, 0) + 1
        except Exception as e:  # noqa: BLE001
            errors.append(f"parse anomalies: {e}")
    print(f"  output: {anom_json}")
    print(f"  total anomali: {n_anom}  per sev: {per_sev}")
    print(f"  ({time.time()-t2:.2f}s)")
    print()

    # ---------- Phase 3: render LHA ----------
    render_done = False
    if not _should_render_lhp(role):
        print(f"[Phase Render] Skipped — role {role} (KKP only, LHP dikerjakan Ketua Tim)\n")
    elif args.no_render:
        print("[Phase 3] Skipped (--no-render)\n")
    elif not context_path.exists():
        print(f"[Phase 3] Skipped — context.md tidak ditemukan di {context_path}", file=sys.stderr)
        errors.append(f"context.md missing: {context_path}")
    else:
        print("[Phase 3] render_lha ...")
        t3 = time.time()
        lhp_dir.mkdir(parents=True, exist_ok=True)
        ok, msg = _run(
            [py, str(RENDER_LHA), str(anom_json), str(context_path), "-o", str(lha_docx)],
            "render_lha",
        )
        if not ok:
            print(f"  FAIL: {msg}", file=sys.stderr)
            errors.append(msg)
        else:
            render_done = True
            print(f"  output: {lha_docx}")
        print(f"  ({time.time()-t3:.2f}s)")
        print()

    # ---------- Meta ----------
    wall = time.time() - t_start
    meta = {
        "skill": "audit-pengadaan",
        "tanggal": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "penugasan": str(penugasan),
        "input_dir": str(input_dir),
        "context_path": str(context_path) if context_path.exists() else None,
        "wall_clock_seconds": round(wall, 3),
        "digest_json": str(digest_json) if digest_json.exists() else None,
        "anomalies_json": str(anom_json) if anom_json.exists() else None,
        "total_anomali": n_anom,
        "per_severity": per_sev,
        "render_lha_done": render_done,
        "lha_path": str(lha_docx) if render_done else None,
        "errors": errors,
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
                        "--skill", "audit-pengadaan", "--model", "claude-sonnet-4-6"], "generate_bukti_ai_docx", timeout=120)
        if not ok:
            print(f"  WARN bukti_ai: {msg}", file=sys.stderr)

    if SUBMIT_GEN.exists():
        ok, msg = _run([py, str(SUBMIT_GEN), "--penugasan", str(penugasan),
                        "--skill", "audit-pengadaan", "--model", "claude-sonnet-4-6"], "generate_submit_json", timeout=60)
        if not ok:
            print(f"  WARN submit_json: {msg}", file=sys.stderr)
        else:
            print(f"  Submit JSON: {penugasan / '_SUBMIT' / 'submit-latest.json'}")
    print(f"  ({time.time()-t_final:.2f}s)\n")


    # ---------- Summary ----------
    print("=" * 72)
    status = "OK" if not errors else "PARTIAL"
    print(f"[{status}] Audit Pengadaan selesai dalam {wall:.1f} detik")
    print(f"   Total anomali: {n_anom}")
    if render_done:
        print(f"   LHA : {lha_docx}")
    print(f"   KKP : {kkp_dir}")
    print(f"   Meta: {meta_path}")
    print("=" * 72)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
