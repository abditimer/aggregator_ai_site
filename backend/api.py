from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from datetime import datetime, timedelta
from backend.database import DB_PATH

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

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/summaries/{timeframe}")
def get_summary(timeframe: str):
    """Get latest summary for timeframe (1d, 7d, 30d, 1y)"""
    conn = get_db_connection()
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
            "summary": result['summary_text'],
            "article_count": result['article_count'],
            "generated_at": result['generated_at']
        }
    return {"error": "No summary found", "timeframe": timeframe}

@app.get("/articles/{timeframe}")
def get_articles(timeframe: str, page: int = 1, limit: int = 20):
    """Get articles for specific timeframe with pagination"""
    if timeframe not in TIMEFRAME_DAYS:
        raise HTTPException(status_code=400, detail="Invalid timeframe")
    
    days = TIMEFRAME_DAYS[timeframe]
    conn = get_db_connection()
    c = conn.cursor()
    
    cutoff = datetime.now() - timedelta(days=days)
    offset = (page - 1) * limit
    
    c.execute('''SELECT id, title, url, source_name, published_at, source_type, summary
                 FROM articles
                 WHERE published_at > ?
                 ORDER BY published_at DESC
                 LIMIT ? OFFSET ?''', (cutoff, limit, offset))
    
    articles = c.fetchall()
    conn.close()
    
    return [
        {
            "id": a['id'],
            "title": a['title'],
            "url": a['url'],
            "source": a['source_name'],
            "published": a['published_at'],
            "type": a['source_type'],
            "summary": a['summary']
        }
        for a in articles
    ]
