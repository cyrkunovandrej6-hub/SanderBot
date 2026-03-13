from flask import Flask, request
import sqlite3
from datetime import datetime, timedelta
import requests
import hashlib
import time

app = Flask(__name__)

# ========== КОНФИГУРАЦИЯ ROBOKASSA ==========
ROBOKASSA_LOGIN = 'sanderfinanceBOT'
ROBOKASSA_PASSWORD2 = 'Ca4afd1BJQ5fyB2zQW6h'  
BOT_TOKEN = '8526938179:AAHKiBZba2oy3cIcW8eigJL8WAfMypV75YI'

# ========== ФУНКЦИЯ ДЛЯ ВЫЧИСЛЕНИЯ ПОДПИСИ MD5 ==========
def get_md5_signature(params_string):
    """Вычисляет MD5-хеш строки параметров"""
    return hashlib.md5(params_string.encode('utf-8')).hexdigest()

@app.route('/payment', methods=['POST'])
def payment_result():
    """Обрабатывает уведомления от Robokassa об успешной оплате"""
    data = request.form.to_dict()
    
    try:
        # Получаем параметры из запроса
        out_sum = data.get('OutSum')
        inv_id = data.get('InvId')
        signature = data.get('SignatureValue')
        user_id = data.get('Shp_user_id')
        sub_type = data.get('Shp_sub_type')
        
        # Проверяем наличие обязательных параметров
        if not user_id or not sub_type:
            print("ERROR: missing user data")
            return "ERROR: missing user data", 400
        
        # Формируем строку для проверки подписи (как в документации Robokassa)
        # Формат: OutSum:InvId:Пароль#2
        expected_signature_str = f"{out_sum}:{inv_id}:{ROBOKASSA_PASSWORD2}"
        expected_signature = get_md5_signature(expected_signature_str)
        
        print(f"DEBUG: Получена подпись: {signature}")
        print(f"DEBUG: Ожидаемая подпись: {expected_signature} из '{expected_signature_str}'")
        
        # Сравниваем подписи
        if signature != expected_signature:
            print("ERROR: bad signature")
            return "ERROR: bad signature", 400
        
        # Активируем подписку
        days = 30 if sub_type == 'month' else 365
        expires_at = datetime.now() + timedelta(days=days)
        expires_at_str = expires_at.strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT OR REPLACE INTO subscriptions (user_id, expires_at, is_active) 
            VALUES (?, ?, 1)
        ''', (user_id, expires_at_str))
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"✅ Подписка активирована для user_id={user_id}, тип={sub_type}, до={expires_at_str}")
        
        # Отправляем уведомление пользователю в Telegram
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        telegram_data = {
            'chat_id': user_id,
            'text': f"✅ *Подписка активирована!*\n\nДействует до: {expires_at.strftime('%d.%m.%Y %H:%M')}",
            'parse_mode': 'Markdown'
        }
        try:
            response = requests.post(telegram_url, data=telegram_data)
            print(f"📨 Уведомление пользователю: {response.status_code}")
        except Exception as e:
            print(f"❌ Ошибка отправки уведомления: {e}")
        
        # Robokassa ждёт ответ "OK{inv_id}"
        return f"OK{inv_id}"
        
    except Exception as e:
        print(f"❌ Ошибка в обработчике: {e}")
        return "ERROR", 500

# ========== НОВЫЕ ОБРАБОТЧИКИ ДЛЯ ПОЛЬЗОВАТЕЛЯ ==========
@app.route('/payment/success', methods=['GET'])
def payment_success():
    """Страница, которую видит пользователь после успешной оплаты"""
    # Здесь можно сделать красивую HTML-страницу или просто отправить сообщение
    return """
    <html>
        <head><title>Оплата прошла успешно</title></head>
        <body style="text-align: center; font-family: Arial; padding: 50px;">
            <h1>✅ Оплата прошла успешно!</h1>
            <p>Спасибо за покупку. Вы можете вернуться в бота и продолжить пользоваться премиум-функциями.</p>
            <p><a href="https://t.me/sanderfinancee_bot">Вернуться в бота</a></p>
        </body>
    </html>
    """, 200

@app.route('/payment/fail', methods=['GET'])
def payment_fail():
    """Страница, которую видит пользователь при ошибке оплаты"""
    return """
    <html>
        <head><title>Ошибка оплаты</title></head>
        <body style="text-align: center; font-family: Arial; padding: 50px;">
            <h1>❌ Оплата не удалась</h1>
            <p>Что-то пошло не так. Попробуйте ещё раз или обратитесь в поддержку.</p>
            <p><a href="https://t.me/sanderfinancee_bot">Вернуться в бота</a></p>
        </body>
    </html>
    """, 200

if __name__ == '__main__':
    print("🚀 Веб-обработчик Robokassa запущен на порту 80")
    print(f"📢 Result URL: http://212.109.223.67:80/payment")
    print(f"📢 Success URL: http://212.109.223.67:80/payment/success")
    print(f"📢 Fail URL: http://212.109.223.67:80/payment/fail")
    app.run(host='0.0.0.0', port=80)
