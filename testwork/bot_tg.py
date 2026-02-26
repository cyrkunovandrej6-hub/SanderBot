import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta

bot = telebot.TeleBot('8526938179:AAHKiBZba2oy3cIcW8eigJL8WAfMypV75YI')
# ==========ХРАНИЛИЩЕ ВРЕМЕННЫХ ДАННЫХ ==========
user_temp_data = {}
#=========== КНОПКА "ТРАТЫ" ==================
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
        cur.execute("INSERT INTO goals (user_id, name, target, current, created_at) VALUES (?, ?, ?, ?, ?)",(user_id, name, target, 0, datetime.now().strftime("%Y-%m-%d")))
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
        cur.execute("INSERT INTO fixed_income (user_id, name, amount, category) VALUES (?, ?, ?, ?)", (user_id, name, amount, category))
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
        cur.execute("INSERT INTO fixed_expenses (user_id, name, amount, category) VALUES (?, ?, ?, ?)", (user_id, name, amount, category))
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
    def week_expence(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute('SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date BETWEEN ? AND ?', (user_id, week_ago, today))
        result = cur.fetchone()[0]
        cur.close()
        conn.close()
        return result if result else 0

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

    def get_category_emoji_static(category):
        emojis = {'🍔 Еда': '🍔','🚇 Транспорт': '🚇','🛍️ Покупки': '🛍️','🎮 Развлечения': '🎮','🏠 Дом': '🏠','💊 Здоровье': '💊'}
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
        cur.execute(
            "INSERT INTO expenses (user_id, amount, category, date) VALUES (?, ?, ?, ?)",
            (self.user_id, self.amount, self.category, self.date)
        )
        conn.commit()
        cur.close()
        conn.close()
        return self

   
    @classmethod
    def get_today_total(cls, user_id):
        conn = sqlite3.connect('finance_bot.db')
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "SELECT SUM(amount) FROM expenses WHERE user_id = ? AND date = ?",
            (user_id, today)
        )
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
        emojys = {
            '🍔 Еда': '🍔',
            '🚇 Транспорт': '🚇',
            '🛍️ Покупки': '🛍️',
            '🎮 Развлечения': '🎮',
            '🏠 Дом': '🏠',
            '💊 Здоровье': '💊'
        }
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

@bot.message_handler(commands=['add_expense'])
def ask_expence(message):
    msg = bot.send_message(message.chat.id, 'Введи сумму траты ✍️')
    bot.register_next_step_handler(msg, process_expense_amount)

def process_expense_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, 'Сумма должна быть больше 0!')
            return
        expense = Expense(user_id=message.from_user.id, amount = amount)
        global user_temp_data
        user_temp_data[message.from_user.id] = expense
        markup = types.InlineKeyboardMarkup(row_width=2)
        categories = ['🍔 Еда', '🚇 Транспорт', '🛍️ Покупки', '🎮 Развлечения', '🏠 Дом', '💊 Здоровье']
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat, callback_data=f'cat_{cat}'))
        markup.add(types.InlineKeyboardButton('✏️ Своя категория', callback_data='custom_category'))
        bot.send_message(message.chat.id, f"💰 Сумма: {amount}₽\n\nВыбери категорию:", reply_markup=markup)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

@bot.callback_query_handler(func=lambda call: call.data == 'custom_category')
def handle_custom_category(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "✏️ Введи название своей категории:")
    bot.register_next_step_handler(msg, process_custom_category)

@bot.callback_query_handler(func = lambda call: call.data.startswith('cat_'))
def process_category(call):
    category = call.data.replace('cat_','')
    user_id = call.from_user.id
    global user_temp_data
    expense = user_temp_data.get(user_id)
    if expense:
        expense.category = category
        expense.save_to_db()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Назад к тратам', callback_data='balance'))
        bot.send_message(call.message.chat.id,expense.format_message())
        del user_temp_data[user_id]
        bot.answer_callback_query(call.id, "✅ Трата добавлена!")
    else:
        bot.answer_callback_query(call.id, "❌ Ошибка! Попробуй сначала")

