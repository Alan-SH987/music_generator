"""Mock provider — a small multi-layer additive synthesizer.

Renders pleasant, *seamlessly loopable* background music entirely offline with
NumPy, so the whole product works end-to-end without any external API or
credentials. It is intentionally lightweight; genuinely original musicality
comes later from the Mubert / Stable Audio providers.

Layers
------
* **Pad**    — sustained chord (detuned for width) with a slow swell.
* **Bass**   — root an octave down, sustained or pulsing on the beat.
* **Melody** — scale-based arpeggio or sparse line with per-note ADSR.
* **Drums**  — soft kick (+ off-beat hat for energetic scenes); skipped when
               ``no_drums`` is set.
* **Reverb** — FFT convolution with a decaying-noise impulse, giving space and
               natural stereo width.

Seamless loop
-------------
Everything is rendered ``crossfade`` seconds longer than requested, then the
tail is cross-faded back over the head (raised-cosine). Because the loop point
ends up joining two *adjacent* samples of the longer render, the result loops
with no click — regardless of melody notes or reverb tails. Determinism is
controlled by ``request.seed`` (the service assigns one and stores it, so any
track can be reproduced).
"""

from __future__ import annotations

import io
import wave

import numpy as np

from ..scenes import MAJ_PENT, get_scene
from .base import GenerationRequest, MusicProvider, ProviderResult

SAMPLE_RATE = 44_100

LICENSE_NOTE = (
    "Procedurally generated placeholder audio, synthesized locally by the built-in "
    "mock engine. Contains no third-party samples, no vocals and no copyrighted "
    "material — free to use for any purpose (development, testing, streaming, video)."
)


class MockProvider(MusicProvider):
    name = "mock"
    implemented = True
    description = (
        "Offline NumPy synth: pad + bass + melody + drums + reverb, with a "
        "click-free crossfade loop. No API key needed."
    )

    def generate(self, request: GenerationRequest) -> ProviderResult:
        scene = get_scene(request.scene)
        stereo, info = _synthesize(scene["audio"], request)
        audio = _to_wav_bytes(stereo, SAMPLE_RATE)
        return ProviderResult(
            audio=audio,
            audio_format="wav",
            sample_rate=SAMPLE_RATE,
            license_note=LICENSE_NOTE,
            source_type="mock_synthesis",
            provider_metadata={
                "engine": "numpy-additive-synth-v2",
                "sample_rate": SAMPLE_RATE,
                "channels": 2,
                "loopable": True,
                **info,
            },
        )


# --------------------------------------------------------------------------- #
# Small DSP helpers
# --------------------------------------------------------------------------- #
def _lf(freq: float, duration: float) -> float:
    """Snap ``freq`` to a whole number of cycles over ``duration`` (loop-friendly)."""
    cycles = max(1, round(freq * duration))
    return cycles / duration


def _next_fast_len(n: int) -> int:
    """Smallest 5-smooth integer >= n (keeps FFT sizes fast without huge padding)."""
    while True:
        m = n
        for p in (2, 3, 5):
            while m % p == 0:
                m //= p
        if m == 1:
            return n
        n += 1


def _add(buffer: np.ndarray, segment: np.ndarray, start: int) -> None:
    """Add ``segment`` into ``buffer`` at ``start`` with bounds clipping."""
    if start < 0:
        segment = segment[-start:]
        start = 0
    end = min(len(buffer), start + len(segment))
    if end > start:
        buffer[start:end] += segment[: end - start]


def _adsr(
    n: int, sr: int, attack: float, decay: float, sustain: float, release: float
) -> np.ndarray:
    """Attack-decay-sustain-release envelope of length ``n`` samples."""
    env = np.zeros(n, dtype=np.float64)
    a = max(1, int(attack * sr))
    d = max(1, int(decay * sr))
    r = max(1, int(release * sr))

    ai = min(a, n)
    if ai > 0:
        env[:ai] = np.linspace(0.0, 1.0, ai, endpoint=False)

    de = min(a + d, n)
    if de > ai:
        env[ai:de] = np.linspace(1.0, sustain, de - ai, endpoint=False)

    se = max(de, n - r)
    if se > de:
        env[de:se] = sustain

    if n > se:
        start_val = env[se - 1] if se > 0 else sustain
        env[se:] = np.linspace(start_val, 0.0, n - se)
    return env


def _crossfade_loop(x: np.ndarray, n: int, xfade: int) -> np.ndarray:
    """Turn a length ``n + xfade`` signal into a seamless length-``n`` loop."""
    out = x[:n].copy()
    if xfade <= 0:
        return out
    fade = 0.5 - 0.5 * np.cos(np.linspace(0.0, np.pi, xfade, endpoint=False))  # 0 -> 1
    head = x[:xfade]
    tail = x[n : n + xfade]
    out[:xfade] = head * fade + tail * (1.0 - fade)
    return out


