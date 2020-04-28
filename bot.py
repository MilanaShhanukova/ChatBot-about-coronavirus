#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import requests
import csv
import logging
import datetime
import pyowm
import corona_parser
from parser_corona_data import Parser_CoronaVirus
from setup import PROXY, TOKEN
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from analyze import Statistics

# import corona_parser
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOG_HISTORY = list()
Location_Aspect = dict()
Options = dict()
Options["Choose_country"] = False
Options["Choose_country_for_search_statistics"] = False
Options["Corona_stats_in_russia"] = False
Options["Shift"] = 0
Options["location"] = " "


# Декоратор для логгирования
def update_log(func):
    def new_func(*argc, **kwargs):
        if argc[0] and hasattr(argc[0], 'message') and hasattr(argc[0], 'effective_user'):
            LOG_HISTORY.append({
                "user": argc[0].effective_user.first_name,
                "function": func.__name__,
                "message": argc[0].message.text,
                "date": argc[0].message.date,
            })
        return func(*argc, **kwargs)

    return new_func


# Идентификаторы
BUTTON1 = "Province_State"
BUTTON2 = "Country_Region"
BUTTON3 = "Confirmed"
BUTTON4 = "Deaths"
BUTTON5 = "Recovered"
BUTTON6 = "CITY1"
BUTTON7 = "CITY2"
BUTTON8 = "CITY3"
BUTTON9 = "DETAILED_INFO_ABOUT_WEATHER"
BUTTON10 = "DOLLAR"
BUTTON11 = "EURO"
BUTTON12 = "CHOOSE_COUNTRY"
BUTTON13 = "Active"
BUTTON14 = "2_days"
BUTTON15 = "7_days"
BUTTON16 = "14_days"
BUTTON17 = "dynamics"
BUTTON18 = "graph_of_confirmed"

# Информация в кнопках
TITLES = {
    BUTTON1: "Провинция/Штат",
    BUTTON2: "Страна/Регион",
    BUTTON3: "Подтвержденные случаи",
    BUTTON4: "Умерло",
    BUTTON5: "Выздоровело",
    BUTTON6: "Нижний Новгород",
    BUTTON7: "Москва",
    BUTTON8: "Санкт-Петербург",
    BUTTON9: "▶ Узнать подробную информацию о погоде на сегодня ◀",
    BUTTON10: "Доллар США ＄",
    BUTTON11: "Евро €",
    BUTTON12: "▶ Ввести название страны ◀",
    BUTTON13: "Зараженные на данный момент",
    BUTTON14: "2 дня",
    BUTTON15: "7 дней",
    BUTTON16: "14 дней",
    BUTTON17: "Отследить динамику распространения вируса",
    BUTTON18: "Посмотреть график подтвержденных случаев"
}


# Клавиатуры:
def corona_stats_keyboard():
    new_keyboard = [[InlineKeyboardButton(TITLES[BUTTON1], callback_data=BUTTON1),
                     InlineKeyboardButton(TITLES[BUTTON2], callback_data=BUTTON2)],
                    [InlineKeyboardButton(TITLES[BUTTON12], callback_data=BUTTON12)]]
    return InlineKeyboardMarkup(new_keyboard)


def corona_stats_dynamics_keyboard():
    new_keyboard = [[InlineKeyboardButton(TITLES[BUTTON14], callback_data=BUTTON14)],
                    [InlineKeyboardButton(TITLES[BUTTON15], callback_data=BUTTON15)],
                    [InlineKeyboardButton(TITLES[BUTTON16], callback_data=BUTTON16)]]
    return InlineKeyboardMarkup(new_keyboard)


def detailed_info_about_weather_keyboard():
    new_keyboard = [[InlineKeyboardButton(TITLES[BUTTON9], callback_data=BUTTON9)]]
    return InlineKeyboardMarkup(new_keyboard)


def city_keyboard():
    new_keyboard = [[InlineKeyboardButton(TITLES[BUTTON6], callback_data=BUTTON6)],
                    [InlineKeyboardButton(TITLES[BUTTON7], callback_data=BUTTON7)],
                    [InlineKeyboardButton(TITLES[BUTTON8], callback_data=BUTTON8)]]
    return InlineKeyboardMarkup(new_keyboard)


