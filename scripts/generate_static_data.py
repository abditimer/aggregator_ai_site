import sqlite3
import json
import os
from datetime import datetime

# Configuration
DB_PATH = 'backend/data.db'
OUTPUT_PATH = 'frontend/public/data.json'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_static_data():
    print(f"Reading from {DB_PATH}...")
    conn = get_db_connection()
    c = conn.cursor()

    # 1. Fetch ALL articles (ordered by date)
    # We fetch everything, frontend will filter/paginate
    print("Fetching articles...")
    c.execute('''SELECT id, title, url, source_name as source, published_at as published, source_type as type, summary
                 FROM articles
                 ORDER BY published_at DESC''')
    articles = [dict(row) for row in c.fetchall()]
    print(f"Found {len(articles)} articles.")

    # 2. Fetch Summaries 
    print("Fetching trend summaries...")
    summaries = {}
    for timeframe in ['30d', '1y']:
        c.execute('''SELECT summary_text, article_count, generated_at
                     FROM summaries
                     WHERE timeframe = ?
                     ORDER BY generated_at DESC
                     LIMIT 1''', (timeframe,))
        row = c.fetchone()
        if row:
            summaries[timeframe] = {
                "summary": row['summary_text'],
                "article_count": row['article_count'],
                "generated_at": row['generated_at']
            }

    conn.close()

    # 3. Construct Data Object
    data = {
        "generated_at": datetime.now().isoformat(),
        "articles": articles,
        "summaries": summaries
    }

    # 4. Write to JSON
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    print(f"Writing to {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(data, f, indent=2)
    
    print("Done! Static data generated.")

if __name__ == "__main__":
    generate_static_data()
