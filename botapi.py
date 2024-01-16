import telebot
from datetime import datetime, timedelta

TOKEN = '6915117121:AAGmTsVhGGkNuV4p0_LIR8qB5TRPxhlKG0o'
bot = telebot.TeleBot(TOKEN)

# Словарь для хранения расписания
schedule = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать! Для бронирования визита используйте команду /reserve.")

@bot.message_handler(commands=['reserve'])
def reserve_time(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Проверка, есть ли у пользователя уже бронь
    if user_id in schedule:
        bot.send_message(chat_id, "У вас уже есть бронь. Вы не можете забронировать еще один визит.")
    else:
        # Проверка наличия свободного времени
        current_time = datetime.now()
        available_time = None

        while available_time is None:
            # Проверяем свободное время с шагом в 30 минут
            if current_time not in schedule.values():
                available_time = current_time
            else:
                current_time += timedelta(minutes=30)

        # Добавляем бронь в расписание
        schedule[user_id] = available_time

        # Отправляем подтверждение
        formatted_time = available_time.strftime("%Y-%m-%d %H:%M")
        bot.send_message(chat_id, f"Ваш визит забронирован на {formatted_time}.")

@bot.message_handler(commands=['cancel'])
def cancel_reservation(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Проверка наличия брони у пользователя
    if user_id in schedule:
        del schedule[user_id]
        bot.send_message(chat_id, "Ваша бронь отменена.")
    else:
        bot.send_message(chat_id, "У вас нет активной брони.")

if __name__ == "__main__":
    bot.polling(none_stop=True)