# Клавиатура с выбором местоположения. В списке КАЖДЫЙ СПИСОК - ОДНА СТРОКА клавиатуры
def money_keyboard():
    new_keyboard = [[InlineKeyboardButton(TITLES[BUTTON10], callback_data=BUTTON10),
                     InlineKeyboardButton(TITLES[BUTTON11], callback_data=BUTTON11)]]
    return InlineKeyboardMarkup(new_keyboard)


# Клавиатура для просмотра графика
def graphic_keyboard():
    new_keyboard = [[InlineKeyboardButton(TITLES[BUTTON18], callback_data=BUTTON18)]]
    return InlineKeyboardMarkup(new_keyboard)


# Клавиатура с выбором критерия для вывода
def aspect_keyboard():
    new_keyboard = [[InlineKeyboardButton(TITLES[BUTTON3], callback_data=BUTTON3)],
                    [InlineKeyboardButton(TITLES[BUTTON13], callback_data=BUTTON13)],
                    [InlineKeyboardButton(TITLES[BUTTON4], callback_data=BUTTON4),
                     InlineKeyboardButton(TITLES[BUTTON5], callback_data=BUTTON5)]]
    return InlineKeyboardMarkup(new_keyboard)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
@update_log
def check_weather(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text="Выберете город! 👀",
        reply_markup=city_keyboard())


@update_log
def money(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text="Выберете валюту!",
        reply_markup=money_keyboard())


# Когда мы вводим /corona_stats, то эта функция выводит текствовое сообщение с запросом местоположения и клавиатуру
# Далее мы попадаем в keyboard_handler
@update_log
def corona_stats(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    text = "Выберете местоположения вируса COVID-19 😈"
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=corona_stats_keyboard())


