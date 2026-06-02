"""Pydantic request/response schemas (the API contract)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Body for ``POST /api/generate_music``."""

    scene: str = Field(..., description="Scene key, e.g. 'finance', 'meditation'.")
    duration: int = Field(60, ge=5, le=600, description="Length in seconds.")
    bpm: int = Field(90, ge=40, le=200, description="Tempo in beats per minute.")
    mood: str = Field("calm", description="Mood keyword, e.g. 'calm', 'energetic'.")
    intensity: int = Field(5, ge=1, le=10, description="Overall energy, 1-10.")
    no_drums: bool = Field(False, description="If true, omit any rhythmic/percussive layer.")
    provider: str | None = Field(
        None, description="Provider key. Defaults to the server's configured provider."
    )
    seed: int | None = Field(
        None,
        ge=0,
        description="Optional seed for reproducible output. Omit for a fresh variation.",
    )


class GenerationOut(BaseModel):
    """A generation record returned by the API."""

    id: str
    scene: str
    provider: str
    prompt: str

    duration: int
    bpm: int
    mood: str
    intensity: int
    no_drums: bool
    seed: int | None = None
    parameters: dict[str, Any]

    filename: str
    audio_format: str

    # Copyright-safety metadata.
    license_note: str
    source_type: str

    generated_at: str
    # Relative URL; the frontend prepends the API base.
    audio_url: str


class SceneOut(BaseModel):
    """Scene metadata for populating the UI."""

    key: str
    label_en: str
    label_zh: str
    description: str
    default_bpm: int
    default_mood: str
    default_intensity: int
    default_no_drums: bool


class ProviderOut(BaseModel):
    key: str
    implemented: bool
    description: str


class PolicyOut(BaseModel):
    policy: str
    rules: list[str]
    moods: list[str]
    default_provider: str
