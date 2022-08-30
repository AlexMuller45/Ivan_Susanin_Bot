import telebot
from telebot.types import InlineKeyboardMarkup, CallbackQuery, Message
from telebot import types
import config
# import bestdeal
# import highprice
# import history
# import lowprice

bot = telebot.TeleBot(config.bot_token)


@bot.message_handler(commands=['start'])
def command_start(message: Message) -> None:
    """
    Функция -обработчик команды /start, приветствие пользователя
    :param message: Message
    :return: None
    """
    bot.send_sticker(message.chat.id, config.sticker_welcom)
    bot.send_message(message.from_user.id,
                     '{}!\n'
                     'Вас приветствует помощник для поиска подходящего Вам отеля\n'
                     'от турагентства "Too Easy Travel"'.format(message.from_user.first_name),
                     reply_markup=main_keyboard(message.text))


@bot.message_handler(commands=['help'])
def command_help(message: Message) -> None:
    """
    Функция -обработчик команды /help
    :param message: Message
    :return: None
    """
    bot.send_sticker(message.chat.id, config.sticker_help)
    bot.send_message(message.from_user.id,
                     '{}, не знаете что делать?'.format(message.from_user.first_name))
    bot.send_message(message.from_user.id, config.help_message,
                     reply_markup=main_keyboard(message.text))


@bot.message_handler(commands=['lowprice'])
def command_lowprice(message: Message) -> None:
    """
    Функция -обработчик команды /lowprice
    :param message: Message
    :return: None
    """
    bot.send_message(message.from_user.id, '/lowprice в разработке')


@bot.message_handler(commands=['highprice'])
def command_highprice(message: Message) -> None:
    """
    Функция -обработчик команды /highprice
    :param message: Message
    :return: None
    """
    bot.send_message(message.from_user.id, '/highprice в разработке')


@bot.message_handler(commands=['bestdeal'])
def command_bestdeal(message: Message) -> None:
    """
    Функция -обработчик команды /bestdeal
    :param message: Message
    :return: None
    """
    bot.send_message(message.from_user.id, '/bestdeal в разработке')


@bot.message_handler(commands=['history'])
def command_history(message: Message) -> None:
    """
    Функция -обработчик команды /history
    :param message: Message
    :return: None
    """
    bot.send_message(message.from_user.id, '/history в разработке')


def main_keyboard(command: str) -> InlineKeyboardMarkup:
    """
    Функция - создаёт inline-клавиатуру для команд
    :param command: str
    :return: InlineKeyboardMarkup
    """
    markup = InlineKeyboardMarkup()
    if command == '/start':
        key_help = types.InlineKeyboardButton(text='Help', callback_data='/help')
        markup.add(key_help)
    elif command == '/help':
        key_lowprice = types.InlineKeyboardButton(text='Low Price', callback_data='/lowprice')
        key_highprice = types.InlineKeyboardButton(text='High Price', callback_data='/highprice')
        key_bestdeal = types.InlineKeyboardButton(text='Best Deal', callback_data='/bestdeal')
        key_history = types.InlineKeyboardButton(text='History', callback_data='/history')
        markup.add(key_lowprice, key_highprice, key_bestdeal, key_history)
    return markup


@bot.callback_query_handler(func=lambda call: True)
def inline_handler(call: CallbackQuery) -> None:
    """
    Функция -обработчик inline-кнопок
    :param call: CallbackQuery
    :return: None
    """
    if call.data == '/help':
        bot.send_sticker(call.from_user.id, config.sticker_help)
        bot.send_message(call.from_user.id, '{}, не знаете что делать?'.format(call.from_user.first_name))
        bot.send_message(call.from_user.id, config.help_message, reply_markup=main_keyboard(call.data))
    elif call.data == '/lowprice':
        bot.send_message(call.message.chat.id, '/lowprice в разработке')
    elif call.data == '/highprice':
        bot.send_message(call.message.chat.id, '/highprice в разработке')
    elif call.data == '/bestdeal':
        bot.send_message(call.message.chat.id, '/bestdeal в разработке')
    elif call.data == '/history':
        bot.send_message(call.message.chat.id, '/history в разработке')


@bot.message_handler(func=lambda message: True, content_types=config.all_type)
def other_message(message: Message) -> None:
    """
    Функция -обработчик всех прочих сообщений
    :param message: Message
    :return: None
    """
    bot.send_message(message.from_user.id,
                     'Для ознакомления с доступными функциями отправьте сообщение /help\nили нажмите кнопку ниже',
                     reply_markup=main_keyboard(command='/start'))


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
