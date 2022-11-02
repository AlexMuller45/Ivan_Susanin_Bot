import requests
import config
import json
import re
import copy

from bot import bot, logger, exception_handler
from telebot.types import Message, CallbackQuery, InputMediaPhoto
from langdetect import detect
from typing import Union, Any
from keyboards.keyboards import city_keyboard, quantity_keyboard, yes_no_keyboard, main_keyboard
from keyboards import calendar
from config import query_hotel, hotel_info, query_photo
from main import command_start, command_help
from commands.history import save_history
from datetime import datetime
from requests import ReadTimeout


city_list = [{'destinationId': '', 'name': ''}]
i_city = {'destinationId': '', 'name': ''}
country_id = ['']
hotels = list(dict())
command_id = {'id': ''}
distance = {'distance_from_center': 0.0, 'units': 'км', 'ratio': 1.609344}


def start_select_city(message: Union[Message, CallbackQuery], identifier: str) -> None:
    """
    Функция запускает сценарий выбора города, запрашивает первые буквы названия города
    :param identifier: string  - идентификатор команды, вызвавший функцию
    :param message: Union[Message, CallbackQuery]
    :return: None
    """
    logger.info(str(message.from_user.id))

    command_id['id'] = identifier

    if isinstance(message, CallbackQuery):
        bot.send_sticker(message.from_user.id, config.sticker_go)
        bot.send_message(message.from_user.id, 'Куда едем?')
        price_message = bot.send_message(message.from_user.id, 'Введите название города или первые буквы')
    else:
        logger.info(str(message.from_user.id))
        bot.send_sticker(message.chat.id, config.sticker_go)
        bot.send_message(message.chat.id, 'Куда поедем?')
        price_message = bot.send_message(message.chat.id, 'Введите название города или первые буквы')

    bot.register_next_step_handler(price_message, select_city)


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
        command_help(message)
    else:
        bot.send_message(message.from_user.id, 'Ничего похожего нет, попробуйте еще раз')
        command_help(message)


