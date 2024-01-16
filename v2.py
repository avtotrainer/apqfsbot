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

    # Получение списка доступных времени и дней для бронирования
    available_slots = get_available_slots(user_id)
    
    if not available_slots:
        bot.send_message(message.chat.id, "Все доступные слоты зарезервированы. Пожалуйста, попробуйте позже.")
    else:
        # Предложение свободного времени и дня
        reply_markup = create_slot_keyboard(available_slots)
        bot.send_message(message.chat.id, "Выберите удобное время и день для визита:", reply_markup=reply_markup)

        # Добавление обработчика для ответа на выбор времени и дня
        bot.register_next_step_handler(message, reserve_slot)

def get_available_slots(user_id):
    current_time = datetime.now()
    current_minutes = current_time.hour * 60 + current_time.minute

    # Получение всех активных резерваций для пользователя
    active_reservations = db.search((Reservations.user_id == user_id) & (Reservations.status == 'active'))

    # Формирование доступных времени и дней для бронирования
    available_slots = []
    interval = 30  # Промежуток времени для бронирования (в минутах)
    days_to_show = 7  # Показывать доступные слоты на неделю вперёд
    
    for day_offset in range(days_to_show):
        current_day = current_time + timedelta(days=day_offset)
        current_day_start = datetime(current_day.year, current_day.month, current_day.day, work_start_time // 60, work_start_time % 60)
        
        for minutes in range(work_start_time, work_end_time, interval):
            current_slot_start = current_day_start + timedelta(minutes=minutes)
            current_slot_end = current_slot_start + timedelta(minutes=interval)

            if all(
                not (
                    (current_slot_start <= res_start < current_slot_end) or
                    (current_slot_end > res_start >= current_slot_start)
                )
                for res_start, _ in [(datetime.strptime(res['start_time'], '%H:%M'), res['duration']) for res in active_reservations]
            ):
                if current_slot_start >= current_time:
                    slot_info = {
                        'day': current_slot_start.strftime('%Y-%m-%d'),
                        'time': current_slot_start.strftime('%H:%M'),
                        'start_minutes': minutes,
                        'end_minutes': minutes + interval,
                    }
                    available_slots.append(slot_info)

    return available_slots

def create_slot_keyboard(available_slots):
    keyboard = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)

    for slot_info in available_slots:
        button_text = f"{slot_info['day']} {slot_info['time']}"
        keyboard.add(types.KeyboardButton(button_text))

    return keyboard

def reserve_slot(message):
    user_id = message.from_user.id
    selected_slot_text = message.text

    # Извлечение информации о слоте
    selected_day_str, selected_time_str = selected_slot_text.split(' ')
    selected_day = datetime.strptime(selected_day_str, '%Y-%m-%d')
    selected_time = datetime.strptime(selected_time_str, '%H:%M')

    # Получение времени начала и окончания слота в минутах относительно полуночи
    selected_minutes = selected_time.hour * 60 + selected_time.minute
    selected_start_minutes = selected_day.hour * 60 + selected_minutes
    selected_end_minutes = selected_start_minutes + 30  # Продолжительность визита 30 минут

    # Проверка доступности выбранного слота
    available_slots = get_available_slots(user_id)
    if not any(
        slot_info['day'] == selected_day_str and slot_info['start_minutes'] == selected_start_minutes
        for slot_info in available_slots
    ):
        bot.send_message(message.chat.id, "Выбранный слот недоступен. Пожалуйста, выберите другой.")
    else:
        # Запись резервации в базу данных
        reservation_data = {
            'user_id': user_id,
            'status': 'active',
            'duration': 30,  # Продолжительность визита в минутах
            'start_time': selected_time_str,
            'start_minutes': selected_start_minutes,
            'end_minutes': selected_end_minutes,
        }
        db.insert(reservation_data)

        bot.send_message(message.chat.id, f"Ваш визит забронирован на {selected_day_str} в {selected_time_str}. Наслаждайтесь!")

# Запуск бота
bot.polling()
