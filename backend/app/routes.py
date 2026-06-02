"""HTTP routes (mounted under the /api prefix)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from . import schemas, service
from .config import settings
from .database import get_db
from .providers import available_providers
from .safety import COPYRIGHT_POLICY, SAFE_GENERATION_RULES
from .scenes import MOODS, SCENES

router = APIRouter()


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "app": settings.app_name}


@router.get("/scenes", response_model=list[schemas.SceneOut])
def list_scenes() -> list[schemas.SceneOut]:
    return [
        schemas.SceneOut(
            key=s["key"],
            label_en=s["label_en"],
            label_zh=s["label_zh"],
            description=s["description"],
            default_bpm=s["default_bpm"],
            default_mood=s["default_mood"],
            default_intensity=s["default_intensity"],
            default_no_drums=s["default_no_drums"],
        )
        for s in SCENES.values()
    ]


@router.get("/providers", response_model=list[schemas.ProviderOut])
def list_providers() -> list[schemas.ProviderOut]:
    return [
        schemas.ProviderOut(
            key=p.name, implemented=p.implemented, description=p.description
        )
        for p in available_providers()
    ]


@router.get("/policy", response_model=schemas.PolicyOut)
def get_policy() -> schemas.PolicyOut:
    return schemas.PolicyOut(
        policy=COPYRIGHT_POLICY,
        rules=SAFE_GENERATION_RULES,
        moods=MOODS,
        default_provider=settings.default_provider,
    )


@router.post("/generate_music", response_model=schemas.GenerationOut)
def generate_music(
    req: schemas.GenerateRequest, db: Session = Depends(get_db)
) -> schemas.GenerationOut:
    try:
        gen = service.generate(db, req)
    except ValueError as exc:  # unknown scene / unsafe prompt
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except KeyError as exc:  # unknown provider
        raise HTTPException(status_code=400, detail=str(exc).strip('"')) from exc
    except NotImplementedError as exc:  # placeholder provider
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    return service.to_out(gen)


@router.get("/history", response_model=list[schemas.GenerationOut])
def history(db: Session = Depends(get_db)) -> list[schemas.GenerationOut]:
    return [service.to_out(g) for g in service.list_history(db)]


@router.delete("/history", status_code=status.HTTP_200_OK)
def clear_history(db: Session = Depends(get_db)) -> dict:
    """Delete every generation (and its audio file)."""
    return {"deleted": service.clear_history(db)}


@router.delete("/history/{gen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_generation(gen_id: str, db: Session = Depends(get_db)) -> None:
    """Delete a single generation (and its audio file)."""
    if not service.delete_generation(db, gen_id):
        raise HTTPException(status_code=404, detail="Generation not found.")
    return None


@router.get("/download/{gen_id}")
def download(
    gen_id: str, download: bool = False, db: Session = Depends(get_db)
) -> FileResponse:
    """Stream a generated audio file.

    Default is ``inline`` (so the <audio> element can play/seek it). Pass
    ``?download=true`` to force a file download with a friendly filename.
    """
    gen = service.get_generation(db, gen_id)
    if gen is None:
        raise HTTPException(status_code=404, detail="Generation not found.")

    path = settings.audio_dir / gen.filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Audio file is missing on disk.")

    media_type = "audio/wav" if gen.audio_format == "wav" else "application/octet-stream"
    nice_name = f"{gen.scene}-{gen.id[:8]}.{gen.audio_format}"
    return FileResponse(
        path,
        media_type=media_type,
        filename=nice_name,
        content_disposition_type="attachment" if download else "inline",
    )
