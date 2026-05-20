"""Routes manajemen penugasan."""
import json
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Penugasan, PenugasanStatus, Role, User
from app.schemas import PenugasanCreate, PenugasanOut
from app.storage import gen_kode_penugasan, penugasan_folder

router = APIRouter(prefix="/penugasan", tags=["penugasan"])


def _scaffold_penugasan_files(folder: Path, kode: str, payload: PenugasanCreate, ketua_tim_name: str | None) -> None:
    """Tulis stub context.md + sasaran-assignment.json saat penugasan dibuat.

    V6 (qc_saipi.py, render_kkp.py) butuh kedua file ini ada di lokasi standar:
    - {folder}/context.md
    - {folder}/_PKP/sasaran-assignment.json

    Format mengikuti yang dibaca parse_context_meta() di V6.
    """
    # 1. context.md stub (placeholder fields yang nanti diisi Ketua Tim)
    context_md_path = folder / "context.md"
    if not context_md_path.exists():
        skill_label = payload.skill.value.replace("-", " ").title()
        tanggal_str = (
            payload.tanggal_st.strftime("%d %B %Y") if payload.tanggal_st else "[DIISI AUDITOR]"
        )
        content = f"""# Konteks Penugasan: {payload.obyek}

## Identitas Penugasan

- Kode: {kode}
- Obyek: {payload.obyek}
- Skill / Jenis Pengawasan: {payload.skill.value}
- Nomor ST: {payload.nomor_st or "[DIISI AUDITOR]"}
- Tanggal ST: {tanggal_str}

## Periode & Anggaran

- Periode: [DIISI AUDITOR — mis. Januari–Desember 2026]
- Tahun Anggaran: [DIISI AUDITOR — mis. 2026]

## Tujuan

[DIISI AUDITOR — sebutkan tujuan reviu sesuai PKP. Contoh:
"Memberikan keyakinan terbatas atas kewajaran HPS dan kepatuhan proses
pengadaan terhadap Perpres 16/2018 jo. Perpres 12/2021."]

## Tim

| Peran | Nama Lengkap | NIP | Jabfung |
|-------|--------------|-----|---------|
| Ketua Tim | {ketua_tim_name or "[DIISI]"} | [NIP] | [Auditor Madya/Muda/Pertama] |
| Anggota | [DIISI] | [NIP] | [Auditor Pertama] |

## Ringkasan Obyek

[DIISI — 3-5 kalimat gambaran umum obyek yang direviu: nilai pengadaan,
periode pelaksanaan, instansi auditi, dll.]
"""
        context_md_path.write_text(content, encoding="utf-8")

    # 2. _PKP/sasaran-assignment.json stub (kosong, auditor lengkapi)
    sasaran_path = folder / "_PKP" / "sasaran-assignment.json"
    if not sasaran_path.exists():
        sasaran_path.parent.mkdir(parents=True, exist_ok=True)
        stub = {
            "penugasan_id": kode,
            "skill": payload.skill.value,
            "schema_version": "v4.0.0",
            "tanggal_dibuat": datetime.utcnow().isoformat() + "Z",
            "sasaran": [
                # Contoh struktur — dihapus/diganti oleh Ketua Tim:
                # {
                #     "sasaran_id": "S-01",
                #     "deskripsi": "Kewajaran HPS",
                #     "assigned_to": ["Nama Anggota Tim"],
                #     "langkah_kerja": ["..."]
                # }
            ],
        }
        sasaran_path.write_text(json.dumps(stub, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. temuan.json stub di _KKP/ supaya render_kkp.py tidak crash bila auditor
    #    coba render sebelum ada temuan. Skema mengikuti render_kkp.py.
    temuan_path = folder / "_KKP" / "temuan.json"
    if not temuan_path.exists():
        temuan_path.parent.mkdir(parents=True, exist_ok=True)
        stub_temuan = {
            "penugasan": {
                "kode": kode,
                "obyek": payload.obyek,
                "jenis_pengawasan": payload.skill.value,
                "nomor_st": payload.nomor_st or "[DIISI AUDITOR]",
                "tanggal_st": payload.tanggal_st.isoformat() if payload.tanggal_st else None,
            },
            "schema_version": "v4.0.0",
            "temuan": [],
        }
        temuan_path.write_text(json.dumps(stub_temuan, ensure_ascii=False, indent=2), encoding="utf-8")


@router.post("", response_model=PenugasanOut, status_code=status.HTTP_201_CREATED)
async def create_penugasan(
    payload: PenugasanCreate,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PenugasanOut:
    user, role = current
    kode = gen_kode_penugasan(payload.skill.value)
    folder = penugasan_folder(kode)

    # Scaffolding file V6 yang harus ada (context.md, sasaran-assignment.json, temuan.json stub)
    # supaya pipeline V6 tidak gagal karena file hilang & agen tidak perlu improvisasi bikin sendiri.
    _scaffold_penugasan_files(
        folder=folder,
        kode=kode,
        payload=payload,
        ketua_tim_name=user.nama_lengkap if role in (Role.KT, Role.PT, Role.PM) else None,
    )

    p = Penugasan(
        kode=kode,
        obyek=payload.obyek,
        skill=payload.skill,
        nomor_st=payload.nomor_st,
        tanggal_st=payload.tanggal_st,
        status=PenugasanStatus.DRAFT,
        ketua_tim_id=user.id if role in (Role.KT, Role.PT, Role.PM) else None,
        folder_path=str(folder),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)
    return PenugasanOut.model_validate(p)


@router.get("", response_model=list[PenugasanOut])
async def list_penugasan(
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PenugasanOut]:
    rows = (await db.execute(select(Penugasan).order_by(Penugasan.created_at.desc()))).scalars().all()
    return [PenugasanOut.model_validate(r) for r in rows]


@router.get("/{penugasan_id}", response_model=PenugasanOut)
async def get_penugasan(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PenugasanOut:
    p = (
        await db.execute(select(Penugasan).where(Penugasan.id == penugasan_id))
    ).scalar_one_or_none()
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Penugasan tidak ditemukan")
    return PenugasanOut.model_validate(p)