@update_log
def corona_stats_in_russia(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    text = "Введите название субъекта РФ для получения текущей информации о вирусе\n (Субъект РФ - республика, край, \
        область, город федерального значения, автономный округ)"
    Options["Corona_stats_in_russia"] = True
    context.bot.send_message(
        chat_id=chat_id,
        text=text)
    corona_parser.parse()


@update_log
def corona_stats_dynamics(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    text = "Динамика распространения вируса 🦠 за последние"
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=corona_stats_dynamics_keyboard())


@update_log
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    smile = u'\U0001F603'
    update.message.reply_text(f"Привет, {update.effective_user.first_name} {smile}!")


@update_log
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    tmp = ["Введи команду /start для начала.",
           "Введите команду /history, чтобы увидеть последние 5 действий.",
           "Введите команду /time, чтобы увидеть время, прошедшее с последнего вашего сообщения.",
           "Введите команду /date, чтобы увидеть текущую дату и время.",
           "Введите команду /fact, чтобы увидеть самый залайканный пост на cat-fact.herokuapp.com",
           "Введите команду /weather, чтобы проверить погоду.",
           "Введите команду /check_exchange_rates, чтобы курс валют.",
           "Введите команду /corona_stats, чтобы увидеть актуальную статистику по короновирусу.",
           "Введите команду /corona_stats_in_russia, чтобы увидеть текущую информацию о короновирусе в России.",
           "Введите команду /corona_stats_dynamics, чтобы увидеть динамику распространения вируса."]
    update.message.reply_text('\n'.join(tmp))


def to_fixed(value: int, digits=0):
    return f"{value:.{digits}f}"


@update_log
def echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    if not (Options["Choose_country"] or Options["Choose_country_for_search_statistics"] or
            Options["Corona_stats_in_russia"]):
        text = update.message.text
        context.bot.send_message(
            chat_id=chat_id,
            text=text)
    elif Options["Corona_stats_in_russia"]:
        location = update.message.text
        with open("russian_data.csv", 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Регион"] == location:
                    context.bot.send_message(
                        chat_id=chat_id,
                        text=f'Регион: {row["Регион"]}\nЗаражено: {row["Заражено"]} \
                            🤒\nВылечено: {row["Вылечено"]} 😇\nПогибло: {row["Погибло"]} 😵')
                    Options["Corona_stats_in_russia"] = False
                    return
            context.bot.send_message(
                chat_id=chat_id,
                text="Введите корректное название города или области 😟")
    elif Options["Choose_country"] or Options["Choose_country_for_search_statistics"]:
        chat_id = update.message.chat_id
        parser = Parser_CoronaVirus()
        data = parser.get_dynamics_info(target_country=update.message.text)
        if not data:
            context.bot.send_message(
                chat_id=chat_id,
                text="Введите корректное название страны 😟")
            return
        # Для корона статс
        if Options["Choose_country"]:
            context.bot.send_message(
                chat_id=chat_id,
                text=f"Confirmed: {data['Confirmed']} 😷🤒\nDeaths: {data['Deaths']} 😵\nRecovered: {data['Recovered']} 😇\nActive: {data['Active']} 🤒")
            Options["Choose_country"] = False
        # Для корона динамикс
        else:
            parser.shift_date = Options["Shift"]
            old_data = parser.get_dynamics_info(target_country=update.message.text)
            growth = {
                "Confirmed_growth": (data["Confirmed"] - old_data["Confirmed"]) / old_data["Confirmed"] * 100,
                "Death_growth": (data["Deaths"] - old_data["Deaths"]) / old_data["Deaths"] * 100,
                "Recovered_growth": (data["Recovered"] - old_data["Recovered"]) / old_data["Recovered"] * 100,
                "Active_growth": (data["Active"] - old_data["Active"]) / old_data["Active"] * 100}
            for key in growth.keys():
                if growth[key] > 0:
                    growth[key] = '+' + to_fixed(abs(growth[key]), 2) + ' % ' + '↗'
                else:
                    growth[key] = '-' + to_fixed(abs(growth[key]), 2) + ' % ' + '↘'
            context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"Confirmed increase🤒: {data['Confirmed'] - old_data['Confirmed']}, {growth['Confirmed_growth']}\n"
                    f"Death increase         😵: {data['Deaths'] - old_data['Deaths']}, {growth['Death_growth']}\n"
                    f"Recovered increase😇: {data['Recovered'] - old_data['Recovered']}, {growth['Recovered_growth']}\n"
                    f"Active increase         😷: {data['Active'] - old_data['Active']}, {growth['Active_growth']}"),
                reply_markup=graphic_keyboard())
            Options["Choose_country_for_search_statistics"] = False
        return


@update_log
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')


@update_log
def elapsed_time(update: Updater, context: CallbackContext):
    user = update.effective_user.first_name
    period = datetime.timedelta(0)
    if len(LOG_HISTORY) > 1:
        for i in range(len(LOG_HISTORY) - 2, -1, -1):
            if LOG_HISTORY[i]["user"] == user:
                time_delta = datetime.timedelta(hours=3, minutes=0, seconds=0)
                period = LOG_HISTORY[i]["date"] + time_delta
                period = datetime.datetime.now() - period
                break
    update.message.reply_text(f"Прошло {period.seconds // 3600} часов, {(period.seconds % 3600) // 60} \
        минут, {(period.seconds % 3600) % 60} секунд с последнего вашего сообщения.")


@update_log
def date(update: Updater, context: CallbackContext):
    now = datetime.datetime.now()
    update.message.reply_text(f"Дата: {now.day}.{now.month}.{now.year}\nВремя: {now.hour}:{now.minute}")


def get_data_with_url(url: str):
    try:
        req = requests.get(url)
        if req.ok:  # проверка на успешное
            return req.json()
    except Exception as err:
        print(f'Error occurred: {err}')


def fact(url="URL"):
    data = get_data_with_url(url)
    if data is None:
        return "We don't see cats, so cannot find the cutest("
    all_posts = data["all"]
    max_upvotes = 0
    max_posts = []
    for post in all_posts:
        if post['upvotes'] >= max_upvotes:
            max_upvotes = post['upvotes']
            max_posts.append(post["text"])

    if max_posts == [] or max_upvotes == 0:
        return "It's impossible to find the most upvoted post, all are cute!"
    return f"Самый залайканный пост это {', '.join(max_posts)}"


