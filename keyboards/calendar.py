from typing import Any
from datetime import datetime, timedelta, date
from bot import bot
from telegram_bot_calendar import DetailedTelegramCalendar

from commands import lowprice
from config import LSTEP, query_hotel
from telebot.types import CallbackQuery


def date_in(call: CallbackQuery) -> None:
    """
    Функция запрашивает дату заезда, формирует календарь
    :param call: CallbackQuery
    :return: None
    """
    min_date = date.today() + timedelta(days=1)
    bot.send_message(call.from_user.id, 'Выберите дату заезда')
    calendar, step = DetailedTelegramCalendar(
        calendar_id=0,
        locale='ru',
        min_date=min_date
    ).build()
    bot.send_message(call.message.chat.id, 'Укажите {}:'.format(LSTEP[step]), reply_markup=calendar)


def date_out(call: CallbackQuery, result: datetime) -> None:
    """
    Функция запрашивает дату отъезда, формирует календарь
    :param call: CallbackQuery
    :return: None
    """
    min_date = result + timedelta(days=1)
    bot.send_message(call.from_user.id, 'Выберите дату отъезда')
    calendar, step = DetailedTelegramCalendar(
        calendar_id=55,
        locale='ru',
        min_date=min_date
    ).build()
    bot.send_message(call.message.chat.id, 'Укажите {}:'.format(LSTEP[step]), reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=0))
def date_in_set(call: CallbackQuery) -> Any:
    """
    Функция-обработчик inline-календаря. Реагтрует только на календарь с ID = 0 (дата заезда).
    после выбора даты, запускает функцию date_out -выбор даты отъезда
    :param call: CallbackQuery
    :return: None
    """
    result, key, step = DetailedTelegramCalendar(
        calendar_id=0,
        locale='ru',
        min_date=date.today()
    ).process(call.data)
    if not result and key:
        bot.edit_message_text('Укажите {}'.format(LSTEP[step]),
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text('Вы выбрали: {}'.format(result),
                              call.message.chat.id,
                              call.message.message_id)

        query_hotel['checkIn'] = result
        date_out(call, result)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=55))
def date_out_set(call: CallbackQuery) -> Any:
    """
    Функция-обработчик inline-календаря. Реагирует только на календарь с ID = 55 (дата отъезда).
    после выбора даты, запускает функцию hotel_amount_set -выбор количества отелей для показа пользователю
    :param call: CallbackQuery
    :return: None
    """
    min_date = query_hotel['checkIn'] + timedelta(days=1)
    result, key, step = DetailedTelegramCalendar(
        calendar_id=55,
        locale='ru',
        min_date=min_date
    ).process(call.data)

    if not result and key:
        bot.edit_message_text('Укажите {}'.format(LSTEP[step]),
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)

    elif result:
        bot.edit_message_text('Вы выбрали: {} '.format(result),
                              call.message.chat.id,
                              call.message.message_id)
        query_hotel['checkOut'] = datetime.strftime(result, '%Y-%m-%d')
        query_hotel['checkIn'] = datetime.strftime(query_hotel['checkIn'], '%Y-%m-%d')
        lowprice.hotel_amount_set(call)