@bot.callback_query_handler(func = lambda call: call.data == 'balance')
def show_balance(call):
    bot.send_message(call.message.chat.id,"💰 Управление тратами", reply_markup=get_expenses_keyboard())
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

def create_income_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS income (id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,amount REAL,category TEXT,date TEXT)''')
    conn.commit()
    cur.close()
    conn.close()
    

def create_goals_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS goals(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,name TEXT,target REAL,current REAL,created_at TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

def create_fixed_income_table():
    conn = sqlite3.connect('finance_bot.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS fixed_income (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, amount REAL,category TEXT)''')
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
    cur.execute('''CREATE TABLE IF NOT EXISTS fixed_expenses(id INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER,name TEXT,amount REAL,category TEXT)''')
    conn.commit()
    cur.close()
    conn.close()

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
# ========= ТАБЛИЦЫ ===========
create_income_table()
create_goals_table()
create_fixed_income_table()
create_fixed_expenses_table()
create_users_table()
create_expenses_table()
# ========== ФУНКЦИИ ДЛЯ БОТА ==========

def process_delete_goal_choice(message):
    try:
        num = int(message.text)
        user_id = message.from_user.id
        goals = user_temp_data[user_id]['delete_goals']
        if 1 <= num <= len(goals):
            goal = goals[num-1]
            goal_id, goal_name = goal[0], goal[1]
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton('✅ Да, удалить', callback_data=f'confirm_delete_goal_{goal_id}'), types.InlineKeyboardButton('❌ Нет', callback_data='goals')) 
            bot.send_message(message.chat.id, f"Точно удалить цель «{goal_name}»?", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Неверный номер. Попробуй снова.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")
    finally:
        if user_id in user_temp_data and 'delete_goals' in user_temp_data[user_id]:
            del user_temp_data[user_id]['delete_goals']

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
    user_temp_data = getattr(bot, 'user_data', {})
    if user_id not in user_temp_data:
        user_temp_data[user_id] = {}
    user_temp_data[user_id]['goal_name'] = name
    msg = bot.send_message(message.chat.id, f"🎯 Название: {name}\n\n" "Введи сумму, которую нужно накопить (только число):")
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
    name = user_temp_data[user_id]['income_name']
    amount = user_temp_data[user_id]['income_amount']
    Expense.add_fixed_income(user_id, name, amount, category)
    bot.send_message(message.chat.id, f"✅ Постоянный доход добавлен!\n\n" f"• {name}: {amount}₽ ({category})")
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
            markup.add(types.InlineKeyboardButton('✅ Да, удалить', callback_data=f'confirm_income_delete_{income_id}'), types.InlineKeyboardButton('❌ Нет', callback_data='fixed_income'))
            bot.send_message(message.chat.id, f"Точно удалить доход '{incomes[num-1][1]}'?", reply_markup=markup)         
        else:
            bot.send_message(message.chat.id, "❌ Неверный номер. Попробуй снова.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_income_name(message):
    name = message.text.strip()
    user_id = message.from_user.id
    user_temp_data = getattr(bot, 'user_data', {})
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
        markup = types.InlineKeyboardMarkup(row_width=2)
        categories = ['💼 Зарплата', '🏠 Аренда', '📈 Инвестиции', '💻 Фриланс', '🎁 Подарки', '💳 Проценты']
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat, callback_data=f'income_cat_{cat}'))
            markup.add(types.InlineKeyboardButton('✏️ Своя', callback_data='income_custom_category'))
            bot.send_message(message.chat.id, f"💰 {name}: {amount}₽\n\nВыбери категорию:", reply_markup=markup)
            user_temp_data[user_id]['income_amount'] = amount
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def process_fixed_name(message):
    name = message.text.strip()
    user_id = message.from_user.id
    if user_id not in user_temp_data:
        user_temp_data[user_id] = {}
    user_temp_data[user_id]['fixed_name'] = name
    
    msg = bot.send_message(
        message.chat.id,
        f"💰 Название: {name}\n\nВведи сумму расхода в месяц:"
    )
    bot.register_next_step_handler(msg, process_fixed_amount)