@update_log
def send_cat_fact(update: Updater, context: CallbackContext):
    cat_post = fact("https://cat-fact.herokuapp.com/facts")
    update.message.reply_text(cat_post)


@update_log
def history(update: Updater, context: CallbackContext):
    i_start, end = 0, 0
    with open("history.txt", 'a') as handle:
        if len(LOG_HISTORY) == 1 and LOG_HISTORY[0]["function"] == "history":
            update.message.reply_text("There are no recent actions")
            handle.write("There are no recent actions\n")
        else:
            answer = []
            if len(LOG_HISTORY) < 5:
                end = len(LOG_HISTORY)
                answer.append("Last actions are:")
            else:
                i_start, end = len(LOG_HISTORY) - 5, len(LOG_HISTORY)
                answer.append("Last five actions are:")
            for i in range(i_start, end):
                answer.append(f"Action {i + 1}:")
                for key, value in LOG_HISTORY[i].items():
                    answer.append(key + " : " + str(value))
                answer[len(answer) - 1] += '\n'
            update.message.reply_text('\n'.join(answer))
            handle.write('\n'.join(answer) + '\n')


# Необходимая функция для команды /check_exchange_rates
def get_money(name):
    my_xml = get_data_with_url("https://www.cbr-xml-daily.ru/daily_json.js")
    countries = my_xml["Valute"]
    answer = None
    for country, currency in countries.items():
        if currency['Name'] == name[:-2] and currency["Value"] != 0:
            answer = f"Стоимость {currency['Name']} сейчас {currency['Value']} ₽"
            return answer

    if answer is None:
        return "Не было найдено информации по данной валюте"


