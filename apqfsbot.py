import telebot

bot = telebot.TeleBot('6915117121:AAGmTsVhGGkNuV4p0_LIR8qB5TRPxhlKG0o')

@bot.message_handler(commands=['start'])
def start(message):
   mess= f'გამარჯობა <b>{message.from_user.first_name} {message.from_user.last_name}</b>'
   bot.send_message(message.chat.id,mess,parse_mode='html')

@bot.message_handler(commands=['info'])
def info(message):
    bot.send_message(message.chat.id, message)

@bot.message_handler()
def get_uset_text(message):
    if message.text == 'info':
        user_message = message
    elif message.text == 'userid':
        user_message = message.from_user.id

    elif message.text == 'id':
        user_message=message.id  
    else:
        user_message=message.text + '- ეს სიტყვა არ ვიცი' 

    bot.send_message(message.chat.id,user_message,parse_mode='html')


bot.polling(none_stop=True)
