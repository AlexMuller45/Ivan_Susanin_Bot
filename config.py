#токен бота
bot_token = '5522049183:AAG8AHjGhfxkpo2s2IhYSI5T3IIT_rrw-8E'

#Hotels API
city_url = 'https://hotels4.p.rapidapi.com/locations/v2/search'

hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'

photo_url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"


hotels_headers = {
    'X-RapidAPI-Key': 'aa78bcbe66msh56c8e06c9bdfbb5p1a25c3jsn9849f53266dd',
    'X-RapidAPI-Host': 'hotels4.p.rapidapi.com'
}

query_city = {
    'query': '',
    'locale': 'ru_RU',
    'currency': 'USD'
}

query_hotel = {
    'destinationId': '',
    'pageNumber': '1',
    'pageSize': '25',
    'checkIn': '',
    'checkOut': '',
    'adults1': '1',
    'sortOrder': 'PRICE',
    'locale': 'en_US',
    'currency': 'USD',
    'hotel_amount': 0,
    'photo_amount': 0
}

query_photo = {
    'id': ''
}


hotel_info = {
    'id': 0000,
    'name': '',
    'address': '',
    'distance_center': '',
    'price': 00.00,
    'fully_bundled_price_per_stay': 00.00,
    'photo_amount': 0,
    'photo': []}


def query_hotel_reset() -> None:
    """
    Функция обнуления данных запроса.
    :return: None
    """
    query_hotel['destinationId'] = ''
    query_hotel['checkIn'] = ''
    query_hotel['checkOut'] = ''
    query_hotel['hotel_amount'] = 0
    query_hotel['photo_amount'] = 0


def hotel_info_reset() -> None:
    """
    Функция обнуления данных.
    :return: None
    """
    hotel_info['id'] = 0000
    hotel_info['name'] = ''
    hotel_info['address'] = ''
    hotel_info['distance_center'] = ''
    hotel_info['price'] = 00.00
    hotel_info['fully_bundled_price_per_stay'] = 0
    hotel_info['photo_amount'] = 0
    hotel_info['photo'].clear()


#стикеры
sticker_welcom = 'CAACAgIAAxkBAAEFtjJjDREuacFYepN2amhbvk_iVqVhOwACVxcAAprXMUovDVqm4UquUykE'
sticker_help = 'CAACAgIAAxkBAAEFtjhjDRqkAZnFVMCjYPiXfr9_tAl-1QACvBYAAkRxEUtIKXB4k2KzECkE'
sticker_go = 'CAACAgIAAxkBAAEFyQ9jGjiizpFVIfk9Joj40ZYnDbSIEAACcRcAAhNGYUoXZ6C6Got-NikE'


#тексты
help_message = 'Доступные функции:\n' \
               '-Low Price- подборка самых дешёвых отелей в городе\n' \
               '-High Price- подборка самых дорогих отелей в городе\n' \
               '-Best Deal- подборка отелей, наиболее подходящих по цене и расположению от центра\n' \
               '-History- вывод истории поиска отелей'


#типы входящих сообщений
all_type = ['text', 'audio', 'document', 'photo', 'sticker', 'video', 'gif',
            'video_note', 'voice', 'location', 'contact', 'pinned_message']


#календарь
LSTEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}
