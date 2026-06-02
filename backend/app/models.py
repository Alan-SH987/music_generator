"""ORM models."""

from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Generation(Base):
    """One generated music track and the metadata needed for copyright safety."""

    __tablename__ = "generations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    scene: Mapped[str] = mapped_column(String, index=True)
    provider: Mapped[str] = mapped_column(String)
    prompt: Mapped[str] = mapped_column(Text)

    # Parameters used for the generation.
    duration: Mapped[int] = mapped_column(Integer)
    bpm: Mapped[int] = mapped_column(Integer)
    mood: Mapped[str] = mapped_column(String)
    intensity: Mapped[int] = mapped_column(Integer)
    no_drums: Mapped[bool] = mapped_column(Boolean, default=False)
    # Full parameter snapshot as JSON (forward-compatible with new fields).
    parameters: Mapped[str] = mapped_column(Text)

    # Stored audio file.
    filename: Mapped[str] = mapped_column(String)
    audio_format: Mapped[str] = mapped_column(String, default="wav")

    # Copyright-safety metadata.
    license_note: Mapped[str] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String)

    # ISO-8601 UTC timestamp (stored as text for portability).
    generated_at: Mapped[str] = mapped_column(String, index=True)
