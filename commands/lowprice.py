from bot import bot

import requests
import config
import json

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from langdetect import detect
from typing import Union
from keyboards.keyboards import city_keyboard, quantity_keyboard, yes_no_keyboard
from keyboards import calendar
from config import query_hotel
from main import command_start, command_help

city_list = [{'destinationId': '', 'name': ''}]
i_city = {'destinationId': '', 'name': ''}
country_id = ['']
hotels_low = list[dict]
hotel_ifo = {
    'id': 0000,
    'name': '',
    'address': '',
    'distance_center': '',
    'price': 00.00,
    'photo_amount': '',
    'photo': []
}


def start_script(message: Union[Message, CallbackQuery], bot: TeleBot) -> None:
    """
    Функция запуска сценария команды lowprice, сценарий начинается с запроса города назначения.
    :param bot: TeleBot
    :param message: Message
    :return: None
    """

    config.query_hotel_rest()

    if isinstance(message, CallbackQuery):
        bot.send_sticker(message.from_user.id, config.sticker_go)
        bot.send_message(message.from_user.id, 'Куда едем?')
        lowprice_message = bot.send_message(message.from_user.id,
                                            'Введите название города или первые буквы')
    else:
        bot.send_sticker(message.chat.id, config.sticker_go)
        bot.send_message(message.chat.id, 'Куда поедем?')
        lowprice_message = bot.send_message(message.chat.id,
                                            'Введите название города или первые буквы')

    bot.register_next_step_handler(lowprice_message, select_city)


def select_city(message: Message) -> None:
    """
    Функция запускает поиск городов по введенным буквам, выводит Inline кнопки c городами для выбора
    :param message: Message
    :return: None
    """
    search_city(message)

    if len(city_list) > 0 and country_id[0] == 'EN':
        bot.send_message(
            message.from_user.id,
            'Выберите город из списка',
            reply_markup=city_keyboard(city_list))

    elif len(city_list) > 0 and country_id[0] == 'RU':
        bot.send_message(
            message.from_user.id,
            'Выберите отель из списка',
            reply_markup=city_keyboard(city_list))
        pass
    # TODO добавить обработку русских отелей

    else:
        bot.send_message(message.from_user.id, 'Ничего похожего нет, попробуйте еще раз')
        start_script(message, bot)


def search_city(message: Message) -> None:
    """
    Функция отправляет запрос на поиск городов по введенным буквам, загружает результаты,
    и готовит список городов с destinationId
    :param message: Message
    :return: city_list: List[dict]
    """

    bot.send_message(message.from_user.id, 'Готовлю подборку...')
    city_list.clear()

    if message.text == '/start':
        command_start(message)
    elif message.text == '/help':
        command_help(message)

    if detect(message.text) == 'ru':
        config.query_city['locale'] = 'ru_RU'
        group_id = 'HOTEL_GROUP'
        type_id = 'HOTEL'
        bot.send_message(message.from_user.id, 'Для России доступен поиск только по отелям')
        country_id[0] = 'RU'
    else:
        config.query_city['locale'] = 'en_US'
        group_id = 'CITY_GROUP'
        type_id = 'CITY'
        country_id[0] = 'EN'

    config.query_city['query'] = message.text.lower()
    response = requests.request('GET', config.city_url, headers=config.hotels_headers, params=config.query_city)
    request_data = json.loads(response.text)

    for i_group in request_data['suggestions']:
        if i_group['group'] == group_id:
            for i_entities in i_group['entities']:

                if i_entities['type'] == type_id:
                    city_list.append({'destinationId': i_entities['destinationId'], 'name': i_entities['name']})


def hotel_amount_set(call: CallbackQuery) -> None:
    """
    Функция запрашивает какое количество отелей выводит по средствам inline-кнопок
    :param call: CallbackQuery
    :return: None
    """
    bot.send_message(call.from_user.id, 'Выберите, сколько отелей показать:', reply_markup=quantity_keyboard())


def photo_necessity(call: CallbackQuery) -> None:
    """
    Функция спрашивает необходимость фото по средствам inline-кнопок
    :param call: CallbackQuery
    :return: None
    """
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Хотите увидеть фото отеля?',
                          reply_markup=yes_no_keyboard())


def request_hotel(call: CallbackQuery) -> None:
    response = requests.request('GET', config.hotel_url, headers=config.hotels_headers, params=query_hotel)
    request_hotel_data = json.loads(response.text)['data']['body']['searchResults']['results']
    print(query_hotel)
    print(request_hotel_data)


#     TODO: взять из запроса "hotel_amount" отелей, загрузить для них 'photo_amount' фото и передать на вывод в бот


def output_hotel(call: CallbackQuery, request_data: list[dict]) -> None:
    pass


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def search_hotel_handler(call: CallbackQuery) -> None:
    """
    Функция-обработчик inline-кнопок с перечнем городов, запускает функцию выбора даты заезда.
    :param call: CallbackQuery
    :return: None
    """
    if call.message:
        query_hotel['destinationId'] = call.data[5:]
        for city in call.message.json['reply_markup']['inline_keyboard']:
            if city[0]['callback_data'] == call.data:
                city_name = city[0]['text']
        text = 'Вы выбрали город -=* {} *=-'.format(city_name)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text,
                              reply_markup=None)
        calendar.date_in(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('quantity_'))
def hotel_photo_amount_handler(call: CallbackQuery) -> None:
    """
    Функция-обработчик inline-кнопок с количеством,
    Если количество отелей не установлено, устанавливает их количество, и запускает сценарий запроса вывода фотографий.
    В противном случае устанавливает количество фото, и запускает сценарий поиска отелей.
    :param call: CallbackQuery
    :return: None
    """
    if query_hotel['hotel_amount'] == '':
        query_hotel['hotel_amount'] = call.data[9:]
        print(query_hotel['hotel_amount'])
        photo_necessity(call)
    else:
        query_hotel['photo_amount'] = call.data[9:]
        print(query_hotel['photo_amount'])
        request_hotel(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
def photo_necessity_handler(call: CallbackQuery) -> None:
    """
    Функция-обработчик inline-кнопок с подтверждением необходимости фото.
    Если фото нужны -запускает сценарий выбора количества фото.
    Если фото не требуется -запускает сценарий поиска отелей.
    :param call: CallbackQuery
    :return: None
    """
    if call.data == 'confirm_no':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='выбрано: -= Без фото =-',
                              reply_markup=None)
        query_hotel['photo_amount'] = 'None'
        request_hotel(call)
    elif call.data == 'confirm_yes':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Сколько фото загружать?',
                              reply_markup=quantity_keyboard())
