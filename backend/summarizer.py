import sqlite3
import ollama
from datetime import datetime, timedelta
from backend.database import DB_PATH
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_article_summaries(db_path=DB_PATH, model='qwen2.5:0.5b-instruct'):
    """Generate one-line summaries for articles that don't have one."""
    conn = get_db_connection(db_path)
    c = conn.cursor()
    
    # fetch articles without summary
    # fetch articles without summary, prioritizing Anthropic
    c.execute("""
        SELECT id, title, content, source_name FROM articles 
        WHERE summary IS NULL OR summary = '' 
        ORDER BY CASE WHEN source_name = 'Anthropic' THEN 1 ELSE 2 END, published_at DESC 
        LIMIT 50
    """)
    articles = c.fetchall()
    
    if not articles:
        logger.info("No articles need summarization.")
        conn.close()
        return 0
    
    count = 0
    for article in articles:
        try:
            # Prepare prompt for one-sentence summary
            content_snippet = article['content'][:1000] if article['content'] else article['title']
            prompt = f"Summarize this news in exactly one concise sentence. Do not use 'Here is a summary' or similar intro. Just the sentence.\n\nTitle: {article['title']}\nContent: {content_snippet}"
            
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt},
            ])
            
            summary_text = response['message']['content'].strip()
            
            # Update DB
            c.execute("UPDATE articles SET summary = ? WHERE id = ?", (summary_text, article['id']))
            conn.commit()
            logger.info(f"Summarized article {article['id']}: {summary_text[:50]}...")
            count += 1
            
        except Exception as e:
            logger.error(f"Error summarizing article {article['id']}: {e}")
            
    conn.close()
    return count

if __name__ == "__main__":
    generate_article_summaries()

def generate_summary(timeframe_days, db_path=DB_PATH, model='qwen2.5:0.5b-instruct'):
    conn = get_db_connection(db_path)
    c = conn.cursor()
    
    # 1. Fetch articles
    cutoff = datetime.now() - timedelta(days=timeframe_days)
    c.execute("SELECT id, title, source_name, published_at FROM articles WHERE published_at > ? ORDER BY published_at DESC", (cutoff,))
    articles = c.fetchall()
    
    if not articles:
        conn.close()
        return None
        
    article_list = "\n".join([f"[{a['id']}] {a['title']}" for a in articles[:50]])
    
    # 2. Generate Summary based on timeframe
    summary_text = None
    try:
        import json
        
        if timeframe_days > 7:
            # Trend Analysis Prompt (JSON)
            prompt = f"""
            Analyze the following AI news articles (IDs are in brackets).
            Group them into 2-3 major trends.
            
            Return ONLY a valid JSON object with this structure:
            {{
                "trends": [
                    {{
                        "name": "Short Headline",
                        "summary": "Concise summary of the trend.",
                        "article_ids": [1, 2]
                    }}
                ]
            }}
            
            Articles:
            {article_list}
            """
            
            response = ollama.chat(model=model, format='json', messages=[
                {'role': 'user', 'content': prompt},
            ])
            
            summary_text = response['message']['content']
            
            # Validate JSON and remove hallucinated article IDs
            real_ids = {a['id'] for a in articles}
            try:
                parsed = json.loads(summary_text)
                for trend in parsed.get('trends', []):
                    original_ids = trend.get('article_ids', [])
                    valid_ids = [i for i in original_ids if i in real_ids]
                    if len(valid_ids) < len(original_ids):
                        removed = set(original_ids) - set(valid_ids)
                        logger.warning(
                            f"Removed hallucinated article IDs {removed} "
                            f"from trend '{trend.get('name')}'"
                        )
                    trend['article_ids'] = valid_ids
                summary_text = json.dumps(parsed)
            except json.JSONDecodeError:
                logger.warning("LLM failed to return valid JSON, falling back to text.")
        else:
            # Short text summary for 1d/7d
            prompt = f"""Briefly summarize these AI news headlines in 2-3 sentences. Be concise and highlight the most important updates.

Articles:
{article_list}
"""
            response = ollama.chat(model=model, messages=[
                {'role': 'user', 'content': prompt},
            ])
            summary_text = response['message']['content'].strip()

        if summary_text is None:
            conn.close()
            return None

        # 3. Store in DB
        timeframe_key = f"{timeframe_days}d" if timeframe_days < 365 else "1y"
        
        c.execute("DELETE FROM summaries WHERE timeframe = ?", (timeframe_key,))
        c.execute("INSERT INTO summaries (timeframe, summary_text, article_count) VALUES (?, ?, ?)", 
                 (timeframe_key, summary_text, len(articles)))
        conn.commit()
        logger.info(f"Generated summary for {timeframe_key}")
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        conn.close()
        return None
        
    conn.close()
    return summary_text
