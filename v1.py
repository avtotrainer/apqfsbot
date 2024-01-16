import telebot
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from telebot import types

# Замените 'YOUR_BOT_TOKEN' на токен, который вам предоставил BotFather
bot = telebot.TeleBot('6915117121:AAGmTsVhGGkNuV4p0_LIR8qB5TRPxhlKG0o')

# Инициализация базы данных
db = TinyDB('reservations.json')
Reservations = Query()

# ID стилиста (владельца бота)
stylist_id = 123456789  # Замените на фактический ID стилиста

# Рабочее время стилиста (в минутах относительно полуночи)
work_start_time = 9 * 60  # Начало рабочего дня (9:00)
work_end_time = 18 * 60   # Конец рабочего дня (18:00)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, "Привет! Я бот для резервирования времени визита. Используйте /reserve для бронирования.")

# Обработчик команды /reserve
@bot.message_handler(commands=['reserve'])
def handle_reserve(message):
    user_id = message.from_user.id

    # Получение списка доступных времен для бронирования
    available_times = get_available_times(user_id)
    
    if not available_times:
        bot.send_message(message.chat.id, "Все доступные времена зарезервированы. Пожалуйста, попробуйте позже.")
    else:
        # Предложение свободного времени
        reply_markup = create_time_keyboard(available_times)
        bot.send_message(message.chat.id, "Выберите удобное время для визита:", reply_markup=reply_markup)

        # Добавление обработчика для ответа на выбор времени
        bot.register_next_step_handler(message, reserve_time)

def get_available_times(user_id):
    current_time = datetime.now()
    current_minutes = current_time.hour * 60 + current_time.minute

    # Получение всех активных резерваций для пользователя
    active_reservations = db.search((Reservations.user_id == user_id) & (Reservations.status == 'active'))

    # Формирование доступных времен для бронирования
    available_times = []
    interval = 30  # Промежуток времени для бронирования (в минутах)
    
    # Перебираем времена от начала до конца рабочего дня
    for minutes in range(work_start_time, work_end_time, interval):
        if all(
            not (minutes >= res['start_minutes'] and minutes < res['end_minutes'])
            for res in active_reservations
        ):
            if minutes >= current_minutes:
                time_str = (datetime(1, 1, 1) + timedelta(minutes=minutes)).strftime('%H:%M')
                available_times.append((time_str, minutes))

    return available_times

def create_time_keyboard(available_times):
    keyboard = types.ReplyKeyboardMarkup(row_width=3, one_time_keyboard=True)
    for time_str, minutes in available_times:
        keyboard.add(types.KeyboardButton(time_str))

    return keyboard

def reserve_time(message):
    user_id = message.from_user.id
    selected_time_str = message.text

    # Извлечение времени из строки и конвертация в минуты относительно полуночи
    selected_time = datetime.strptime(selected_time_str, '%H:%M')
    selected_minutes = selected_time.hour * 60 + selected_time.minute

    # Проверка доступности выбранного времени
    available_times = get_available_times(user_id)
    if selected_minutes not in [minutes for _, minutes in available_times]:
        bot.send_message(message.chat.id, "Выбранное время недоступно. Пожалуйста, выберите другое.")
    else:
        # Запись резервации в базу данных
        reservation_data = {
            'user_id': user_id,
            'status': 'active',
            'duration': 30,  # Продолжительность визита в минутах
            'start_time': selected_time_str,
            'start_minutes': selected_minutes,
            'end_minutes': selected_minutes + 30,  # Продолжительность визита 30 минут
        }
        db.insert(reservation_data)

        bot.send_message(message.chat.id, f"Ваш визит забронирован на {selected_time_str}. Наслаждайтесь!")

# Запуск бота
bot.polling()
