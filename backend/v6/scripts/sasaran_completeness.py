#!/usr/bin/env python3
"""
sasaran_completeness.py — Cek apakah semua sasaran sudah terjawab di KKP.

Dipanggil oleh Task 04 SEBELUM ketua tim mulai menulis LHP. Jika ada
sasaran yang belum SELESAI_KKP atau belum punya temuan terkait, script
ini exit code 2 + cetak reminder yang siap di-tampilkan ke ketua tim
(siapa yang belum mengerjakan, sasaran apa).

Pemakaian:
    python3 scripts/sasaran_completeness.py --penugasan penugasan/2026-05-001-xxx
    # exit 0 = lengkap, lanjut LHP
    # exit 2 = belum lengkap, blokir LHP + tampilkan reminder

Optional flag --emit-reminder akan memanggil audit_trail.log_event
dengan action=REMINDER_SENT (default: tidak emit, supaya idempotent).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
from audit_trail import log_event  # noqa: E402


def load_json(path: Path) -> Any:
    if not path.exists():
        sys.stderr.write(f"File tidak ditemukan: {path}\n")
        sys.exit(1)
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--penugasan", required=True)
    ap.add_argument("--emit-reminder", action="store_true",
                    help="Kalau ada gap, tulis event REMINDER_SENT ke audit trail.")
    args = ap.parse_args()

    pen_dir = Path(args.penugasan)
    sasaran_path = pen_dir / "_PKP" / "sasaran-assignment.json"
    temuan_path = pen_dir / "_KKP" / "temuan.json"

    sasaran_doc = load_json(sasaran_path)
    if temuan_path.exists():
        temuan_doc = load_json(temuan_path)
        temuan_per_sasaran: dict[str, list[dict]] = {}
        for t in temuan_doc.get("temuan", []):
            temuan_per_sasaran.setdefault(t["sasaran_id"], []).append(t)
    else:
        temuan_per_sasaran = {}

    gaps = []
    for s in sasaran_doc.get("sasaran", []):
        sid = s["sasaran_id"]
        status = s.get("status", "BELUM_DIKERJAKAN")
        temuan_count = len(temuan_per_sasaran.get(sid, []))
        # Sasaran dianggap "terjawab" kalau status >= SELESAI_KKP DAN punya >=1 temuan
        # (temuan kosong = "tidak ada temuan" juga sah, asal status sudah SELESAI_KKP)
        if status not in ("SELESAI_KKP", "DIREVIU_KT", "FINAL"):
            assignees = ", ".join(
                f"{a['nama_lengkap']} ({a['role_kode']})" for a in s.get("assigned_to", [])
            ) or "(belum ada)"
            gaps.append({
                "sasaran_id": sid,
                "deskripsi": s.get("deskripsi", ""),
                "status": status,
                "assigned_to": assignees,
                "temuan_count": temuan_count,
            })

    if not gaps:
        print("OK — semua sasaran sudah SELESAI_KKP. LHP boleh dimulai.")
        return 0

    # ---- bangun reminder ----
    print("=" * 72)
    print("⛔ BLOKIR: LHP belum boleh dibuat — masih ada sasaran yang belum dikerjakan.")
    print("=" * 72)
    print(f"\nPenugasan: {sasaran_doc.get('penugasan_id', pen_dir.name)}")
    print(f"Sasaran tertunda: {len(gaps)} dari {len(sasaran_doc.get('sasaran', []))}\n")
    print(f"{'Sasaran':<8} {'Status':<22} {'Anggota Tim':<40}")
    print("-" * 72)
    for g in gaps:
        print(f"{g['sasaran_id']:<8} {g['status']:<22} {g['assigned_to']:<40}")
        print(f"         └─ {g['deskripsi'][:80]}")
    print()
    print("Reminder untuk Ketua Tim:")
    print("  Hubungi anggota tim di atas untuk menyelesaikan KKP mereka.")
    print("  Setelah KKP selesai, jalankan ulang Task 04 (LHP).\n")

    if args.emit_reminder:
        log_event(
            pen_dir,
            action="REMINDER_SENT",
            target="LHP_BLOCKED",
            payload={"missing_sasaran": gaps, "total_sasaran": len(sasaran_doc.get("sasaran", []))},
            task="04",
        )
        print("[audit_trail] Event REMINDER_SENT ditulis.")

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
