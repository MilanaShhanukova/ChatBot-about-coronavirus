#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging, requests, datetime, csv, pyowm, classes
from classes import Calculator
from setup import PROXY, TOKEN
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater
from analyze import Statistics
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOG_HISTORY = list()
Location_Aspect = dict()
Options = dict()
Options["Choose_country"] = False
Options["Choose_country_for_search_statistics"] = False
Options["Shift"] = 0
Options["location"] = " "

# Декоратор для логгирования:
def update_log(func):
    def new_func(*argc, **kwargs):
        if argc[0] and hasattr(argc[0], 'message') and hasattr(argc[0], 'effective_user'):
            LOG_HISTORY.append({
                "user" : argc[0].effective_user.first_name,
                "function" : func.__name__,
                "message" : argc[0].message.text,
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
BUTTON11 = "EVRO"
BUTTON12 = "CHOOSE_COUNTRY"
BUTTON13 = "Active"
BUTTON14 = "2_days"
BUTTON15 = "7_days"
BUTTON16 = "14_days"
BUTTON17 = "dynamics"
BUTTON18 = "graf_of_confirmed"
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
def corona__stats_keyboard():
    new_keyboard = [
        [
            InlineKeyboardButton(TITLES[BUTTON1], callback_data=BUTTON1),
            InlineKeyboardButton(TITLES[BUTTON2], callback_data=BUTTON2),
        ],
        [
            InlineKeyboardButton(TITLES[BUTTON12], callback_data=BUTTON12),
        ]
    ]
    return InlineKeyboardMarkup(new_keyboard)


def corona_stats_dynamics_keyboard():
    new_keyboard = [
        [
            InlineKeyboardButton(TITLES[BUTTON14], callback_data=BUTTON14),
        ],
        [
            InlineKeyboardButton(TITLES[BUTTON15], callback_data=BUTTON15),
        ],
        [
            InlineKeyboardButton(TITLES[BUTTON16], callback_data=BUTTON16),
        ]
    ]
    return InlineKeyboardMarkup(new_keyboard)

def detailed_info_about_weather_keyboard():
    new_keyboard = [
        [InlineKeyboardButton(TITLES[BUTTON9], callback_data=BUTTON9)],
    ]
    return InlineKeyboardMarkup(new_keyboard)

def city_keyboard():
    new_keyboard = [
        [InlineKeyboardButton(TITLES[BUTTON6], callback_data=BUTTON6)],
        [InlineKeyboardButton(TITLES[BUTTON7], callback_data=BUTTON7)],
        [InlineKeyboardButton(TITLES[BUTTON8], callback_data=BUTTON8)],
    ]
    return InlineKeyboardMarkup(new_keyboard)

# Клава с выбором местоположения. В списке КАЖДЫЙ СПИСОК - ОДНА СТРОКА клавы. Тут 1 строка

def money_keyboard():
    new_keyboard = [
        [
        InlineKeyboardButton(TITLES[BUTTON10], callback_data=BUTTON10),
        InlineKeyboardButton(TITLES[BUTTON11], callback_data=BUTTON11),
        ]
    ]
    return InlineKeyboardMarkup(new_keyboard)

#клава для просмотра графика
def grafik_keyboard():
    new_keyboard = [
        [
        InlineKeyboardButton(TITLES[BUTTON18], callback_data=BUTTON18),
        ]
    ]
    return InlineKeyboardMarkup(new_keyboard)

# Клава с выбором критерия для вывода. 2 строки ( в списке 2 списка)
def aspect_keyboard():
    new_keyboard = [
        [
            InlineKeyboardButton(TITLES[BUTTON3], callback_data=BUTTON3),
        ],
        [
            InlineKeyboardButton(TITLES[BUTTON13], callback_data=BUTTON13),
        ],
        [
            InlineKeyboardButton(TITLES[BUTTON4], callback_data=BUTTON4),
            InlineKeyboardButton(TITLES[BUTTON5], callback_data=BUTTON5),
        ],
    ]
    return InlineKeyboardMarkup(new_keyboard)

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

@update_log
def check_weather(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text= "Выберете город! 👀",
        reply_markup= city_keyboard(),
    )
@update_log
def money(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    context.bot.send_message(
        chat_id=chat_id,
        text="Выберете валюту!",
        reply_markup=money_keyboard(),
    )

# Когда мы вводим /corono_stats, то эта функция выводит текствовое сообщение с запросом местоположения и клаву.
# Дальше мы попадаем в keyboard_handler, смотреть выше
@update_log
def corona_stats(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    text = "Выберете местоположения вируса COVID-19 😈"
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=corona__stats_keyboard(),
    )

@update_log
def corona_stats_dynamics(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    text = "Динамика распространения вируса 🦠 за последние"
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=corona_stats_dynamics_keyboard(),
    )

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
           "Введите команду /corona_stats_dynamics, чтобы увидеть динамику распространения вируса."
           ]
    update.message.reply_text('\n'.join(tmp))

def to_fixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

@update_log
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    if not (Options["Choose_country"] or Options["Choose_country_for_search_statistics"]):
        chat_id = update.message.chat_id
        text = update.message.text
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
        )
    elif Options["Choose_country"] or Options["Choose_country_for_search_statistics"]:
        new_places = Calculator.get_dynamics_info(target_country=update.message.text, shift_date=0)
        if not new_places:
            chat_id = update.message.chat_id
            context.bot.send_message(
                chat_id=chat_id,
                text="Введите корректное название страны 😟",
            )
            return
        for row in new_places:
            if row[0] == update.message.text and Options["Choose_country"]:
                chat_id = update.message.chat_id
                context.bot.send_message(
                    chat_id=chat_id,
                    text=f"Confirmed: {row[1]} 😷🤒\nDeaths: {row[2]} 😵\nRecovered: {row[3]} 😇\nActive: {row[4]} 🤒"
                )
                break
            elif row[0] == update.message.text and Options["Choose_country_for_search_statistics"]:
                new_places_after_shift = Calculator.get_dynamics_info(target_country=update.message.text, shift_date=Options["Shift"])
                Options["location"] = row[0]
                for target_row in new_places_after_shift:
                    if target_row[0] == update.message.text:
                        chat_id = update.message.chat_id
                        value_1 = (row[1] - target_row[1]) / target_row[1] * 100 if target_row[1] else 0
                        value_2 = (row[2] - target_row[2]) / target_row[2] * 100 if target_row[2] else 0
                        value_3 = (row[3] - target_row[3]) / target_row[3] * 100 if target_row[3] else 0
                        value_4 = (row[4] - target_row[4]) / target_row[4] * 100 if target_row[4] else 0
                        growth = {
                            "Confirmed_growth": value_1,
                            "Death_growth": value_2,
                            "Recovered_growth": value_3,
                            "Active_growth": value_4,
                        }
                        for key in growth.keys():
                            if growth[key] > 0:
                                growth[key] = '+' + to_fixed(abs(growth[key]), 2) + ' % ' + '↗'
                            else:
                                growth[key] = '-' + to_fixed(abs(growth[key]), 2) + ' % ' + '↘'
                        context.bot.send_message(
                            chat_id=chat_id,
                            text=(f"Confirmed increase🤒: {row[1] - target_row[1]}, {growth['Confirmed_growth']}\n"
                                  f"Death increase         😵: {row[2] - target_row[2]}, {growth['Death_growth']}\n"
                                  f"Recovered increase😇: {row[3] - target_row[3]}, {growth['Recovered_growth']}\n"
                                  f"Active increase         😷: {row[4] - target_row[4]}, {growth['Active_growth']}"),
                            reply_markup=grafik_keyboard(),)
                        break
        Options["Choose_country"] = False
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
                print(str(i), str(period))
                break
    update.message.reply_text(f"Прошло {period.seconds // 3600} часов, {(period.seconds % 3600) // 60} минут, {(period.seconds % 3600) % 60} секунд с последнего вашего сообщения.")

@update_log
def date(update: Updater, context: CallbackContext):
    now = datetime.datetime.now()
    update.message.reply_text(f"Дата: {now.day}.{now.month}.{now.year}\nВремя: {now.hour}:{now.minute}")

@update_log
def fact(update: Updater, context: CallbackContext):
    r = requests.get("https://cat-fact.herokuapp.com/facts")
    p = r.json()
    all_posts = p["all"]
    all_votes = [all_posts[i]["upvotes"] for i in range(len(all_posts) - 1)]
    update.message.reply_text(f"Самый залайканный пост это { all_posts[all_votes.index(max(all_votes))]['text']}")


@update_log
def history(update: Updater, context: CallbackContext):
    I_start, end = 0, 0
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
                I_start, end = len(LOG_HISTORY) - 5, len(LOG_HISTORY)
                answer.append("Last five actions are:")
            for i in range(I_start, end):
                answer.append(f"Action {i + 1}:")
                for key, value in LOG_HISTORY[i].items():
                    answer.append(key + " : " + str(value))
                answer[len(answer) - 1] += '\n'
            update.message.reply_text('\n'.join(answer))
            handle.write('\n'.join(answer) + '\n')

# Необходимые функции для команды /corono_stats

# Необходимая функция для команды /know_money
def get_money(name):
    my_xml = requests.get("https://www.cbr-xml-daily.ru/daily_json.js").json()
    countries = my_xml["Valute"]
    answer = ""
    for country in countries.keys():
        all_feat = countries[country] #словарик всех данных о валюте
        if all_feat['Name'] == name[:-2]:
            answer = f"Стоимость {all_feat['Name']} сейчас {all_feat['Value']} ₽"
    return answer

# Обработчик клавиатуры. Тут происходит вся логика после нажатий на клавиши:
def keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    if data == BUTTON1 or data == BUTTON2:
        text = {BUTTON1: "Выберете критерий, по которому будет показан топ 5 провиниций/штатов с необходимой информацией!",
                BUTTON2: "Выберете критерий, по которому будет показано топ 5 стран/регионов с необходимой информацией!"}
        Location_Aspect["location"] = data
        context.bot.send_message(
            chat_id=chat_id,
            text=text[data],
            reply_markup=aspect_keyboard(),
        )
    elif data == BUTTON3 or data == BUTTON4 or data == BUTTON5 or data == BUTTON13:
        smile = { BUTTON3: '😷🤒', BUTTON4: '😵', BUTTON5: '😇', BUTTON13: '🤒'}
        Location_Aspect["aspect"] = data
        answer = Calculator.download_actual_file(0)
        answer.append(Location_Aspect["aspect"] + ':' + smile[data])
        Calculator.get_necessary_corona_info(Location_Aspect["location"], Location_Aspect["aspect"], answer)
        context.bot.send_message(
            chat_id=chat_id,
            text='\n'.join(answer),
        )
    elif data == BUTTON6 or data == BUTTON7 or data == BUTTON8:
        place = TITLES[data]
        Location_Aspect["CURRENT_CITY"] = place
        owm = pyowm.OWM('6d00d1d4e704068d70191bad2673e0cc', language="ru")
        observation = owm.weather_at_place(place)
        w = observation.get_weather()
        status = w.get_detailed_status()
        temp = w.get_temperature('celsius')
        answer = "В городе " + place + " сейчас " + status
        if status == "ясно":
            answer += "☀\n"
        elif status == "облачно":
            answer += "☁\n"
        elif status == "дождливо":
            answer += "🌧\n"
        else:
            answer += "\n"
        if temp["temp"] <= 0:
            answer += "Сейчас очень холодно! Одевайся как танк!! 🥶\n"
        elif temp["temp"] < 16:
            answer += "Сейчас прохладно, лучше оденься потеплее! 👍\n"
        else:
            answer += "Температура в самый раз! Одевайся, как хочешь! 😊\n"
        context.bot.send_message(
            chat_id=chat_id,
            text=answer,
            reply_markup=detailed_info_about_weather_keyboard(),
        )
    elif data == BUTTON9:
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
            text=answer,
        )
    elif data == BUTTON10:
        context.bot.send_message(
            chat_id=chat_id,
            text=get_money(TITLES[data]),
        )
    elif data == BUTTON11:
        context.bot.send_message(
            chat_id=chat_id,
            text=get_money(TITLES[data]),
        )
    elif data == BUTTON12:
        Options["Choose_country"] = True
    elif data == BUTTON14 or data == BUTTON15 or data == BUTTON16:
        context.bot.send_message(
            chat_id=chat_id,
            text="Введите название страны",
        )
        Options["Shift"] = int(data[:data.find("_")]) + 1
        Options["Choose_country_for_search_statistics"] = True
    elif data == BUTTON18:
        print(Options["location"])
        Statistics.grafik_draw(Options["Shift"], Options["location"])
        context.bot.send_photo(
            chat_id=chat_id,
            photo=open("grafik.png", "rb")
        )


# Создание бота, объявление обработчиков, запуск бота:
def main():
    bot = Bot(
        token=TOKEN,
        base_url=PROXY,  # delete it if connection via VPN
    )
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
    updater.dispatcher.add_handler(CommandHandler('corona_stats_dynamics', corona_stats_dynamics))
    updater.dispatcher.add_handler(CommandHandler('check_exchange_rates', money))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback=keyboard_handler, pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
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