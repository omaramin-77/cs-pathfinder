"""
 feed parsing and blog management
"""

import feedparser
import requests
from datetime import datetime
from DB import get_db_connection
from bs4 import BeautifulSoup

RSS_FEED_URL = "https://www.kdnuggets.com/feed"


def fetch_rss_feed(feed_url=RSS_FEED_URL):
    """Fetch RSS feed from URL"""
    try:
        feed = feedparser.parse(feed_url)
        if feed.bozo:
            print(f"Warning: Feed parsing had issues: {feed.bozo_exception}")
        return feed
    except Exception as e:
        print(f"Error fetching RSS feed: {e}")
        return None

def extract_image_from_entry(entry):
    """Extract image URL from feed entry"""
    # Try media_content first
    if hasattr(entry, 'media_content') and entry.media_content:
        if isinstance(entry.media_content, list) and len(entry.media_content) > 0:
            if 'url' in entry.media_content[0]:
                return entry.media_content[0]['url']
    # Try summary_detail with HTML parsing
    if hasattr(entry, 'summary_detail') and entry.summary_detail:
        try:
            soup = BeautifulSoup(entry.summary_detail.get('value', ''), 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag.get('src')
        except:
            pass
    # Try summary with HTML parsing
    if hasattr(entry, 'summary'):
        try:
            soup = BeautifulSoup(entry.summary, 'html.parser')
            img_tag = soup.find('img')
            if img_tag and img_tag.get('src'):
                return img_tag.get('src')
        except:
            pass
    
    return None

def parse_feed_entries(feed):
    """Parse feed entries and extract required fields"""
    entries = []
    
    if not feed or not hasattr(feed, 'entries'):
        return entries
    
    for entry in feed.entries:
        try:
            title = entry.get('title', 'Untitled')
            url = entry.get('link', '')
            summary = entry.get('summary', '')
            published_date = entry.get('published', '')
            image_url = extract_image_from_entry(entry)
            
            entries.append({
                'title': title,
                'url': url,
                'summary': summary,
                'image_url': image_url,
                'published_date': published_date
            })
        except Exception as e:
            print(f"Error parsing entry: {e}")
            continue
    
    return entries

def scrape_article(url, timeout=15):
    """Fetch article page and extract full text content, author, thumbnail, and published date"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        if not soup:
            print(f"Failed to parse HTML for {url}")
            return None

        # Title
        title = None
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            title = og_title.get('content')
        if not title and soup.title:
            title = soup.title.string

        # Author
        author = None
        author_meta = soup.find('meta', {'name': 'author'})
        if author_meta and author_meta.get('content'):
            author = author_meta.get('content')
        else:
            article_author = soup.find('meta', property='article:author')
            if article_author and article_author.get('content'):
                author = article_author.get('content')

        # Published date
        pub_date = None
        pub_meta = soup.find('meta', property='article:published_time')
        if pub_meta and pub_meta.get('content'):
            pub_date = pub_meta.get('content')
        elif soup.find('time'):
            try:
                time_tag = soup.find('time')
                pub_date = time_tag.get('datetime') or time_tag.text
            except:
                pub_date = None

        # Thumbnail
        thumbnail = None
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            thumbnail = og_image.get('content')
        else:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                thumbnail = twitter_image.get('content')

        # Remove unwanted elements
        for selector in ['script', 'style', 'aside', 'nav', 'footer', 'header', 'form', 'noscript', 'iframe']:
            for el in soup.find_all(selector):
                el.decompose()

        # Remove ads, social widgets, and navigation by class/id
        for el in soup.find_all(True):
            if el is None:
                continue
            try:
                cls = ' '.join(el.get('class', []) or []) if el.get('class') else ''
                idv = el.get('id', '') or ''
                combined = (cls + ' ' + idv).lower()
                noise_keywords = ['subscribe', 'newsletter', 'follow', 'share', 'social', 'ad', 'advert', 
                                'comment', 'sidebar', 'menu', 'navigation', 'related', 'recommend']
                if any(k in combined for k in noise_keywords):
                    el.decompose()
            except:
                pass
        # Extract main article content
        content = None
        # Try common article containers
        candidates = [
            ('article', None),
            ('div', {'class': 'entry-content'}),
            ('div', {'class': 'post-content'}),
            ('div', {'class': 'article-content'}),
            ('div', {'id': 'content'}),
            ('main', None)
        ]
        for tag, attrs in candidates:
            if attrs:
                el = soup.find(tag, attrs=attrs)
            else:
                el = soup.find(tag)
            if el:
                content = el
                break

    except Exception as e:
        import traceback
        print(f"Error scraping article {url}: {e}")
        print(traceback.format_exc())
        return None

