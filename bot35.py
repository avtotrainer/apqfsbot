import telebot
import sqlite3
from telebot import types
from datetime import datetime, timedelta

# Токен вашего бота
TOKEN = '6915117121:AAGmTsVhGGkNuV4p0_LIR8qB5TRPxhlKG0o'

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Создание или подключение к базе данных SQLite
conn = sqlite3.connect('visits.db')
cursor = conn.cursor()

# Создание таблицы для хранения клиентов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        username TEXT,
        is_bot BOOLEAN
    )
''')
conn.commit()

# Создание таблицы для хранения зарегистрированных визитов
cursor.execute('''
    CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY,
        client_id INTEGER,
        visit_time DATETIME
    )
''')
conn.commit()

# Функция, которая проверяет, является ли пользователь ботом
def is_user_bot(user_id):
    user = bot.get_chat_member('@yourchannel', user_id)  # Замените на имя вашего канала
    return user.status == 'bot'

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    username = message.from_user.username
    is_bot = is_user_bot(user_id)

    # Проверка, является ли пользователь ботом
    if is_bot:
        bot.send_message(message.chat.id, "Извините, боты не могут использовать этот бот.")
        return

    # Проверка, зарегистрирован ли пользователь в базе данных
    cursor.execute('SELECT * FROM clients WHERE user_id=?', (user_id,))
    existing_client = cursor.fetchone()

    if not existing_client:
        # Регистрация нового клиента
        cursor.execute('INSERT INTO clients (user_id, username, is_bot) VALUES (?, ?, ?)', (user_id, username, is_bot))
        conn.commit()
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы!")
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы!")

# Обработчик команды /schedule для отображения расписания
@bot.message_handler(commands=['schedule'])
def schedule(message):
    user_id = message.from_user.id
    username = message.from_user.username
    is_bot = is_user_bot(user_id)

    # Проверка, является ли пользователь ботом
    if is_bot:
        bot.send_message(message.chat.id, "Извините, боты не могут использовать этот бот.")
        return

    # Генерация клавиатуры с доступными временами визитов
    keyboard = types.ReplyKeyboardMarkup(row_width=4)
    current_time = datetime.now().replace(second=0, microsecond=0)
    for _ in range(18):
        keyboard.add(types.KeyboardButton(current_time.strftime("%H:%M")))
        current_time += timedelta(minutes=30)

    bot.send_message(message.chat.id, "Выберите время для записи:", reply_markup=keyboard)

# Обработчик для регистрации визита клиента
@bot.message_handler(func=lambda message: True)
def register_visit(message):
    user_id = message.from_user.id
    username = message.from_user.username
    is_bot = is_user_bot(user_id)

    # Проверка, является ли пользователь ботом
    if is_bot:
        bot.send_message(message.chat.id, "Извините, боты не могут использовать этот бот.")
        return

    # Проверка, зарегистрирован ли пользователь в базе данных
    cursor.execute('SELECT * FROM clients WHERE user_id=?', (user_id,))
    existing_client = cursor.fetchone()

    if not existing_client:
        bot.send_message(message.chat.id, "Вы не зарегистрированы. Используйте команду /start для регистрации.")
    else:
        # Получение времени визита от пользователя
        visit_time = message.text
        try:
            visit_time = datetime.strptime(visit_time, "%H:%M")
        except ValueError:
            bot.send_message(message.chat.id, "Неверный формат времени. Используйте формат HH:MM.")
            return

        # Проверка, доступно ли выбранное время
        cursor.execute('SELECT * FROM visits WHERE visit_time=?', (visit_time.strftime("%Y-%m-%d %H:%M:%S"),))
        existing_visit = cursor.fetchone()

        if existing_visit:
            bot.send_message(message.chat.id, "Выбранное время уже занято.")
        else:
            # Регистрация визита
            cursor.execute('INSERT INTO visits (client_id, visit_time) VALUES (?, ?)', (existing_client[0], visit_time.strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            bot.send_message(message.chat.id, f"Ваш визит зарегистрирован на {visit_time.strftime('%H:%M')}.")
            
# Запуск бота
if __name__ == '__main__':
    bot.polling(none_stop=True)

