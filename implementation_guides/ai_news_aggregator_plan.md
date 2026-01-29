# AI News Aggregator - Simplified Project Plan

## Project Overview

**Goal**: Build a simple website that summarizes AI news from top companies and key people across 4 timeframes.

**Principle**: Start minimal, scale later.

---

## Features

### Time Aggregations
- **1 Day**: Today's updates
- **7 Days**: Weekly digest
- **30 Days**: Monthly summary
- **1 Year**: Annual review

### Data Sources (That's It)

#### Tech Companies (News Pages/Blogs Only)
- OpenAI blog
- Anthropic blog
- Google DeepMind blog
- Meta AI blog

**Total Sources**: 4 company blogs

*Note: Twitter/X sources removed for initial build. Can add later.*

---

## Architecture (Simplified)

```
┌─────────────────────────────────────────┐
│          Data Collection                 │
│  - Blog scrapers (RSS feeds)            │
│  - Twitter scrapers (API or web)        │
│  (runs every 6 hours via cron)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│          SQLite Database                 │
│  - articles table                        │
│  - summaries table                       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       Summarization (LLM)                │
│  - Group by timeframe                    │
│  - Generate summary via API              │
│  (runs daily)                            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│        FastAPI Backend                   │
│  - GET /summaries/{timeframe}            │
│  - GET /articles (optional)              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         React Frontend                   │
│  - 4 tabs (1d, 7d, 30d, 1y)             │
│  - Display summaries                     │
│  - Link to source articles              │
└─────────────────────────────────────────┘
```

---

## Tech Stack (Minimal)

### Backend
- **Python 3.11+**
- **FastAPI** (API server)
- **SQLite** (database - easy, no setup)
- **feedparser** (RSS parsing)
- **httpx** (HTTP requests)
- **ollama** (local LLM - free, runs on your machine)

### Frontend
- **React** (Vite)
- **TailwindCSS** (styling)
- **date-fns** (date handling)

### Deployment
- **Backend**: Railway or Render (free tier)
- **Frontend**: Vercel (free tier)
- **Database**: SQLite file (commit to repo or use volume)
- **LLM**: Ollama running locally (development) or on server (production)

### Total Cost: $0/month (everything runs locally or on free tiers)

---

## Database Schema (Simple)

```sql
-- Articles: everything we scrape
CREATE TABLE articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content TEXT,
    published_at TIMESTAMP NOT NULL,
    source_type TEXT, -- 'blog' or 'twitter'
    source_name TEXT, -- 'OpenAI' or 'Sam Altman'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Summaries: LLM-generated summaries per timeframe
CREATE TABLE summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timeframe TEXT NOT NULL, -- '1d', '7d', '30d', '1y'
    summary_text TEXT NOT NULL,
    article_count INTEGER,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_articles_published ON articles(published_at);
CREATE INDEX idx_summaries_timeframe ON summaries(timeframe, generated_at);
```

---

## Implementation Plan

### Week 1: Core Pipeline
**Goal**: Scrape one source, generate one summary

1. Set up project structure
2. Create SQLite database
3. Build scraper for OpenAI blog (RSS)
4. Store articles in database
5. Write script to generate 7-day summary using OpenAI API
6. Test end-to-end

**Deliverable**: Command-line tool that prints a 7-day summary

---

### Week 2: All Sources + All Timeframes
**Goal**: Complete data pipeline

1. Add scrapers for all 4 company blogs
2. Add Twitter scrapers for 6 people (using nitter or Twitter API)
3. Generate summaries for all 4 timeframes (1d, 7d, 30d, 1y)
4. Build FastAPI with 2 endpoints:
   - `GET /summaries/{timeframe}` - get latest summary
   - `GET /articles?days=X` - get recent articles (optional)
5. Set up cron job to run scrapers every 6 hours

**Deliverable**: Working API that returns summaries

---

### Week 3: Simple Frontend
**Goal**: Deployable website

1. Create React app with Vite
2. Build 4-tab layout (1d, 7d, 30d, 1y)
3. Fetch and display summaries from API
4. Add basic styling with Tailwind
5. Deploy frontend to Vercel
6. Deploy backend to Railway/Render

**Deliverable**: Live website at yourdomain.vercel.app

---

## Project Structure

```
ai-news-aggregator/
├── backend/
│   ├── scraper.py           # All scraping logic
│   ├── summarizer.py        # LLM summarization
│   ├── database.py          # SQLite setup + queries
│   ├── api.py               # FastAPI app
│   ├── config.py            # API keys, settings
│   ├── requirements.txt
│   └── data.db              # SQLite database file
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   ├── components/
│   │   │   └── TimeframeTabs.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── index.html
└── README.md
```

