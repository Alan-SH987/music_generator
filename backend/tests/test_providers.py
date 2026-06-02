"""Mock synthesizer (audio engine) tests."""

from __future__ import annotations

import numpy as np
import pytest

from app.providers import get_provider
from app.providers.base import GenerationRequest
from app.providers.mock import MockProvider


def _request(**kwargs) -> GenerationRequest:
    base = dict(
        scene="tech",
        duration=8,
        bpm=120,
        mood="energetic",
        intensity=6,
        no_drums=False,
        prompt="x",
        seed=7,
    )
    base.update(kwargs)
    return GenerationRequest(**base)


def test_registry_returns_mock() -> None:
    assert isinstance(get_provider("mock"), MockProvider)


def test_unknown_provider_raises() -> None:
    with pytest.raises(KeyError):
        get_provider("nope")


def test_wav_is_valid_stereo(decode_wav) -> None:
    result = MockProvider().generate(_request(duration=5))
    assert result.audio_format == "wav"
    assert result.sample_rate == 44_100
    frames = decode_wav(result.audio)
    assert frames.shape == (5 * 44_100, 2)


def test_no_clipping(decode_wav) -> None:
    frames = decode_wav(MockProvider().generate(_request(intensity=10)).audio)
    assert np.abs(frames).max() < 32_768


def test_seed_is_deterministic() -> None:
    a = MockProvider().generate(_request(seed=42)).audio
    b = MockProvider().generate(_request(seed=42)).audio
    c = MockProvider().generate(_request(seed=43)).audio
    assert a == b
    assert a != c


def test_no_drums_drops_drum_layer() -> None:
    with_drums = MockProvider().generate(_request(scene="sports", no_drums=False))
    no_drums = MockProvider().generate(_request(scene="sports", no_drums=True))
    assert "drums" in with_drums.provider_metadata["layers"]
    assert "drums" not in no_drums.provider_metadata["layers"]


def test_loop_seam_not_outlier_with_drums(decode_wav) -> None:
    """Seam (last->first frame) is no worse than the loudest in-track step."""
    frames = decode_wav(MockProvider().generate(_request(scene="sports", duration=8)).audio)
    diffs = np.abs(np.diff(frames, axis=0))
    seam = int(np.abs(frames[0] - frames[-1]).max())
    assert seam <= 1.3 * int(diffs.max()) + 5


def test_loop_seamless_for_drone(decode_wav) -> None:
    """A drum-free drone has no transients, so the seam must be a normal step."""
    frames = decode_wav(
        MockProvider().generate(_request(scene="meditation", duration=10, no_drums=True)).audio
    )
    diffs = np.abs(np.diff(frames, axis=0))
    seam = int(np.abs(frames[0] - frames[-1]).max())
    p99 = float(np.percentile(diffs, 99.0))
    assert seam <= max(50.0, 4.0 * p99)


@pytest.mark.parametrize(
    "scene", ["finance", "reading", "tech", "meditation", "cafe", "sports", "golf"]
)
def test_every_scene_renders(scene: str, decode_wav) -> None:
    frames = decode_wav(MockProvider().generate(_request(scene=scene, duration=4)).audio)
    assert frames.shape == (4 * 44_100, 2)
    assert np.abs(frames).max() > 0  # not silent
