"""Provider registry and factory."""

from __future__ import annotations

from .base import GenerationRequest, MusicProvider, ProviderResult
from .local_loop import LocalLoopProvider
from .mock import MockProvider
from .mubert import MubertProvider
from .stable_audio import StableAudioProvider

# Registry of provider classes keyed by their stable ``name``.
_REGISTRY: dict[str, type[MusicProvider]] = {
    MockProvider.name: MockProvider,
    MubertProvider.name: MubertProvider,
    LocalLoopProvider.name: LocalLoopProvider,
    StableAudioProvider.name: StableAudioProvider,
}


def available_providers() -> list[type[MusicProvider]]:
    """All registered provider classes (for listing in the API/UI)."""
    return list(_REGISTRY.values())


def get_provider(name: str) -> MusicProvider:
    """Instantiate a provider by name. Raises ``KeyError`` if unknown."""
    cls = _REGISTRY.get(name)
    if cls is None:
        valid = ", ".join(_REGISTRY.keys())
        raise KeyError(f"Unknown provider '{name}'. Valid providers: {valid}.")
    return cls()


__all__ = [
    "GenerationRequest",
    "ProviderResult",
    "MusicProvider",
    "MockProvider",
    "MubertProvider",
    "LocalLoopProvider",
    "StableAudioProvider",
    "available_providers",
    "get_provider",
]
