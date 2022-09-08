from bot import bot
import config
from keyboards.keyboards import main_keyboard
from commands import lowprice
from telebot.types import CallbackQuery, Message


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
    # bot.send_message(message.from_user.id, '/lowprice в разработке')
    lowprice.start_script(message, bot)


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


@bot.callback_query_handler(func=lambda call: call.data.startswith('/'))
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
        bot.send_message(call.from_user.id, '/lowprice в разработке, но попробуем')
        lowprice.start_script(call, bot)

    elif call.data == '/highprice':
        bot.send_message(call.from_user.id, '/highprice в разработке')
    elif call.data == '/bestdeal':
        bot.send_message(call.from_user.id, '/bestdeal в разработке')
    elif call.data == '/history':
        bot.send_message(call.from_user.id, '/history в разработке')


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
    bot.infinity_polling()
