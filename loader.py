import telebot
import config

bot = telebot.TeleBot(config.bot_token)

bot.polling(none_stop=True, interval=0)
