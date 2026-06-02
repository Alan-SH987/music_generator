# Backend — FastAPI

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API docs (Swagger): http://localhost:8000/docs
- Health: http://localhost:8000/api/health

Or use the helper script (macOS/Linux):

```bash
./run.sh
```

## Tests & linting

Install the dev dependencies, then run the suite (isolated temp DB + audio dir,
no server required) and the linter:

```bash
pip install -r requirements-dev.txt
pytest          # API, audio engine (loop/seed), and copyright-guard tests
ruff check .    # lint
```

Tests live in `tests/`; pytest/ruff config is in `pyproject.toml`.

## Configuration

Environment variables (prefix `MUSICGEN_`), all optional — see `.env.example`:

| Variable                          | Default | Purpose                              |
| --------------------------------- | ------- | ------------------------------------ |
| `MUSICGEN_DEFAULT_PROVIDER`       | `mock`  | Provider used when none is requested |
| `MUSICGEN_CORS_ORIGINS`           | localhost:3000 | Allowed frontend origins (JSON array) |
| `MUSICGEN_MUBERT_API_KEY`         | —       | Future Mubert integration            |
| `MUSICGEN_STABLE_AUDIO_API_KEY`   | —       | Future Stable Audio integration      |
| `MUSICGEN_LOCAL_LOOP_LIBRARY_DIR` | —       | Future local loop library            |

## Storage

- SQLite DB: `storage/app.db`
- Audio files: `storage/audio/<id>.wav`

Both are created automatically on first run.

## Adding a provider

See [`../docs/PROVIDERS.md`](../docs/PROVIDERS.md).
