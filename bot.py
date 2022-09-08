import telebot
import config


bot = telebot.TeleBot(config.bot_token)

print(bot.get_me())
