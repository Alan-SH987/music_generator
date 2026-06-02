"""Provider abstraction.

A provider turns a :class:`GenerationRequest` into rendered audio bytes plus the
metadata we need for copyright safety. New backends (Mubert, Stable Audio, a
local loop library, ...) only need to subclass :class:`MusicProvider`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class GenerationRequest:
    """Normalized input handed to a provider."""

    scene: str
    duration: int
    bpm: int
    mood: str
    intensity: int
    no_drums: bool
    prompt: str
    # Deterministic seed (resolved by the service). Same seed + params -> same track.
    seed: int | None = None


@dataclass
class ProviderResult:
    """Rendered audio plus copyright-safety metadata."""

    audio: bytes
    audio_format: str  # e.g. "wav", "mp3"
    sample_rate: int
    license_note: str
    source_type: str
    provider_metadata: dict[str, Any] = field(default_factory=dict)


class MusicProvider(ABC):
    """Base class for all music providers."""

    #: Stable key used in the API and registry.
    name: str = "base"

    #: Whether this provider can actually render audio today.
    implemented: bool = False

    #: Short human-readable description (shown in the UI / docs).
    description: str = ""

    @abstractmethod
    def generate(self, request: GenerationRequest) -> ProviderResult:
        """Render audio for ``request`` and return it with metadata."""
        raise NotImplementedError
