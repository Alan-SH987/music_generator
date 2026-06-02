"""Local loop-library provider (placeholder).

Idea: keep a folder of pre-cleared, royalty-free loops on disk
(``settings.local_loop_library_dir``), organised by scene/mood. To "generate",
pick a matching loop and concatenate/crossfade it up to the requested duration.
Fully offline and 100% license-safe (you own/clear the loops).

Integration outline (see docs/PROVIDERS.md):
  1. Index the library by scene/mood/bpm.
  2. Select the best-matching loop for the request.
  3. Tile + crossfade to the requested duration; export as wav/mp3.
  4. Record the loop's source/license in ``license_note``.
"""

from __future__ import annotations

from ..config import settings
from .base import GenerationRequest, MusicProvider, ProviderResult


class LocalLoopProvider(MusicProvider):
    name = "local_loop"
    implemented = False
    description = "Tile/crossfade pre-cleared local loops to length. Offline. Not yet wired up."

    def __init__(self, library_dir=None) -> None:
        self.library_dir = library_dir or settings.local_loop_library_dir

    def generate(self, request: GenerationRequest) -> ProviderResult:
        raise NotImplementedError(
            "LocalLoopProvider is a placeholder. To enable it: set "
            "MUSICGEN_LOCAL_LOOP_LIBRARY_DIR to a folder of cleared royalty-free loops, "
            "implement loop selection + tiling/crossfade in this method, and return the "
            "result as a ProviderResult. See docs/PROVIDERS.md."
        )
