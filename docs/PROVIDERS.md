# Providers

A **provider** turns a normalized `GenerationRequest` into rendered audio plus
copyright-safety metadata. Adding a real music backend is the main extension
point of this project.

## The contract

Every provider subclasses `MusicProvider` (`backend/app/providers/base.py`):

```python
class MusicProvider(ABC):
    name: str = "base"          # stable key used in the API + registry
    implemented: bool = False   # can it actually render audio today?
    description: str = ""        # shown in the UI / docs

    @abstractmethod
    def generate(self, request: GenerationRequest) -> ProviderResult: ...
```

`GenerationRequest` fields: `scene, duration, bpm, mood, intensity, no_drums, prompt`.
The `prompt` is already built **copyright-safe** in `app/scenes.build_prompt`
(no artists, no song titles, instrumental only — see `app/safety.py`).

`ProviderResult` fields you must return:

| field               | meaning                                              |
| ------------------- | ---------------------------------------------------- |
| `audio`             | the rendered file as `bytes`                         |
| `audio_format`      | `"wav"`, `"mp3"`, …                                  |
| `sample_rate`       | e.g. `44100`                                          |
| `license_note`      | human-readable licensing for this track (**saved**)  |
| `source_type`       | short tag, e.g. `"mubert"`, `"stable_audio"`         |
| `provider_metadata` | free-form dict stored alongside the parameters       |

## Registering a provider

Add it to the registry in `backend/app/providers/__init__.py`:

```python
_REGISTRY = {
    MockProvider.name: MockProvider,
    MubertProvider.name: MubertProvider,
    # ...
}
```

It then appears in `GET /api/providers` and can be selected per request via the
`provider` field of `POST /api/generate_music`, or made the server default with
`MUSICGEN_DEFAULT_PROVIDER`.

## Status

| key            | implemented | notes                                                        |
| -------------- | ----------- | ------------------------------------------------------------ |
| `mock`         | ✅          | Offline NumPy synth. Loopable ambient audio. No key needed.  |
| `mubert`       | ⬜          | Commercial generative API. Needs `MUSICGEN_MUBERT_API_KEY`.  |
| `local_loop`   | ⬜          | Tile/crossfade pre-cleared local loops. Fully offline.        |
| `stable_audio` | ⬜          | Stable Audio (open/local or hosted). Prompt-driven.          |

### Mubert (`mubert.py`)
1. Authenticate with `settings.mubert_api_key`.
2. Map scene + mood → Mubert tags; pass `bpm`, `duration`.
3. Request a render, poll until ready, download the track.
4. Record Mubert's license terms in `license_note`, set `source_type="mubert"`.

### Local loop library (`local_loop.py`)
1. Point `MUSICGEN_LOCAL_LOOP_LIBRARY_DIR` at a folder of cleared royalty-free loops.
2. Index by scene/mood/bpm; select the best match.
3. Tile + crossfade to `duration`; export wav/mp3.
4. Put the loop's source/license in `license_note`.

### Stable Audio (`stable_audio.py`)
1. Load the local model (`stable-audio-tools` / diffusers) or auth the hosted API.
2. Feed `request.prompt` + `duration`; use `no_drums` via negative prompting if supported.
3. Encode audio to wav/mp3.
4. Record model + license in `license_note`, set `source_type="stable_audio"`.

## Copyright safety reminder

Keep generation original and instrumental. Do **not** add free-text prompts that
reference real artists, bands or song titles. If you add a free-text prompt input
later, route it through `app.safety.assert_safe_prompt` first.
