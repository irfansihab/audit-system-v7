#!/usr/bin/env python3
"""
role_check.py — Validator role-based access untuk audit-system-v4.

Dipanggil oleh setiap task (01, 03, 04) di langkah pertama. Membaca
`_ROLE.md` dari folder penugasan dan memastikan role pemanggil
diizinkan menjalankan task tersebut.

Contoh:
    python3 scripts/role_check.py --penugasan penugasan/2026-05-001-xxx --task 03
    # exit 0 kalau diizinkan, exit 2 + pesan stderr kalau ditolak.

Juga bisa dipakai sebagai modul:
    from scripts.role_check import check_role
    role = check_role(penugasan_dir, "03")
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Matriks izin: role_kode -> list of allowed task ids
ROLE_PERMISSIONS = {
    "AT": ["00", "01", "03"],            # Anggota Tim
    "KT": ["00", "04"],                  # Ketua Tim
    "PT": ["00", "04"],                  # Pengendali Teknis (default = setara KT)
    "PM": ["00", "04"],                  # Pengendali Mutu (default = setara KT)
}

REQUIRED_ROLE_FOR_TASK = {
    "01": ["AT"],
    "03": ["AT"],
    "04": ["KT", "PT", "PM"],
}


@dataclass
class Role:
    nama_lengkap: str
    role: str
    role_kode: str
    validated_against_pkp: bool
    session_start: Optional[str]


def parse_role_md(path: Path) -> Optional[Role]:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    # Frontmatter parser sederhana (key: value, sampai --- ke-2)
    m = re.match(r"---\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return None
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    if "nama_lengkap" not in fm or "role_kode" not in fm:
        return None
    return Role(
        nama_lengkap=fm["nama_lengkap"],
        role=fm.get("role", ""),
        role_kode=fm["role_kode"].upper(),
        validated_against_pkp=str(fm.get("role_validated_against_pkp", "false")).lower() == "true",
        session_start=fm.get("session_start"),
    )


def check_role(penugasan_dir: Path, task_id: str) -> Role:
    role_path = penugasan_dir / "_ROLE.md"
    role = parse_role_md(role_path)
    if role is None:
        sys.stderr.write(
            f"[role_check] DENIED: _ROLE.md tidak ditemukan di {penugasan_dir}.\n"
            f"  -> Jalankan Task 00 (Identifikasi Role) lebih dulu.\n"
        )
        sys.exit(2)
    allowed = ROLE_PERMISSIONS.get(role.role_kode, [])
    if task_id not in allowed:
        required = REQUIRED_ROLE_FOR_TASK.get(task_id, [])
        sys.stderr.write(
            f"[role_check] DENIED: role '{role.role}' (kode={role.role_kode}) "
            f"tidak boleh menjalankan Task {task_id}.\n"
            f"  -> Task {task_id} hanya boleh oleh: {', '.join(required) or '(tidak diatur)'}.\n"
            f"  -> Minta orang yang sesuai untuk login (Task 00) sebelum melanjutkan.\n"
        )
        sys.exit(2)
    return role


def main() -> int:
    ap = argparse.ArgumentParser(description="Validator role untuk task audit-system-v4.")
    ap.add_argument("--penugasan", required=True, help="Path folder penugasan (yang berisi _ROLE.md).")
    ap.add_argument("--task", required=True, help="ID task yang dipanggil (00, 01, 03, 04).")
    args = ap.parse_args()

    penugasan_dir = Path(args.penugasan)
    role = check_role(penugasan_dir, args.task)
    print(f"[role_check] OK — {role.nama_lengkap} ({role.role}) boleh menjalankan Task {args.task}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
