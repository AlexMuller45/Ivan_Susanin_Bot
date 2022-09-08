#токен бота
bot_token = '5522049183:AAG8AHjGhfxkpo2s2IhYSI5T3IIT_rrw-8E'

#Hotels API
city_url = 'https://hotels4.p.rapidapi.com/locations/v2/search'

hotel_url = 'https://hotels4.p.rapidapi.com/properties/list'

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
    'hotel_amount': '',
    'photo_amount': ''}


def query_hotel_rest() -> None:
    """
    Функция обнуления данных запроса.
    :return: None
    """
    query_hotel['destinationId'] = ''
    query_hotel['checkIn'] = ''
    query_hotel['checkOut'] = ''
    query_hotel['hotel_amount'] = ''
    query_hotel['photo_amount'] = ''


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