def process_fixed_amount(message):
    try:
        amount = float(message.text)
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше 0!")
            return
            
        user_id = message.from_user.id
        name = user_temp_data[user_id].get('fixed_name', 'Без названия')
        markup = types.InlineKeyboardMarkup(row_width=2)
        categories = ['🏠 Коммуналка', '💳 Кредиты', '📺 Подписки', '🚗 Транспорт', '🏥 Здоровье', '📚 Обучение']
        for cat in categories:
            markup.add(types.InlineKeyboardButton(cat, callback_data=f'fixed_cat_{cat}'))
        markup.add(types.InlineKeyboardButton('✏️ Своя категория', callback_data='fixed_custom_category'))
        user_temp_data[user_id]['fixed_amount'] = amount
        
        bot.send_message(
            message.chat.id,
            f"💰 {name}: {amount}₽\n\nВыбери категорию:",
            reply_markup=markup
        )
        
    except ValueError:
        bot.send_message(message.chat.id, "❌ Введи число!")

def get_fixed_expenses_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('➕ Добавить', callback_data='add_fixed'), types.InlineKeyboardButton('📋 Список', callback_data='list_fixed'))
    markup.add(types.InlineKeyboardButton('✏️ Редактировать', callback_data='edit_fixed'), types.InlineKeyboardButton('🗑 Удалить', callback_data='delete_fixed'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    return markup

def get_user_name(message):
    if message.from_user.first_name:
        return message.from_user.first_name
    elif message.from_user.username:
        return message.from_user.username
    else:
        return "Пользователь"
#===========КЛАВИАТУРЫ================
def get_main_menu_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    markup.add(
        types.InlineKeyboardButton('🎩 Траты', callback_data='balance'),
        types.InlineKeyboardButton('📊 Статистика', callback_data='stats')
    )
    
    markup.add(
        types.InlineKeyboardButton('💸 Расходы', callback_data='fixed_expenses'),
        types.InlineKeyboardButton('💼 Постоянные доходы', callback_data='income')
    )
    
    markup.add(
        types.InlineKeyboardButton('🧩 Цели', callback_data='goals'),
    )
    
    markup.add(
        types.InlineKeyboardButton('🧮 Калькулятор', callback_data='calculator')
    )
    
    markup.add(
        types.InlineKeyboardButton('💎 Подписка', callback_data='subscription'),
        types.InlineKeyboardButton('📞 Поддержка', callback_data='support')
    )
    
    return markup
def get_goals_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('➕ Новая цель', callback_data='add_goal'),
        types.InlineKeyboardButton('📋 Мои цели', callback_data='list_goals')
    )
    markup.add(
        types.InlineKeyboardButton('💰 Пополнить', callback_data='fund_goal'),
        types.InlineKeyboardButton('❌ Удалить', callback_data='delete_goal')
    )
    markup.add(
        types.InlineKeyboardButton('🔙 Назад', callback_data='menu')
    )
    return markup

def get_fixed_expenses_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('➕ Добавить', callback_data='add_fixed_expense'), types.InlineKeyboardButton('📋 Список', callback_data='list_fixed_expenses'))
    markup.add(types.InlineKeyboardButton('✏️ Редактировать', callback_data='edit_fixed_expense'), types.InlineKeyboardButton('🗑 Удалить', callback_data='delete_fixed_expense'))
    markup.add(types.InlineKeyboardButton('🔙 Назад в меню', callback_data='menu'))
    return markup
def get_fixed_income_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton('➕ Добавить', callback_data='add_income'), types.InlineKeyboardButton('📋 Список', callback_data='list_income'))
    markup.add(types.InlineKeyboardButton('✏️ Редактировать', callback_data='edit_income'), types.InlineKeyboardButton('🗑 Удалить', callback_data='delete_income'))
    markup.add(types.InlineKeyboardButton('🔙 Назад', callback_data='menu'))
    return markup

def get_expenses_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton('➕ Добавить трату', callback_data='add_expense_menu'),
        types.InlineKeyboardButton('📊 Анализ трат', callback_data='expense_analysis')
    )
    
    markup.add(
        types.InlineKeyboardButton('📆 Траты за неделю', callback_data='expenses_week')
    )
    
    markup.add(
        types.InlineKeyboardButton('🔙 Назад в меню', callback_data='menu')
    )
    
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

