import config

from bot import bot, logger, exception_handler
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from typing import Union, List
from os import path

user_history = list()
current_user = {'id': 00}


@exception_handler
def start_script_history(message: Union[Message, CallbackQuery], bot: TeleBot) -> None:
    """
    Функция запускает сценарий вывода истории поиска
    :param message: Union[Message, CallbackQuery]
    :param bot: TeleBot
    :return: None
    """

    bot.send_sticker(message.from_user.id, config.sticker_history)
    current_user['id'] = message.from_user.id

    logger.info(str(current_user))

    bot.send_message(current_user['id'], 'История поиска')

    load_history(current_user['id'])


@exception_handler
def load_history(user_id: int) -> None:
    """
    Функция загружает историю из файла и выбирает записи относящиеся к текущему пользователю
    :param user_id: dict
    :return: None
    """
    user_history.clear()
    with open('history.log', 'r', encoding='UTF-8') as file:
        for i_line in file:
            history_line = i_line.split('# ')
            if int(history_line[0]) == user_id:
                user_history.append(history_line.copy())
    print(user_history)

    show_history(user_history)


@exception_handler
def show_history(history_list: List) -> None:
    """
    Функция передает боту историю запросов пользователя
    :param history_list: List
    :return: None
    """
    for i_elem in history_list:
        user_id = current_user['id']
        result = '\n'.join(i_elem[3:])
        text = 'Команда: {command}\n' \
               'Дата и время команды: {command_date}\n' \
               'Результаты поиска: \n{result}'.format(
                                                    command=i_elem[1],
                                                    command_date=i_elem[2],
                                                    result=result)
        bot.send_message(user_id, text)

    bot.send_message(user_id, '-= конец архива =-')


@exception_handler
def save_history(call: CallbackQuery, script_history: str) -> None:
    """
    Функция записывает в файл строку с командой, датой и результатом поиска
    :param call: CallbackQuery
    :param script_history: str
    :return: None
    """
    logger.info(str(call.from_user.id))

    mode = 'a' if path.exists('history.log') else 'w'
    with open('history.log', mode, encoding='UTF-8') as file:
        file.write(script_history)

