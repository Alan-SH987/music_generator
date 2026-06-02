"""Generation service — ties providers, storage and the database together."""

from __future__ import annotations

import json
import secrets
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from . import models, schemas
from .config import settings
from .providers import GenerationRequest as ProviderRequest
from .providers import get_provider
from .scenes import build_prompt, get_scene


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def generate(db: Session, req: schemas.GenerateRequest) -> models.Generation:
    """Render a track, persist the file + metadata, and return the DB row.

    Raises:
        ValueError: unknown scene.
        KeyError: unknown provider.
        NotImplementedError: provider is a not-yet-implemented placeholder.
    """
    get_scene(req.scene)  # validate scene early (raises ValueError)
    provider_name = req.provider or settings.default_provider

    prompt = build_prompt(
        req.scene,
        bpm=req.bpm,
        mood=req.mood,
        intensity=req.intensity,
        no_drums=req.no_drums,
    )

    # Resolve a seed so the track is always reproducible (stored below).
    seed = req.seed if req.seed is not None else secrets.randbelow(2**31)

    provider = get_provider(provider_name)
    result = provider.generate(
        ProviderRequest(
            scene=req.scene,
            duration=req.duration,
            bpm=req.bpm,
            mood=req.mood,
            intensity=req.intensity,
            no_drums=req.no_drums,
            prompt=prompt,
            seed=seed,
        )
    )

    gen_id = uuid.uuid4().hex
    filename = f"{gen_id}.{result.audio_format}"
    (settings.audio_dir / filename).write_bytes(result.audio)

    parameters = {
        "scene": req.scene,
        "duration": req.duration,
        "bpm": req.bpm,
        "mood": req.mood,
        "intensity": req.intensity,
        "no_drums": req.no_drums,
        "seed": seed,
        "sample_rate": result.sample_rate,
        "provider_metadata": result.provider_metadata,
    }

    generation = models.Generation(
        id=gen_id,
        scene=req.scene,
        provider=provider_name,
        prompt=prompt,
        duration=req.duration,
        bpm=req.bpm,
        mood=req.mood,
        intensity=req.intensity,
        no_drums=req.no_drums,
        parameters=json.dumps(parameters, ensure_ascii=False),
        filename=filename,
        audio_format=result.audio_format,
        license_note=result.license_note,
        source_type=result.source_type,
        generated_at=_utcnow_iso(),
    )

    db.add(generation)
    db.commit()
    db.refresh(generation)
    return generation


def list_history(db: Session, limit: int = 100) -> list[models.Generation]:
    """Most recent generations first."""
    return (
        db.query(models.Generation)
        .order_by(models.Generation.generated_at.desc())
        .limit(limit)
        .all()
    )


def get_generation(db: Session, gen_id: str) -> models.Generation | None:
    return db.get(models.Generation, gen_id)


def _remove_audio_file(gen: models.Generation) -> None:
    try:
        (settings.audio_dir / gen.filename).unlink(missing_ok=True)
    except OSError:
        pass  # best-effort; the DB row is the source of truth


def delete_generation(db: Session, gen_id: str) -> bool:
    """Delete one generation (DB row + audio file). Returns False if not found."""
    gen = db.get(models.Generation, gen_id)
    if gen is None:
        return False
    _remove_audio_file(gen)
    db.delete(gen)
    db.commit()
    return True


def clear_history(db: Session) -> int:
    """Delete all generations and their audio files. Returns the count removed."""
    generations = db.query(models.Generation).all()
    for gen in generations:
        _remove_audio_file(gen)
        db.delete(gen)
    db.commit()
    return len(generations)


def to_out(gen: models.Generation) -> schemas.GenerationOut:
    """Serialize a DB row into the API response shape."""
    parameters = json.loads(gen.parameters)
    return schemas.GenerationOut(
        id=gen.id,
        scene=gen.scene,
        provider=gen.provider,
        prompt=gen.prompt,
        duration=gen.duration,
        bpm=gen.bpm,
        mood=gen.mood,
        intensity=gen.intensity,
        no_drums=gen.no_drums,
        seed=parameters.get("seed"),
        parameters=parameters,
        filename=gen.filename,
        audio_format=gen.audio_format,
        license_note=gen.license_note,
        source_type=gen.source_type,
        generated_at=gen.generated_at,
        audio_url=f"/api/download/{gen.id}",
    )
