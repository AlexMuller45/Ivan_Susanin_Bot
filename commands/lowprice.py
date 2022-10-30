import requests
import config
import json
import re
import copy

from bot import bot, logger, exception_handler
from telebot import TeleBot
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from langdetect import detect
from typing import Union, Any
from keyboards.keyboards import city_keyboard, quantity_keyboard, yes_no_keyboard
from keyboards import calendar
from config import query_hotel, hotel_info, query_photo
from main import command_start, command_help
from datetime import datetime


city_list = [{'destinationId': '', 'name': ''}]
i_city = {'destinationId': '', 'name': ''}
country_id = ['']
hotels_low = list(dict())


@exception_handler
def start_script(message: Union[Message, CallbackQuery], bot: TeleBot) -> None:
    """
    Функция запуска сценария команды lowprice, сценарий начинается с запроса города назначения.
    :param bot: TeleBot
    :param message: Message
    :return: None
    """

    config.query_hotel_reset()
    logger.info(str(message.from_user.id))

    if isinstance(message, CallbackQuery):
        bot.send_sticker(message.from_user.id, config.sticker_go)
        bot.send_message(message.from_user.id, 'Куда едем?')
        lowprice_message = bot.send_message(message.from_user.id,
                                            'Введите название города или первые буквы')
    else:
        logger.info(str(message.from_user.id))
        bot.send_sticker(message.chat.id, config.sticker_go)
        bot.send_message(message.chat.id, 'Куда поедем?')
        lowprice_message = bot.send_message(message.chat.id,
                                            'Введите название города или первые буквы')

    bot.register_next_step_handler(lowprice_message, select_city)

@exception_handler
def select_city(message: Message) -> None:
    """
    Функция запускает поиск городов по введенным буквам, выводит Inline кнопки c городами для выбора
    :param message: Message
    :return: None
    """
    logger.info(str(message.from_user.id))

    search_city(message)

    if len(city_list) > 0 and country_id[0] == 'EN':
        bot.send_message(
            message.from_user.id,
            'Выберите город из списка',
            reply_markup=city_keyboard(city_list))

    elif len(city_list) > 0 and country_id[0] == 'RU':
        # bot.send_message(
        #     message.from_user.id,
        #     'Выберите отель из списка',
        #     reply_markup=city_keyboard(city_list))
        # pass
        bot.send_message(message.from_user.id, 'Поиск Российских городов временно приостановлен!')
    # TODO добавить обработку русских отелей

    else:
        bot.send_message(message.from_user.id, 'Ничего похожего нет, попробуйте еще раз')
        start_script(message, bot)


@exception_handler
def search_city(message: Message) -> None:
    """
    Функция отправляет запрос на поиск городов по введенным буквам, загружает результаты,
    и готовит список городов с destinationId
    :param message: Message
    :return: city_list: List[dict]
    """
    logger.info(str(message.from_user.id))
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


@exception_handler
def hotel_amount_set(call: CallbackQuery) -> None:
    """
    Функция запрашивает какое количество отелей выводит по средствам inline-кнопок
    :param call: CallbackQuery
    :return: None
    """
    bot.send_message(call.from_user.id, 'Выберите, сколько отелей показать:', reply_markup=quantity_keyboard())


@exception_handler
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


