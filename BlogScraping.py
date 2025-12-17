"""
 feed parsing and blog management
"""
import json
from pathlib import Path
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
        # Fallback: find largest text block
        if not content:
            divs = soup.find_all(['div', 'article', 'main'])
            best = None
            best_len = 0
            for d in divs:
                text = d.get_text(strip=True)
                if len(text) > best_len:
                    best_len = len(text)
                    best = d
            content = best
        # Extract HTML content with styling preserved
        if content:
            # Process images to ensure they load
            for img in content.find_all('img'):
                # Ensure images have proper src
                if img.get('data-src'):
                    img['src'] = img['data-src']
                elif img.get('data-lazy-src'):
                    img['src'] = img['data-lazy-src']
                
                # Remove lazy loading attributes
                for attr in ['data-src', 'data-lazy-src', 'data-srcset', 'loading']:
                    if img.get(attr):
                        del img[attr]
                
                # Add class for styling
                img_classes = img.get('class', [])
                if isinstance(img_classes, list):
                    img_classes.append('article-img')
                else:
                    img_classes = ['article-img']
                img['class'] = img_classes            
            # Remove inline styles that conflict with dark theme
            for el in content.find_all(True):
                if el.get('style'):
                    # Remove background colors and text colors that conflict
                    style = el.get('style', '')
                    # Remove problematic inline styles
                    style_parts = [s.strip() for s in style.split(';') if s.strip()]
                    cleaned_styles = []
                    for part in style_parts:
                        if ':' in part:
                            prop = part.split(':')[0].strip().lower()
                            # Keep only safe styles
                            if prop not in ['background', 'background-color', 'color', 'background-image']:
                                cleaned_styles.append(part)
                    
                    if cleaned_styles:
                        el['style'] = '; '.join(cleaned_styles)
                    else:
                        del el['style']
                
                # Remove classes that might conflict
                if el.get('class'):
                    classes = el.get('class', [])
                    if isinstance(classes, list):
                        # Keep classes but they'll be overridden by our CSS
                        pass
            
            # Get the cleaned HTML string
            full_html = str(content)
            
            # Also get plain text as fallback
            full_text = content.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            full_text = '\n'.join(lines)
        else:
            full_html = ''
            full_text = ''

        return {
            'title': title or 'Untitled',
            'author': author,
            'published_date': pub_date,
            'full_text': full_text,
            'full_html': full_html,
            'thumbnail': thumbnail
        }
    except Exception as e:
        import traceback
        print(f"Error scraping article {url}: {e}")
        print(traceback.format_exc())
        return None



def count_words(text):
    """Count words in text"""
    if not text:
        return 0
    return len(text.split())



def main():
    print("Fetching RSS feed...")
    feed = fetch_rss_feed()

    if not feed:
        print("Failed to fetch feed.")
        return
    print("Parsing feed entries...")
    entries = parse_feed_entries(feed)

    if not entries:
        print("No entries found.")
        return

    print(f"Found {len(entries)} feed entries")
    max_articles = 5
    results = []

    print(f"Scraping up to {max_articles} full articles...")

    for idx, entry in enumerate(entries[:max_articles], start=1):
        url = entry.get("url")
        if not url:
            continue

        print(f"  [{idx}/{max_articles}] Scraping: {url}")
        article = scrape_article(url)

        if not article:
            print("Failed to scrape article.")
            continue

        results.append({
            **entry,
            **article,
            "word_count": count_words(article.get("full_text")),
            "scraped_at": datetime.utcnow().isoformat()
        })
    if not results:
        print("No articles scraped successfully.")
        return

    
    output_file = "scraped_articles.json"
    output_path = Path(output_file)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Saved {len(results)} articles to: {output_path.resolve()}")

if __name__ == "__main__":
    main()
