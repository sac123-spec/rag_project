# Repository Guidelines

## Project Structure & Module Organization
`app/` contains the FastAPI service (`api.py`), ingestion/retrieval pipelines, OpenAI helpers, the reranker under `models/`, and `tests/`. `frontend/` hosts the static dashboard that FastAPI serves directly, so no extra build pipeline is required. Runtime artifacts sit in `data/` (PDFs in `raw/`, Chroma in `chroma/`, reranker datasets in `training/`), and `run_api.py` remains the entrypoint; keep new scripts inside `app/` so they inherit `app/config.py`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create a local environment.
- `pip install -r app/requirements.txt` — install backend and training dependencies.
- `python run_api.py` — start FastAPI plus the dashboard at http://localhost:8000.
- `python -m app.ingestion` — ingest PDFs from `data/raw/` into the persistent Chroma store.
- `pytest app/tests -q` — run the smoke suite; use `-k <pattern>` for focused runs.

## Coding Style & Naming Conventions
Follow PEP 8: 4-space indentation, snake_case functions, and PascalCase classes like the Pydantic models in `api.py`. Keep modules type-hinted with small functions and push configuration values into `app/config.py` instead of scattering constants. `frontend/` sticks to modern ES modules, `async`/`await`, and descriptive IDs that match the Tailwind utility classes; add new scripts only under `app/` or `frontend/`.

## Testing Guidelines
Pytest discovers `test_*.py` under `app/tests/`; mirror that layout when covering ingestion, retrieval, or reranker logic. Extend `test_smoke.py` with fast unit tests that monkeypatch OpenAI calls and act on mock `Document` instances or temporary directories so `data/` stays untouched. Run `pytest app/tests -q` before each PR and call out any scenarios that still need live API keys.

## Commit & Pull Request Guidelines
History uses short imperative messages (for example, "Initial commit"), so keep commits under ~72 characters and prefer `<component>: <action>`. PRs must describe the problem, solution, and manual test evidence (shell commands or dashboard screenshots) and link any issue. Flag schema or data changes—especially anything that invalidates `data/chroma/`—and include lint/test results when meaningful.

## Security & Configuration Tips
Never commit `.env` files or artifacts containing `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, `OPENAI_EMBEDDING_MODEL`, or other `RAG_*` variables—load them locally through ignored files or shell exports. Remove sensitive PDFs from `data/raw/` after ingestion, share Chroma indexes or reranker weights only via secure storage, and record expected paths in `app/config.py` so teammates can reproduce safely.
