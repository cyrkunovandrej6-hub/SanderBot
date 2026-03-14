import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import time
import hashlib
import random

bot = telebot.TeleBot('8526938179:AAHKiBZba2oy3cIcW8eigJL8WAfMypV75YI')
user_temp_data = {}
bot.timeout = 90

ADMIN_ID = 5933197105

# ========== ROBOKASSA ==========
ROBOKASSA_LOGIN = 'sanderfinanceBOT'
ROBOKASSA_PASSWORD1 = 'LZHn2Civ0n1Wyq5ra2pd'
ROBOKASSA_PASSWORD2 = 'Ca4afd1BJQ5fyB2zQW6h'
ROBOKASSA_TEST_MODE = False
SUBSCRIPTION_PRICES = {'month': 149, 'year': 1699}

ABOUT_TEXT = """
📌 *SANDER FINANCE — ПОЛНАЯ ИНФОРМАЦИЯ*

━━━━━━━━━━━━━━━━━━━━━━
📦 *ТОВАРЫ И УСЛУГИ*
━━━━━━━━━━━━━━━━━━━━━━

🔹 *Характеристики:*
• Учёт расходов и доходов
• Аналитика по категориям
• Постоянные платежи (коммуналка, кредиты, подписки)
• Финансовые цели с отслеживанием прогресса
• Калькуляторы (кредитный, вкладов, NPV, налогов, точка безубыточности)

• Premium-подписка с расширенными возможностями

🔹 *Цена:*

• 1 месяц - 150₽
• 1 год - 1650₽
• Базовая версия — полностью бесплатна

━━━━━━━━━━━━━━━━━━━━━━
📞 *КОНТАКТНАЯ ИНФОРМАЦИЯ*
━━━━━━━━━━━━━━━━━━━━━━

🔹 *Контакты:*
• Поддержка: @hXwlssS
• По вопросам сотрудничества: @hXwlssS

🔹 *Заказ:*
• Для начала работы напишите /start и пройдите регистрацию
• Premium-доступ открывается мгновенно после оплаты
• Срок действия подписки отсчитывается с момента оплаты

🔹 *Оплата:*
• Банковские карты (Visa, MasterCard, МИР)
• СБП (Система быстрых платежей)
• ЮMoney, QIWI, SberPay
• Платёжный сервис Robokassa

🔹 *Доставка / Оказание услуг:*
• Услуга предоставляется дистанционно, сразу после оплаты
• Физические товары не поставляются — только цифровой доступ к боту

━━━━━━━━━━━━━━━━━━━━━━
↩️ *ВОЗВРАТ И ОТКАЗ ОТ ПОКУПКИ*
━━━━━━━━━━━━━━━━━━━━━━

🔹 *Условия возврата:*
• В течение 14 дней после оплаты, если услуга не была оказана
• Возврат не производится при частичном использовании платного функционала

🔹 *Алгоритм действий для возврата:*
1. Напишите в поддержку @hXwlssS с темой «Возврат»
2. Укажите ваш Telegram ID, дату и сумму платежа, причину возврата
3. Запрос рассматривается до 3 рабочих дней
4. При одобрении деньги возвращаются на ту же карту или счёт
5. Срок зачисления средств — до 10 рабочих дней (зависит от банка)

⚠️ *Важно:* возврат производится в полной сумме, без вычета комиссий платёжной системы или банка (согласно законодательству РФ)

━━━━━━━━━━━━━━━━━━━━━━
📄 *РЕКВИЗИТЫ И ПЕРСОНАЛЬНЫЕ ДАННЫЕ*
━━━━━━━━━━━━━━━━━━━━━━

🔹 *Реквизиты самозанятого:*
• ФИО: Цыркунов Андрей Сергеевич
• ИНН: 637591970507
• Статус: самозанятый (налог на профессиональный доход)

🔹 *Политика обработки персональных данных:*
• Бот НЕ собирает: паспортные данные, платёжные данные карт, пароли
• Хранятся только: Telegram ID, имя при регистрации, история операций
• Данные не передаются третьим лицам
• Удалить свои данные можно через поддержку @hXwlssS

━━━━━━━━━━━━━━━━━━━━━━
✨ Спасибо, что пользуетесь Sander Finance!
"""


