"""Stable Audio provider (placeholder).

Targets Stability AI's Stable Audio (e.g. the open model run locally, or the
hosted API). This is the path to genuinely original, prompt-driven music.

Integration outline (see docs/PROVIDERS.md):
  1. Load the local model (diffusers/`stable-audio-tools`) or auth the hosted API
     with ``settings.stable_audio_api_key``.
  2. Feed it ``request.prompt`` (already built copyright-safe in app.scenes) plus
     duration; respect ``no_drums`` via negative prompting if supported.
  3. Receive audio, encode to wav/mp3.
  4. Record the model + license terms in ``license_note``,
     ``source_type='stable_audio'``.
"""

from __future__ import annotations

from ..config import settings
from .base import GenerationRequest, MusicProvider, ProviderResult


class StableAudioProvider(MusicProvider):
    name = "stable_audio"
    implemented = False
    description = "Stable Audio (open/local or hosted) — prompt-driven music. Not yet wired up."

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.stable_audio_api_key

    def generate(self, request: GenerationRequest) -> ProviderResult:
        raise NotImplementedError(
            "StableAudioProvider is a placeholder. To enable it: install/host Stable Audio, "
            "implement the inference call in this method using request.prompt + duration, and "
            "return the audio as a ProviderResult. See docs/PROVIDERS.md."
        )
