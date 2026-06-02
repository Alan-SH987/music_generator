"""Scene catalogue.

Each scene bundles:
  * UI metadata (labels, description, sensible defaults), and
  * an ``audio`` block of musical hints consumed by the mock synthesizer.

Frequencies are given in Hz for the chord *root*; ``chord`` holds semitone
offsets from that root. ``brightness`` (0..1) controls how much upper-harmonic
"air" is added, and ``pulse`` toggles a subtle rhythmic layer.
"""

from __future__ import annotations

from .safety import assert_safe_prompt

# Mood keywords offered in the UI. Free-form moods are still accepted by the API.
MOODS = ["calm", "focused", "warm", "uplifting", "energetic", "dramatic", "neutral"]

# Pentatonic scales (semitone offsets) used by the mock melody layer. Pentatonics
# avoid dissonant intervals, so random note choices still sound musical.
MAJ_PENT = [0, 2, 4, 7, 9]
MIN_PENT = [0, 3, 5, 7, 10]


SCENES: dict[str, dict] = {
    "finance": {
        "key": "finance",
        "label_en": "Finance Live",
        "label_zh": "财经直播",
        "description": "Professional, confident and steady — for market and finance streams.",
        "default_bpm": 90,
        "default_mood": "focused",
        "default_intensity": 5,
        "default_no_drums": False,
        "prompt_template": (
            "Calm, professional corporate background music for a finance live stream, "
            "subtle synth pads and gentle electric piano, clean and trustworthy."
        ),
        "audio": {
            "base_freq": 130.81, "chord": [0, 7, 12, 16], "brightness": 0.40, "pulse": True,
            "scale": MAJ_PENT, "melody": "sparse", "mel_oct": 2.0,
            "reverb": 0.25, "reverb_decay": 1.2, "energetic": False,
        },
    },
    "reading": {
        "key": "reading",
        "label_en": "Reading",
        "label_zh": "读书",
        "description": "Warm, mellow and unobtrusive — easy to focus and read to.",
        "default_bpm": 70,
        "default_mood": "calm",
        "default_intensity": 4,
        "default_no_drums": True,
        "prompt_template": (
            "Soft, warm lo-fi style instrumental for quiet reading, mellow keys and "
            "gentle pads, relaxed and unobtrusive."
        ),
        "audio": {
            "base_freq": 110.00, "chord": [0, 3, 7, 10], "brightness": 0.20, "pulse": False,
            "scale": MIN_PENT, "melody": "sparse", "mel_oct": 2.0,
            "reverb": 0.30, "reverb_decay": 1.5, "energetic": False,
        },
    },
    "tech": {
        "key": "tech",
        "label_en": "Tech / Futuristic",
        "label_zh": "科技感",
        "description": "Bright, modern and synthetic — product demos and tech content.",
        "default_bpm": 112,
        "default_mood": "energetic",
        "default_intensity": 6,
        "default_no_drums": False,
        "prompt_template": (
            "Bright modern electronic background music with a futuristic feel, clean "
            "synth arpeggios and airy pads, forward-moving and optimistic."
        ),
        "audio": {
            "base_freq": 146.83, "chord": [0, 7, 12, 19], "brightness": 0.80, "pulse": True,
            "scale": MAJ_PENT, "melody": "arp", "mel_oct": 2.0,
            "reverb": 0.22, "reverb_decay": 1.0, "energetic": True,
        },
    },
    "meditation": {
        "key": "meditation",
        "label_en": "Meditation",
        "label_zh": "冥想",
        "description": "Soft drone, no rhythm — calm, spacious and slow.",
        "default_bpm": 60,
        "default_mood": "calm",
        "default_intensity": 3,
        "default_no_drums": True,
        "prompt_template": (
            "Ambient meditation music, slow evolving drones and soft pads, deeply calm "
            "and spacious, no percussion."
        ),
        "audio": {
            "base_freq": 98.00, "chord": [0, 7, 12], "brightness": 0.12, "pulse": False,
            "scale": MIN_PENT, "melody": "none", "mel_oct": 2.0,
            "reverb": 0.50, "reverb_decay": 2.2, "energetic": False,
        },
    },
    "cafe": {
        "key": "cafe",
        "label_en": "Cafe",
        "label_zh": "咖啡馆",
        "description": "Warm and jazzy — a relaxed coffee-shop atmosphere.",
        "default_bpm": 85,
        "default_mood": "warm",
        "default_intensity": 4,
        "default_no_drums": False,
        "prompt_template": (
            "Warm jazzy cafe background music, soft electric piano chords and mellow "
            "bass, relaxed and cozy."
        ),
        "audio": {
            "base_freq": 116.54, "chord": [0, 4, 7, 11], "brightness": 0.35, "pulse": True,
            "scale": MAJ_PENT, "melody": "sparse", "mel_oct": 2.0,
            "reverb": 0.28, "reverb_decay": 1.2, "energetic": False,
        },
    },
    "sports": {
        "key": "sports",
        "label_en": "Sports / Workout",
        "label_zh": "运动",
        "description": "Energetic and driving — workouts and action highlights.",
        "default_bpm": 128,
        "default_mood": "energetic",
        "default_intensity": 7,
        "default_no_drums": False,
        "prompt_template": (
            "Energetic upbeat electronic workout music, driving rhythm and bright "
            "synths, motivating and powerful."
        ),
        "audio": {
            "base_freq": 164.81, "chord": [0, 7, 12], "brightness": 0.70, "pulse": True,
            "scale": MIN_PENT, "melody": "arp", "mel_oct": 2.0,
            "reverb": 0.18, "reverb_decay": 0.8, "energetic": True,
        },
    },
    "golf": {
        "key": "golf",
        "label_en": "Golf",
        "label_zh": "高尔夫",
        "description": "Calm, airy and refined — relaxed outdoor coverage.",
        "default_bpm": 75,
        "default_mood": "calm",
        "default_intensity": 4,
        "default_no_drums": True,
        "prompt_template": (
            "Calm refined acoustic background music for golf coverage, gentle airy "
            "pads and light guitar, open and relaxed."
        ),
        "audio": {
            "base_freq": 110.00, "chord": [0, 4, 7, 14], "brightness": 0.30, "pulse": False,
            "scale": MAJ_PENT, "melody": "sparse", "mel_oct": 2.0,
            "reverb": 0.35, "reverb_decay": 1.6, "energetic": False,
        },
    },
}


def get_scene(key: str) -> dict:
    """Return the scene config, or raise ``ValueError`` for an unknown key."""
    scene = SCENES.get(key)
    if scene is None:
        valid = ", ".join(SCENES.keys())
        raise ValueError(f"Unknown scene '{key}'. Valid scenes: {valid}.")
    return scene


def build_prompt(
    scene_key: str,
    *,
    bpm: int,
    mood: str,
    intensity: int,
    no_drums: bool,
) -> str:
    """Compose a copyright-safe text prompt from a scene + parameters.

    The prompt is always descriptive (mood, instrumentation, tempo). It never
    references artists, songs or "in the style of X" — see :mod:`app.safety`.
    """
    scene = get_scene(scene_key)
    drums = "No drums or percussion. " if no_drums else ""
    prompt = (
        f"{scene['prompt_template']} "
        f"Mood: {mood}. Tempo around {bpm} BPM. {drums}"
        f"Instrumental only — no vocals and no lyrics. "
        f"Energy {intensity}/10. Original, royalty-free background music."
    )
    assert_safe_prompt(prompt)
    return prompt
