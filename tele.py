from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import sqlite3
from datetime import datetime, timedelta

# Инициализация базы данных
conn = sqlite3.connect('schedule.db')
cursor = conn.cursor()

# Создание таблицы расписания
cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedule (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        date_time TEXT
    )
''')
conn.commit()

# Функция для бронирования визита
def reserve(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    current_time = datetime.now()
    end_time = current_time + timedelta(minutes=30)

    # Проверка доступности времени
    cursor.execute('SELECT * FROM schedule WHERE date_time BETWEEN ? AND ?', (current_time, end_time))
    if cursor.fetchone() is not None:
        update.message.reply_text('Время занято. Выберите другое время.')
        return

    # Запись в базу данных
    cursor.execute('INSERT INTO schedule (client_id, date_time) VALUES (?, ?)', (user_id, current_time))
    conn.commit()

    update.message.reply_text('Ваш визит забронирован.')

# Функция для просмотра расписания
def view_schedule(update: Update, context: CallbackContext) -> None:
    cursor.execute('SELECT * FROM schedule')
    schedule = cursor.fetchall()

    if schedule:
        schedule_str = '\n'.join([f"{row[0]}. {row[2]}" for row in schedule])
        update.message.reply_text(f'Расписание:\n{schedule_str}')
    else:
        update.message.reply_text('Расписание пусто.')

# Инициализация бота
updater = Updater('6915117121:AAGmTsVhGGkNuV4p0_LIR8qB5TRPxhlKG0o', use_context=True)
dispatcher = updater.dispatcher

# Добавление хэндлеров команд
dispatcher.add_handler(CommandHandler('reserve', reserve))
dispatcher.add_handler(CommandHandler('schedule', view_schedule))

# Запуск бота
updater.start_polling()
updater.idle()

# Закрытие соединения с базой данных при выходе
conn.close()