class Expense:
    @classmethod
    def delete_goal(cls, goal_id, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (goal_id, user_id))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def get_goals_count(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM goals WHERE user_id = ?", (user_id,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result

    @classmethod
    def get_active_goals(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM goals WHERE user_id = ? AND current < target", (user_id,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result

    @classmethod
    def get_fixed_income_total(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM fixed_income WHERE user_id = ?", (user_id,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result if result else 0

    @classmethod
    def get_fixed_expenses_total(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM fixed_expenses WHERE user_id = ?", (user_id,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result if result else 0

    @classmethod
    def get_total_income(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM income WHERE user_id = ?", (user_id,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result if result else 0

    @classmethod
    def get_total_expenses(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ?", (user_id,))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result if result else 0

    @classmethod
    def add_goal(cls, user_id, name, target):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO goals (user_id, name, target, current, created_at) VALUES (?, ?, ?, ?, ?)",
                    (user_id, name, target, 0, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def get_goals(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name, target, current FROM goals WHERE user_id = ?", (user_id,))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results

    @classmethod
    def update_goal(cls, goal_id, amount):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("UPDATE goals SET current = current + ? WHERE id = ?", (amount, goal_id))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def get_fixed_income(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name, amount, category FROM fixed_income WHERE user_id = ?", (user_id,))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results

    @classmethod
    def add_fixed_income(cls, user_id, name, amount, category):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO fixed_income (user_id, name, amount, category) VALUES (?, ?, ?, ?)",
                    (user_id, name, amount, category))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def get_fixed_expenses(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT id, name, amount, category FROM fixed_expenses WHERE user_id = ?", (user_id,))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return results

    @classmethod
    def add_fixed_expense(cls, user_id, name, amount, category):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("INSERT INTO fixed_expenses (user_id, name, amount, category) VALUES (?, ?, ?, ?)",
                    (user_id, name, amount, category))
        conn.commit()
        cur.close()
        conn.close()

    @classmethod
    def get_most_common_category(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT category, COUNT(*) as count FROM expenses WHERE user_id = ? GROUP BY category ORDER BY count DESC LIMIT 1", (user_id,))
        result = cur.fetchone()
        cur.close()
        conn.close()
        if result:
            return result[0], result[1]
        return "нет данных", 0

    @classmethod
    def get_week_comparison(cls, user_id):
        today = datetime.now()
        week_ago = today - timedelta(days=7)
        two_weeks_ago = today - timedelta(days=14)
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute('''SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ?''', (user_id, week_ago.strftime("%Y-%m-%d"), today.strftime("%Y-%m-%d")))
        current = cur.fetchone()[0] or 0
        cur.execute('''SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ? ''', (user_id, two_weeks_ago.strftime("%Y-%m-%d"), week_ago.strftime("%Y-%m-%d")))
        previous = cur.fetchone()[0] or 0
        cur.close()
        conn.close()
        return current, previous

    @classmethod
    def get_by_category(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute('SELECT category, SUM(amount) FROM expenses WHERE user_id = ? AND date = ? GROUP BY category', (user_id, today))
        results = cur.fetchall()
        cur.close()
        conn.close()
        return {cat: amount for cat, amount in results}

    @classmethod
    def get_max_today(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute('SELECT MAX(amount) FROM expenses WHERE user_id = ? AND date = ?', (user_id, today))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result if result else 0

    @classmethod
    def get_avg_today(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute('SELECT AVG(amount) FROM expenses WHERE user_id = ? AND date = ?', (user_id, today))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return round(result) if result else 0

    @staticmethod
    def get_category_emoji_static(category):
        emojis = {'🍔 Еда': '🍔', '🚇 Транспорт': '🚇', '🛍️ Покупки': '🛍️', '🎮 Развлечения': '🎮', '🏠 Дом': '🏠', '💊 Здоровье': '💊'}
        if category and category[0] in '🍔🚇🛍️🎮🏠💊✏️📚🐱':
            return category[0]
        return emojis.get(category, '📌')

    def __init__(self, user_id, amount=None, category=None, date=None):
        self.user_id = user_id
        self.amount = amount
        self.category = category
        self.date = date or datetime.now().strftime("%Y-%m-%d")
        self.db_path = 'finance_bot.db'

    def save_to_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
                    (self.user_id, self.amount, self.category, self.date))
        conn.commit()
        cur.close()
        conn.close()
        return self

    @classmethod
    def get_today_total(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date = ?", (user_id, today))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result if result else 0

    def get_comment(self):
        daily_budget = 2000
        percent = (self.amount / daily_budget) * 100
        if self.amount == 0:
            return 'Кто-то явно экономит на обедах!😄'
        elif percent <= 5:
            return 'Так держать! Ты точно понимаешь как тратить деньги с умом!🤠'
        elif percent <= 15:
            return 'Ты большой молодец! Я уверен что эта/и покупка/и принесла/и пользу!👍'
        elif percent <= 30:
            return 'Ой-ой, похоже что ты потратил уже много на сегодня! Попробуй сократить траты😕'
        elif percent <= 50:
            return 'ОСТОРОЖНО!⚠️ Похоже что ты потратил почти 50% бюджета, будь внимательнее к тому что покупаешь!😱'
        elif percent <= 70:
            return 'ТЫ ПОТРАТИЛ ПОЧТИ ВСЕ ДЕНЬГИ!😱'
        elif percent <= 100:
            return 'СРОЧНО! Ты потратил все деньги🙁 В следующий раз будь более внимателен в покупках!'
        else:
            return '🔥 Ты превысил бюджет! Завтра придется экономить!'

    def get_category_emojy(self):
        emojys = {'🍔 Еда': '🍔', '🚇 Транспорт': '🚇', '🛍️ Покупки': '🛍️', '🎮 Развлечения': '🎮', '🏠 Дом': '🏠', '💊 Здоровье': '💊'}
        return emojys.get(self.category, '💰')

    def format_message(self):
        if self.category and self.category[0] in '🍔🚇🛍️🎮🏠💊✏️📚🐱':
            emoji = self.category[0]
            category_text = self.category[1:].strip()
        else:
            emoji = self.get_category_emojy()
            category_text = self.category
        comment = self.get_comment()
        return f"""{emoji} Трата: {self.amount}₽
📌 Категория: {category_text}
{comment}"""

def process_custom_category(message):
    category = message.text.strip()
    user_id = message.from_user.id
    expense = user_temp_data.get(user_id)
    if not expense:
        bot.send_message(message.chat.id, "❌ Ошибка: сначала введи сумму")
        return
    expense.category = category
    expense.save_to_db()
    bot.send_message(message.chat.id, expense.format_message())
    bot.send_message(message.chat.id, "💰 Управление тратами\n\nВыбери действие:", reply_markup=get_expenses_keyboard())
    del user_temp_data[user_id]

@bot.message_handler(commands=['otz'])
def handle_otz_command(message):
    bot.send_message(message.chat.id, "📝 *ОСТАВИТЬ ОТЗЫВ*\n\nНапиши свои пожелания, идеи или замечания — ", parse_mode='Markdown')
    bot.register_next_step_handler(message, process_feedback)

def process_feedback(message):
    feedback = message.text
    user_id = message.from_user.id
    username = message.from_user.username or "нет username"
    first_name = message.from_user.first_name or ""
    DEVELOPER_ID = 5933197105
    dev_message = (f"📩 *НОВЫЙ ОТЗЫВ*\n\n" f"👤 Пользователь: {first_name}\n" f"🆔 ID: {user_id}\n" f"📱 Username: @{username}\n" f"💬 Отзыв:\n{feedback}")
    try:
        bot.send_message(DEVELOPER_ID, dev_message, parse_mode='Markdown')
        bot.send_message(message.chat.id, "✅ Спасибо за отзыв! Он уже отправлен разработчику.\nТвоё мнение помогает нам становиться лучше! ✨")
    except Exception as e:
        bot.send_message(message.chat.id, "❌ Не удалось отправить отзыв. Попробуй позже или свяжись с поддержкой.")

@bot.message_handler(commands=['about'])
def handle_about_command(message):
    bot.send_message(message.chat.id, ABOUT_TEXT, parse_mode='Markdown')

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('👥 Всего пользователей', callback_data='admin_users_total'),
        types.InlineKeyboardButton('🟢 Сейчас в боте', callback_data='admin_users_now'),
        types.InlineKeyboardButton('📢 Рассылка', callback_data='admin_broadcast'),
        types.InlineKeyboardButton('📊 Статистика', callback_data='admin_stats')
    )
    
    bot.send_message(
        message.chat.id,
        "🛠 *АДМИН-ПАНЕЛЬ*\n\nВыбери действие:",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(commands=['add_expense'])
def ask_expence(message):
    msg = bot.send_message(message.chat.id, 'Введи сумму траты ✍️')
    bot.register_next_step_handler(msg, process_expense_amount)

def process_expense_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, '❌ Сумма должна быть больше 0!')
            return
        expense = Expense(user_id=message.from_user.id, amount=amount)
        user_temp_data[message.from_user.id] = expense
        markup = types.InlineKeyboardMarkup(row_width=2)
        categories = ['🍔 Еда', '🚇 Транспорт', '🛍️ Покупки', '🎮 Развлечения', '🏠 Дом', '💊 Здоровье']
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat, callback_data=f'cat_{cat}'))
        markup.add(types.InlineKeyboardButton('✏️ Своя категория', callback_data='custom_category'))
        bot.send_message(message.chat.id, f"💰 Сумма: {amount}₽\n\nВыбери категорию:", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_tax_expenses(message):
    try:
        expenses = float(message.text)
        user_id = message.from_user.id
        if user_id not in user_temp_data or 'tax_income' not in user_temp_data[user_id]:
            bot.send_message(message.chat.id, "❌ Ошибка: начни сначала")
            return
        
        income = user_temp_data[user_id]['tax_income']
        
        if expenses > income:
            bot.send_message(message.chat.id, "❌ Расходы не могут быть больше дохода!")
            return
            
        taxable = income - expenses
        tax = taxable * 0.15
        total = income - tax
        
        text = f"🧾 *НАЛОГ 15% (Доходы - Расходы)*\n\n"
        text += f"• Доход: {income:,.0f}₽\n"
        text += f"• Расход: {expenses:,.0f}₽\n"
        text += f"• Налогооблагаемая база: {taxable:,.0f}₽\n"
        text += f"• Налог: {tax:,.0f}₽\n"
        text += f"• К выплате: {total:,.0f}₽"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔄 Новый расчёт', callback_data='calc_tax'))
        markup.add(types.InlineKeyboardButton('🔙 В меню', callback_data='calc_finance'))
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='Markdown')
        del user_temp_data[user_id]
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

@bot.callback_query_handler(func=lambda call: call.data == 'custom_category')
def handle_custom_category(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "✏️ Введи название своей категории:")
  
@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))
def admin_callback(call):
    if call.from_user.id != ADMIN_ID:
        return

    if call.data == 'admin_users_total':
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM users")
        unique_users = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM registrations")
        unique_reg = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM users")
        total_rows = cur.fetchone()[0]
        cur.close()
        conn.close()
        bot.send_message(
            call.message.chat.id,
            f"📊 *СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ*\n\n"
            f"👤 *Уникальных:* {unique_users}\n"
            f"📝 *Уникальных регистраций:* {unique_reg}\n"
            f"📦 *Всего записей (с дублями):* {total_rows}",
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)

    elif call.data == 'admin_users_now':
        bot.send_message(
            call.message.chat.id,
            "🟢 *Активных прямо сейчас:* ~0\n"
            "(Функция в разработке)",
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)

    elif call.data == 'admin_stats':
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM subscriptions WHERE is_active = 1")
        active_subs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM expenses")
        total_expenses = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM expenses")
        users_with_expenses = cur.fetchone()[0]
        cur.close()
        conn.close()
        bot.send_message(
            call.message.chat.id,
            f"📊 *ОБЩАЯ СТАТИСТИКА*\n\n"
            f"💎 Активных подписок: {active_subs}\n"
            f"💰 Всего трат: {total_expenses}\n"
            f"👥 Пользователей с тратами: {users_with_expenses}",
            parse_mode='Markdown'
        )
        bot.answer_callback_query(call.id)

    else:
        bot.answer_callback_query(call.id, "❌ Неизвестная команда")

@bot.callback_query_handler(func=lambda call: call.data.startswith('deposit_cap_'))
def process_deposit_cap(call):
    data = call.data.split('_')
    cap = data[2]
    user_id = int(data[3])
    if user_id not in user_temp_data:
        bot.answer_callback_query(call.id, "❌ Ошибка, начни сначала")
        return
    data = user_temp_data[user_id]
    amount = data['deposit_amount']
    term = data['deposit_term']
    rate = data['deposit_rate']
    if cap == 'yes':
        total = amount * (1 + rate/100/12) ** term
    else:
        total = amount * (1 + rate/100/12 * term)
    profit = total - amount
    result = f"💰 *РАСЧЁТ ВКЛАДА*\n\n"
    result += f"• Сумма: {amount:,.0f}₽\n"
    result += f"• Срок: {term} мес\n"
    result += f"• Ставка: {rate}%\n"
    result += f"• Капитализация: {'✅' if cap == 'yes' else '❌'}\n\n"
    result += f"📈 Итог: {total:,.0f}₽\n"
    result += f"💵 Доход: {profit:,.0f}₽"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔄 Новый расчёт', callback_data='calc_deposit'))
    markup.add(types.InlineKeyboardButton('🔙 В меню', callback_data='calc_finance'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=result, reply_markup=markup)
    bot.answer_callback_query(call.id)
    del user_temp_data[user_id]

@bot.callback_query_handler(func=lambda call: call.data.startswith('tax_'))
def process_tax_calc(call):
    rate = call.data.replace('tax_', '')
    user_id = call.from_user.id
    if user_id not in user_temp_data:
        bot.answer_callback_query(call.id, "❌ Ошибка, начни сначала")
        return
    income = user_temp_data[user_id]['tax_income']
    
    if rate == '6':
        tax = income * 0.06
        total = income - tax
        text = f"🧾 *НАЛОГ 6% (УСН Доходы)*\n\nДоход: {income:,.0f}₽\nНалог: {tax:,.0f}₽\nК выплате: {total:,.0f}₽"
        
    elif rate == '13':
        tax = income * 0.13
        total = income - tax
        text = f"🧾 *НДФЛ 13%*\n\nДоход: {income:,.0f}₽\nНалог: {tax:,.0f}₽\nК выплате: {total:,.0f}₽"
        
    elif rate == '20':
        tax = income * 0.22
        total = income - tax
        text = f"🧾 *НДС 22%*\n\nСумма без НДС: {income:,.0f}₽\nНДС: {tax:,.0f}₽\nСумма с НДС: {income + tax:,.0f}₽"
        
    elif rate == '15':
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Ввести расходы', callback_data='tax_expenses'))
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🧾 Введи сумму расходов:",
            reply_markup=markup
        )
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔄 Новый расчёт', callback_data='calc_tax'))
    markup.add(types.InlineKeyboardButton('🔙 В меню', callback_data='calc_finance'))
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=markup, parse_mode='Markdown')
    del user_temp_data[user_id]
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_'))
def process_category(call):
    category = call.data.replace('cat_', '')
    user_id = call.from_user.id
    expense = user_temp_data.get(user_id)
    if not expense:
        bot.answer_callback_query(call.id, "❌ Ошибка: сначала введи сумму")
        return
    expense.category = category
    expense.save_to_db()
    bot.send_message(call.message.chat.id, expense.format_message())
    bot.send_message(call.message.chat.id, "💰 Управление тратами\n\nВыбери действие:", reply_markup=get_expenses_keyboard())
    del user_temp_data[user_id]
    bot.answer_callback_query(call.id, "✅ Трата добавлена!")

@bot.callback_query_handler(func=lambda call: call.data == 'broadcast_send')
def admin_broadcast_send(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    broadcast_text = user_temp_data.get(f"broadcast_{ADMIN_ID}")
    if not broadcast_text:
        bot.answer_callback_query(call.id, "❌ Ошибка: текст не найден")
        return
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📢 *РАССЫЛКА ЗАПУЩЕНА*\n\n"
             f"Всего пользователей: {len(users)}\n"
             f"Отправка началась...",
        parse_mode='Markdown'
    )
    success = 0
    failed = 0

    for (user_id,) in users:
        try:
            bot.send_message(user_id, broadcast_text, parse_mode='Markdown')
            success += 1
        except Exception as e:
            failed += 1
            print(f"Не удалось отправить пользователю {user_id}: {e}")

        time.sleep(0.05)
    bot.send_message(
        call.message.chat.id,
        f"📊 *ИТОГИ РАССЫЛКИ*\n\n"
        f"✅ Успешно: {success}\n"
        f"❌ Ошибок: {failed}\n"
        f"👥 Всего: {len(users)}",
        parse_mode='Markdown'
    )
    del user_temp_data[f"broadcast_{ADMIN_ID}"]

@bot.callback_query_handler(func=lambda call: call.data == 'admin_panel')
def admin_panel_return(call):
    if call.from_user.id != ADMIN_ID:
        return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('👥 Всего пользователей', callback_data='admin_users_total'),
        types.InlineKeyboardButton('🟢 Сейчас в боте', callback_data='admin_users_now'),
        types.InlineKeyboardButton('📢 Рассылка', callback_data='admin_broadcast'),
        types.InlineKeyboardButton('📊 Статистика', callback_data='admin_stats')
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="🛠 *АДМИН-ПАНЕЛЬ*\n\nВыбери действие:",
        parse_mode='Markdown',
        reply_markup=markup
    )
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'balance')
def show_balance(call):
    bot.send_message(call.message.chat.id, "💰 Управление тратами", reply_markup=get_expenses_keyboard())
    bot.answer_callback_query(call.id)

def show_balance_expenses(call):
    user_id = call.from_user.id
    today_total = Expense.get_today_total(user_id)
    temp_expense = Expense(user_id, today_total)
    daily_budget = 2000
    percent = (today_total / daily_budget) * 100
    message = f"""💰 Траты сегодня: {today_total}₽
📊 Использовано: {percent:.1f}% от дневного бюджета

{temp_expense.get_comment()}

Чтобы добавить трату, нажми /add_expense"""
    bot.send_message(call.message.chat.id, message, reply_markup=get_main_menu_keyboard())

def create_users_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    name TEXT, 
                    pss TEXT)''')
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Таблица users создана")

def create_registrations_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS registrations 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    username TEXT,
                    first_name TEXT,
                    registered_at TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def create_subscriptions_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS subscriptions (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE, expires_at TEXT, is_active INTEGER DEFAULT 1)''')
    conn.commit()
    cur.close()
    conn.close()

def create_income_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS income 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    category TEXT,
                    date TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def create_goals_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS goals
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    target REAL,
                    current REAL,
                    created_at TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def create_fixed_income_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS fixed_income 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    amount REAL,
                    category TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def create_expenses_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS expenses 
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    category TEXT,
                    date TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def create_fixed_expenses_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS fixed_expenses
                   (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT,
                    amount REAL,
                    category TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def is_premium(user_id):
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''SELECT is_active FROM subscriptions WHERE user_id = ? AND expires_at > datetime('now')''', (user_id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result is not None

def save_user_to_db(name):
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, pss) VALUES (?, ?)", (name, 'temp_password'))
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

# ====== ТАБЛИЦЫ =======
create_income_table()
create_goals_table()
create_fixed_income_table()
create_fixed_expenses_table()
create_users_table()
create_expenses_table()
create_subscriptions_table()
create_registrations_table()

def process_delete_goal_choice(message):
    try:
        num = int(message.text)
        user_id = message.from_user.id
        goals = user_temp_data[user_id]['delete_goals']
        if 1 <= num <= len(goals):
            goal = goals[num-1]
            goal_id, goal_name = goal[0], goal[1]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('✅ Да, удалить', callback_data=f'confirm_delete_goal_{goal_id}'),
                       types.InlineKeyboardButton('❌ Нет', callback_data='goals'))
            bot.send_message(message.chat.id, f"Точно удалить цель «{goal_name}»?", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Неверный номер. Попробуй снова.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")
    finally:
        if user_id in user_temp_data and 'delete_goals' in user_temp_data[user_id]:
            del user_temp_data[user_id]['delete_goals']

def admin_broadcast_confirm(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    broadcast_text = message.text
    user_temp_data[f"broadcast_{ADMIN_ID}"] = broadcast_text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton('✅ Отправить', callback_data='broadcast_send'),
        types.InlineKeyboardButton('❌ Отмена', callback_data='admin_panel')
    )
    bot.send_message(
        message.chat.id,
        f"📢 *ПРЕДПРОСМОТР*\n\n"
        f"{broadcast_text}\n\n"
        f"👉 Отправляем всем пользователям?",
        parse_mode='Markdown',
        reply_markup=markup
    )

def process_fund_choice(message):
    try:
        num = int(message.text)
        user_id = message.from_user.id
        goals = user_temp_data[user_id]['fund_goals']
        if 1 <= num <= len(goals):
            goal = goals[num-1]
            user_temp_data[user_id]['fund_goal_id'] = goal[0]
            user_temp_data[user_id]['fund_goal_name'] = goal[1]
            msg = bot.send_message(message.chat.id, f"🎯 Цель: {goal[1]}\n" f"💰 Накоплено: {goal[3]}₽ / {goal[2]}₽\n\n" f"Введи сумму пополнения:")
            bot.register_next_step_handler(msg, process_fund_amount)
        else:
            bot.send_message(message.chat.id, "❌ Неверный номер. Попробуй снова.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_fund_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
        user_id = message.from_user.id
        goal_id = user_temp_data[user_id]['fund_goal_id']
        goal_name = user_temp_data[user_id]['fund_goal_name']
        Expense.update_goal(goal_id, amount)
        goals = Expense.get_goals(user_id)
        for g in goals:
            if g[0] == goal_id:
                current, target = g[3], g[2]
                break
        bot.send_message(message.chat.id, f"✅ Готово!\n\n" f"• {goal_name}: {current}₽ / {target}₽\n" f"• Прогресс: {(current/target)*100:.1f}%")
        markup = get_goals_keyboard()
        bot.send_message(message.chat.id, "🎯 УПРАВЛЕНИЕ ЦЕЛЯМИ", reply_markup=markup)
        del user_temp_data[user_id]['fund_goal_id']
        del user_temp_data[user_id]['fund_goal_name']
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_goal_name(message):
    name = message.text.strip()
    user_id = message.from_user.id
    if user_id not in user_temp_data:
        user_temp_data[user_id] = {}
    user_temp_data[user_id]['goal_name'] = name
    msg = bot.send_message(message.chat.id, f"🎯 Название: {name}\n\nВведи сумму, которую нужно накопить (только число):")
    bot.register_next_step_handler(msg, process_goal_target)

def process_goal_target(message):
    try:
        target = float(message.text)
        if target <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
        user_id = message.from_user.id
        name = user_temp_data[user_id]['goal_name']
        Expense.add_goal(user_id, name, target)
        bot.send_message(message.chat.id, f"✅ Цель добавлена!\n\n" f"• {name}: 0₽ / {target}₽")
        markup = get_goals_keyboard()
        bot.send_message(message.chat.id, "🎯 УПРАВЛЕНИЕ ЦЕЛЯМИ", reply_markup=markup)
        del user_temp_data[user_id]['goal_name']
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_income_custom_category(message):
    category = message.text.strip()
    user_id = message.from_user.id
    if user_id not in user_temp_data:
        bot.send_message(message.chat.id, "❌ Ошибка: начни сначала")
        return
    name = user_temp_data[user_id].get('income_name', '')
    amount = user_temp_data[user_id].get('income_amount', 0)
    if not name or not amount:
        bot.send_message(message.chat.id, "❌ Ошибка: данные не найдены")
        return
    Expense.add_fixed_income(user_id, name, amount, category)
    bot.send_message(message.chat.id, f"✅ Постоянный доход добавлен!\n\n" f"• {name}: {amount}₽ ({category})")
    if 'income_name' in user_temp_data[user_id]:
        del user_temp_data[user_id]['income_name']
    if 'income_amount' in user_temp_data[user_id]:
        del user_temp_data[user_id]['income_amount']
    markup = get_fixed_income_keyboard()
    bot.send_message(message.chat.id, "💼 ПОСТОЯННЫЕ ДОХОДЫ", reply_markup=markup)

def progress_bar(current, target, length=20):
    if target == 0:
        return '▱' * length
    percent = (current / target) * 100
    filled = int(percent / 100 * length)
    return '▰' * filled + '▱' * (length - filled)

def process_delete_income(message):
    try:
        num = int(message.text)
        user_id = message.from_user.id
        incomes = user_temp_data[user_id]['income_delete_list']
        if 1 <= num <= len(incomes):
            income_id = incomes[num-1][0]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('✅ Да, удалить', callback_data=f'confirm_income_delete_{income_id}'),
                       types.InlineKeyboardButton('❌ Нет', callback_data='fixed_income'))
            bot.send_message(message.chat.id, f"Точно удалить доход '{incomes[num-1][1]}'?", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Неверный номер. Попробуй снова.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_income_name(message):
    name = message.text.strip()
    user_id = message.from_user.id
    if user_id not in user_temp_data:
        user_temp_data[user_id] = {}
    user_temp_data[user_id]['income_name'] = name
    msg = bot.send_message(message.chat.id, f"💰 Название: {name}\n\n" "Введи сумму дохода в месяц:")
    bot.register_next_step_handler(msg, process_income_amount)

def process_income_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
        user_id = message.from_user.id
        name = user_temp_data[user_id]['income_name']
        user_temp_data[user_id]['income_amount'] = amount
        markup = types.InlineKeyboardMarkup(row_width=2)
        categories = ['💼 Зарплата', '🏠 Аренда', '📈 Инвестиции', '💻 Фриланс', '🎁 Подарки', '💳 Проценты']
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat, callback_data=f'income_cat_{cat}'))
        markup.add(types.InlineKeyboardButton('✏️ Своя', callback_data='income_custom_category'))
        bot.send_message(message.chat.id, f"💰 {name}: {amount}₽\n\nВыбери категорию:", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_fixed_name(message):
    name = message.text.strip()
    user_id = message.from_user.id
    if user_id not in user_temp_data:
        user_temp_data[user_id] = {}
    user_temp_data[user_id]['fixed_name'] = name
    msg = bot.send_message(message.chat.id, f"💰 Название: {name}\n\nВведи сумму расхода в месяц:")
    bot.register_next_step_handler(msg, process_fixed_amount)

def process_fixed_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
        user_id = message.from_user.id
        name = user_temp_data[user_id].get('fixed_name', 'Без названия')
        user_temp_data[user_id]['fixed_amount'] = amount
        markup = types.InlineKeyboardMarkup(row_width=2)
        categories = ['🏠 Коммуналка', '💳 Кредиты', '📺 Подписки', '🚗 Транспорт', '🏥 Здоровье', '📚 Обучение']
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat, callback_data=f'fixed_cat_{cat}'))
        markup.add(types.InlineKeyboardButton('✏️ Своя категория', callback_data='fixed_custom_category'))
        bot.send_message(message.chat.id, f"💰 {name}: {amount}₽\n\nВыбери категорию:", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def get_calculator_main_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('🧮 Обычный', callback_data='calc_simple'), types.InlineKeyboardButton('💰 Финансовый', callback_data='calc_finance'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    return markup

def get_finance_calculator_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('💰 Кредит', callback_data='calc_credit'), types.InlineKeyboardButton('💰 Вклады', callback_data='calc_deposit'))
    markup.add(types.InlineKeyboardButton('💼 Рентабельность', callback_data='calc_profit'), types.InlineKeyboardButton('📊 Точка безубыточности', callback_data='calc_breakeven'))
    markup.add(types.InlineKeyboardButton('🧾 Налоги', callback_data='calc_tax'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='calculator'))
    return markup

def get_subscription_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('💎 1 месяц — 149₽', callback_data='sub_month'), types.InlineKeyboardButton('👑 1 год — 1699₽', callback_data='sub_year'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    return markup

def get_fixed_expenses_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('➕ Добавить', callback_data='add_fixed'),
               types.InlineKeyboardButton('📋 Список', callback_data='list_fixed'))
    markup.add(types.InlineKeyboardButton('🗑 Удалить', callback_data='delete_fixed'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    return markup

def get_user_name(message):
    if message.from_user.first_name:
        return message.from_user.first_name
    elif message.from_user.username:
        return message.from_user.username
    else:
        return "Пользователь"

def get_main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('🎩 Траты', callback_data='balance'),
               types.InlineKeyboardButton('📊 Статистика', callback_data='stats'))
    markup.add(types.InlineKeyboardButton('💸 Расходы', callback_data='fixed_expenses'),
               types.InlineKeyboardButton('💼 Постоянные доходы', callback_data='income'))
    markup.add(types.InlineKeyboardButton('🧩 Цели', callback_data='goals'))
    markup.add(types.InlineKeyboardButton('🧮 Калькулятор', callback_data='calculator'))
    markup.add(types.InlineKeyboardButton('💎 Подписка', callback_data='subscription'))
    return markup

def get_goals_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('➕ Новая цель', callback_data='add_goal'),
               types.InlineKeyboardButton('📋 Мои цели', callback_data='list_goals'))
    markup.add(types.InlineKeyboardButton('💰 Пополнить', callback_data='fund_goal'),
               types.InlineKeyboardButton('❌ Удалить', callback_data='delete_goal'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    return markup

def get_fixed_income_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('➕ Добавить', callback_data='add_income'),
               types.InlineKeyboardButton('📋 Список', callback_data='list_income'))
    markup.add(types.InlineKeyboardButton('🗑 Удалить', callback_data='delete_income'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    return markup

def get_expenses_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('➕ Добавить трату', callback_data='add_expense_menu'),
               types.InlineKeyboardButton('📊 Анализ трат', callback_data='expense_analysis'))
    markup.add(types.InlineKeyboardButton('📆 Траты за неделю', callback_data='expenses_week'))
    markup.add(types.InlineKeyboardButton('🔙 Назад в меню', callback_data='menu'))
    return markup

def format_main_menu(user_name, user_id):
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
    goals_count = Expense.get_goals_count(user_id)
    active_goals = Expense.get_active_goals(user_id)
    fixed_income = Expense.get_fixed_income_total(user_id)
    fixed_expenses = Expense.get_fixed_expenses_total(user_id)
    today_total = Expense.get_today_total(user_id)
    current_week, _ = Expense.get_week_comparison(user_id)
    week_total = current_week
    goals_status = f"{active_goals} активных / {goals_count} всего" if goals_count > 0 else "🎯 Нет целей"
    menu_text = f"""
☀️ {greeting}, {user_name}! 👋

✨ ДОБРО ПОЖАЛОВАТЬ В SANDER FINANCE!
Ваш персональный финансовый помощник с калькулятором 🏦

📊 ВАША ФИНАНСОВАЯ СВОДКА:

💸 РАСХОДЫ:
• Сегодня: {today_total:,.0f}₽
• За неделю: {week_total:,.0f}₽

🎯 ЦЕЛИ:
• Всего целей: {goals_count}
• Активных: {active_goals}
• Статус: {goals_status}

💼 РЕГУЛЯРНЫЕ ОПЕРАЦИИ:
• Доходы в месяц: {fixed_income:,.0f}₽
• Расходы в месяц: {fixed_expenses:,.0f}₽
• Финансовое здоровье: ⚖️ Сбалансированный бюджет

🧮 Финансовый калькулятор:
• Кредиты и вклады
• Инфляция и ROI
• Цели накоплений

📞 Поддержка: @hXwlssS
"""
    return menu_text

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_goal_'))
def confirm_delete_goal(call):
    goal_id = int(call.data.replace('confirm_delete_goal_', ''))
    user_id = call.from_user.id
    Expense.delete_goal(goal_id, user_id)
    bot.answer_callback_query(call.id, "✅ Цель удалена!", show_alert=True)
    markup = get_goals_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,text="🎯 УПРАВЛЕНИЕ ЦЕЛЯМИ", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('income_cat_'))
def process_income_category(call):
    category = call.data.replace('income_cat_', '')
    user_id = call.from_user.id
    if user_id not in user_temp_data:
        bot.answer_callback_query(call.id, "❌ Ошибка: начни сначала")
        return
    user_data = user_temp_data.get(user_id, {})
    name = user_data.get('income_name', '')
    amount = user_data.get('income_amount', 0)
    if not name or not amount:
        bot.answer_callback_query(call.id, "❌ Ошибка: данные не найдены")
        return
    Expense.add_fixed_income(user_id, name, amount, category)
    bot.send_message(call.message.chat.id, f"✅ Постоянный доход добавлен!\n\n" f"• {name}: {amount}₽ ({category})")
    if 'income_name' in user_temp_data[user_id]:
        del user_temp_data[user_id]['income_name']
    if 'income_amount' in user_temp_data[user_id]:
        del user_temp_data[user_id]['income_amount']
    markup = get_fixed_income_keyboard()
    bot.send_message(call.message.chat.id, "💼 ПОСТОЯННЫЕ ДОХОДЫ", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'income_custom_category')
def handle_income_custom_category(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "✏️ Введи название своей категории дохода:")
    bot.register_next_step_handler(msg, process_income_custom_category)

@bot.callback_query_handler(func=lambda call: call.data == 'admin_broadcast')
def admin_broadcast_start(call):
    if call.from_user.id != ADMIN_ID:
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        "📢 *РАССЫЛКА*\n\n"
        "Введи сообщение, которое нужно отправить всем пользователям:\n"
        "(можно использовать Markdown)",
        parse_mode='Markdown'
    )
    bot.register_next_step_handler(msg, admin_broadcast_confirm)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_income_delete_'))
def confirm_delete_income(call):
    income_id = int(call.data.replace('confirm_income_delete_', ''))
    user_id = call.from_user.id
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM fixed_income WHERE id = ? AND user_id = ?", (income_id, user_id))
    conn.commit()
    cur.close()
    conn.close()
    bot.answer_callback_query(call.id, "✅ Доход удалён!", show_alert=True)
    markup = get_fixed_income_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="💼 ПОСТОЯННЫЕ ДОХОДЫ\n\nУправляй своими поступлениями:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_fixed_'))
def confirm_delete_fixed(call):
    expense_id = int(call.data.replace('delete_fixed_', ''))
    user_id = call.from_user.id
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute("DELETE FROM fixed_expenses WHERE id = ? AND user_id = ?", (expense_id, user_id))
    conn.commit()
    cur.close()
    conn.close()
    bot.answer_callback_query(call.id, "✅ Удалено!", show_alert=True)
    markup = get_fixed_expenses_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="💸 ПОСТОЯННЫЕ РАСХОДЫ\n\nУправляй своими регулярными платежами:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('fixed_cat_'))
def process_fixed_category(call):
    category = call.data.replace('fixed_cat_', '')
    user_id = call.from_user.id
    user_data = user_temp_data.get(user_id, {})
    name = user_data.get('fixed_name', 'Без названия')
    amount = user_data.get('fixed_amount', 0)
    if not name or not amount:
        bot.answer_callback_query(call.id, "❌ Ошибка: начни сначала")
        return
    Expense.add_fixed_expense(user_id, name, amount, category)
    bot.send_message(call.message.chat.id, f"✅ Постоянный расход добавлен!\n\n" f"• {name}: {amount}₽ ({category})")
    markup = get_fixed_expenses_keyboard()
    bot.send_message(call.message.chat.id, "💸 ПОСТОЯННЫЕ РАСХОДЫ", reply_markup=markup)
    if user_id in user_temp_data:
        if 'fixed_name' in user_temp_data[user_id]:
            del user_temp_data[user_id]['fixed_name']
        if 'fixed_amount' in user_temp_data[user_id]:
            del user_temp_data[user_id]['fixed_amount']
    bot.answer_callback_query(call.id, "✅ Готово!")

@bot.callback_query_handler(func=lambda call: call.data == 'fixed_custom_category')
def handle_fixed_custom_category(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "✏️ Введи название своей категории:")
    bot.register_next_step_handler(msg, process_fixed_custom_category)

def process_fixed_custom_category(message):
    category = message.text.strip()
    user_id = message.from_user.id
    if user_id not in user_temp_data:
        bot.send_message(message.chat.id, "❌ Ошибка: начни сначала")
        return
    name = user_temp_data[user_id].get('fixed_name', '')
    amount = user_temp_data[user_id].get('fixed_amount', 0)
    if not name or not amount:
        bot.send_message(message.chat.id, "❌ Ошибка: данные не найдены")
        return
    Expense.add_fixed_expense(user_id, name, amount, category)
    bot.send_message(message.chat.id, f"✅ Постоянный расход добавлен!\n\n" f"• {name}: {amount}₽ ({category})")
    if 'fixed_name' in user_temp_data[user_id]:
        del user_temp_data[user_id]['fixed_name']
    if 'fixed_amount' in user_temp_data[user_id]:
        del user_temp_data[user_id]['fixed_amount']
    markup = get_fixed_expenses_keyboard()
    bot.send_message(message.chat.id, "💸 ПОСТОЯННЫЕ РАСХОДЫ", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🧩 Цели')
def handle_goals_reply(message):
    markup = get_goals_keyboard()
    bot.send_message(message.chat.id, "🎯 УПРАВЛЕНИЕ ЦЕЛЯМИ\n\nСтавь финансовые цели и отслеживай прогресс:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🧮 Калькулятор')
def handle_calculator_reply(message):
    markup = get_calculator_main_keyboard()
    bot.send_message(message.chat.id,  "🧮 *ВЫБЕРИТЕ РЕЖИМ РАБОТЫ*\n\nДоступны два режима:\n• Обычный калькулятор — просто отправь пример (2+2)\n• Финансовый калькулятор — расширенные расчёты", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💼 Начать работу 💼', callback_data='start_registration'))
    try:
        with open('Текст абзаца.jpg', 'rb') as photo_file:
            bot.send_photo(message.chat.id, photo_file,
                           caption='Привет! Я Sander, твой личный финансовый помощник! Я помогу сохранить твой кошелек даже когда ну оооочень хочется потратить куда нибудь деньги!',
                           reply_markup=markup)
    except:
        bot.send_message(message.chat.id,
                         'Привет! Я Sander, твой личный финансовый помощник! Я помогу сохранить твой кошелек даже когда ну оооочень хочется потратить куда нибудь деньги!',
                         reply_markup=markup)

@bot.message_handler(func=lambda message: message.text and any(op in message.text for op in ['+', '-', '*', '/']) and not message.text.startswith('/'))
def handle_simple_calculator(message):
    try:
        text = message.text.replace(' ', '')
        if '+' in text:
            a, b = map(float, text.split('+'))
            result = a + b
            op = '+'
        elif '-' in text:
            a, b = map(float, text.split('-'))
            result = a - b
            op = '-'
        elif '*' in text:
            a, b = map(float, text.split('*'))
            result = a * b
            op = '×'
        elif '/' in text:
            a, b = map(float, text.split('/'))
            if b == 0:
                bot.reply_to(message, "❌ На ноль делить нельзя!")
                return
            result = a / b
            op = '÷'
        else:
            return
        
        bot.reply_to(message, f"🧮 Результат: {a:g} {op} {b:g} = {result:g}") 
    except:
        bot.reply_to(message, "❌ Неверный формат. Используй: 2+2, 10-3, 7*8, 15/4")

@bot.message_handler(func=lambda message: message.text == '💼 Постоянные доходы')
def handle_fixed_income(message):
    markup = get_fixed_income_keyboard()
    bot.send_message(message.chat.id, "💼 ПОСТОЯННЫЕ ДОХОДЫ\n\nУправляй своими регулярными поступлениями:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '💸 Постоянные расходы')
def handle_fixed_expenses(message):
    markup = get_fixed_expenses_keyboard()
    bot.send_message(message.chat.id,"💸 ПОСТОЯННЫЕ РАСХОДЫ\n\nЗдесь ты можешь управлять регулярными платежами:\n• 🏠 Коммуналка\n• 💳 Кредиты\n• 📺 Подписки\n• и другие ежемесячные расходы", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🎩 Траты')
def handle_traits(message):
    bot.send_message(message.chat.id, "💰 Управление тратами", reply_markup=get_expenses_keyboard())

@bot.message_handler(func=lambda message: message.text == '💎 Подписка')
def handle_subscription_reply(message):
    markup = get_subscription_keyboard()
    bot.send_message(
        message.chat.id,
        "💎 *SANDER PREMIUM*\n\n"
        "💰 Цены на подписку:\n"
        "• 1 месяц — 149₽\n"
        "• 1 год — 1699₽ (скидка 37%)\n\n"
        "🎁 Преимущества Premium:\n"
        "1 - Отдельный VIP-бот с обновлениями\n"
        "2 - VIP-чат с админом\n\n"
        "Выбери срок подписки:",
        parse_mode='Markdown',
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == '📊 Статистика')
def handle_stats(message):
    user_id = message.from_user.id
    user_name = get_last_user_name() or "Пользователь"
    most_common_category_name, most_common_category_count = Expense.get_most_common_category(user_id)
    msg = f"📊 СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ: {user_name}\n\n"
    msg += f"🔥 Самая частая категория: {most_common_category_name} — {most_common_category_count} раз(а)"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🔙 Назад в меню', callback_data='menu'))
    bot.send_message(message.chat.id, msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'start_registration':
        bot.send_message(callback.message.chat.id, '📝 Давай зарегистрируемся! Как мне тебя называть? 🤔')
        bot.register_next_step_handler(callback.message, get_user_name_for_registration)

    elif callback.data == 'fund_goal':
        user_id = callback.from_user.id
        goals = Expense.get_goals(user_id)
        if not goals:
            bot.answer_callback_query(callback.id, "❌ У тебя нет целей для пополнения", show_alert=True)
            return
        msg = "💰 ВЫБЕРИ ЦЕЛЬ ДЛЯ ПОПОЛНЕНИЯ:\n\n"
        for i, goal in enumerate(goals, 1):
            name, target, current = goal[1], goal[2], goal[3]
            percent = (current / target) * 100
            msg += f"{i}. {name} — {current}₽ / {target}₽ ({percent:.1f}%)\n"
        msg += "\nНапиши номер цели:"
        bot.send_message(callback.message.chat.id, msg)
        user_temp_data[user_id] = {'fund_goals': goals}
        bot.register_next_step_handler(callback.message, process_fund_choice)
        bot.answer_callback_query(callback.id)
    
    elif callback.data == 'admin_users_now':
        bot.send_message(
            callback.message.chat.id,
            "🟢 *Активных прямо сейчас:* ~0\n"
            "(Функция в разработке)",
            parse_mode='Markdown'
        )
    elif callback.data == 'admin_broadcast':
        msg = bot.send_message(
            callback.message.chat.id,
            "📢 Введи сообщение для рассылки:"
        )
        bot.register_next_step_handler(msg, admin_broadcast_send)
    
    elif callback.data == 'admin_stats':
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM subscriptions WHERE is_active = 1")
        active_subs = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM expenses")
        total_expenses = cur.fetchone()[0]
        cur.execute("SELECT COUNT(DISTINCT user_id) FROM expenses")
        users_with_expenses = cur.fetchone()[0]
        cur.close()
        conn.close()
        bot.send_message(
            callback.message.chat.id,
            f"📊 *ОБЩАЯ СТАТИСТИКА*\n\n"
            f"💎 Активных подписок: {active_subs}\n"
            f"💰 Всего трат: {total_expenses}\n"
            f"👥 Пользователей с тратами: {users_with_expenses}",
            parse_mode='Markdown'
        )

    elif callback.data in ['sub_month', 'sub_year']:
        sub_type = callback.data.replace('sub_', '')
        user_id = callback.from_user.id
        payment_link, inv_id = generate_payment_link(user_id, sub_type)
        user_temp_data[f"order_{user_id}"] = {'inv_id': inv_id, 'sub_type': sub_type, 'user_id': user_id}
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('💳 Перейти к оплате', url=payment_link))
        markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='subscription'))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=f"💎 *ОФОРМЛЕНИЕ ПОДПИСКИ*\n\n" f"Ты выбрал: *{sub_type}*\n" f"Сумма к оплате: *{SUBSCRIPTION_PRICES[sub_type]}₽*\n\n" f"После оплаты подписка активируется автоматически. Обычно это занимает 1–2 минуты.", parse_mode='Markdown', reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'calc_credit':
        msg = bot.send_message(callback.message.chat.id, "💰 *КРЕДИТНЫЙ КАЛЬКУЛЯТОР*\n\nВведи сумму кредита в рублях:")
        bot.register_next_step_handler(msg, process_credit_amount)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'calc_deposit':
        msg = bot.send_message(callback.message.chat.id, "💰 *КАЛЬКУЛЯТОР ВКЛАДОВ*\n\nВведи начальную сумму в рублях:")
        bot.register_next_step_handler(msg, process_deposit_amount)
        bot.answer_callback_query(callback.id)
    
    elif callback.data == 'calc_npv':
        msg = bot.send_message(callback.message.chat.id, "📈 *NPV (Чистая приведенная стоимость)*\n\nВведи начальные инвестиции (₽):")
        bot.register_next_step_handler(msg, process_npv_investment)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'calc_profit':
        msg = bot.send_message(callback.message.chat.id, "💼 *РЕНТАБЕЛЬНОСТЬ*\n\nВведи выручку (₽):")
        bot.register_next_step_handler(msg, process_profit_revenue)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'calc_breakeven':
        msg = bot.send_message(callback.message.chat.id, "📊 *ТОЧКА БЕЗУБЫТОЧНОСТИ*\n\nВведи постоянные затраты (₽):")
        bot.register_next_step_handler(msg, process_breakeven_fixed)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'calc_tax':
        msg = bot.send_message(callback.message.chat.id, "🧾 *НАЛОГОВЫЙ КАЛЬКУЛЯТОР*\n\nВведи сумму дохода (₽):")
        bot.register_next_step_handler(msg, process_tax_income)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'calculator':
        markup = get_calculator_main_keyboard()
        bot.send_message(
            callback.message.chat.id,
            "🧮 *ВЫБЕРИТЕ РЕЖИМ РАБОТЫ*\n\n"
            "Доступны два режима:\n"
            "• Обычный калькулятор — просто отправь пример (2+2)\n"
            "• Финансовый калькулятор — расширенные расчёты",
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(callback.id)
    
    elif callback.data == 'calc_simple':
        bot.send_message(
            callback.message.chat.id,
            "🧮 *ОБЫЧНЫЙ КАЛЬКУЛЯТОР*\n\n"
            "Просто напиши мне пример:\n"
            "`2 + 2`\n"
            "`10 - 3`\n"
            "`7 * 8`\n"
            "`15 / 4`\n\n"
            "Я отвечу результатом.",
            parse_mode='Markdown'
        )
        bot.answer_callback_query(callback.id)
    
    elif callback.data == 'calc_finance':
        markup = get_finance_calculator_keyboard()
        bot.send_message(
            callback.message.chat.id,
            "💰 *ФИНАНСОВЫЙ КАЛЬКУЛЯТОР*\n\n"
            "Выберите тип расчёта:",
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(callback.id)

    elif callback.data == 'delete_goal':
        user_id = callback.from_user.id
        goals = Expense.get_goals(user_id)
        if not goals:
            bot.answer_callback_query(callback.id, "❌ У тебя нет целей для удаления", show_alert=True)
            return
        msg = "❌ ВЫБЕРИ ЦЕЛЬ ДЛЯ УДАЛЕНИЯ:\n\n"
        for i, goal in enumerate(goals, 1):
            name, target, current = goal[1], goal[2], goal[3]
            percent = (current / target) * 100
            msg += f"{i}. {name} — {current}₽ / {target}₽ ({percent:.1f}%)\n"
        msg += "\nНапиши номер цели, которую хочешь удалить:"
        bot.send_message(callback.message.chat.id, msg)
        user_temp_data[user_id] = {'delete_goals': goals}
        bot.register_next_step_handler(callback.message, process_delete_goal_choice)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'list_goals':
        user_id = callback.from_user.id
        goals = Expense.get_goals(user_id)
        if not goals:
            bot.send_message(callback.message.chat.id, "📋 ТВОИ ЦЕЛИ\n\nУ тебя пока нет целей.\nНажми ➕ Новая цель, чтобы создать.")
        else:
            msg = "🎯 ТВОИ ЦЕЛИ:\n\n"
            for goal in goals:
                goal_id, name, target, current = goal
                percent = (current / target) * 100
                bar = progress_bar(current, target)
                msg += f"<b>{name}</b>\n"
                msg += f"   {current:,.0f}₽ / {target:,.0f}₽ ({percent:.1f}%)\n"
                msg += f"   {bar}\n\n"
            bot.send_message(callback.message.chat.id, msg, parse_mode='HTML')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Назад к целям', callback_data='goals'))
        bot.send_message(callback.message.chat.id, "👇 Вернуться в меню:", reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'add_goal':
        msg = bot.send_message(callback.message.chat.id, "➕ НОВАЯ ЦЕЛЬ\n\nВведи название цели (например: MacBook, Машина, Путешествие):")
        bot.register_next_step_handler(msg, process_goal_name)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'goals':
        markup = get_goals_keyboard()
        bot.send_message(callback.message.chat.id, "🎯 УПРАВЛЕНИЕ ЦЕЛЯМИ\n\nСтавь финансовые цели и отслеживай прогресс:", reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'income':
        markup = get_fixed_income_keyboard()
        bot.send_message(callback.message.chat.id,
                         "💼 ПОСТОЯННЫЕ ДОХОДЫ\n\n💰 Регулярные поступления:\n• Зарплата\n• Аренда\n• Проценты\n• Подработки\n• Другие источники",
                         reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'add_income':
        msg = bot.send_message(callback.message.chat.id, "➕ ДОБАВЛЕНИЕ ПОСТОЯННОГО ДОХОДА\n\nВведи название:")
        bot.register_next_step_handler(msg, process_income_name)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'list_income':
        user_id = callback.from_user.id
        incomes = Expense.get_fixed_income(user_id)
        if not incomes:
            bot.send_message(callback.message.chat.id, "📋 ПОСТОЯННЫЕ ДОХОДЫ\n\nУ тебя пока нет доходов.")
        else:
            msg = "📋 ТВОИ ПОСТОЯННЫЕ ДОХОДЫ:\n\n"
            total = 0
            for inc in incomes:
                msg += f"• {inc[1]}: {inc[2]}₽ ({inc[3]})\n"
                total += inc[2]
            msg += f"\n💰 Итого в месяц: {total}₽"
            bot.send_message(callback.message.chat.id, msg)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'delete_income':
        user_id = callback.from_user.id
        incomes = Expense.get_fixed_income(user_id)
        if not incomes:
            bot.answer_callback_query(callback.id, "❌ Нет доходов для удаления", show_alert=True)
            return
        msg = "🗑 ВЫБЕРИ ДОХОД ДЛЯ УДАЛЕНИЯ:\n\n"
        for i, inc in enumerate(incomes, 1):
            msg += f"{i}. {inc[1]} — {inc[2]}₽ ({inc[3]})\n"
        msg += "\nНапиши номер дохода, который хочешь удалить:"
        bot.send_message(callback.message.chat.id, msg)
        user_temp_data[user_id] = {'income_delete_list': incomes}
        bot.register_next_step_handler(callback.message, process_delete_income)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'fixed_expenses':
        markup = get_fixed_expenses_keyboard()
        bot.send_message(callback.message.chat.id,
                         "💸 ПОСТОЯННЫЕ РАСХОДЫ\n\nЗдесь ты можешь управлять регулярными платежами:\n• 🏠 Коммуналка\n• 💳 Кредиты\n• 📺 Подписки\n• и другие ежемесячные расходы",
                         reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'add_fixed':
        msg = bot.send_message(callback.message.chat.id, "➕ ДОБАВЛЕНИЕ ПОСТОЯННОГО РАСХОДА\n\nВведи название (например: Коммуналка, Кредит, Интернет):")
        bot.register_next_step_handler(msg, process_fixed_name)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'list_fixed':
        user_id = callback.from_user.id
        expenses = Expense.get_fixed_expenses(user_id)
        if not expenses:
            bot.send_message(callback.message.chat.id, "📋 СПИСОК ПОСТОЯННЫХ РАСХОДОВ\n\nУ тебя пока нет расходов.")
        else:
            msg = "📋 ТВОИ ПОСТОЯННЫЕ РАСХОДЫ:\n\n"
            total = 0
            for exp in expenses:
                msg += f"• {exp[1]}: {exp[2]}₽ ({exp[3]})\n"
                total += exp[2]
            msg += f"\n💰 Итого в месяц: {total}₽"
            bot.send_message(callback.message.chat.id, msg)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'delete_fixed':
        user_id = callback.from_user.id
        expenses = Expense.get_fixed_expenses(user_id)
        if not expenses:
            bot.answer_callback_query(callback.id, "❌ Нет расходов для удаления", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for exp in expenses:
            markup.add(types.InlineKeyboardButton(f"❌ {exp[1]} — {exp[2]}₽ ({exp[3]})", callback_data=f'delete_fixed_{exp[0]}'))
        markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='fixed_expenses'))
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id,
                              text="🗑 ВЫБЕРИ РАСХОД ДЛЯ УДАЛЕНИЯ:", reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'expenses_week':
        try:
            user_id = callback.from_user.id
            current, previous = Expense.get_week_comparison(user_id)
            change = 0
            if previous > 0:
                change = ((current - previous) / previous) * 100
            if previous > 0:
                if change > 0:
                    arrow = "📈"
                    change_text = f"{arrow} {change:+.1f}%"
                elif change < 0:
                    arrow = "📉"
                    change_text = f"{arrow} {change:+.1f}%"
                else:
                    arrow = "➡️"
                    change_text = f"{arrow} 0.0%"
            else:
                change_text = "📊 нет данных за прошлый период"

            msg = f"📊 *АНАЛИЗ ТРАТ ЗА 7 ДНЕЙ*\n\n"
            msg += f"📆 Последние 7 дней: *{current:,.0f}₽*\n"
            msg += f"📅 Предыдущие 7 дней: {previous:,.0f}₽\n"
            msg += f"📈 Динамика: {change_text}\n"

            if previous > 0:
                if current > previous:
                    msg += f"\n⚠️ Траты выросли на {abs(change):.1f}% по сравнению с прошлой неделей."
                elif current < previous:
                    msg += f"\n✅ Молодец! Траты снизились на {abs(change):.1f}%."
                else:
                    msg += f"\n➡️ Траты остались на том же уровне."
            else:
                msg += f"\n📭 Недостаточно данных для сравнения с прошлым периодом."

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('🔙 Назад к тратам', callback_data='balance'))
            bot.send_message(callback.message.chat.id, msg, parse_mode='Markdown', reply_markup=markup)
            bot.answer_callback_query(callback.id)

        except Exception as e:
            bot.send_message(callback.message.chat.id, f"❌ Ошибка: {e}")
            bot.answer_callback_query(callback.id)

    elif callback.data == 'menu':
        user_name = get_last_user_name()
        user_id = callback.from_user.id
        if not user_name:
            user_name = get_user_name(callback.message)
        menu_text = format_main_menu(user_name, user_id)
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text=menu_text, reply_markup=get_main_menu_keyboard())
        bot.answer_callback_query(callback.id)

    elif callback.data == 'add_expense_menu':
        msg = bot.send_message(callback.message.chat.id, 'Введи сумму траты:')
        bot.register_next_step_handler(msg, process_expense_amount)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'expense_analysis':
        user_id = callback.from_user.id
        today_total = Expense.get_today_total(user_id)
        expenses_by_category = Expense.get_by_category(user_id)
        max_expense = Expense.get_max_today(user_id)
        avg_expense = Expense.get_avg_today(user_id)
        message = f"📊 Анализ трат за сегодня:\n\n"
        message += f"📊 СЕГОДНЯ:\n"
        message += f"• 💸 Потрачено: {today_total}₽\n"
        message += f"• 📈 Средний чек: {avg_expense}₽\n"
        message += f"• 💎 Самая дорогая: {max_expense}₽\n\n"
        if expenses_by_category:
            message += "📌 ПО КАТЕГОРИЯМ:\n"
            for category, amount in expenses_by_category.items():
                emoji = Expense.get_category_emoji_static(category)
                message += f"{emoji} {category}: {amount}₽\n"
        else:
            message += "📭 Сегодня еще не было трат.\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Назад к тратам', callback_data='balance'))
        bot.send_message(callback.message.chat.id, message, reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'stats':
        user_id = callback.from_user.id
        user_name = get_last_user_name() or "Пользователь"
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        cur.execute("SELECT registered_at FROM registrations WHERE user_id = ? ORDER BY registered_at DESC LIMIT 1", (user_id,))
        reg_data = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM registrations WHERE user_id = ?", (user_id,))
        reg_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        reg_date = reg_data[0] if reg_data else "неизвестно"
        reg_date_obj = datetime.strptime(reg_date, "%Y-%m-%d %H:%M:%S")
        days_in_bot = (datetime.now() - reg_date_obj).days
        total_income = Expense.get_total_income(user_id)
        total_expenses = Expense.get_total_expenses(user_id)
        balance = total_income - total_expenses  
        message = f"📊 *СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ*\n\n"
        message += f"🆔 *ID:* `{user_id}`\n"
        message += f"📅 *В боте с:* {reg_date_obj.strftime('%d.%m.%Y')}\n"
        message += f"⏳ *Дней в боте:* {days_in_bot}\n"
        message += f"🔄 *Перерегистраций:* {reg_count - 1}\n\n"
        message += f"💰 *ОБЩИЕ ПОКАЗАТЕЛИ:*\n"
        message += f"• Всего доходов: {total_income}₽\n"
        message += f"• Всего расходов: {total_expenses}₽\n"
        message += f"• Денежный поток: {balance}₽\n"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Назад в меню', callback_data='menu'))
        bot.send_message(callback.message.chat.id, message, parse_mode='Markdown', reply_markup=markup)

    elif callback.data == 'balance':
        show_balance_expenses(callback)

    elif callback.data == 'subscription':
        markup = get_subscription_keyboard()
        bot.send_message(
            callback.message.chat.id,
            "💎 *SANDER PREMIUM*\n\n"
            "💰 Цены на подписку:\n"
            "• 1 месяц — 149₽\n"
            "• 1 год — 1699₽ (скидка 37%)\n\n"
            "🎁 Преимущества Premium:\n"
            "1 - Отдельный вип бот в котором заранее выходят обновления!😎"
            "2 - Чат с админом для общения на прямую!😮‍💨"
            "Выбери срок подписки:",
            parse_mode='Markdown',
            reply_markup=markup
        )
        bot.answer_callback_query(callback.id)

def get_user_name_for_registration(message):
    name = message.text.strip()
    save_user_to_db(name)
    user_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT OR IGNORE INTO registrations (user_id, username, first_name, registered_at) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, first_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    cur.close()
    conn.close()
    bot.send_message(message.chat.id, f"✅ Отлично, {name}! Регистрация успешно завершена!")
    menu_text = format_main_menu(name, user_id)
    bot.send_message(message.chat.id, menu_text, reply_markup=get_main_menu_keyboard())
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    reply_markup.add(
        types.KeyboardButton('🎩 Траты'),
        types.KeyboardButton('📊 Статистика'),
        types.KeyboardButton('💸 Постоянные расходы'),
        types.KeyboardButton('💼 Постоянные доходы'),
        types.KeyboardButton('🧩 Цели'),
        types.KeyboardButton('🧮 Калькулятор'),
        types.KeyboardButton('💎 Подписка')
    )
    bot.send_message(message.chat.id, "👇 Быстрое меню снизу:", reply_markup=reply_markup)

# ========== КАЛЬКУЛЯТОР ==========

def process_credit_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
        user_temp_data[message.from_user.id] = {'credit_amount': amount}
        msg = bot.send_message(message.chat.id, "💰 Введи срок кредита (в месяцах):")
        bot.register_next_step_handler(msg, process_credit_term)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_credit_term(message):
    try:
        term = int(message.text)
        if term <= 0:
            bot.send_message(message.chat.id, "❌ Срок должен быть больше 0!")
            return
        user_id = message.from_user.id
        user_temp_data[user_id]['credit_term'] = term
        msg = bot.send_message(message.chat.id, "💰 Введи процентную ставку (% годовых):")
        bot.register_next_step_handler(msg, process_credit_rate)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи целое число!")

def process_credit_rate(message):
    try:
        rate = float(message.text)
        if rate <= 0:
            bot.send_message(message.chat.id, "❌ Ставка должна быть больше 0!")
            return
        user_id = message.from_user.id
        data = user_temp_data[user_id]
        amount = data['credit_amount']
        term = data['credit_term']
        monthly_rate = rate / 100 / 12
        payment = amount * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
        total = payment * term
        overpayment = total - amount
        result = f"💰 *РАСЧЁТ КРЕДИТА*\n\n"
        result += f"• Сумма: {amount:,.0f}₽\n"
        result += f"• Срок: {term} мес\n"
        result += f"• Ставка: {rate}%\n\n"
        result += f"📊 Ежемесячный платёж: {payment:,.0f}₽\n"
        result += f"📉 Переплата: {overpayment:,.0f}₽\n"
        result += f"💸 Общая выплата: {total:,.0f}₽"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔄 Новый расчёт', callback_data='calc_credit'))
        markup.add(types.InlineKeyboardButton('🔙 В меню', callback_data='calc_finance'))
        bot.send_message(message.chat.id, result, reply_markup=markup)
        del user_temp_data[user_id]
    except:
        bot.send_message(message.chat.id, "❌ Ошибка расчёта")

def process_deposit_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
        user_temp_data[message.from_user.id] = {'deposit_amount': amount}
        msg = bot.send_message(message.chat.id, "💰 Введи срок вклада (в месяцах):")
        bot.register_next_step_handler(msg, process_deposit_term)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_deposit_term(message):
    try:
        term = int(message.text)
        if term <= 0:
            bot.send_message(message.chat.id, "❌ Срок должен быть больше 0!")
            return
        user_id = message.from_user.id
        user_temp_data[user_id]['deposit_term'] = term
        msg = bot.send_message(message.chat.id, "💰 Введи процентную ставку (% годовых):")
        bot.register_next_step_handler(msg, process_deposit_rate)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи целое число!")

def process_deposit_rate(message):
    try:
        rate = float(message.text)
        if rate <= 0:
            bot.send_message(message.chat.id, "❌ Ставка должна быть больше 0!")
            return
        user_id = message.from_user.id
        data = user_temp_data[user_id]
        amount = data['deposit_amount']
        term = data['deposit_term']
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton('✅ Да', callback_data=f'deposit_cap_yes_{user_id}'), types.InlineKeyboardButton('❌ Нет', callback_data=f'deposit_cap_no_{user_id}'))
        user_temp_data[user_id]['deposit_rate'] = rate
        bot.send_message(message.chat.id, "💰 Капитализация процентов?", reply_markup=markup)
    except:
        bot.send_message(message.chat.id, "❌ Ошибка")

def process_npv_investment(message):
    try:
        investment = float(message.text)
        if investment <= 0:
            bot.send_message(message.chat.id, "❌ Инвестиции должны быть больше 0!")
            return
        user_temp_data[message.from_user.id] = {'npv_investment': investment, 'npv_cashflows': []}
        msg = bot.send_message(message.chat.id, "📈 Введи доход за 1-й год (или 0 для расчёта):")
        bot.register_next_step_handler(msg, process_npv_cashflow)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_npv_cashflow(message):
    try:
        cash = float(message.text)
        user_id = message.from_user.id
        if user_id not in user_temp_data:
            user_temp_data[user_id] = {'npv_cashflows': []}
        if cash == 0 or len(user_temp_data[user_id].get('npv_cashflows', [])) >= 5:
            if len(user_temp_data[user_id].get('npv_cashflows', [])) == 0:
                bot.send_message(message.chat.id, "❌ Введи хотя бы один доход!")
                return
            msg = bot.send_message(message.chat.id, "📈 Введи ставку дисконтирования (%):")
            bot.register_next_step_handler(msg, process_npv_rate)
        else:
            user_temp_data[user_id]['npv_cashflows'].append(cash)
            year = len(user_temp_data[user_id]['npv_cashflows']) + 1
            msg = bot.send_message(message.chat.id, f"📈 Введи доход за {year}-й год (или 0 для расчёта):")
            bot.register_next_step_handler(msg, process_npv_cashflow)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_npv_rate(message):
    try:
        rate = float(message.text) / 100
        user_id = message.from_user.id
        data = user_temp_data[user_id]
        investment = data['npv_investment']
        cashflows = data['npv_cashflows']
        
        npv = -investment
        for i, cash in enumerate(cashflows, 1):
            npv += cash / ((1 + rate) ** i)
        
        result = f"📈 *NPV (Чистая приведенная стоимость)*\n\n"
        result += f"• Инвестиции: -{investment:,.0f}₽\n"
        result += f"• Доходы: " + ", ".join([f"{i+1}г: {c:,.0f}₽" for i, c in enumerate(cashflows)]) + "\n"
        result += f"• Ставка: {rate*100}%\n\n"
        result += f"💎 NPV: {npv:,.0f}₽\n"
        result += f"➡️ {'✅ Проект выгоден' if npv > 0 else '❌ Проект невыгоден' if npv < 0 else '⚖️ На границе'}"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔄 Новый расчёт', callback_data='calc_npv'))
        markup.add(types.InlineKeyboardButton('🔙 В меню', callback_data='calc_finance'))
        
        bot.send_message(message.chat.id, result, reply_markup=markup)
        del user_temp_data[user_id]
    except:
        bot.send_message(message.chat.id, "❌ Ошибка расчёта")

def process_profit_revenue(message):
    try:
        revenue = float(message.text)
        if revenue <= 0:
            bot.send_message(message.chat.id, "❌ Выручка должна быть больше 0!")
            return
        user_temp_data[message.from_user.id] = {'profit_revenue': revenue}
        msg = bot.send_message(message.chat.id, "💼 Введи затраты (₽):")
        bot.register_next_step_handler(msg, process_profit_cost)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_profit_cost(message):
    try:
        cost = float(message.text)
        if cost <= 0:
            bot.send_message(message.chat.id, "❌ Затраты должны быть больше 0!")
            return
        user_id = message.from_user.id
        revenue = user_temp_data[user_id]['profit_revenue']
        profit = revenue - cost
        margin = (profit / revenue) * 100 if revenue != 0 else 0
        
        result = f"💼 *РЕНТАБЕЛЬНОСТЬ*\n\n"
        result += f"• Выручка: {revenue:,.0f}₽\n"
        result += f"• Затраты: {cost:,.0f}₽\n"
        result += f"• Прибыль: {profit:,.0f}₽\n"
        result += f"• Маржинальность: {margin:.1f}%"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔄 Новый расчёт', callback_data='calc_profit'))
        markup.add(types.InlineKeyboardButton('🔙 В меню', callback_data='calc_finance'))
        
        bot.send_message(message.chat.id, result, reply_markup=markup)
        del user_temp_data[user_id]
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_breakeven_fixed(message):
    try:
        fixed = float(message.text)
        if fixed <= 0:
            bot.send_message(message.chat.id, "❌ Затраты должны быть больше 0!")
            return
        user_temp_data[message.from_user.id] = {'breakeven_fixed': fixed}
        msg = bot.send_message(message.chat.id, "📊 Введи цену за единицу (₽):")
        bot.register_next_step_handler(msg, process_breakeven_price)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_breakeven_price(message):
    try:
        price = float(message.text)
        if price <= 0:
            bot.send_message(message.chat.id, "❌ Цена должна быть больше 0!")
            return
        user_id = message.from_user.id
        user_temp_data[user_id]['breakeven_price'] = price
        msg = bot.send_message(message.chat.id, "📊 Введи переменные затраты на единицу (₽):")
        bot.register_next_step_handler(msg, process_breakeven_variable)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_breakeven_variable(message):
    try:
        variable = float(message.text)
        if variable < 0:
            bot.send_message(message.chat.id, "❌ Затраты не могут быть отрицательными!")
            return
        user_id = message.from_user.id
        data = user_temp_data[user_id]
        fixed = data['breakeven_fixed']
        price = data['breakeven_price']
        if price <= variable:
            bot.send_message(message.chat.id, "❌ Цена должна быть выше переменных затрат!")
            return
        breakeven = fixed / (price - variable)
        result = f"📊 *ТОЧКА БЕЗУБЫТОЧНОСТИ*\n\n"
        result += f"• Постоянные затраты: {fixed:,.0f}₽\n"
        result += f"• Цена за ед.: {price:,.0f}₽\n"
        result += f"• Переменные затраты на ед.: {variable:,.0f}₽\n"
        result += f"• Маржинальный доход на ед.: {price - variable:,.0f}₽\n\n"
        result += f"✅ Нужно продать: {breakeven:.0f} ед.\n"
        result += f"💰 Выручка: {breakeven * price:,.0f}₽"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔄 Новый расчёт', callback_data='calc_breakeven'))
        markup.add(types.InlineKeyboardButton('🔙 В меню', callback_data='calc_finance'))
        bot.send_message(message.chat.id, result, reply_markup=markup)
        del user_temp_data[user_id]
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_tax_income(message):
    try:
        income = float(message.text)
        if income <= 0:
            bot.send_message(message.chat.id, "❌ Доход должен быть больше 0!")
            return
        user_temp_data[message.from_user.id] = {'tax_income': income}
        
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton('6% (Доходы)', callback_data='tax_6'),
            types.InlineKeyboardButton('15% (Доходы-Расходы)', callback_data='tax_15'),
            types.InlineKeyboardButton('13% (НДФЛ)', callback_data='tax_13'),
            types.InlineKeyboardButton('20% (НДС)', callback_data='tax_20')
        )
        bot.send_message(message.chat.id, "🧾 Выбери ставку налога:", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def activate_subscription(user_id, sub_type):
    days = 30 if sub_type == 'month' else 365
    expires_at = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''INSERT OR REPLACE INTO subscriptions (user_id, expires_at, is_active) VALUES (?, ?, 1)''', (user_id, expires_at))
    conn.commit()
    cur.close()
    conn.close()
    vip_bot = "@sandervip_bot"
    vip_chat = "https://t.me/+3ZD7JG_KRDNhNDA6"
    vip_message = (
        f"✅ *Подписка активирована!*\n\n"
        f"📅 Действует до: {expires_at}\n\n"
        f"🎁 *VIP-ДОСТУП:*\n"
        f"🤖 VIP-бот: {vip_bot}\n"
        f"💬 VIP-чат: {vip_chat}\n\n"
        f"Спасибо за поддержку! 🎉"
    )
    bot.send_message(user_id, vip_message, parse_mode='Markdown')
    bot.send_message(
        ADMIN_ID,
        f"💰 *Новая подписка*\n\n"
        f"👤 Пользователь ID: `{user_id}`\n"
        f"📅 Тип: {sub_type}\n"
        f"✅ Активирована до: {expires_at}",
        parse_mode='Markdown'
    )

def generate_payment_link(user_id, subscription_type):
    price = SUBSCRIPTION_PRICES[subscription_type]
    inv_id = int(time.time()) % 100000
    
    # Описание без спецсимволов (как в документации)
    descriptions = {
        'month': 'Подписка на месяц',
        'year': 'Подписка на год'
    }
    
    # Shp-параметры в алфавитном порядке
    shp_params = {
        'Shp_sub_type': subscription_type,
        'Shp_user_id': user_id
    }
    
    # Сортировка ключей по алфавиту
    sorted_keys = sorted(shp_params.keys())
    
    # Формируем строку подписи по схеме из документации
    # MerchantLogin:OutSum:InvId:Пароль#1:Shp_ключ=значение:Shp_ключ=значение
    signature_base = f"{ROBOKASSA_LOGIN}:{price}:{inv_id}:{ROBOKASSA_PASSWORD1}"
    for key in sorted_keys:
        signature_base += f":{key}={shp_params[key]}"
    
    signature = hashlib.md5(signature_base.encode('utf-8')).hexdigest()
    
    # URL из документации
    url = "https://auth.robokassa.ru/Merchant/Index.aspx"
    
    # Параметры для ссылки
    params = {
        'MerchantLogin': ROBOKASSA_LOGIN,
        'OutSum': str(price),
        'InvId': str(inv_id),
        'Description': descriptions[subscription_type],
        'SignatureValue': signature,
        'Shp_user_id': str(user_id),
        'Shp_sub_type': subscription_type
    }
    
    query = '&'.join([f"{k}={v}" for k, v in params.items()])
    link = f"{url}?{query}"
    
    print(f"Подпись: {signature}")
    print(f"Строка подписи: {signature_base}")
    
    return link, inv_id

if __name__ == '__main__':
    bot.polling(none_stop=True)
