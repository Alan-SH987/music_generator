"""Shared pytest fixtures.

Storage is isolated to a throwaway temp dir, configured via env vars *before* the
app is imported (config + DB engine are created at import time). Each test runs
against a clean database and audio folder.
"""

from __future__ import annotations

import io
import os
import shutil
import tempfile
import warnings
import wave
from collections.abc import Callable, Iterator
from pathlib import Path

import numpy as np
import pytest

# --- Isolate storage BEFORE importing the app -------------------------------
_TMP = Path(tempfile.mkdtemp(prefix="musicgen_pytest_"))
os.environ["MUSICGEN_AUDIO_DIR"] = str(_TMP / "audio")
os.environ["MUSICGEN_DATABASE_URL"] = f"sqlite:///{(_TMP / 'test.db').as_posix()}"
os.environ.setdefault("MUSICGEN_DEFAULT_PROVIDER", "mock")

warnings.filterwarnings("ignore", message="Using `httpx` with `starlette.testclient`")

from fastapi.testclient import TestClient  # noqa: E402

from app.config import settings  # noqa: E402
from app.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _cleanup_tmp() -> Iterator[None]:
    yield
    shutil.rmtree(_TMP, ignore_errors=True)


@pytest.fixture(scope="session")
def _client() -> Iterator[TestClient]:
    # The context manager runs the app lifespan (which calls init_db()).
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def client(_client: TestClient) -> TestClient:
    """A TestClient backed by a clean DB + empty audio dir for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    for wav_file in settings.audio_dir.glob("*.wav"):
        wav_file.unlink()
    return _client


@pytest.fixture()
def decode_wav() -> Callable[[bytes], np.ndarray]:
    """Return a helper that decodes WAV bytes into an (n, channels) int64 array."""

    def _decode(data: bytes) -> np.ndarray:
        with wave.open(io.BytesIO(data)) as wav:
            channels = wav.getnchannels()
            frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2")
        return frames.reshape(-1, channels).astype(np.int64)

    return _decode
