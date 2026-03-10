from flask import Flask, request
import sqlite3
from datetime import datetime, timedelta
import requests
import robokassa

app = Flask(__name__)

# Конфигурация Robokassa (из твоего бота)
ROBOKASSA_LOGIN = 'sanderfinanceBOT'
ROBOKASSA_PASSWORD2 = 'cyrkunovandrej67'
BOT_TOKEN = '8526938179:AAHKiBZba2oy3cIcW8eigJL8WAfMypV75YI'

@app.route('/payment', methods=['POST'])
def payment_result():
    """Обрабатывает уведомления от Robokassa об успешной оплате"""
    data = request.form.to_dict()
    
    try:
        out_sum = data.get('OutSum')
        inv_id = data.get('InvId')
        signature = data.get('SignatureValue')
        user_id = data.get('Shp_user_id')
        sub_type = data.get('Shp_sub_type')
        
        if not user_id or not sub_type:
            return "ERROR: missing user data", 400
        
        # Проверяем подпись (Пароль #2)
        expected = robokassa.get_hash(f"{out_sum}:{inv_id}:{ROBOKASSA_PASSWORD2}")
        if signature != expected:
            return "ERROR: bad signature", 400
        
        # Активируем подписку
        days = 30 if sub_type == 'month' else 365
        expires_at = datetime.now() + timedelta(days=days)
        
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT OR REPLACE INTO subscriptions (user_id, expires_at, is_active) 
            VALUES (?, ?, 1)
        ''', (user_id, expires_at.strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
        cur.close()
        conn.close()
        
        # Уведомление пользователю
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        telegram_data = {
            'chat_id': user_id,
            'text': f"✅ *Подписка активирована!*\n\nДействует до: {expires_at.strftime('%d.%m.%Y')}",
            'parse_mode': 'Markdown'
        }
        requests.post(telegram_url, data=telegram_data)
        
        return f"OK{inv_id}"
        
    except Exception as e:
        print(f"Error: {e}")
        return "ERROR", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


