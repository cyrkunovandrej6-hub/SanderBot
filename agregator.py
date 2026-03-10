import feedparser
import sqlite3
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

DB_PATH = '/root/SanderBot/news.db'

def init_db():
    """Создаёт таблицу для новостей, если её нет"""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            link TEXT UNIQUE,
            fetched_at TEXT
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных готова (таблица news создана)")

def fetch_news():
    """Собирает последние новости с Lenta.ru и сохраняет в базу"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Проверяю новости Lenta.ru...")
    
    try:
        # Парсим RSS Lenta.ru
        feed = feedparser.parse('https://lenta.ru/rss')
        
        if not feed.entries:
            print("❌ Не удалось получить новости (пустой ответ)")
            return
            
        print(f"✅ Получено {len(feed.entries)} новостей")
        
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        added = 0
        for entry in feed.entries[:10]:  # Берём последние 10 новостей
            try:
                cur.execute(
                    "INSERT OR IGNORE INTO news (title, link, fetched_at) VALUES (?, ?, ?)",
                    (entry.title, entry.link, datetime.now().isoformat())
                )
                if cur.rowcount > 0:
                    added += 1
            except Exception as e:
                print(f"  Ошибка при сохранении: {e}")
        
        conn.commit()
        conn.close()
        print(f"✅ Добавлено {added} новых новостей")
        
    except Exception as e:
        print(f"❌ Ошибка при парсинге: {e}")

if __name__ == '__main__':
    print("📰 Агрегатор новостей запущен")
    init_db()
    
    # Первый запуск сразу
    fetch_news()
    
    # Планировщик каждые 5 минут
    scheduler = BlockingScheduler()
    scheduler.add_job(fetch_news, 'interval', minutes=5)
    
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n🛑 Агрегатор остановлен")
