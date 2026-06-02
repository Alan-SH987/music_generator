"""Mubert provider (placeholder).

Integration outline (see docs/PROVIDERS.md):
  1. Authenticate with ``settings.mubert_api_key``.
  2. Map our :class:`GenerationRequest` to Mubert tags/params
     (scene + mood -> tags, bpm, duration).
  3. Request a render, poll until ready, download the audio.
  4. Return a :class:`ProviderResult` with Mubert's license terms recorded in
     ``license_note`` and ``source_type='mubert'``.
"""

from __future__ import annotations

from ..config import settings
from .base import GenerationRequest, MusicProvider, ProviderResult


class MubertProvider(MusicProvider):
    name = "mubert"
    implemented = False
    description = "Mubert API (commercial royalty-free generative music). Not yet wired up."

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.mubert_api_key

    def generate(self, request: GenerationRequest) -> ProviderResult:
        raise NotImplementedError(
            "MubertProvider is a placeholder. To enable it: set MUSICGEN_MUBERT_API_KEY, "
            "implement the Mubert API calls in this method, and return the rendered audio "
            "as a ProviderResult. See docs/PROVIDERS.md."
        )
