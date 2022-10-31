import config

from bot import bot, logger, exception_handler
from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from typing import Union
from commands import functions



@exception_handler
def start_script_lowprice(message: Union[Message, CallbackQuery], bot: TeleBot) -> None:
    """
    Функция запуска сценария команды lowprice, сценарий начинается с запроса города назначения.
    :param bot: TeleBot
    :param message: Message
    :return: None
    """

    config.query_hotel_reset()
    logger.info(str(message.from_user.id))

    functions.start_select_city(message, identifier='lowprice')