---

## Data Sources Details

### Company Blogs (RSS Feeds)
```python
COMPANY_FEEDS = {
    'OpenAI': 'https://openai.com/blog/rss.xml',
    'Anthropic': 'https://www.anthropic.com/news/rss.xml',
    'Google DeepMind': 'https://deepmind.google/blog/rss.xml',
    'Meta AI': 'https://ai.meta.com/blog/rss/'
}
```

---

## Week 1 Implementation Guide

### Step 0: Install Ollama
```bash
# Install Ollama (https://ollama.ai)
# macOS/Linux:
curl -fsSL https://ollama.com/install.sh | sh

# Pull a model (we'll use llama3.1 - fast and good quality)
ollama pull llama3.1

# Test it
ollama run llama3.1 "Hello!"
```

**Model Recommendations:**
- `llama3.1` (8B): Fast, good quality, ~5GB RAM
- `llama3.1:70b`: Better quality, slower, ~40GB RAM (if you have GPU)
- `mistral`: Alternative, similar performance to llama3.1

**Hardware Requirements:**
- Minimum: 8GB RAM for llama3.1
- Recommended: 16GB RAM + GPU for faster generation
- Generation time: 30-60 seconds for summaries on CPU

### Step 1: Setup
```bash
mkdir ai-news-aggregator
cd ai-news-aggregator
mkdir backend frontend

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install fastapi uvicorn feedparser httpx python-dotenv ollama
```

**Create `requirements.txt`:**
```
fastapi==0.109.0
uvicorn==0.27.0
feedparser==6.0.10
httpx==0.26.0
python-dotenv==1.0.0
ollama==0.1.6
```

Install with: `pip install -r requirements.txt`

### Step 2: Database (`database.py`)
```python
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS articles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  url TEXT UNIQUE NOT NULL,
                  title TEXT NOT NULL,
                  content TEXT,
                  published_at TIMESTAMP NOT NULL,
                  source_type TEXT,
                  source_name TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS summaries
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timeframe TEXT NOT NULL,
                  summary_text TEXT NOT NULL,
                  article_count INTEGER,
                  generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    conn.commit()
    conn.close()
```

### Step 3: Scraper (`scraper.py`)
```python
import feedparser
from datetime import datetime
import sqlite3

COMPANY_FEEDS = {
    'OpenAI': 'https://openai.com/blog/rss.xml',
    # Add others
}

def scrape_blogs():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    for company, feed_url in COMPANY_FEEDS.items():
        feed = feedparser.parse(feed_url)
        
        for entry in feed.entries:
            try:
                c.execute('''INSERT OR IGNORE INTO articles 
                           (url, title, content, published_at, source_type, source_name)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                         (entry.link, 
                          entry.title, 
                          entry.get('summary', ''),
                          datetime(*entry.published_parsed[:6]),
                          'blog',
                          company))
            except Exception as e:
                print(f"Error: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    scrape_blogs()
    print("Scraping complete!")
```

### Step 4: Summarizer (`summarizer.py`)
```python
import ollama
import sqlite3
from datetime import datetime, timedelta

def get_articles_for_timeframe(days):
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    c.execute('''SELECT title, content, source_name, published_at 
                 FROM articles 
                 WHERE published_at > ? 
                 ORDER BY published_at DESC''', (cutoff,))
    
    articles = c.fetchall()
    conn.close()
    return articles

def generate_summary(timeframe_days):
    articles = get_articles_for_timeframe(timeframe_days)
    
    if not articles:
        return "No articles found for this timeframe."
    
    # Format articles for prompt
    articles_text = "\n\n".join([
        f"**{article[2]}** - {article[0]}\n{article[1][:500]}..."  # Truncate content
        for article in articles
    ])
    
    prompt = f"""Summarize the following AI news from the past {timeframe_days} days.
Focus on key developments, announcements, and trends.
Keep the summary concise but informative (3-5 paragraphs).

{articles_text}

Summary:"""
    
    # Use Ollama for local LLM
    response = ollama.chat(
        model='llama3.1',
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    summary = response['message']['content']
    
    # Save to database
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO summaries (timeframe, summary_text, article_count)
                 VALUES (?, ?, ?)''',
             (f'{timeframe_days}d', summary, len(articles)))
    conn.commit()
    conn.close()
    
    return summary

if __name__ == "__main__":
    print("Generating 7-day summary...")
    summary = generate_summary(7)
    print("\n" + "="*50)
    print(summary)
    print("="*50)
```

