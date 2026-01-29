# AI News Aggregator Implementation Guide

*Building a Minimalist News Site with Editorial Design*

---

## Overview

This guide details how to implement the minimalist, Claude-inspired frontend design for your AI news aggregator. The design emphasizes refined typography, generous whitespace, and subtle interactions to create a calm, focused reading experience for AI researchers.

---

## Design Philosophy

- **Editorial Typography**: Lora serif for headlines (professional gravitas) + Inter for metadata (clean readability)
- **Warm Color Palette**: Cream background (#faf9f7) instead of stark white, with muted grays and company-specific accent colors
- **Generous Spacing**: 32px between articles, 64px section margins for breathing room
- **Subtle Interactions**: Hover states with translate effects, staggered fade-in animations
- **Visual Hierarchy**: Color-coded left borders identify sources at a glance

---

## Modified Architecture

The frontend design requires modifications to the backend API to support article listing instead of just summaries. Here's the updated data flow:

1. Scrapers collect articles every 6 hours → SQLite database
2. FastAPI backend exposes `/articles` endpoint with timeframe filtering
3. React frontend fetches articles and renders them in the minimalist stream layout

---

## Backend Modifications

### Updated API Endpoints (api.py)

Replace the existing API with this enhanced version that properly handles timeframes:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime, timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

TIMEFRAME_DAYS = {
    '1d': 1,
    '7d': 7,
    '30d': 30,
    '1y': 365
}

@app.get("/articles/{timeframe}")
def get_articles(timeframe: str):
    """Get articles for specific timeframe"""
    if timeframe not in TIMEFRAME_DAYS:
        return {"error": "Invalid timeframe"}
    
    days = TIMEFRAME_DAYS[timeframe]
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    
    c.execute('''SELECT title, url, source_name, published_at
                 FROM articles
                 WHERE published_at > ?
                 ORDER BY published_at DESC''', (cutoff,))
    
    articles = c.fetchall()
    conn.close()
    
    return [
        {
            "id": i,
            "title": a[0],
            "url": a[1],
            "source": a[2],
            "published": a[3]
        }
        for i, a in enumerate(articles)
    ]
```

---

## Frontend Implementation

### Project Setup

Create the React app with Vite and install dependencies:

```bash
npm create vite@latest ai-news-frontend -- --template react
cd ai-news-frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Component Structure

The main component (App.jsx) handles:

- Timeframe state management (1d, 7d, 30d, 1y)
- API calls to backend on timeframe change
- Article rendering with source-specific color coding
- Loading states and empty states

### Complete Component Code

Replace `src/App.jsx` with the provided minimalist component from `ai-news-page.jsx`.

**Key modifications needed:**

1. Update API endpoint in the `useEffect`:
```javascript
fetch(`${import.meta.env.VITE_API_URL}/articles/${activeTab}`)
```

2. Remove `MOCK_ARTICLES` and use real API data

---

## Key Design Features

| Feature | Implementation |
|---------|----------------|
| Typography | Google Fonts: Lora (serif, 600 weight) for headlines, Inter (sans-serif, 400-600) for body |
| Colors | Background: #faf9f7 (warm cream), Text: #1a1a1a to #9b9995 (hierarchy), Accents: Company-specific colors |
| Animations | Staggered fadeInUp (0.05s delay increments), hover translateX(4px), cubic-bezier easing |
| Layout | Max-width: 800px centered, generous vertical spacing (32px between articles, 64px sections) |

---

## Company Color Scheme

Each AI company has a signature color used for left border accents and source badges:

| Company | Hex Code | Purpose |
|---------|----------|---------|
| OpenAI | #10a37f | OpenAI brand teal |
| Anthropic | #d4a574 | Warm gold/tan |
| Google DeepMind | #4285f4 | Google blue |
| Meta AI | #0081fb | Meta brand blue |

---

## Updated 3-Week Implementation Plan

### Week 1: Backend Foundation (Unchanged)

1. Set up SQLite database with articles table
2. Build RSS scraper for OpenAI blog
3. Test data collection pipeline

### Week 2: Complete Data Pipeline + API

1. Add scrapers for all 4 company blogs (Anthropic, Google DeepMind, Meta AI)
2. Build FastAPI with `/articles/{timeframe}` endpoint
3. Set up CORS for frontend access
4. Test API with sample timeframes

### Week 3: Minimalist Frontend

1. Create React app with Vite
2. Implement the minimalist component with editorial typography
3. Add Google Fonts (Lora + Inter)
4. Implement timeframe filters and article stream
5. Add animations and hover states
6. Deploy frontend to Vercel, backend to Railway

---

## Environment Configuration

### Backend `.env`

```bash
# No API keys needed for local LLM
DATABASE_PATH=data.db
SCRAPE_INTERVAL_HOURS=6
```

### Frontend `.env`

```bash
VITE_API_URL=http://localhost:8000
# For production: https://your-backend.railway.app
```

---

## Deployment

### Backend (Railway)

1. Create `railway.json` in backend directory:
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
3. Connect repository to Railway
4. Add environment variables in Railway dashboard

### Frontend (Vercel)

1. Update `VITE_API_URL` to Railway backend URL
2. Push frontend to GitHub
3. Import to Vercel
4. Deploy (automatic on push)

---

## Testing Checklist

- [ ] Verify all 4 timeframe filters work correctly
- [ ] Check article links open in new tabs
- [ ] Test hover states and animations
- [ ] Verify correct source colors appear
- [ ] Test empty states (no articles for timeframe)
- [ ] Check loading states display properly
- [ ] Test responsive design on mobile

---

## Performance Optimizations

- **Font Loading**: Preload Google Fonts in index.html to prevent flash of unstyled text
- **CSS Animations**: Use CSS-only animations for better performance (no JavaScript)
- **API Caching**: Consider caching article responses for 5-10 minutes
- **Image Optimization**: If adding source logos later, use WebP format

---

## Future Enhancements

1. Add article preview on hover (tooltip with first 2-3 sentences)
2. Implement search/filter by company
3. Add dark mode toggle
4. RSS feed export for users to subscribe
5. Email digest option (daily/weekly summaries)
6. Add Twitter feeds from key AI researchers
7. Company logos next to source badges

---

## File Structure

```
ai-news-aggregator/
├── backend/
│   ├── scraper.py           # All scraping logic
│   ├── database.py          # SQLite setup + queries
│   ├── api.py               # FastAPI app
│   ├── config.py            # Settings
│   ├── requirements.txt
│   ├── railway.json         # Deployment config
│   └── data.db              # SQLite database file
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main component
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── .env
│   └── index.html
└── README.md
```

---

## Quick Start Commands

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Run scraper
python scraper.py

# Start API
uvicorn api:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173` to see your site.

---

## Troubleshooting

### CORS Issues
If you see CORS errors, ensure your backend has the middleware configured:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Font Not Loading
Add this to your `index.html` `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### Database Issues
If articles aren't appearing, check:
```bash
sqlite3 data.db "SELECT COUNT(*) FROM articles;"
sqlite3 data.db "SELECT * FROM articles LIMIT 5;"
```

---

## Conclusion

This minimalist design prioritizes readability and focus, perfect for AI researchers who want to quickly scan updates without distraction. The editorial typography and warm color palette create a professional, calm environment for consuming technical content. By following this implementation guide, you'll have a production-ready news aggregator running on free hosting tiers within 3 weeks.

**Key principle**: Start simple, scale later. The design is intentionally minimal to ship quickly while maintaining professional polish.

---

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vite React Guide](https://vitejs.dev/guide/)
- [TailwindCSS Docs](https://tailwindcss.com/docs)
- [Railway Deployment](https://docs.railway.app/)
- [Vercel Deployment](https://vercel.com/docs)
