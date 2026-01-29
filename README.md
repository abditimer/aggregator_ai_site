# AI News Aggregator
> **Summarised by Abdi Timer and his AI Team**

![AI News Inteface](/Users/abditimer/.gemini/antigravity/brain/538042c8-63be-45f6-9b43-6236df183875/.system_generated/recordings/ui_verification_final_polished_1769724612696/screenshot_ai_news_articles.png)

A minimalist, editorial-style news aggregator that curates the latest updates from the frontier of Artificial Intelligence. Powered by a local LLM (**Qwen 2.5**) to provide instant, intelligent summaries.

## Features

- **Multi-Source Aggregation**: Real-time feeds from OpenAI, Anthropic, Google DeepMind, and Meta AI.
- **Intelligent Summarization**: 
  - **Instant Glances**: Every article gets a one-line AI generated summary.
  - **Trend Analysis**: 30-day and 1-year views feature a "Trend Report" identifying macro patterns (e.g., "The Rise of Open Weights").
- **Privacy-First**: Runs completely locally using SQLite and Ollama.
- **Editorial Design**: Distraction-free reading experience with `Lora` (Serif) typography.

## Tech Stack

- **Frontend**: React, Vite, TailwindCSS (Editorial Theme)
- **Backend**: Python, FastAPI, SQLite
- **AI Engine**: Ollama (running `qwen2.5:0.5b-instruct`)

## Getting Started

### Prerequisites

- [Ollama](https://ollama.ai/) installed and running.
- Node.js & Python 3.10+

### Installation

1. **Clone the repo**
   ```bash
   git clone https://github.com/yourusername/aggregator_ai_site.git
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m backend.database  # Init DB
   ```

3. **Start Servers**
   ```bash
   # Terminal 1: Backend
   source backend/venv/bin/activate
   uvicorn backend.api:app --reload

   # Terminal 2: Frontend
   cd frontend
   npm install
   npm run dev
   ```

4. **Populate Data**
   ```bash
   # Run the scraper and summarizer
   python -m backend.scraper
   python -m backend.summarizer
   ```

## Deployment (GitHub Pages)

This site is deployed as a **Static Snapshot**. The database is not queried in real-time on the live site. Instead, a static JSON file is generated and served.

### 1. Generate Static Data
Dumps the current SQLite database (and generated summaries) into `frontend/public/data.json`:
```bash
python scripts/generate_static_data.py
```

### 2. Build & Deploy
Bundles the React app (with the data file) and pushes to the `gh-pages` branch:
```bash
cd frontend
npm run build
# The build output is in dist/
# Use a tool like gh-pages or manually push dist/ to the gh-pages branch
```

MIT © 2026 Abdi Timer