@exception_handler
def request_hotel(call: CallbackQuery) -> None:
    """
    Функция формирует и отправляет запрос на отели в определенном городе,
    получает ответ с сортировкой отелей по возрастанию стоимости проживания,
    готовит список отелей и подгружает, при необходимости фото.
    :param call: CallbackQuery
    :return: None
    """
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выбрано {hotels} отелей и {photos} фотографий'.format(
                              hotels=query_hotel['hotel_amount'],
                              photos=query_hotel['photo_amount']
                          ),
                          reply_markup=None)

    bot.send_message(call.from_user.id, 'Подбираю варианты...')

    query_string = query_hotel.copy()
    del query_string['hotel_amount']
    del query_string['photo_amount']
    response = requests.request('GET', config.hotel_url, headers=config.hotels_headers, params=query_string)
    request_hotel_data = json.loads(response.text)['data']['body']['searchResults']['results']
    print(query_hotel)
    print(request_hotel_data)

    day_per_stay = datetime.strptime(query_hotel['checkOut'], '%Y-%m-%d') - datetime.strptime(query_hotel['checkIn'],
                                                                                              "%Y-%m-%d")

    hotels_low.clear()

    for i_hotel in range(query_hotel['hotel_amount']):
        config.hotel_info_reset()
        hotel_info['id'] = request_hotel_data[i_hotel]['id']
        hotel_info['name'] = request_hotel_data[i_hotel]['name']
        hotel_info['address'] = request_hotel_data[i_hotel]['address']['streetAddress'] + ', ' \
                                + request_hotel_data[i_hotel]['address']['locality'] + ', ' \
                                + request_hotel_data[i_hotel]['address']['countryName']
        hotel_info['distance_center'] = request_hotel_data[i_hotel]['landmarks'][0]['distance']
        hotel_info['price'] = request_hotel_data[i_hotel]['ratePlan']['price']['exactCurrent']
        hotel_info['fully_bundled_price_per_stay'] \
            = (day_per_stay.days - 1) * hotel_info['price']
        hotel_info['night_per_stay'] = day_per_stay.days - 1

        # загрузка фото
        if query_hotel['photo_amount'] <= 0:
            pass
        else:
            bot.send_message(call.from_user.id, 'Подгружаю фото...')
            query_photo['id'] = hotel_info['id']
            photo_response = requests.request(
                "GET",
                config.photo_url,
                headers=config.hotels_headers,
                params=query_photo
            )

            if not photo_response:
                return bot.send_message(call.from_user.id, "Произошла ошибка.\nПопробуйте снова.")
            else:
                request_hotel_photo = json.loads(photo_response.text)

                if len(request_hotel_photo['hotelImages']) > query_hotel['photo_amount']:
                    # если на сервере фото больше чем надо
                    for i_photo in range(query_hotel['photo_amount']):
                        base_url = request_hotel_photo['hotelImages'][i_photo]['baseUrl'].format(size='y')
                        hotel_info['photo'].append(InputMediaPhoto(media=base_url))
                else:
                    # если фото мало
                    for i_photo in range(len(request_hotel_photo['hotelImages'])):
                        base_url = request_hotel_photo['hotelImages'][i_photo]['baseUrl'].format(size='y')
                        hotel_info['photo'].append(InputMediaPhoto(media=base_url))

        hotels_low.append(copy.deepcopy(hotel_info))

    print(hotels_low)
    output_hotel(call, hotels_low)


@exception_handler
def output_hotel(call: CallbackQuery, request_data: Any) -> None:
    exchange_rate = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']['Value']
    in_order = 1
    bot.send_message(call.from_user.id, 'Срок пребывания {night} ночей'.format(night=request_data[0]['night_per_stay']))
    for i_hotel_info in request_data:
        price_rub = i_hotel_info['price'] * exchange_rate
        price_rub = round(price_rub, 2)
        total_rub = i_hotel_info['fully_bundled_price_per_stay'] * exchange_rate
        total_rub = round(total_rub, 2)
        distance_meters = float(re.search(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?',
                                          i_hotel_info['distance_center']).group()) * 1.609344
        distance_meters = round(distance_meters, 3)
        text = '{order}. Название отеля:\n  = {name} =\n' \
               'Адрес отеля: {address}\n' \
               'Расстояние до центра: {distance} км\n' \
               'Стоимость за сутки: {price} руб.\n' \
               'Стоимость за все время прибывания: {total} руб.\n'.format(
                                                                        order=in_order,
                                                                        name=i_hotel_info['name'],
                                                                        address=i_hotel_info['address'],
                                                                        distance=distance_meters,
                                                                        price=price_rub,
                                                                        total=total_rub)

        if query_hotel['photo_amount'] > 0:
            bot.send_message(call.from_user.id, text)
            bot.send_media_group(call.from_user.id, i_hotel_info['photo'])
        else:
            bot.send_message(call.from_user.id, text)

        in_order += 1
        line = '- - - = = = *** = = = - - -'
        bot.send_message(call.from_user.id, line)

    bot.send_message(call.from_user.id, '-= Поиск завершен =-')


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
@exception_handler
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
@exception_handler
def hotel_photo_amount_handler(call: CallbackQuery) -> None:
    """
    Функция-обработчик inline-кнопок с количеством,
    Если количество отелей не установлено, устанавливает их количество, и запускает сценарий запроса вывода фотографий.
    В противном случае устанавливает количество фото, и запускает сценарий поиска отелей.
    :param call: CallbackQuery
    :return: None
    """
    if query_hotel['hotel_amount'] == 0:
        query_hotel['hotel_amount'] = int(call.data[9:])
        # print(query_hotel['hotel_amount'])
        photo_necessity(call)
    else:
        query_hotel['photo_amount'] = int(call.data[9:])
        # print(query_hotel['photo_amount'])
        request_hotel(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_'))
@exception_handler
def photo_necessity_handler(call: CallbackQuery) -> None:
    """
    Функция-обработчик inline-кнопок с подтверждением необходимости фото.
    Если фото нужны - запускает сценарий выбора количества фото.
    Если фото не требуется - запускает сценарий поиска отелей.
    :param call: CallbackQuery
    :return: None
    """
    if call.data == 'confirm_no':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='выбрано: -= Без фото =-',
                              reply_markup=None)
        query_hotel['photo_amount'] = 0
        request_hotel(call)
    elif call.data == 'confirm_yes':
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text='Сколько фото загружать?',
                              reply_markup=quantity_keyboard())
