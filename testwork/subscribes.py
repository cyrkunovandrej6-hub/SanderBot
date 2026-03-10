import sqlite3
import telebot
from datetime import datetime, timedelta
import time
import threading

# Токен твоего бота
BOT_TOKEN = '8526938179:AAHKiBZba2oy3cIcW8eigJL8WAfMypV75YI'
bot = telebot.TeleBot(BOT_TOKEN)

# Твой Telegram ID (куда присылать уведомления)
ADMIN_ID = 5933197105

def check_expired_subscriptions():
    """Проверяет истекшие подписки и уведомляет админа"""
    while True:
        try:
            conn = sqlite3.connect('finance_bot.db')
            cur = conn.cursor()
            
            # Находим подписки, которые истекают сегодня или уже истекли
            today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute('''
                SELECT user_id, expires_at FROM subscriptions 
                WHERE expires_at < ? AND is_active = 1
            ''', (today,))
            
            expired_users = cur.fetchall()
            
            for user_id, expires_at in expired_users:
                # Отключаем подписку в БД
                cur.execute('''
                    UPDATE subscriptions SET is_active = 0 
                    WHERE user_id = ?
                ''', (user_id,))
                
                # Уведомление админу
                try:
                    bot.send_message(
                        ADMIN_ID,
                        f"⚠️ *Подписка истекла*\n\n"
                        f"👤 Пользователь ID: `{user_id}`\n"
                        f"📅 Истекла: {expires_at}\n\n"
                        f"Можно удалить пользователя из чатов вручную.",
                        parse_mode='Markdown'
                    )
                except:
                    pass
                
                # Уведомление пользователю
                try:
                    bot.send_message(
                        user_id,
                        "❌ *Срок вашей подписки истёк*\n\n"
                        "Premium-функции отключены. Чтобы продолжить пользоваться, "
                        "оформите новую подписку через меню.",
                        parse_mode='Markdown'
                    )
                except:
                    pass
            
            conn.commit()
            
            # Проверяем подписки, которые истекают через 3 дня (напоминание)
            three_days_later = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d %H:%M:%S")
            cur.execute('''
                SELECT user_id, expires_at FROM subscriptions 
                WHERE expires_at <= ? AND expires_at > ? AND is_active = 1
            ''', (three_days_later, today))
            
            soon_expiring = cur.fetchall()
            
            for user_id, expires_at in soon_expiring:
                exp_date = datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S")
                days_left = (exp_date - datetime.now()).days
                
                bot.send_message(
                    user_id,
                    f"⚠️ *Подписка скоро закончится*\n\n"
                    f"Осталось дней: {days_left}\n"
                    f"Дата окончания: {exp_date.strftime('%d.%m.%Y')}\n\n"
                    f"Чтобы продлить подписку, используй меню.",
                    parse_mode='Markdown'
                )
            
            cur.close()
            conn.close()
            
        except Exception as e:
            print(f"Ошибка в проверке подписок: {e}")
        
        # Проверка раз в 6 часов
        time.sleep(6 * 3600)

def start_checker():
    thread = threading.Thread(target=check_expired_subscriptions)
    thread.daemon = True
    thread.start()
    print("✅ Проверщик подписок запущен")

if __name__ == '__main__':
    start_checker()
    # Здесь можно добавить что-то ещё, если нужно
    while True:
        time.sleep(1)



