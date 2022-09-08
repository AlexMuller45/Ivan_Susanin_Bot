from telebot import types
from telebot.types import InlineKeyboardMarkup
from typing import List


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


def city_keyboard(city_list: List[dict]) -> InlineKeyboardMarkup:
    """
    Функция - создаёт inline-клавиатуру городов из списка city_list
    :param city_list: List[dict]
    :return: InlineKeyboardMarkup
    """
    markup = InlineKeyboardMarkup(row_width=1)
    for i_city in city_list:
        key = types.InlineKeyboardButton(text=i_city['name'], callback_data='city_' + i_city['destinationId'])
        markup.add(key)
    return markup


def quantity_keyboard() -> InlineKeyboardMarkup:
    """
    Функция создает клавиатуру для выбора количества отелей, фото
    :return: InlineKeyboardMarkup
    """
    markup = InlineKeyboardMarkup()
    key_three = types.InlineKeyboardButton(text='3', callback_data='quantity_3')
    key_five = types.InlineKeyboardButton(text='5', callback_data='quantity_5')
    key_ten = types.InlineKeyboardButton(text='10', callback_data='quantity_10')
    markup.add(key_three, key_five, key_ten)
    return markup


def yes_no_keyboard() -> InlineKeyboardMarkup:
    """
    Функция создает клавиатуру для выбора да/нет
    :return: InlineKeyboardMarkup
    """
    markup = InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='confirm_yes')
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='confirm_no')
    markup.add(key_yes, key_no)
    return markup

