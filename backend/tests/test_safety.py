"""Copyright-safety guard and prompt-builder tests."""

from __future__ import annotations

import pytest

from app.safety import UnsafePromptError, assert_safe_prompt
from app.scenes import SCENES, build_prompt


def test_safe_prompt_allowed() -> None:
    # The tool's own negative phrasing must pass.
    assert_safe_prompt("Original instrumental background music, no vocals and no lyrics.")


@pytest.mark.parametrize(
    "prompt",
    [
        "in the style of a famous artist",
        "make it sound like that band",
        "a cover of a hit song",
        "song with vocals",
        "please add lyrics",
        "a rap verse over the beat",
    ],
)
def test_unsafe_prompts_rejected(prompt: str) -> None:
    with pytest.raises(UnsafePromptError):
        assert_safe_prompt(prompt)


@pytest.mark.parametrize("scene", list(SCENES.keys()))
def test_built_prompts_are_safe_and_instrumental(scene: str) -> None:
    prompt = build_prompt(scene, bpm=90, mood="calm", intensity=5, no_drums=False)
    # build_prompt calls assert_safe_prompt internally; also sanity-check content.
    assert "no vocals" in prompt.lower()
    assert "instrumental" in prompt.lower()


def test_no_drums_phrasing() -> None:
    prompt = build_prompt("meditation", bpm=60, mood="calm", intensity=3, no_drums=True)
    assert "no drums" in prompt.lower()
