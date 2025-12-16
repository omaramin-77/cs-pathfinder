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

        