@exception_handler
def search_city(message: Message) -> None:
    """
    Функция отправляет запрос на поиск городов по введенным буквам, загружает результаты,
    и готовит список городов с destinationId
    :param message: Message
    :return: None
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
        bot.send_message(message.from_user.id, 'Поиск Российских городов временно приостановлен!')
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
def check_bestdeal(call: CallbackQuery) -> None:
    """
    Функция проверяет для какого сценария была вызвана,
    при выполнении условия в сценарий включаются дополнительные функции
    :param call: CallbackQuery
    :return: None
    """
    logger.info(str(call.from_user.id))

    if command_id['id'] == 'bestdeal':
        bestdeal_message = bot.send_message(call.from_user.id, 'Укажите диапазон цен, руб., например 5000-8000: ')
        bot.register_next_step_handler(bestdeal_message, set_price_range)

    else:
        hotel_amount_set(call)


@exception_handler
def set_price_range(message: Message) -> None:
    """
    Функция для сценария bestdeal, задает разбег цен для поиска отеля
    :param message: Message
    :return: None
    """
    logger.info(str(message.from_user.id))
    price_renge = message.text.split('-')
    exchange_rate = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']['Value']
    if len(price_renge) == 2:
        if price_renge[0].isdigit() and price_renge[1].isdigit():
            price_renge[0] = str(round(float(price_renge[0]) / exchange_rate, 2))
            price_renge[1] = str(round(float(price_renge[1]) / exchange_rate, 2))
            if float(price_renge[0]) < float(price_renge[1]):
                query_hotel['priceMin'] = price_renge[0]
                query_hotel['priceMax'] = price_renge[1]
            else:
                query_hotel['priceMin'] = price_renge[1]
                query_hotel['priceMax'] = price_renge[0]
        else:
            logger.error('ошибка ввода данных')
            bot.register_next_step_handler('оба числа должны быть цифрами', check_bestdeal)
    else:
        logger.error('ошибка ввода данных')
        bot.register_next_step_handler('должно быть два числа разделенных "-" без пробелов', check_bestdeal)

    distance_message = bot.send_message(message.from_user.id, 'Введите удаленность от центра в км')
    bot.register_next_step_handler(distance_message, set_distance)


@exception_handler
def set_distance(message: Message) -> None:
    """
    Функция для сценария bestdeal, задает удаленность от центра для поиска отеля,
    возвращает в общий сценарий
    :param message: Message
    :return: None
    """
    logger.info(str(message.from_user.id))
    requested_distance = re.match(r'\d*\.?\d+', message.text.replace(',', '.')).group()
    if requested_distance.isdigit():
        distance['distance_from_center'] = float(requested_distance)
    else:
        logger.error('ошибка ввода данных')
        bot.send_message(message.chat.id, 'число должно быть из цифр')
        repeat_message = bot.send_message(message.from_user.id, 'Введите удаленность от центра в км')
        bot.register_next_step_handler(repeat_message, set_distance)

    bot.send_message(message.from_user.id, 'Выберите, сколько отелей показать:', reply_markup=quantity_keyboard())


@exception_handler
def hotel_amount_set(call: CallbackQuery) -> None:
    """
    Функция запрашивает какое количество отелей выводит по средствам inline-кнопок
    :param call: CallbackQuery
    :return: None
    """
    logger.info(str(call.from_user.id))
    bot.send_message(call.from_user.id, 'Выберите, сколько отелей показать:', reply_markup=quantity_keyboard())


@exception_handler
def photo_necessity(call: CallbackQuery) -> None:
    """
    Функция спрашивает необходимость фото по средствам inline-кнопок
    :param call: CallbackQuery
    :return: None
    """
    logger.info(str(call.from_user.id))
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
    logger.info(str(call.from_user.id))
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text='Выбрано показать {hotels} отелей и {photos} фотографий'.format(
                              hotels=query_hotel['hotel_amount'],
                              photos=query_hotel['photo_amount']
                          ),
                          reply_markup=None)

    bot.send_message(call.from_user.id, 'Подбираю варианты...')
    if query_hotel['photo_amount'] > 0:
        bot.send_message(call.from_user.id, ' и подгружаю фото...')

    if command_id['id'] == 'highprice':
        query_hotel['sortOrder'] = '-PRICE'
    elif command_id['id'] == 'lowprice':
        query_hotel['sortOrder'] = 'PRICE'
    elif command_id['id'] == 'bestdeal':
        query_hotel['sortOrder'] = 'DISTANCE_FROM_LANDMARK'

    query_string = query_hotel.copy()
    del query_string['hotel_amount']
    del query_string['photo_amount']

    try:
        response = requests.request('GET', config.hotel_url, headers=config.hotels_headers, params=query_string)
    except (ConnectionError, TimeoutError, ReadTimeout) as error:
        logger.error('В работе бота возникло исключение', exc_info=error)
        bot.send_message(call.from_user.id,
                         '{}!\n'
                         'Ошибка соединения с сервером, попробуйте позже.'.format(call.from_user.first_name),
                         reply_markup=main_keyboard('/help'))

    request_hotel_data = json.loads(response.text)['data']['body']['searchResults']['results']

    print(query_hotel)
    print(request_hotel_data)

    day_per_stay = datetime.strptime(query_hotel['checkOut'], '%Y-%m-%d') - datetime.strptime(query_hotel['checkIn'],
                                                                                              "%Y-%m-%d")

    if command_id['id'] == 'bestdeal':
        request_hotel_data = sort_bestdeal(request_hotel_data)

    if len(request_hotel_data) < 1:
        logger.info('Поиск не дал результата')
        bot.send_message(call.from_user.id,
                         '{}!\n'
                         'Подходящих отелей нет, попробуйте другие условия.'.format(call.from_user.first_name),
                         reply_markup=main_keyboard('/help'))
    elif len(request_hotel_data) < query_hotel['hotel_amount']:
        query_hotel['hotel_amount'] = len(request_hotel_data)

    hotels.clear()

    for i_hotel in range(query_hotel['hotel_amount']):
        config.hotel_info_reset()
        hotel_info['id'] = request_hotel_data[i_hotel]['id']
        hotel_info['url'] = request_hotel_data[i_hotel]['urls']
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

        hotels.append(copy.deepcopy(hotel_info))

    print(hotels)
    output_hotel(call, hotels)


@exception_handler
def sort_bestdeal(hotel_data: list[dict]) -> list[dict]:
    """
    Функция для сценария bestdeal, убирает из запроса отеле, расположенные от центра дальше чем требуется по запросу
    :param hotel_data: list[dict]
    :return: hotel_data: list[dict]
    """
    for i_elem in range(query_hotel['hotel_amount']):
        i_distance = float(re.search(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?',
                                     hotel_data[i_elem]['landmarks'][0]['distance']).group()) * distance['ratio']
        if i_distance > distance['distance_from_center']:
            return hotel_data

    return hotel_data


@exception_handler
def output_hotel(call: CallbackQuery, request_data: Any) -> None:
    """
    Функция выводи в чате результаты поиска по заданным параметрам
    :param call: CallbackQuery
    :param request_data: Any
    :return: None
    """
    logger.info(str(call.from_user.id))
    exchange_rate = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()['Valute']['USD']['Value']
    in_order = 1
    bot.send_message(call.from_user.id, 'Срок пребывания {night} ночей'.format(night=request_data[0]['night_per_stay']))
    hotels_text_line = ''
    for i_hotel_info in request_data:
        price_rub = i_hotel_info['price'] * exchange_rate
        price_rub = round(price_rub, 2)
        total_rub = i_hotel_info['fully_bundled_price_per_stay'] * exchange_rate
        total_rub = round(total_rub, 2)
        distance_meters = float(re.search(r'(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?',
                                          i_hotel_info['distance_center']).group()) * distance['ratio']
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
        hotels_text_line += i_hotel_info['name'] + '# '

        if query_hotel['photo_amount'] > 0:
            bot.send_message(call.from_user.id, text)
            bot.send_media_group(call.from_user.id, i_hotel_info['photo'])
        else:
            bot.send_message(call.from_user.id, text)

        in_order += 1
        line = '- - - = = = *** = = = - - -'
        bot.send_message(call.from_user.id, line)

    data_now = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    histore_line = str(call.from_user.id) + '# ' + command_id['id'] + '# ' + data_now + '# ' + hotels_text_line + '\n'
    save_history(call, histore_line)
    print(histore_line)

    bot.send_message(call.from_user.id, '-= Поиск завершен =-')


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
@exception_handler
def search_hotel_handler(call: CallbackQuery) -> None:
    """
    Функция-обработчик inline-кнопок с перечнем городов, запускает функцию выбора даты заезда.
    :param call: CallbackQuery
    :return: None
    """
    logger.info(str(call.from_user.id))
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
        photo_necessity(call)
    else:
        query_hotel['photo_amount'] = int(call.data[9:])
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