📅 ДНЕВНОЙ БЮДЖЕТ: 1,000₽
📈 СТАТУС БЮДЖЕТА: 💎 Отлично

💸 РАСХОДЫ:
• Сегодня: 0₽
• За неделю: 0₽

🎯 ЦЕЛИ:
• Всего целей: 0
• Активных: 0
• Статус: 🎯 Нет целей

💼 РЕГУЛЯРНЫЕ ОПЕРАЦИИ:
• Доходы в месяц: 0₽
• Расходы в месяц: 0₽
• Финансовое здоровье: ⚖️ Сбалансированный бюджет

💎 ПОДПИСКА: 🆓 Бесплатный тариф

🧮 Финансовый калькулятор:
• Кредиты и вклады
• Инфляция и ROI
• Цели накоплений

📈 СОВЕТ НА СЕГОДНЯ:
💡 Баланс низкий. Рассмотрите возможность добавления постоянного дохода.

📞 Поддержка: @hXwlssS

"""
    return menu_text

# ========== ОБРАБОТЧИКИ ==========
@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_goal_'))
def confirm_delete_goal(call):
    goal_id = int(call.data.replace('confirm_delete_goal_', ''))
    user_id = call.from_user.id
    Expense.delete_goal(goal_id, user_id)
    bot.answer_callback_query(call.id, "✅ Цель удалена!", show_alert=True)
    markup = get_goals_keyboard()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎯 УПРАВЛЕНИЕ ЦЕЛЯМИ", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('income_cat_'))
def process_income_category(call):
    category = call.data.replace('income_cat_', '')
    user_id = call.from_user.id
    name = user_temp_data[user_id]['income_name']
    amount = user_temp_data[user_id]['income_amount']
    Expense.add_fixed_income(user_id, name, amount, category)
    bot.send_message(call.message.chat.id, f"✅ Постоянный доход добавлен!\n\n" f"• {name}: {amount}₽ ({category})")
    markup = get_fixed_income_keyboard()
    bot.send_message(call.message.chat.id, "💼 ПОСТОЯННЫЕ ДОХОДЫ", reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'income_custom_category')
def handle_income_custom_category(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "✏️ Введи название своей категории дохода:")
    bot.register_next_step_handler(msg, process_income_custom_category)

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
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💼 ПОСТОЯННЫЕ ДОХОДЫ\n\nУправляй своими поступлениями:", reply_markup=markup)

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
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="💸 ПОСТОЯННЫЕ РАСХОДЫ\n\nУправляй своими регулярными платежами:", reply_markup=markup)

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
    bot.send_message(
        call.message.chat.id,
        f"✅ Постоянный расход добавлен!\n\n"
        f"• {name}: {amount}₽ ({category})"
    )
    markup = get_fixed_expenses_keyboard()
    bot.send_message(call.message.chat.id, "💸 ПОСТОЯННЫЕ РАСХОДЫ", reply_markup=markup)
    if user_id in user_temp_data:
        if 'fixed_name' in user_temp_data[user_id]:
            del user_temp_data[user_id]['fixed_name']
        if 'fixed_amount' in user_temp_data[user_id]:
            del user_temp_data[user_id]['fixed_amount']
    
    bot.answer_callback_query(call.id, "✅ Готово!")

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

@bot.callback_query_handler(func=lambda call: call.data == 'fixed_custom_category')
def handle_fixed_custom_category(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "✏️ Введи название своей категории:")
    bot.register_next_step_handler(msg, process_fixed_custom_category)
def process_fixed_custom_category(message):
    category = message.text.strip()
    user_id = message.from_user.id
    name = user_temp_data[user_id]['fixed_name']
    amount = user_temp_data[user_id]['fixed_amount']
    Expense.add_fixed_expense(user_id, name, amount, category)
    bot.send_message(message.chat.id, f"✅ Постоянный расход добавлен!\n\n" f"• {name}: {amount}₽ ({category})")
    markup = get_fixed_expenses_keyboard()
    bot.send_message(message.chat.id, "💸 ПОСТОЯННЫЕ РАСХОДЫ", reply_markup=markup)


@bot.message_handler(commands=['start']) 
def start(message):
    # Создаем таблицу при запуске
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('💼 Начать работу 💼', callback_data='start_registration'))
    with open('Текст абзаца.jpg', 'rb') as photo_file:
         bot.send_photo(
        message.chat.id,photo_file,
        caption = 'Привет! Я Sander, твой личный финансовый помощник! Я помогу сохранить твой кошелек даже когда ну оооочень хочется потратить куда нибудь деньги!', 
        reply_markup=markup
    )


# ========== ОБРАБОТЧИКИ REPLY-КНОПОК ==========

@bot.message_handler(func=lambda message: message.text == '💼 Постоянные доходы')
def handle_fixed_income(message):
    markup = get_fixed_income_keyboard()
    bot.send_message(message.chat.id, "💼 ПОСТОЯННЫЕ ДОХОДЫ\n\n" "Управляй своими регулярными поступлениями:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '💸 Постоянные расходы')
def handle_fixed_expenses(message):
    markup = get_fixed_expenses_keyboard()
    bot.send_message(message.chat.id, "💸 ПОСТОЯННЫЕ РАСХОДЫ\n\n" "Здесь ты можешь управлять регулярными платежами:\n" "• 🏠 Коммуналка\n" "• 💳 Кредиты\n" "• 📺 Подписки\n" "• и другие ежемесячные расходы", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🎩 Траты')
def handle_traits(message):
    bot.send_message(message.chat.id, "💰 Управление тратами", reply_markup=get_expenses_keyboard())

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


# ========== ОБРАБОТЧИКИ КОЛБЭКОВ ==========
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'start_registration':
        # Начинаем регистрацию
        bot.send_message(callback.message.chat.id, '📝 Давай зарегистрируемся! Как мне тебя называть? 🤔')
        # Регистрируем следующий шаг - получение имени
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

    elif callback.data == 'delete_goal':
        user_id = callback.from_user.id
        goals = Expense.get_goals(user_id)
        if not goals:
            bot.answer_callback_query(callback.id, "❌ У тебя нет целей для удаления", show_alert=True )
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
            bot.send_message(callback.message.chat.id, "📋 ТВОИ ЦЕЛИ\n\n" "У тебя пока нет целей.\n" "Нажми ➕ Новая цель, чтобы создать." )
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
        msg = bot.send_message(callback.message.chat.id, "➕ НОВАЯ ЦЕЛЬ\n\n" "Введи название цели (например: MacBook, Машина, Путешествие):")
        bot.register_next_step_handler(msg, process_goal_name)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'goals':
        markup = get_goals_keyboard()
        bot.send_message(callback.message.chat.id, "🎯 УПРАВЛЕНИЕ ЦЕЛЯМИ\n\n" "Ставь финансовые цели и отслеживай прогресс:", reply_markup=markup)
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

    elif callback.data == 'list_income':
        user_id = callback.from_user.id
        incomes = Expense.get_fixed_income(user_id)
        if not incomes:
            bot.send_message(callback.message.chat.id, "📋 ПОСТОЯННЫЕ ДОХОДЫ\n\n" "У тебя пока нет постоянных доходов.\n" "Нажми ➕ Добавить, чтобы создать." )
        else:
            msg = "📋 ТВОИ ПОСТОЯННЫЕ ДОХОДЫ:\n\n"
            total = 0
            for inc in incomes:
                msg += f"• {inc[1]}: {inc[2]}₽ ({inc[3]})\n"
                total += inc[2]
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
        bot.edit_message_text(chat_id=callback.message.chat.id, message_id=callback.message.message_id, text="🗑 ВЫБЕРИ РАСХОД ДЛЯ УДАЛЕНИЯ:", reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'add_income':
        msg = bot.send_message(callback.message.chat.id, "➕ ДОБАВЛЕНИЕ ПОСТОЯННОГО ДОХОДА\n\n" "Введи название :")
        bot.register_next_step_handler(msg, process_income_name)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'fixed_income':
        markup = get_fixed_income_keyboard()
        bot.send_message(
        callback.message.chat.id,
        "💼 ПОСТОЯННЫЕ ДОХОДЫ\n\n"
        "💰 Регулярные поступления:\n"
        "• Зарплата\n"
        "• Аренда\n"
        "• Проценты\n"
        "• Подработки\n"
        "• Другие источники",
        reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'add_fixed':
        msg = bot.send_message(callback.message.chat.id, "➕ ДОБАВЛЕНИЕ ПОСТОЯННОГО РАСХОДА\n\n" "Введи название (например: Коммуналка, Кредит, Интернет):")
        bot.register_next_step_handler(msg, process_fixed_name)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'list_fixed':
        user_id = callback.from_user.id
        expenses = Expense.get_fixed_expenses(user_id)

        if not expenses:
            bot.send_message(callback.message.chat.id, "📋 СПИСОК ПОСТОЯННЫХ РАСХОДОВ\n\n" "У тебя пока нет постоянных расходов.\n" "Нажми ➕ Добавить, чтобы создать.")
        else:
            msg = "📋 ТВОИ ПОСТОЯННЫЕ РАСХОДЫ:\n\n"
            total = 0
            for exp in expenses:
                msg += f"• {exp[1]}: {exp[2]}₽ ({exp[3]})\n"
                total += exp[2]
            msg += f"\n💰 Итого в месяц: {total}₽"
            bot.send_message(callback.message.chat.id, msg)

        bot.answer_callback_query(callback.id)

    elif callback.data == 'fixed_expenses':
        markup = get_fixed_expenses_keyboard()
        bot.send_message(callback.message.chat.id,
        "💸 ПОСТОЯННЫЕ РАСХОДЫ\n\n"
        "Здесь ты можешь управлять регулярными платежами:\n"
        "• 🏠 Коммуналка\n"
        "• 💳 Кредиты\n"
        "• 📺 Подписки\n"
        "• и другие ежемесячные расходы",
        reply_markup=markup )
        bot.answer_callback_query(callback.id)


    elif callback.data == 'expenses_week':
        user_id = callback.from_user.id
        week_total = Expense.week_expence(user_id)
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Назад к тратам', callback_data='balance'))
        bot.send_message(callback.message.chat.id, f"📆 Траты за неделю: {week_total}₽")
        bot.answer_callback_query(callback.id)

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
    elif callback.data == 'add_expense_menu':
        msg = bot.send_message(callback.message.chat.id, 'Введи сумму траты :')
        bot.register_next_step_handler(msg, process_expense_amount)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'expenses_week':
        bot.send_message(callback.message.chat.id, '📆 Траты за неделю')
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
        bot.send_message(callback.message.chat.id, message)
        bot.answer_callback_query(callback.id)
    
    elif callback.data == 'stats':
        user_id = callback.from_user.id
        user_name = get_last_user_name() or "Пользователь"
        total_income = Expense.get_total_income(user_id)
        total_expenses = Expense.get_total_expenses(user_id)
        balance = total_income - total_expenses
    
        message = f"📊 СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ: {user_name}\n\n"
        message += f"💰 ОБЩИЕ ПОКАЗАТЕЛИ:\n"
        message += f"• Всего доходов: {total_income}₽\n"
        message += f"• Всего расходов: {total_expenses}₽\n"
        message += f"• Денежный поток: {balance}₽\n"
    
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('🔙 Назад в меню', callback_data='menu'))
    
        bot.send_message(callback.message.chat.id, message, reply_markup=markup)
        bot.answer_callback_query(callback.id)

    elif callback.data == 'balance':
        show_balance_expenses(callback)
    
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
    reply_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    reply_markup.add(
        types.KeyboardButton('🎩 Траты'),
        types.KeyboardButton('📊 Статистика'),
        types.KeyboardButton('💸 Постоянные расходы'),
        types.KeyboardButton('💼 Постоянные доходы'),
        types.KeyboardButton('🧩 Цели'),
        types.KeyboardButton('🧮 Калькулятор'),
        types.KeyboardButton('💎 Подписка'),
        types.KeyboardButton('📞 Поддержка')
    )
    bot.send_message(message.chat.id, "👇 Быстрое меню снизу:", reply_markup=reply_markup)

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    bot.polling(none_stop=True)



