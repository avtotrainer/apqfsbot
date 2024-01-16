import telebot
from telebot import types
from datetime import datetime, timedelta
# Создание бота (замените 'YOUR_TOKEN' на реальный токен вашего бота)
BOT_TOKEN = '6915117121:AAGmTsVhGGkNuV4p0_LIR8qB5TRPxhlKG0o'
bot = telebot.TeleBot('BOT_TOKEN')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """
    Обработчик команды /start, отправляет приветственное сообщение.
    """
    bot.reply_to(message, "Добро пожаловать в наш сервис!")

@bot.message_handler(commands=['registration'])
def registration(message):
    """
    Обработчик команды /registration, регистрирует нового пользователя.

    """
    # Здесь должен быть код для регистрации пользователя
    bot.reply_to(message, "Вы успешно зарегистрированы!")

@bot.message_handler(commands=['confirmation'])
def confirmation(message):
    """
    Обработчик команды /confirmation, подтверждение или отмена визита администратором.
    """
    # Код для подтверждения или отмены визита
    bot.reply_to(message, "Визит подтвержден/отменен.")

@bot.message_handler(commands=['book'])
def book_appointment(message):
    """
    Обработчик команды /book, позволяет клиенту забронировать время визита.
    """
    # Код для бронирования времени визита
    bot.reply_to(message, "Выберите удобное время для визита.")

@bot.message_handler(commands=['admin'])
def admin_panel(message):
    """
    Обработчик команды /admin, панель администратора для управления сервисом.
    """
    # Код для административной панели
    bot.reply_to(message, "Добро пожаловать в административную панель.")

# Здесь могут быть другие обработчики сообщений и команд
def generate_schedule(start_time='08:00', end_time='19:00', lunch_start='13:00', lunch_duration=1, appointment_duration=15):
    """
    Генерирует расписание рабочего дня.

    Параметры:
    start_time (str): время начала рабочего дня (формат ЧЧ:ММ).
    end_time (str): время окончания рабочего дня (формат ЧЧ:ММ).
    lunch_start (str): время начала обеденного перерыва (формат ЧЧ:ММ).
    lunch_duration (int): продолжительность обеденного перерыва в часах.
    appointment_duration (int): продолжительность одного визита в минутах.
    
    Возвращает:
    list: список временных слотов для визитов.
    """
    schedule = []

    current_time = datetime.strptime(start_time, '%H:%M')
    end_time = datetime.strptime(end_time, '%H:%M')
    lunch_start = datetime.strptime(lunch_start, '%H:%M')
    lunch_end = lunch_start + timedelta(hours=lunch_duration)

    while current_time < end_time:
        if lunch_start <= current_time < lunch_end:
            schedule.append(f"Перерыв - {current_time.strftime('%H:%M')}")
            current_time = lunch_end
        else:
            schedule.append(f"Визит - {current_time.strftime('%H:%M')}")
            current_time += timedelta(minutes=appointment_duration)

    return schedule


def create_booking_buttons(schedule):
    """
    Создает сетку инлайн-кнопок для бронирования визитов.

    Параметры:
    schedule (list): список временных слотов.

    Возвращает:
    InlineKeyboardMarkup: сетка инлайн-кнопок.
    """
    markup = types.InlineKeyboardMarkup(row_width=4)
    buttons = []

    for slot in schedule:
        if "Визит" in slot:
            time = slot.split(' - ')[1]
            button = types.InlineKeyboardButton(time, callback_data=f'book_{time}')
            buttons.append(button)

    # Добавляем кнопки в сетку по 4 в ряд
    while buttons:
        row = buttons[:4]
        buttons = buttons[4:]
        markup.add(*row)

    return markup

# Пример использования функции
# daily_schedule = generate_schedule()
# booking_buttons = create_booking_buttons(daily_schedule)

# Для отправки сообщения с этими кнопками:
# bot.send_message(chat_id, "Выберите удобное время для визита:", reply_markup=booking_buttons)
def create_schedule_buttons(schedule):
    """
    Создает сетку инлайн кнопок для расписания.

    Параметры:
    schedule (list): список временных слотов и перерывов.

    Возвращает:
    types.InlineKeyboardMarkup: объект сетки кнопок.
    """
    markup = types.InlineKeyboardMarkup(row_width=4)
    for slot in schedule:
        if "Перерыв" in slot:
            # Для перерыва создаем широкую кнопку
            break_button = types.InlineKeyboardButton(slot, callback_data="break", width=4)
            markup.add(break_button)
        else:
            # Для обычных слотов создаем кнопки бронирования
            book_button = types.InlineKeyboardButton(slot, callback_data="book")
            markup.row(book_button)

    return markup

# Пример использования функции для отправки сообщения с кнопками
@bot.message_handler(commands=['schedule'])
def send_schedule(message):
    # Предположим, что daily_schedule - это ваше расписание
    daily_schedule = generate_schedule()  # Функция генерации расписания, определенная ранее
    markup = create_schedule_buttons(daily_schedule)
    bot.send_message(message.chat.id, "Выберите удобное время для визита:", reply_markup=markup)

# Не забудьте запустить бота
bot.polling()
