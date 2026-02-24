import telebot
from telebot import types
import sqlite3
from datetime import datetime

bot = telebot.TeleBot('8526938179:AAHKiBZba2oy3cIcW8eigJL8WAfMypV75YI')

# ========== РАБОТА С БАЗОЙ ДАННЫХ ==========
def create_users_table():
    # SQLite не требует подключения к серверу, просто файл
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    
    # ВАША ТАБЛИЦА (адаптированная для SQLite)
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    pss TEXT)''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблица users создана")

def save_user_to_db(name):
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    
    cur.execute(
        "INSERT INTO users (name, pss) VALUES (?, ?)",
        (name, 'temp_password')
    )
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"➕ Добавлен пользователь: {name}")

def get_last_user_name():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    
    cur.execute("SELECT name FROM users ORDER BY id DESC LIMIT 1")
    result = cur.fetchone()
    
    cur.close()
    conn.close()
    
    if result:
        return result[0]
    return None

# ========== ФУНКЦИИ ДЛЯ БОТА ==========
def get_user_name(message):
    if message.from_user.first_name:
        return message.from_user.first_name
    elif message.from_user.username:
        return message.from_user.username
    else:
        return "Пользователь"

def get_main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        types.InlineKeyboardButton('💰 Баланс', callback_data='balance'),
        types.InlineKeyboardButton('📊 Статистика', callback_data='stats')
    )
    
    markup.add(
        types.InlineKeyboardButton('💸 Расходы', callback_data='expenses'),
        types.InlineKeyboardButton('💵 Доходы', callback_data='income')
    )
    
    markup.add(
        types.InlineKeyboardButton('🎯 Цели', callback_data='goals'),
        types.InlineKeyboardButton('📅 Регулярные', callback_data='regular')
    )
    
    markup.add(
        types.InlineKeyboardButton('🏆 Достижения', callback_data='achievements'),
        types.InlineKeyboardButton('🧮 Калькулятор', callback_data='calculator')
    )
    
    markup.add(
        types.InlineKeyboardButton('💎 Подписка', callback_data='subscription'),
        types.InlineKeyboardButton('📞 Поддержка', callback_data='support')
    )
    
    markup.add(types.InlineKeyboardButton('🔄 Обновить', callback_data='menu'))
    
    return markup

def format_main_menu(user_name):
    current_time = datetime.now()
    greeting = "Добрый день"
    
    if 6 <= current_time.hour < 12:
        greeting = "Доброе утро"
    elif 12 <= current_time.hour < 18:
        greeting = "Добрый день"
    elif 18 <= current_time.hour < 24:
        greeting = "Добрый вечер"
    else:
        greeting = "Доброй ночи"
    
    menu_text = f"""
☀️ {greeting}, {user_name}! 👋

✨ ДОБРО ПОЖАЛОВАТЬ В SANDER FINANCE 5.1!
Ваш персональный финансовый помощник с калькулятором 🏦

📊 ВАША ФИНАНСОВАЯ СВОДКА:

💰 БАЛАНС: 0₽
📅 ДНЕВНОЙ БЮДЖЕТ: 1,000₽
📈 СТАТУС БЮДЖЕТА: 💎 Отлично

💸 РАСХОДЫ:
• Сегодня: 0₽
• За неделю: 0₽
• Использовано: 0.0%

🎯 ЦЕЛИ:
• Всего целей: 0
• Активных: 0
• Прогресс: 0.0%
• Статус: 🎯 Нет целей

💼 РЕГУЛЯРНЫЕ ОПЕРАЦИИ:
• Доходы в месяц: 0₽
• Расходы в месяц: 0₽
• Финансовое здоровье: ⚖️ Сбалансированный бюджет

🏆 ДОСТИЖЕНИЯ:
• Уровень: 1
• Опыт: 0 XP
• Серия дней: 0 дн.

💎 ПОДПИСКА: 🆓 Бесплатный тариф

🧮 НОВИНКА! Финансовый калькулятор:
• Кредиты и вклады
• Инфляция и ROI
• Цели накоплений

📈 СОВЕТ НА СЕГОДНЯ:
💡 Баланс низкий. Рассмотрите возможность добавления постоянного дохода.

📞 Поддержка по VIP подписке: @hXwlssS

Используйте кнопки ниже для управления финансами
"""
    return menu_text

# ========== ОБРАБОТЧИКИ ==========
@bot.message_handler(commands=['start'])
def start(message):
    # Создаем таблицу при запуске
    create_users_table()
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💼 Начать работу 💼', callback_data='start_registration'))
    bot.send_message(
        message.chat.id,
        'Привет! Я Sander, твой личный финансовый помощник! Я помогу сохранить твой кошелек даже когда ну оооочень хочется потратить куда нибудь деньги!😃', 
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'start_registration':
        # Начинаем регистрацию
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text='📝 Давай зарегистрируемся! Как мне тебя называть? 🤔
        )
        # Регистрируем следующий шаг - получение имени
        bot.register_next_step_handler(callback.message, get_user_name_for_registration)
    
    elif callback.data == 'menu':
        # Пытаемся получить имя из БД
        user_name = get_last_user_name()
        if not user_name:
            user_name = get_user_name(callback.message)
        
        menu_text = format_main_menu(user_name)
        
        bot.edit_message_text(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
            text=menu_text,
            reply_markup=get_main_menu_keyboard()
        )
    
    elif callback.data == 'balance':
        bot.answer_callback_query(callback.id, "💰 Баланс: 0₽", show_alert=True)
    
    elif callback.data == 'stats':
        bot.answer_callback_query(callback.id, "📊 Статистика в разработке", show_alert=True)
    
    elif callback.data == 'expenses':
        bot.answer_callback_query(callback.id, "💸 Расходы: 0₽ сегодня", show_alert=True)
    
    elif callback.data == 'income':
        bot.answer_callback_query(callback.id, "💵 Доходы: 0₽ сегодня", show_alert=True)
    
    elif callback.data == 'goals':
        bot.answer_callback_query(callback.id, "🎯 У вас нет активных целей", show_alert=True)
    
    elif callback.data == 'regular':
        bot.answer_callback_query(callback.id, "📅 Регулярные операции отсутствуют", show_alert=True)
    
    elif callback.data == 'achievements':
        bot.answer_callback_query(callback.id, "🏆 Уровень 1 | Опыт: 0 XP", show_alert=True)
    
    elif callback.data == 'calculator':
        bot.answer_callback_query(callback.id, "🧮 Калькулятор скоро будет доступен", show_alert=True)
    
    elif callback.data == 'subscription':
        bot.answer_callback_query(callback.id, "💎 Бесплатный тариф", show_alert=True)
    
    elif callback.data == 'support':
        bot.answer_callback_query(callback.id, "📞 VIP поддержка: @hXwlssS", show_alert=True)

def get_user_name_for_registration(message):
    name = message.text.strip()
    
    # Сохраняем пользователя в БД
    save_user_to_db(name)
    
    # Отправляем подтверждение
    bot.send_message(
        message.chat.id,
        f"✅ Отлично, {name}! Регистрация успешно завершена!"
    )
    
    # Показываем главное меню
    menu_text = format_main_menu(name)
    bot.send_message(
        message.chat.id,
        menu_text,
        reply_markup=get_main_menu_keyboard()
    )

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🤖 Бот Sander Finance запущен...")
    print("📦 Используется SQLite база данных (файл finance_bot.db)")
    bot.polling(none_stop=True)




