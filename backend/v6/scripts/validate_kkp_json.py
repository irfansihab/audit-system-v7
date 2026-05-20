#!/usr/bin/env python3
"""
validate_kkp_json.py — Validator JSON KKP (temuan + sasaran-assignment)
terhadap schema di schemas/.

Tanpa external deps (pakai jsonschema kalau ada, fallback ke validator manual
sederhana). Pemakaian:

  python3 scripts/validate_kkp_json.py penugasan/2026-05-001-xxx/_KKP/temuan.json
  python3 scripts/validate_kkp_json.py penugasan/2026-05-001-xxx/_PKP/sasaran-assignment.json

Auto-deteksi schema dari nama file (temuan.json -> kkp-temuan; sasaran*.json
-> sasaran-assignment).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"


def detect_schema(path: Path) -> Path:
    n = path.name.lower()
    if "temuan" in n:
        return SCHEMAS / "kkp-temuan.schema.json"
    if "sasaran" in n:
        return SCHEMAS / "sasaran-assignment.schema.json"
    raise SystemExit(f"Tidak bisa deteksi schema untuk {path.name}. Pakai --schema.")


def validate_with_jsonschema(data, schema) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return []
    errors = []
    validator = jsonschema.Draft7Validator(schema)
    for err in validator.iter_errors(data):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{loc}: {err.message}")
    return errors


# -------- fallback manual checks (cukup untuk smoke test tanpa deps) --------

def manual_check_temuan(data) -> list[str]:
    errs = []
    for required in ("penugasan", "generated_at", "schema_version", "temuan"):
        if required not in data:
            errs.append(f"(root): missing '{required}'")
    if data.get("schema_version") != "v4.0.0":
        errs.append(f"schema_version: harus 'v4.0.0' (got {data.get('schema_version')!r})")
    for i, t in enumerate(data.get("temuan", [])):
        prefix = f"temuan[{i}]"
        for req in ("id_temuan", "sasaran_id", "anggota_tim", "judul_temuan",
                    "kondisi", "kriteria", "akibat", "dokumen_sumber",
                    "tanggal_input", "status"):
            if req not in t:
                errs.append(f"{prefix}.{req}: missing")
        if "id_temuan" in t and not re.match(r"^T-\d{3}$", t["id_temuan"]):
            errs.append(f"{prefix}.id_temuan: harus format T-NNN")
        if "sasaran_id" in t and not re.match(r"^S-\d{2}$", t["sasaran_id"]):
            errs.append(f"{prefix}.sasaran_id: harus format S-NN")
        if "judul_temuan" in t and re.match(
            r"^(TERPENUHI|TIDAK TERPENUHI|MEMADAI|TIDAK MEMADAI)", t["judul_temuan"]
        ):
            errs.append(f"{prefix}.judul_temuan: tidak boleh diawali label status (mis. 'TERPENUHI')")
        if "dokumen_sumber" in t and not t["dokumen_sumber"]:
            errs.append(f"{prefix}.dokumen_sumber: minimal 1 dokumen sumber wajib (anti-halusinasi)")
    return errs


def manual_check_sasaran(data) -> list[str]:
    errs = []
    for req in ("penugasan_id", "extracted_from_pkp", "extracted_at", "sasaran"):
        if req not in data:
            errs.append(f"(root): missing '{req}'")
    for i, s in enumerate(data.get("sasaran", [])):
        prefix = f"sasaran[{i}]"
        for req in ("sasaran_id", "deskripsi", "assigned_to", "status"):
            if req not in s:
                errs.append(f"{prefix}.{req}: missing")
        if "assigned_to" in s and not s["assigned_to"]:
            errs.append(f"{prefix}.assigned_to: minimal 1 anggota wajib")
    return errs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="Path JSON yang divalidasi.")
    ap.add_argument("--schema", default=None, help="Override path schema.")
    args = ap.parse_args()

    p = Path(args.file)
    if not p.exists():
        sys.stderr.write(f"File tidak ditemukan: {p}\n")
        return 1

    with p.open(encoding="utf-8") as f:
        data = json.load(f)

    schema_path = Path(args.schema) if args.schema else detect_schema(p)
    with schema_path.open(encoding="utf-8") as f:
        schema = json.load(f)

    errors = validate_with_jsonschema(data, schema)
    used = "jsonschema"
    if not errors:
        # fallback / komplementer
        if "temuan" in p.name.lower():
            errors = manual_check_temuan(data)
        elif "sasaran" in p.name.lower():
            errors = manual_check_sasaran(data)
        used = "manual" if errors else used

    if errors:
        print(f"FAILED ({used}) — {len(errors)} error:")
        for e in errors:
            print(f"  - {e}")
        return 2

    print(f"OK — {p.name} valid terhadap {schema_path.name}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