### Step 5: Test
```bash
# Make sure Ollama is running (it should auto-start)
# If not: ollama serve

# Initialize database
python -c "from database import init_db; init_db()"

# Run scraper
python scraper.py

# Generate summary (this will take 30-60 seconds with local LLM)
python summarizer.py
```

**Expected output**: A 3-5 paragraph summary of recent AI news from the 4 company blogs.

---

## Week 2: FastAPI Backend

```python
# api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/summaries/{timeframe}")
def get_summary(timeframe: str):
    """Get latest summary for timeframe (1d, 7d, 30d, 1y)"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    c.execute('''SELECT summary_text, article_count, generated_at
                 FROM summaries
                 WHERE timeframe = ?
                 ORDER BY generated_at DESC
                 LIMIT 1''', (timeframe,))
    
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            "timeframe": timeframe,
            "summary": result[0],
            "article_count": result[1],
            "generated_at": result[2]
        }
    return {"error": "No summary found"}

@app.get("/articles")
def get_articles(days: int = 7):
    """Get recent articles"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    from datetime import datetime, timedelta
    cutoff = datetime.now() - timedelta(days=days)
    
    c.execute('''SELECT title, url, source_name, published_at
                 FROM articles
                 WHERE published_at > ?
                 ORDER BY published_at DESC''', (cutoff,))
    
    articles = c.fetchall()
    conn.close()
    
    return [{
        "title": a[0],
        "url": a[1],
        "source": a[2],
        "published": a[3]
    } for a in articles]
```

Run with: `uvicorn api:app --reload`

---

## Week 3: React Frontend

```jsx
// App.jsx
import { useState, useEffect } from 'react'

const TIMEFRAMES = [
  { id: '1d', label: '1 Day' },
  { id: '7d', label: '7 Days' },
  { id: '30d', label: '30 Days' },
  { id: '1y', label: '1 Year' }
]

function App() {
  const [activeTab, setActiveTab] = useState('7d')
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetch(`http://localhost:8000/summaries/${activeTab}`)
      .then(res => res.json())
      .then(data => {
        setSummary(data)
        setLoading(false)
      })
  }, [activeTab])

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">AI News Aggregator</h1>
        
        <div className="flex gap-4 mb-8">
          {TIMEFRAMES.map(tf => (
            <button
              key={tf.id}
              onClick={() => setActiveTab(tf.id)}
              className={`px-4 py-2 rounded ${
                activeTab === tf.id 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-white text-gray-700'
              }`}
            >
              {tf.label}
            </button>
          ))}
        </div>

        {loading ? (
          <p>Loading...</p>
        ) : summary?.summary ? (
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-sm text-gray-500 mb-4">
              {summary.article_count} articles • Generated {new Date(summary.generated_at).toLocaleDateString()}
            </div>
            <div className="prose">{summary.summary}</div>
          </div>
        ) : (
          <p>No summary available</p>
        )}
      </div>
    </div>
  )
}

export default App
```

---

## Deployment

### Backend (Railway)

**Option 1: Deploy with Ollama (requires paid plan)**
1. Create `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn api:app --host 0.0.0.0 --port $PORT"
  }
}
```

2. Push to GitHub
3. Connect to Railway
4. Install Ollama on Railway instance (may require custom Dockerfile)

**Option 2: Keep LLM local, deploy API only (recommended for MVP)**
- Run summarization locally on your machine
- Only deploy the API + database to Railway
- Frontend fetches pre-generated summaries

### Frontend (Vercel)
1. Update API URL in code to Railway URL (or localhost for testing)
2. Push to GitHub
3. Import to Vercel
4. Deploy

---

## Next Steps (After Week 3)

- [ ] Add Twitter scraping for key individuals
- [ ] Improve UI design with better typography
- [ ] Add article list view (show all articles used in summary)
- [ ] Implement caching to avoid re-generating summaries
- [ ] Add error handling and retry logic for failed scrapes
- [ ] Set up automated scraping (cron job or scheduled task)
- [ ] Add charts/visualizations (trend graphs)
- [ ] Consider switching to cloud LLM API for production (if needed)
- [ ] Add RSS feed export
- [ ] Optimize Ollama prompt for better summaries

---

## Quick Reference

### Scraping Schedule
- Run every 6 hours: `0 */6 * * *` (cron)
- Generate summaries daily: `0 0 * * *`

### Timeframe Mapping
- `1d` = last 1 day
- `7d` = last 7 days  
- `30d` = last 30 days
- `1y` = last 365 days

### Estimated Costs
- Local LLM (Ollama): Free
- Hosting: Free (Railway + Vercel free tiers)
- **Total: $0/month**