# Обработчик клавиатуры. Тут происходит вся логика после нажатий на клавиши:
def keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    if data in (BUTTON1, BUTTON2):
        text = {
            BUTTON1: "Выберете критерий, по которому будет показан топ 5 провиниций/штатов с необходимой информацией!",
            BUTTON2: "Выберете критерий, по которому будет показано топ 5 стран/регионов с необходимой информацией!"}
        Location_Aspect["location"] = data
        context.bot.send_message(
            chat_id=chat_id,
            text=text[data],
            reply_markup=aspect_keyboard())
    elif data in (BUTTON3, BUTTON4, BUTTON5, BUTTON13):
        smile = {BUTTON3: '😷🤒', BUTTON4: '😵', BUTTON5: '😇', BUTTON13: '🤒'}
        Location_Aspect["aspect"] = data
        parser = Parser_CoronaVirus()
        parser.write_data_corona()
        parser.answer.append(Location_Aspect["aspect"] + ' ' + smile[data])
        parser.find_top_five(Location_Aspect["location"], Location_Aspect["aspect"])
        context.bot.send_message(
            chat_id=chat_id,
            text='\n'.join(parser.answer))
    elif data in (BUTTON6, BUTTON7, BUTTON8):
        place = TITLES[data]
        Location_Aspect["CURRENT_CITY"] = place
        owm = pyowm.OWM('6d00d1d4e704068d70191bad2673e0cc', language="ru")
        observation = owm.weather_at_place(place)
        w = observation.get_weather()
        status = w.get_detailed_status()
        temp = w.get_temperature('celsius')
        kinds_of_weather = {"ясно": "☀\n", "облачно": "☁\n", "дождливо": "🌧\n", "other": "\n"}
        if status not in kinds_of_weather.keys():
            kind_of_weather = kinds_of_weather["other"]
        else:
            kind_of_weather = kinds_of_weather[status]
        answer = "В городе " + place + " сейчас " + status + kind_of_weather
        if temp["temp"] <= 0:
            answer += "Сейчас очень холодно! Одевайся как танк!! 🥶\n"
        elif temp["temp"] < 16:
            answer += "Сейчас прохладно, лучше оденься потеплее! 👍\n"
        else:
            answer += "Температура в самый раз! Одевайся, как хочешь! 😊\n"
        context.bot.send_message(
            chat_id=chat_id,
            text=answer,
            reply_markup=detailed_info_about_weather_keyboard())
    elif data in BUTTON9:
        owm = pyowm.OWM('6d00d1d4e704068d70191bad2673e0cc', language="ru")
        observation = owm.weather_at_place(Location_Aspect["CURRENT_CITY"])
        w = observation.get_weather()
        status = w.get_detailed_status()
        temp = w.get_temperature('celsius')
        sunrise = w.get_sunrise_time('iso')
        sunset = w.get_sunset_time('iso')
        sunrise = sunrise[sunrise.find(" "): sunrise.find("+")]
        sunset = sunset[sunset.find(" "): sunset.find("+")]
        shift = int(sunrise[:sunrise.find(":")]) + 3
        if shift < 10:
            sunrise = '0' + str(shift) + sunrise[sunrise.find(":"):]
        else:
            sunrise = str(shift) + sunrise[sunrise.find(":"):]
        shift = int(sunset[:sunset.find(":")]) + 3
        if shift < 10:
            sunset = '0' + str(shift) + sunset[sunset.find(":"):]
        else:
            sunset = str(shift) + sunset[sunset.find(":"):]
        answer = "Сегодня: \n"
        answer += "✅ В городе " + Location_Aspect["CURRENT_CITY"] + " сейчас " + status + '\n'
        answer += "✅ Максимальная температура: " + str(temp["temp_max"]) + ' градусов \n'
        answer += "✅ Средняя температура: " + str(temp["temp"]) + ' градусов \n'
        answer += "✅ Минимальная температура: " + str(temp["temp_min"]) + ' градусов \n'
        answer += "✅ Скорость ветра: " + str(w.get_wind()['speed']) + ' м/с \n'
        answer += "✅ Влажность воздуха: " + str(w.get_humidity()) + ' % \n'
        answer += "✅ Давление: " + str(round(w.get_pressure()['press'] * 100 * 0.00750063755419211)) + ' мм.рт.ст\n'
        answer += "✅ Время рассвета: " + sunrise + ' \n'
        answer += "✅ Время заката: " + sunset + ' \n'
        context.bot.send_message(
            chat_id=chat_id,
            text=answer)
    elif data in BUTTON10:
        context.bot.send_message(
            chat_id=chat_id,
            text=get_money(TITLES[data]))
    elif data in BUTTON11:
        context.bot.send_message(
            chat_id=chat_id,
            text=get_money(TITLES[data]))
    elif data in BUTTON12:
        Options["Choose_country"] = True
    elif data == BUTTON14 or data == BUTTON15 or data == BUTTON16:
        context.bot.send_message(
            chat_id=chat_id,
            text="Введите название страны")
        Options["Shift"] = int(data[:data.find("_")]) + 1
        Options["Choose_country_for_search_statistics"] = True
    elif data in BUTTON18:
        print(Options["location"])
        Statistics.graphic_draw(Options["Shift"], Options["location"])
        context.bot.send_photo(
            chat_id=chat_id,
            photo=open("graphic.png", "rb"))


# Создание бота, объявление обработчиков, запуск бота:
def main():
    bot = Bot(
        token=TOKEN,
        base_url=PROXY)  # delete it if connection via VPN
    updater = Updater(bot=bot, use_context=True)

    # on different commands - answer in Telegram
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('help', chat_help))
    updater.dispatcher.add_handler(CommandHandler('history', history))
    updater.dispatcher.add_handler(CommandHandler('time', elapsed_time))
    updater.dispatcher.add_handler(CommandHandler('date', date))
    updater.dispatcher.add_handler(CommandHandler('fact', fact))
    updater.dispatcher.add_handler(CommandHandler('weather', check_weather))
    updater.dispatcher.add_handler(CommandHandler('corona_stats', corona_stats))
    updater.dispatcher.add_handler(CommandHandler('corona_stats_in_russia', corona_stats_in_russia))
    updater.dispatcher.add_handler(CommandHandler('corona_stats_dynamics', corona_stats_dynamics))
    updater.dispatcher.add_handler(CommandHandler('check_exchange_rates', money))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback=keyboard_handler, pass_chat_data=True))

    # on non-command i.e message - echo the message on Telegram
    updater.dispatcher.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    logger.info('Start Bot')
    main()