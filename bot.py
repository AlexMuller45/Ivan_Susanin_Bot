import telebot
import config

from logging_config import custom_logger
from typing import Callable


logger = custom_logger('bot_logger')

bot = telebot.TeleBot(config.bot_token)
print(bot.get_me())


def exception_handler(func: Callable) -> Callable:
    """
    Декоратор - оборачивающий функцию в try-except блок.
    :param func: Callable
    :return: Callable
    """
    def wrapped_func(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as error:
            logger.error('В работе бота возникло исключение', exc_info=error)
    return wrapped_func

