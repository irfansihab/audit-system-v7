"""Tools wiki — agen akses pattern temuan dari knowledge base auditor.

Folder wiki/ berisi pattern temuan + (rencana) peraturan/glossary. Struktur:

    wiki/
    └── temuan-patterns/
        ├── reviu-pengadaan/
        │   ├── README.md
        │   └── RP-08-hps-rfi-minimum.md
        └── reviu-rka-kl/
            ├── README.md
            └── RKA-01-tor-7-blok.md

Setiap file pattern punya YAML frontmatter (id, skill, kategori, severity,
judul, kriteria_baku, tags) lalu body markdown.

Path resolusi via env var APP_WIKI_PATH (lihat config.py).
"""
import json
import re
from pathlib import Path

from claude_agent_sdk import tool

from app.config import get_settings

settings = get_settings()


def _parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter sederhana di awal file.

    Format:
        ---
        key: value
        list: [a, b, c]
        ---
        body markdown...

    Return (metadata_dict, body_str). Kalau tidak ada frontmatter, return ({}, content).
    Parser ini sederhana — tidak butuh dep tambahan PyYAML.
    """
    if not content.startswith("---"):
        return {}, content

    # Cari closing ---
    end_match = re.search(r"^---\s*$", content[3:], re.MULTILINE)
    if not end_match:
        return {}, content

    fm_text = content[3 : end_match.start() + 3].strip()
    body = content[end_match.end() + 3:].lstrip("\n")

    metadata: dict = {}
    for line in fm_text.splitlines():
        line = line.rstrip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*(.+?)\s*$", line)
        if not m:
            continue
        key, raw_value = m.group(1), m.group(2).strip()

        # Strip quotes
        if (raw_value.startswith('"') and raw_value.endswith('"')) or (
            raw_value.startswith("'") and raw_value.endswith("'")
        ):
            metadata[key] = raw_value[1:-1]
            continue

        # List inline [a, b, c]
        if raw_value.startswith("[") and raw_value.endswith("]"):
            inner = raw_value[1:-1].strip()
            items = [it.strip().strip('"').strip("'") for it in inner.split(",") if it.strip()]
            metadata[key] = items
            continue

        metadata[key] = raw_value

    return metadata, body


def _patterns_dir(skill: str) -> Path:
    """Folder pattern untuk skill tertentu. Skill di-slugify untuk safety."""
    skill_slug = re.sub(r"[^a-zA-Z0-9\-]", "-", skill.lower())
    return settings.wiki_path / "temuan-patterns" / skill_slug


def _scan_pattern_files(skill: str) -> list[Path]:
    """List semua .md di folder skill (kecuali README.md)."""
    folder = _patterns_dir(skill)
    if not folder.exists():
        return []
    return sorted([p for p in folder.glob("*.md") if p.name.lower() != "readme.md"])


@tool(
    "list_temuan_patterns",
    "Daftar semua pattern temuan dari wiki untuk skill tertentu. "
    "Return list ringkas {id, judul, kategori, severity, tags} per pattern. "
    "Pakai SEBELUM susun temuan substantif supaya kamu tahu pattern apa yang sudah "
    "ada di knowledge base tim. Untuk baca detail pattern, panggil `get_temuan_pattern`.",
    {"skill": str},
)
async def list_temuan_patterns(args: dict) -> dict:
    skill = args["skill"].strip().lower()
    if skill not in {"reviu-pengadaan", "reviu-rka-kl"}:
        return {
            "content": [{
                "type": "text",
                "text": f"FAILED|skill='{skill}' tidak valid. Gunakan: reviu-pengadaan atau reviu-rka-kl",
            }],
            "is_error": True,
        }

    files = _scan_pattern_files(skill)
    if not files:
        return {
            "content": [{
                "type": "text",
                "text": (
                    f"WIKI_KOSONG|skill={skill}|wiki_path={settings.wiki_path}|"
                    f"Belum ada pattern temuan untuk skill ini. "
                    f"Auditor manusia perlu menambahkan file pattern di "
                    f"wiki/temuan-patterns/{skill}/ — lanjutkan tanpa pattern."
                ),
            }]
        }

    summaries: list[dict] = []
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
        except OSError:
            continue
        meta, _ = _parse_frontmatter(content)
        summaries.append({
            "id": meta.get("id", f.stem),
            "judul": meta.get("judul", ""),
            "kategori": meta.get("kategori", ""),
            "severity": meta.get("severity", ""),
            "tags": meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
            "kriteria_baku": meta.get("kriteria_baku", ""),
            "file": str(f.relative_to(settings.wiki_path)),
        })

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(
                {
                    "skill": skill,
                    "total": len(summaries),
                    "patterns": summaries,
                },
                ensure_ascii=False,
            ),
        }]
    }


@tool(
    "get_temuan_pattern",
    "Baca isi LENGKAP satu pattern temuan dari wiki berdasarkan ID (mis. 'RP-08' atau 'RKA-01'). "
    "Return metadata + body markdown. Pakai SETELAH `list_temuan_patterns` untuk dapat detail "
    "pattern yang ingin di-referensikan saat menyusun temuan.",
    {"pattern_id": str},
)
async def get_temuan_pattern(args: dict) -> dict:
    pid = args["pattern_id"].strip()
    if not pid:
        return {
            "content": [{"type": "text", "text": "FAILED|pattern_id kosong"}],
            "is_error": True,
        }

    # Search di semua skill folder
    base = settings.wiki_path / "temuan-patterns"
    if not base.exists():
        return {
            "content": [{
                "type": "text",
                "text": f"FAILED|folder wiki tidak ada: {base}",
            }],
            "is_error": True,
        }

    found: Path | None = None
    found_meta: dict | None = None
    for skill_dir in base.iterdir():
        if not skill_dir.is_dir():
            continue
        for f in skill_dir.glob("*.md"):
            if f.name.lower() == "readme.md":
                continue
            try:
                content = f.read_text(encoding="utf-8")
            except OSError:
                continue
            meta, _ = _parse_frontmatter(content)
            if meta.get("id") == pid or f.stem.upper().startswith(pid.upper()):
                found = f
                found_meta = meta
                break
        if found:
            break

    if not found:
        return {
            "content": [{
                "type": "text",
                "text": (
                    f"NOT_FOUND|pattern_id={pid}|"
                    f"Coba list_temuan_patterns(skill) untuk lihat ID yang tersedia."
                ),
            }],
            "is_error": True,
        }

    content = found.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(content)

    return {
        "content": [{
            "type": "text",
            "text": json.dumps(
                {
                    "pattern_id": meta.get("id", found.stem),
                    "judul": meta.get("judul", ""),
                    "skill": meta.get("skill", ""),
                    "kategori": meta.get("kategori", ""),
                    "severity": meta.get("severity", ""),
                    "kriteria_baku": meta.get("kriteria_baku", ""),
                    "tags": meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
                    "file": str(found.relative_to(settings.wiki_path)),
                    "body_markdown": body[:8000],  # cap 8KB supaya context agen tidak meledak
                },
                ensure_ascii=False,
            ),
        }]
    }


WIKI_TOOLS = [list_temuan_patterns, get_temuan_pattern]
