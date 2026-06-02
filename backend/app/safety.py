"""Copyright-safety policy and prompt guard.

The MVP only ever builds prompts from a fixed scene catalogue plus structured
parameters, so prompts are safe by construction. This module centralises the
policy text (shown in the UI) and provides :func:`assert_safe_prompt`, a guard
that becomes important the moment free-text prompts are added later.
"""

from __future__ import annotations

COPYRIGHT_POLICY = (
    "All tracks are generated as original, instrumental, royalty-free background "
    "music intended for live streams and videos. By design this tool does not "
    "generate vocals or lyrics, does not imitate any specific artist or band, and "
    "never uses real song or album titles as prompts. Every generation is saved "
    "with its provider, prompt, parameters, timestamp, license note and source "
    "type so you always have a clear record of how a track was made."
)

# Shown to the user as a checklist of guarantees.
SAFE_GENERATION_RULES = [
    "No vocals and no lyrics — instrumental only.",
    "No imitation of any specific artist, band or singer.",
    "No real song, album or recording titles used as prompts.",
    "Original generation only; no third-party samples in the mock provider.",
    "Full metadata (provider, prompt, parameters, license, timestamp) saved per track.",
]

# Phrases that signal an attempt to copy a known work/artist or to add vocals.
# These target *requests for* such content; the tool's own negative phrasing
# ("instrumental only, no vocals, no lyrics") is intentionally allowed.
# Matching is case-insensitive substring, mainly a guard for future free-text input.
BANNED_PHRASES = [
    "in the style of",
    "sounds like",
    "sound like",
    "cover of",
    "remix of",
    "feat.",
    "featuring ",
    "with vocals",
    "with lyrics",
    "add vocals",
    "add lyrics",
    "vocal track",
    "rap verse",
    "rapping",
]


class UnsafePromptError(ValueError):
    """Raised when a prompt violates the copyright-safety policy."""


def assert_safe_prompt(prompt: str) -> None:
    """Raise :class:`UnsafePromptError` if the prompt looks copyright-unsafe."""
    lowered = prompt.lower()
    for phrase in BANNED_PHRASES:
        if phrase in lowered:
            raise UnsafePromptError(
                f"Prompt rejected for copyright safety (matched '{phrase.strip()}'). "
                "Prompts must be original and instrumental, and must not reference "
                "artists, songs or vocals."
            )
