# Copilot Instructions

## Project Overview

This is an **AI News Aggregator** — a minimalist, editorial-style web application that curates the latest updates from the frontier of Artificial Intelligence. It scrapes blog RSS feeds and HTML pages from OpenAI, Anthropic, Google DeepMind, Meta AI, and NVIDIA, uses a local LLM (Qwen 2.5 via Ollama) to generate article summaries and trend reports, and serves the result as a static snapshot deployed to GitHub Pages.

## Tech Stack

- **Frontend**: React (JSX), Vite, TailwindCSS — located in `frontend/`
- **Backend**: Python 3.11, FastAPI, SQLite — located in `backend/`
- **AI Engine**: Ollama running `qwen2.5:0.5b-instruct` (local, not a cloud API)
- **Tests**: Python `unittest` with `pytest` as the test runner — located in `tests/`
- **Deployment**: GitHub Pages via a static JSON snapshot (`frontend/public/data.json`)

## Repository Structure

```
aggregator_ai_site/
├── backend/
│   ├── api.py          # FastAPI app with /articles/{timeframe} and /summaries/{timeframe} endpoints
│   ├── database.py     # SQLite schema init and DB_PATH constant
│   ├── scraper.py      # RSS + HTML scraping logic (COMPANY_FEEDS dict)
│   ├── summarizer.py   # Ollama-powered article and trend summarisation
│   └── requirements.txt
├── frontend/           # React/Vite app
│   └── src/
│       ├── App.jsx
│       └── components/
├── scripts/
│   └── generate_static_data.py  # Dumps DB → frontend/public/data.json
├── tests/
│   ├── test_api.py
│   ├── test_database.py
│   ├── test_scraper.py
│   └── test_summarizer.py
└── .github/workflows/
    ├── deploy.yml           # Builds & deploys to GitHub Pages on push to main
    └── scheduled_update.yml # Periodic scrape + summarise + deploy
```

## Key Conventions & Patterns

### Backend (Python)

- All backend modules are importable as `backend.<module>` (e.g. `from backend.database import DB_PATH`).
- `DB_PATH` is the single source of truth for the SQLite file location; always import it rather than hardcoding a path.
- `scrape_blogs()` always calls `scrape_anthropic_html()` first (custom HTML scraper) and then skips the `'Anthropic'` entry when iterating `COMPANY_FEEDS` for RSS feeds.
- Tests use an isolated temporary SQLite database (`TEST_DB`) created in `setUp` and deleted in `tearDown` — never use the real `data.db`.
- Use `unittest.mock.patch` / `MagicMock` for network calls (feedparser, httpx, ollama) in tests.
- The `summary` column on the `articles` table starts as `NULL`; `generate_article_summaries()` fills it in.
- Trend summaries (for `30d` / `1y` timeframes) are stored as JSON strings in the `summaries` table.

### Frontend (React/Vite)

- Uses TailwindCSS utility classes with an editorial serif theme (`Lora` font).
- The live site reads from the static `frontend/public/data.json` file — there is **no live API call** in production.
- Run `npm run dev` (inside `frontend/`) for local development with hot-reload.
- Run `npm run build` to produce the deployable `frontend/dist/` output.

## How to Develop Locally

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m backend.database      # Initialise the DB
uvicorn backend.api:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Populate data (requires Ollama running locally)

```bash
python -m backend.scraper
python -m backend.summarizer
python scripts/generate_static_data.py
```

## Running Tests

```bash
# From the repo root (with backend venv active)
pip install -r backend/requirements.txt
pytest tests/
```

Tests mock all external calls (HTTP requests, Ollama). No network access or running Ollama instance is required.

## Deployment

The site is deployed as a **static snapshot**:

1. `scripts/generate_static_data.py` dumps the SQLite DB to `frontend/public/data.json`.
2. `npm run build` bundles the React app (including the data file) into `frontend/dist/`.
3. The `deploy.yml` workflow pushes `frontend/dist/` to the `gh-pages` branch.

Do **not** commit `frontend/dist/` or `backend/data.db` — these are build/runtime artifacts.
