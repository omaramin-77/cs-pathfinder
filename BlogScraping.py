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



def article_exists(url):
    """Check if article with given URL already exists in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM blogs WHERE url = ?', (url,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def save_blog_post(title, url, summary, image_url, published_date):
    """Save a blog post to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO blogs (title, url, summary, image_url, published_date, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, url, summary, image_url, published_date, datetime.utcnow()))

        conn.commit()
        post_id = cursor.lastrowid
        conn.close()
        return post_id
    except Exception as e:
        print(f"Error saving blog post: {e}")
        return None

def refresh_rss_feed(feed_url=RSS_FEED_URL):
    """Fetch RSS feed and save new articles to database. Skips articles with less than 200 words."""
    feed = fetch_rss_feed(feed_url)
    
    if not feed:
        return {
            'success': False,
            'new_count': 0,
            'total_count': 0,
            'message': 'Failed to fetch RSS feed'
        }
    
    entries = parse_feed_entries(feed)
    new_count = 0
    skipped_count = 0

    for entry in entries:
        if not article_exists(entry['url']):
            # Scrape full article content
            scraped = scrape_article(entry['url'])
            if scraped and isinstance(scraped, dict):
                title = scraped.get('title') or entry['title']
                author = scraped.get('author')
                full_text = scraped.get('full_text')
                thumb = scraped.get('thumbnail') or entry.get('image_url')
                pub = scraped.get('published_date') or entry.get('published_date')

                # Check article length - skip if less than 200 words
                article_text = full_text or entry.get('summary', '')
                word_count = count_words(article_text)
                
                if word_count < 200:
                    print(f"⏭️ Skipping article '{title}' - only {word_count} words (minimum 200 required)")
                    skipped_count += 1
                    continue
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Check if full_html column exists, if not use full_text
                    full_html = scraped.get('full_html', full_text)
                    
                    cursor.execute('''
                        INSERT INTO blogs (title, url, summary, full_text, author, thumbnail, published_date, scraped_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        title,
                        entry['url'],
                        entry.get('summary'),
                        full_html or full_text,  # Use HTML if available, fallback to text
                        author,
                        thumb,
                        pub,
                        datetime.utcnow()
                    ))
                    conn.commit()
                    post_id = cursor.lastrowid
                    conn.close()
                    if post_id:
                        new_count += 1
                except Exception as e:
                    print(f"Error saving scraped article: {e}")
            else:
                # Fallback to saving RSS summary only - check length first
                summary_text = entry.get('summary', '')
                word_count = count_words(summary_text)
                
                if word_count < 200:
                    print(f"⏭️ Skipping article '{entry['title']}' - only {word_count} words (minimum 200 required)")
                    skipped_count += 1
                    continue
                
                post_id = save_blog_post(
                    entry['title'],
                    entry['url'],
                    summary_text,
                    entry.get('image_url'),
                    entry.get('published_date')
                )
                if post_id:
                    new_count += 1

    # Get total blog count
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM blogs')
    total = cursor.fetchone()['count']
    conn.close()

    message = f'Added {new_count} new articles'
    if skipped_count > 0:
        message += f', skipped {skipped_count} articles (too short)'
    
    return {
        'success': True,
        'new_count': new_count,
        'total_count': total,
        'message': message
    }


def get_all_blogs(limit=None):
    """Get all blog posts from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if limit:
        cursor.execute(
            'SELECT * FROM blogs ORDER BY published_date DESC LIMIT ?',
            (limit,)
        )
        blogs = cursor.fetchall()
    else:
        cursor.execute(
            'SELECT * FROM blogs ORDER BY published_date DESC'
        )
        blogs = cursor.fetchall()
    
    conn.close()
    return [dict(blog) for blog in blogs] if blogs else []

def get_blogs_paginated(page=1, per_page=10):
    """Return tagged blogs and total count"""
    offset = (page - 1) * per_page
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as count FROM blogs')
    total = cursor.fetchone()['count']
    cursor.execute(
        'SELECT * FROM blogs ORDER BY published_date DESC LIMIT ? OFFSET ?',
        (per_page, offset)
    )
    blogs = cursor.fetchall()
    conn.close()
    return {
        'total': total,
        'blogs': [dict(b) for b in blogs]
    }

def get_blog_by_id(blog_id):
    """Get a single blog post by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM blogs WHERE id = ?', (blog_id,))
    blog = cursor.fetchone()
    conn.close()
    return dict(blog) if blog else None
    

def update_blog(blog_id):
    """Update blog post details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating blog: {e}")
        return False