# --------------------------------------------------------------------------- #
# Instrument layers
# --------------------------------------------------------------------------- #
def _pad(
    t: np.ndarray, duration: float, root: float, chord: list[int], brightness: float
) -> np.ndarray:
    out = np.zeros_like(t)
    for i, semitone in enumerate(chord):
        f = _lf(root * (2 ** (semitone / 12.0)), duration)
        amp = 0.5 / (1 + i * 0.4)
        out += amp * np.sin(2 * np.pi * f * t)
        # Subtle detuned layer for chorus/width (seam handled by the crossfade).
        out += amp * 0.5 * np.sin(2 * np.pi * (f * 1.004) * t)
        if brightness > 0:
            out += amp * (0.3 * brightness) * np.sin(2 * np.pi * _lf(2 * f, duration) * t)
    swell = 0.82 + 0.18 * np.sin(2 * np.pi * _lf(1.0 / 8.0, duration) * t)  # ~8s swell
    return out * swell


def _bass(
    t: np.ndarray,
    duration: float,
    root: float,
    beat_period: float,
    pulse: bool,
    no_drums: bool,
) -> np.ndarray:
    f = _lf(root / 2.0, duration)
    tone = np.sin(2 * np.pi * f * t) + 0.22 * np.sin(2 * np.pi * _lf(2 * f, duration) * t)
    if pulse and not no_drums:
        phase = np.mod(t, beat_period)
        env = 0.35 + 0.65 * np.exp(-phase * 5.0)
        return tone * env
    return tone * 0.55


def _melody(
    M: int,
    sr: int,
    rng: np.random.Generator,
    root: float,
    scale: list[int],
    style: str,
    beat_period: float,
    brightness: float,
    mel_oct: float,
) -> np.ndarray:
    out = np.zeros(M, dtype=np.float64)
    if style == "none":
        return out

    if style == "arp":
        step = beat_period / 2.0
        ring = step * 1.8
        adsr = (0.004, 0.06, 0.55, step * 0.95)
        rest_p = 0.05
    else:  # "sparse"
        step = beat_period * 2.0
        ring = step * 1.4
        adsr = (0.03, 0.18, 0.6, ring * 0.7)
        rest_p = 0.35

    partials = [
        (1, 1.0),
        (2, 0.5 * brightness + 0.25),
        (3, 0.28 * brightness + 0.05),
        (4, 0.12 * brightness),
    ]

    degrees = [
        root * mel_oct * (2 ** ((s + 12 * octv) / 12.0))
        for octv in (0, 1)
        for s in scale
    ]

    nlen = max(1, int(ring * sr))
    nt = np.arange(nlen) / sr
    idx = len(degrees) // 3
    pos = 0.0
    duration = M / sr
    while pos < duration:
        idx = int(np.clip(idx + int(rng.integers(-2, 3)), 0, len(degrees) - 1))
        if rng.random() >= rest_p:
            f = degrees[idx]
            sig = np.zeros(nlen, dtype=np.float64)
            for mult, amp in partials:
                if amp > 0:
                    sig += amp * np.sin(2 * np.pi * f * mult * nt)
            env = _adsr(nlen, sr, *adsr)
            vel = 0.55 + 0.45 * rng.random()
            _add(out, sig * env * vel, int(pos * sr))
        pos += step

    peak = float(np.max(np.abs(out))) or 1.0
    return out / peak * 0.8


def _drums(
    M: int,
    sr: int,
    rng: np.random.Generator,
    beat_period: float,
    intensity: float,
    energetic: bool,
) -> np.ndarray:
    out = np.zeros(M, dtype=np.float64)
    duration = M / sr
    n_beats = int(duration / beat_period) + 1

    klen = int(0.2 * sr)
    kt = np.arange(klen) / sr
    pitch = 120.0 * np.exp(-kt * 28.0) + 45.0  # pitch-swept kick
    kick = np.sin(2 * np.pi * np.cumsum(pitch) / sr) * np.exp(-kt * 11.0)

    for b in range(n_beats):
        _add(out, kick * 0.9, int(b * beat_period * sr))
        if energetic:
            hlen = int(0.06 * sr)
            hat = rng.standard_normal(hlen) * np.exp(-np.arange(hlen) / sr * 55.0)
            _add(out, hat * 0.18, int((b + 0.5) * beat_period * sr))

    return out * (0.5 + 0.6 * intensity)


