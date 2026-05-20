#!/usr/bin/env python3
"""
audit_trail.py — Helper append-only event log untuk audit-system-v4.

Setiap aksi yang relevan (login, gate konfirmasi, file generate,
temuan ditambah, LHP final, reminder) ditulis sebagai 1 baris JSON
ke `penugasan/[nama]/_AUDIT-TRAIL/events.jsonl` (JSON Lines).

Format event:
{
  "event_id": "evt_<uuid4>",
  "timestamp": "2026-05-02T14:30:00+07:00",
  "actor": {"nama": "Sarah Aulia", "role": "Anggota Tim", "role_kode": "AT"},
  "action": "ROLE_LOGIN",
  "target": "_ROLE.md",
  "payload": {...},
  "task": "00",
  "penugasan": "2026-05-001-reviu-pengadaan-bakti"
}

Contoh CLI:
  python3 scripts/audit_trail.py log-event \
      --penugasan penugasan/2026-05-001-xxx \
      --action ROLE_LOGIN \
      --task 00 \
      --target _ROLE.md \
      --payload '{"validated_against_pkp": true}'

  python3 scripts/audit_trail.py log-batch \
      --penugasan penugasan/2026-05-001-xxx \
      --events '[{"action":"TASK_STARTED","task":"01"}, {"action":"FILE_GENERATED","task":"01","target":"context.md"}]'

  python3 scripts/audit_trail.py show \
      --penugasan penugasan/2026-05-001-xxx
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

KNOWN_ACTIONS = {
    "ROLE_LOGIN",
    "TASK_STARTED",
    "TASK_COMPLETED",
    "GATE_PASSED",
    "GATE_REJECTED",
    "FILE_GENERATED",
    "FILE_UPDATED",
    "KKP_TEMUAN_ADDED",
    "KKP_TEMUAN_UPDATED",
    "SASARAN_COMPLETED",
    "LHP_FINALIZED",
    "REMINDER_SENT",
    "ROLE_DENIED",
    "VALIDATION_FAILED",
    "VALIDATION_PASSED",
    "INTEGRAL_EXPORT",
    "SAIPI_CHECK",
    "INGEST_TO_WIKI",
}

WIB = timezone(timedelta(hours=7))


def _now_iso() -> str:
    return datetime.now(WIB).isoformat(timespec="seconds")


def _read_role(penugasan_dir: Path) -> dict:
    role_path = penugasan_dir / "_ROLE.md"
    if not role_path.exists():
        return {"nama": "(unknown)", "role": "(unknown)", "role_kode": "?"}
    text = role_path.read_text(encoding="utf-8")
    out = {"nama": "(unknown)", "role": "(unknown)", "role_kode": "?"}
    in_fm = False
    for line in text.splitlines():
        if line.strip() == "---":
            in_fm = not in_fm
            continue
        if in_fm and ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k == "nama_lengkap":
                out["nama"] = v
            elif k == "role":
                out["role"] = v
            elif k == "role_kode":
                out["role_kode"] = v.upper()
    return out


def log_event(
    penugasan_dir: Path,
    action: str,
    target: str = "",
    payload: Optional[dict] = None,
    task: str = "",
    actor_override: Optional[dict] = None,
) -> dict:
    if action not in KNOWN_ACTIONS:
        sys.stderr.write(f"[audit_trail] WARN: action '{action}' belum terdaftar di KNOWN_ACTIONS.\n")

    actor = actor_override or _read_role(penugasan_dir)
    event = {
        "event_id": "evt_" + uuid.uuid4().hex[:12],
        "timestamp": _now_iso(),
        "actor": actor,
        "action": action,
        "target": target,
        "payload": payload or {},
        "task": task,
        "penugasan": penugasan_dir.name,
    }

    trail_dir = penugasan_dir / "_AUDIT-TRAIL"
    trail_dir.mkdir(parents=True, exist_ok=True)
    log_path = trail_dir / "events.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

    return event


def show(penugasan_dir: Path, last: Optional[int] = None) -> None:
    log_path = penugasan_dir / "_AUDIT-TRAIL" / "events.jsonl"
    if not log_path.exists():
        print(f"(belum ada event di {log_path})")
        return
    lines = log_path.read_text(encoding="utf-8").splitlines()
    if last:
        lines = lines[-last:]
    for line in lines:
        try:
            evt = json.loads(line)
        except json.JSONDecodeError:
            print(f"[corrupt] {line}")
            continue
        actor = evt.get("actor", {})
        print(
            f"{evt['timestamp']}  [{evt['action']:22s}] "
            f"{actor.get('nama','?')} ({actor.get('role_kode','?')}) "
            f"-> {evt.get('target','')}  task={evt.get('task','')}"
        )


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    log_p = sub.add_parser("log-event", help="Tulis 1 event ke audit trail.")
    log_p.add_argument("--penugasan", required=True)
    log_p.add_argument("--action", required=True)
    log_p.add_argument("--target", default="")
    log_p.add_argument("--task", default="")
    log_p.add_argument("--payload", default="{}", help="JSON string.")

    show_p = sub.add_parser("show", help="Tampilkan audit trail.")
    show_p.add_argument("--penugasan", required=True)
    show_p.add_argument("--last", type=int, default=None)

    # v4.0.4 — log-batch hemat subprocess overhead untuk Task 01/03/04
    batch_p = sub.add_parser("log-batch", help="Tulis banyak event sekaligus dari JSON array.")
    batch_p.add_argument("--penugasan", required=True)
    batch_p.add_argument("--events", default=None, help="JSON array string of events.")
    batch_p.add_argument("--events-file", default=None, help="Path file JSON array, '-' untuk stdin.")

    args = ap.parse_args()
    pen_dir = Path(args.penugasan)

    if args.cmd == "log-event":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"--payload bukan JSON valid: {e}\n")
            return 1
        evt = log_event(pen_dir, action=args.action, target=args.target,
                        payload=payload, task=args.task)
        print(json.dumps(evt, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "show":
        show(pen_dir, args.last)
        return 0

    if args.cmd == "log-batch":
        if args.events is not None:
            raw = args.events
        elif args.events_file is not None:
            raw = sys.stdin.read() if args.events_file == "-" else Path(args.events_file).read_text(encoding="utf-8")
        else:
            sys.stderr.write("log-batch: butuh --events atau --events-file\n")
            return 1
        try:
            events = json.loads(raw)
        except json.JSONDecodeError as e:
            sys.stderr.write(f"log-batch: JSON tidak valid: {e}\n")
            return 1
        if not isinstance(events, list):
            sys.stderr.write("log-batch: events harus berupa JSON array\n")
            return 1
        written = 0
        for i, e in enumerate(events):
            if not isinstance(e, dict) or "action" not in e:
                sys.stderr.write(f"log-batch: event[{i}] harus dict dengan field 'action'\n")
                return 1
            log_event(pen_dir, action=e["action"], target=e.get("target", ""),
                      payload=e.get("payload") or {}, task=e.get("task", ""))
            written += 1
        print(f"log-batch: {written} event ditulis ke {pen_dir.name}/_AUDIT-TRAIL/events.jsonl")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
