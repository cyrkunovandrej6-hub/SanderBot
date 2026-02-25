
import feedparser
import sqlite3
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import time

# ========== НАСТРОЙКИ ==========
RSS_FEEDS = {
    'bbc_world': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    'cnn_world': 'http://rss.cnn.com/rss/edition_world.rss',
    'reuters_world': 'https://feeds.reuters.com/reuters/worldnews'
}
DB_PATH = 'news.db'
# ========== СОЗДАНИЕ БАЗЫ ==========
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            link TEXT UNIQUE,
            summary TEXT,
            published TEXT,
            fetched_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных готова")
# ========== ПАРСИНГ RSS ==========
def fetch_feeds():
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Проверяю RSS...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            print(f"  {source}: {len(feed.entries)} новостей")
            for entry in feed.entries[:3]:
                try:
                    cur.execute('''
                        INSERT OR IGNORE INTO news (source, title, link, summary, published, fetched_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        source,
                        entry.title,
                        entry.link,
                        entry.get('summary', '')[:500],
                        entry.get('published', datetime.now().isoformat()),
                        datetime.now().isoformat()
                    ))
                except Exception as e:
                    print(f"    Ошибка при сохранении: {e}")
        except Exception as e:
            print(f"  Ошибка при парсинге {source}: {e}")
    conn.commit()
    conn.close()
    print(f"✅ Готово")
# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("📰 Агрегатор новостей запущен")
    init_db()
    fetch_feeds()
    scheduler = BlockingScheduler()             
    scheduler.add_job(fetch_feeds, 'interval', minutes=5)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n🛑 Остановлено")





