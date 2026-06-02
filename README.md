# 🎵 Royalty-Free Music Generator

A web tool for generating **original, instrumental, royalty-free background
music** for live streams and videos. Pick a scene → tune parameters → generate →
loop → download. Every track is saved with full metadata for copyright safety.

This is the **MVP**: a fully working end-to-end product built around a clean
provider abstraction, so swapping in a real engine (Mubert, Stable Audio, a local
loop library) later is a drop-in change.

---

## Features

- **Scenes**: Finance Live (财经直播), Reading (读书), Tech (科技感),
  Meditation (冥想), Cafe (咖啡馆), Sports (运动), Golf (高尔夫)
- **Parameters**: duration, BPM, mood, intensity, "no drums" toggle, provider selector
- **Player** with a **Loop** switch, **Download**, **Regenerate (same seed)** /
  **New variation**, and the generated **prompt** (with copy-to-clipboard)
- **History** of past generations — click to reload, ✕ to delete, or clear all
- **Copyright safety**: per-track metadata (provider, prompt, parameters,
  `generated_at`, `license_note`, `source_type`) and a visible policy panel
- **Provider abstraction**: `MockProvider` (working), plus `MubertProvider`,
  `LocalLoopProvider`, `StableAudioProvider` placeholders

The MVP ships a **mock provider** — a small multi-layer NumPy synth (pad + bass +
melody/arpeggio + soft drums + reverb) that renders **click-free, seamlessly
loopable** stereo WAV, with no API keys and no internet. Output is reproducible
via an optional `seed` (omit it for a fresh variation).

## Tech stack

| Layer    | Tech                                  |
| -------- | ------------------------------------- |
| Frontend | Next.js (App Router) + TypeScript     |
| Backend  | FastAPI + SQLAlchemy                   |
| Database | SQLite (`backend/storage/app.db`)     |
| Storage  | Local files (`backend/storage/audio`) |

---

## Quick start

### Fastest: Docker

With Docker + Docker Compose:

```bash
docker compose up --build
```

Frontend → http://localhost:3000 · Backend → http://localhost:8000 (state persists
in the `backend-storage` volume; stop with `docker compose down`).

### Or run locally

You need **Python 3.10+** and **Node 18+**. Run the backend and frontend in two
terminals — or use the **Makefile** (`make install`, then `make backend` /
`make frontend`; `make help` lists all targets).

#### 1. Backend (FastAPI, port 8000)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

> Shortcut: `./backend/run.sh` does the venv + install + run for you (macOS/Linux).

Run the tests (isolated temp DB, no server needed):

```bash
cd backend && pip install -r requirements-dev.txt && pytest
```

#### 2. Frontend (Next.js, port 3000)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

If your backend is not on `http://localhost:8000`, copy `.env.local.example` to
`.env.local` and set `NEXT_PUBLIC_API_BASE`.

---

## Development

```bash
make install         # backend venv + dev deps, and frontend deps
make backend         # run FastAPI (reload) on :8000
make frontend        # run Next.js dev on :3000
make test            # backend pytest suite
make lint            # ruff (backend)
make typecheck       # tsc --noEmit (frontend)
make up / make down  # full stack via Docker Compose
```

Backend tests live in `backend/tests/` (pytest, isolated to a throwaway temp
DB + audio dir). CI runs ruff + pytest and the frontend type-check + build on
every push — see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## API

Base URL: `http://localhost:8000/api`

| Method | Path                  | Description                                  |
| ------ | --------------------- | -------------------------------------------- |
| GET    | `/health`             | Health check                                 |
| GET    | `/scenes`             | Scene catalogue + per-scene defaults         |
| GET    | `/providers`          | Providers and whether each is implemented    |
| GET    | `/policy`             | Copyright policy, rules, moods, default provider |
| POST   | `/generate_music`     | Generate a track; returns the record         |
| GET    | `/history`            | All generations, newest first                |
| DELETE | `/history`            | Delete all generations (+ their audio files) |
| DELETE | `/history/{id}`       | Delete one generation (+ its audio file)     |
| GET    | `/download/{id}`      | Stream audio (`?download=true` to download)  |

**Generate request body**

```json
{
  "scene": "finance",
  "duration": 60,
  "bpm": 90,
  "mood": "focused",
  "intensity": 5,
  "no_drums": false,
  "provider": "mock",
  "seed": 12345
}
```

`provider` is optional (defaults to `MUSICGEN_DEFAULT_PROVIDER`, i.e. `mock`).
`seed` is optional too — pass it to reproduce a track exactly, or omit it for a
new variation (the server records the seed it used in the track's parameters).

---

## Copyright safety

By design the tool only produces original, instrumental music:

- **No vocals, no lyrics.**
- **No imitation** of any specific artist, band or singer.
- **No real song/album titles** used as prompts.
- Prompts are built from a fixed scene catalogue + structured parameters and
  pass through `app.safety.assert_safe_prompt`.
- Every generation stores `provider`, `prompt`, `parameters`, `generated_at`,
  `license_note` and `source_type`, surfaced in the UI's license panel.

See [`docs/PROVIDERS.md`](docs/PROVIDERS.md) before wiring up a real engine.

---

## Project structure

```
royalty-free-music-generator/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app + CORS + lifespan
│   │   ├── routes.py        # /api endpoints
│   │   ├── service.py       # generate → store file + DB row
│   │   ├── scenes.py        # scene catalogue + safe prompt builder
│   │   ├── safety.py        # copyright policy + prompt guard
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── models.py        # SQLAlchemy ORM
│   │   ├── database.py      # SQLite engine/session
│   │   ├── config.py        # settings (env-driven)
│   │   └── providers/       # provider abstraction
│   │       ├── base.py      # MusicProvider ABC + dataclasses
│   │       ├── mock.py      # ✅ offline NumPy synth
│   │       ├── mubert.py            # ⬜ placeholder
│   │       ├── local_loop.py        # ⬜ placeholder
│   │       └── stable_audio.py      # ⬜ placeholder
│   ├── tests/               # pytest suite (api / providers / safety)
│   ├── storage/audio/       # generated audio files
│   ├── requirements.txt     # runtime deps
│   ├── requirements-dev.txt # + pytest, ruff
│   ├── pyproject.toml       # pytest + ruff config
│   ├── Dockerfile
│   └── run.sh
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # main UI
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   └── components/      # SceneSelector, ParameterControls, AudioPlayer,
│   │                        # HistoryList, CopyrightNotice
│   ├── lib/                 # api client, types, formatters
│   └── Dockerfile
├── .github/workflows/ci.yml # ruff + pytest + frontend build
├── docker-compose.yml       # one-command full stack
├── Makefile                 # make help
└── docs/PROVIDERS.md
```

## Roadmap

- Implement a real provider (start with `LocalLoopProvider` or `StableAudioProvider`).
- MP3 export (via `ffmpeg`/`pydub`).
- Even richer arrangements (chord progressions, more instruments).
- Tagging / search over history; favorites.
