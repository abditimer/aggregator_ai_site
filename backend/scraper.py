import feedparser
import sqlite3
import datetime
import logging
from dateutil import parser as date_parser
from backend.database import DB_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMPANY_FEEDS = {
    'OpenAI': 'https://openai.com/blog/rss.xml',
    'Anthropic': 'https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic.xml',
    'Google DeepMind': 'https://deepmind.google/blog/rss.xml',
    'Meta AI': 'https://engineering.fb.com/feed/'
}

def parse_date(entry):
    """Attempt to parse date from feed entry."""
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
         return datetime.datetime(*entry.published_parsed[:6])
    if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
        return datetime.datetime(*entry.updated_parsed[:6])
    # Fallback to current time if parsing fails
    return datetime.datetime.now()

from bs4 import BeautifulSoup
import re

def scrape_anthropic_html(c):
    """Custom scraper for Anthropic news page using HTML parsing."""
    url = "https://www.anthropic.com/news"
    logger.info(f"Scraping Anthropic HTML from {url}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    count = 0
    import httpx 
    
    try:
        response = httpx.get(url, headers=headers, timeout=10.0, follow_redirects=True)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 1. Featured Articles (Grid Items)
        featured_items = soup.find_all('a', class_=lambda x: x and 'gridItem' in x)
        # 2. List Items
        list_items = soup.find_all('a', class_=lambda x: x and 'listItem' in x)
        
        all_items = featured_items + list_items
        
        for item in all_items:
            try:
                link = item.get('href')
                if not link: continue
                
                if not link.startswith('http'):
                    link = f"https://www.anthropic.com{link}"
                
                # FILTER: Exclude legal/policy/careers
                if any(x in link.lower() for x in ['/legal/', '/careers', '/company', 'policy', 'terms']):
                    continue

                # Title Extraction
                # Try finding specific heading tags first
                title_tag = item.find('h3') or item.find('h4')
                
                if not title_tag:
                     # List items often have class="...title..."
                     title_span = item.find('span', class_=lambda x: x and 'title' in x.lower())
                     if title_span:
                         title_tag = title_span
                     else:
                         # Fallback: Check for generic spans, usually the last one or longest one is the title
                         spans = item.find_all('span')
                         if len(spans) > 0:
                             # Often the date category is short, title is long
                             title_tag = max(spans, key=lambda s: len(s.get_text()))
                
                if not title_tag:
                    continue # Skip if no title found
                    
                title = title_tag.get_text().strip()
                if not title or title.lower() == "anthropic news":
                    continue

                # Date Extraction
                date_tag = item.find('time')
                if date_tag:
                    try:
                        dt = date_parser.parse(date_tag.get_text())
                    except:
                        dt = datetime.datetime.now()
                else:
                    dt = datetime.datetime.now()
                
                # Insert
                c.execute('''INSERT OR IGNORE INTO articles 
                           (url, title, content, published_at, source_type, source_name)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                          (link, title, '', dt, 'blog', 'Anthropic'))
                
                if c.rowcount > 0:
                    count += 1
                    logger.info(f"Scraped Anthropic: {title}")
                    
            except Exception as e:
                # logger.warning(f"Failed to parse inner Anthropic item: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scraping Anthropic HTML: {e}")
        
    return count

def scrape_blogs(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    new_articles_count = 0
    
    # Custom Anthropic Scraper
    new_articles_count += scrape_anthropic_html(c)
    
    import httpx
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for company, feed_url in COMPANY_FEEDS.items():
        if company == 'Anthropic': continue
        logger.info(f"Scraping {company} from {feed_url}...")
        try:
            # Use httpx to fetch raw content first to handle User-Agent blocking
            try:
                response = httpx.get(feed_url, headers=headers, timeout=10.0, follow_redirects=True)
                response.raise_for_status()
                feed_content = response.text
                feed = feedparser.parse(feed_content)
            except Exception as fetch_err:
                logger.warning(f"Failed to fetch {company} with httpx, checking feedparser directly: {fetch_err}")
                feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed {company} has issues: {feed.bozo_exception}")

            for entry in feed.entries:
                try:
                    url = entry.link
                    title = entry.title
                    # Some feeds put content in 'content' list, others in 'summary'
                    content = ''
                    if hasattr(entry, 'content'):
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    published_at = parse_date(entry)
                    
                    c.execute('''INSERT OR IGNORE INTO articles 
                               (url, title, content, published_at, source_type, source_name)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                             (url, 
                              title, 
                              content,
                              published_at,
                              'blog',
                              company))
                    
                    if c.rowcount > 0:
                        new_articles_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing entry for {company}: {e}")

                    
        except Exception as e:
            logger.error(f"Error scraping {company}: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Scraping complete. {new_articles_count} new articles.")
    return new_articles_count

if __name__ == "__main__":
    scrape_blogs()