def _reverb_stereo(
    dry: np.ndarray,
    sr: int,
    rng: np.random.Generator,
    amount: float,
    decay_s: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Stereo reverb via FFT convolution with two decaying-noise impulses."""
    M = len(dry)
    if amount <= 0:
        return dry.copy(), dry.copy()

    ir_len = max(1, int(decay_s * sr))
    n_fft = _next_fast_len(M + ir_len)
    spectrum = np.fft.rfft(dry, n=n_fft)
    dry_peak = float(np.max(np.abs(dry))) or 1.0

    # Low-pass kernel: a raw white-noise impulse sounds hissy/metallic, so we
    # smooth the noise into a darker, more natural diffuse tail.
    w = max(5, int(sr * 0.0004))
    smooth = np.hanning(w)
    smooth /= smooth.sum()

    def make_ir() -> np.ndarray:
        idx = np.arange(ir_len)
        env = np.exp(-idx / (decay_s * sr / 3.0))
        noise = np.convolve(rng.standard_normal(ir_len), smooth, mode="same")
        ir = noise * env
        ir[0] += 1.0  # keep some direct signal
        return ir

    def wet(ir: np.ndarray) -> np.ndarray:
        y = np.fft.irfft(spectrum * np.fft.rfft(ir, n=n_fft), n=n_fft)[:M]
        peak = float(np.max(np.abs(y))) or 1.0
        return y / peak * dry_peak

    wet_l = wet(make_ir())
    wet_r = wet(make_ir())
    left = dry * (1.0 - amount) + wet_l * amount
    right = dry * (1.0 - amount) + wet_r * amount
    return left, right


# --------------------------------------------------------------------------- #
# Top-level synthesis
# --------------------------------------------------------------------------- #
def _synthesize(cfg: dict, req: GenerationRequest) -> tuple[np.ndarray, dict]:
    sr = SAMPLE_RATE
    rng = np.random.default_rng(req.seed)

    duration = max(1, int(req.duration))
    n = sr * duration
    xfade = max(1, int(min(0.5, duration * 0.25) * sr))
    M = n + xfade
    t = np.arange(M) / sr
    # Sustained layers are tuned to be periodic over the *loop length* n, so they
    # need no crossfade work; the melody/drums/reverb are what the crossfade joins.
    loop_dur = n / sr

    root = float(cfg["base_freq"])
    chord = list(cfg["chord"])
    brightness = float(cfg["brightness"])
    pulse = bool(cfg["pulse"])
    scale = list(cfg.get("scale", MAJ_PENT))
    mel_style = cfg.get("melody", "sparse")
    mel_oct = float(cfg.get("mel_oct", 2.0))
    reverb_amount = float(cfg.get("reverb", 0.25))
    reverb_decay = float(cfg.get("reverb_decay", 1.3))
    energetic = bool(cfg.get("energetic", False))
    intensity = req.intensity / 10.0

    # Beat grid: a whole number of beats over the *looped* length n, so the
    # downbeat lands on the loop point.
    beats = max(1, round((n / sr) * req.bpm / 60.0))
    beat_period = (n / sr) / beats

    drums_on = pulse and not req.no_drums

    pad = _pad(t, loop_dur, root, chord, brightness)
    bass = _bass(t, loop_dur, root, beat_period, pulse, req.no_drums)
    melody = _melody(M, sr, rng, root, scale, mel_style, beat_period, brightness, mel_oct)

    dry = pad * 0.5 + bass * 0.5 + melody * 0.6
    if drums_on:
        dry = dry + _drums(M, sr, rng, beat_period, intensity, energetic) * 0.8

    dry *= 0.55 + 0.5 * intensity

    left, right = _reverb_stereo(dry, sr, rng, reverb_amount, reverb_decay)
    left = _crossfade_loop(left, n, xfade)
    right = _crossfade_loop(right, n, xfade)
    stereo = np.stack([left, right], axis=1)

    # Normalize, then gentle soft-clip for glue, then a final safety normalize.
    peak = float(np.max(np.abs(stereo))) or 1.0
    stereo = stereo / peak * 0.95
    stereo = np.tanh(stereo * 1.1) / np.tanh(1.1)
    peak = float(np.max(np.abs(stereo))) or 1.0
    stereo = stereo / peak * 0.95

    info = {
        "seed": int(req.seed) if req.seed is not None else None,
        "layers": ["pad", "bass"]
        + (["melody"] if mel_style != "none" else [])
        + (["drums"] if drums_on else []),
        "reverb": round(reverb_amount, 3),
        "crossfade_ms": round(xfade / sr * 1000.0, 1),
        "bpm_effective": round(60.0 / beat_period, 2),
    }
    return stereo, info


def _to_wav_bytes(stereo: np.ndarray, sample_rate: int) -> bytes:
    """Encode an (n, 2) float array in [-1, 1] as 16-bit PCM WAV bytes."""
    clipped = np.clip(stereo, -1.0, 1.0)
    pcm = (clipped * 32767.0).astype("<i2")  # interleaved L,R little-endian
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav:
        wav.setnchannels(2)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm.tobytes())
    return buffer.getvalue()
