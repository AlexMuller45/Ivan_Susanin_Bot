Итогового проект.
Тема:
    Telegram-бот для анализа сайта Hotels.com и поиска подходящих пользователю отелей

Проект состоит из скрипта main.py и Telegram-бота https://t.me/forgettrip_bot
Пользователь с помощью специальных команд бота может выполнить следующие
действия (получить следующую информацию):
- Узнать топ самых дешёвых отелей в городе (команда /lowprice).
- Узнать топ самых дорогих отелей в городе (команда /highprice).
- Узнать топ отелей, наиболее подходящих по цене и расположению от центра
  (самые дешёвые и находятся ближе всего к центру) (команда /bestdeal).
- Узнать историю поиска отелей (команда /history).

##Описание работы команд##

##Команда /lowprice##
После ввода команды у пользователя запрашивается:
1 Город, где будет проводиться поиск.
2 Количество отелей, которые необходимо вывести в результате (не больше
  заранее определённого максимума).
3 Необходимость загрузки и вывода фотографий для каждого отеля («Да/Нет»):
    a. При положительном ответе пользователь также вводит количество
    необходимых фотографий (не больше заранее определённого
    максимума).

##Команда /highprice##
После ввода команды у пользователя запрашивается:
1 Город, где будет проводиться поиск.
2 Количество отелей, которые необходимо вывести в результате (не больше
  заранее определённого максимума).
3 Необходимость загрузки и вывода фотографий для каждого отеля («Да/Нет»):
    a. При положительном ответе пользователь также вводит количество
    необходимых фотографий (не больше заранее определённого максимума).

##Команда /bestdeal##
После ввода команды у пользователя запрашивается:
1 Город, где будет проводиться поиск.
2 Диапазон цен.
3 Диапазон расстояния, на котором находится отель от центра.
4 Количество отелей, которые необходимо вывести в результате (не больше заранее определённого максимума).
5 Необходимость загрузки и вывода фотографий для каждого отеля («Да/Нет»):
    a. При положительном ответе пользователь также вводит количество
    необходимых фотографий (не больше заранее определённого максимума).

##Команда /history##
После ввода команды пользователю выводится история поиска отелей. Сама история
содержит:
1 Команду, которую вводил пользователь.
2 Дату и время ввода команды.
3 Отели, которые были найдены.

##Описание внешнего вида и UI##
Окно Telegram-бота, который при запущенном Python-скрипте должен уметь
воспринимать следующие команды:
    /help — помощь по командам бота
    /lowprice — вывод самых дешёвых отелей в городе
    /highprice — вывод самых дорогих отелей в городе
    /bestdeal — вывод отелей, наиболее подходящих по цене и расположению от центра,
    /history — вывод истории поиска отелей.