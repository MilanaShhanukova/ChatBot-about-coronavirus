#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import requests
import datetime
import csv
import urllib

from setup import PROXY, TOKEN
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOG_HISTORY = list()
Location_Aspect = dict()

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
BUTTON1 = "LOCATION_BUTTON_LEFT"
BUTTON2 = "LOCATION_BUTTON_RIGHT"
BUTTON3 = "ASPECT_BUTTON_TOP"
BUTTON4 = "ASPECT_BUTTON_LEFT"
BUTTON5 = "ASPECT_BUTTON_RIGHT"
# Информация в кнопках
TITLES = {
    BUTTON1: "Провинция/Штат",
    BUTTON2: "Страна/Регион",
    BUTTON3: "Подтвержденные случаи",
    BUTTON4: "Умерло",
    BUTTON5: "Выздоровело",
}
# Клава с выбором местоположения. В списке КАЖДЫЙ СПИСОК - ОДНА СТРОКА клавы. Тут 1 строка
def location_keyboard():
    new_keyboard = [
        [
        InlineKeyboardButton(TITLES[BUTTON1], callback_data=BUTTON1),
        InlineKeyboardButton(TITLES[BUTTON2], callback_data=BUTTON2),
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
            InlineKeyboardButton(TITLES[BUTTON4], callback_data=BUTTON4),
            InlineKeyboardButton(TITLES[BUTTON5], callback_data=BUTTON5),
        ]
    ]
    return InlineKeyboardMarkup(new_keyboard)

# Скачиваем последний возможный файл с гитхаба и возвращаем часть ответного сообщения
def download_actual_file():
    answer = list()
    now = datetime.datetime.today()
    now = now.strftime("%m/%d/%Y")
    now = now.split('/')
    link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{now[0]}-{now[1]}-{now[2]}.csv"
    r = requests.get(link)
    if r.status_code == 200:
        answer.append("Информация о вирусе на сегодня:")
    # If there isn't information today, we will take the information for yesterday
    else:
        while not r.status_code == 200:
            now[1] = int(now[1])
            if now[1] <= 10:
                now[1] = '0' + str(now[1] - 1)
            else:
                now[1] = str(now[1] - 1)
            link = f"https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{now[0]}-{now[1]}-{now[2]}.csv"
            r = requests.get(link)
        answer.append(f"Информация на сегодня пока нет. Последние данные на {'/'.join(now)} о вирусе:")

    # Downloading current file
    with open("current_info.csv", 'w') as csvfile:
        csvfile.writelines(r.text)
    return answer

# Получив местоположение и критерий, втаскиваем нужную информацию в ответное сообщение answer через буферный словарь Provinces
def get_necessary_corona_info(location: str, aspect: str, answer: list):
    # Getting information
    with open("current_info.csv", 'r') as csvfile:
        Provinces = dict()
        reader = csv.DictReader(csvfile)
        # Append number of infected people in provinces
        for row in reader:
            if row[location]:
                Provinces[row[location]] = row[aspect]
                if len(Provinces) == 5:
                    break
        #Creating an answer
        for key in Provinces.keys():
            answer.append(key + ' : ' + Provinces[key])
# Вся логика нажатий. При нажатие на первой клаве срабатывает первая ветка IF , вторая клава - ветка ELSE
# Запоминаем location и aspect в глобальный дикт Location_Aspect Так, как при нажатие на первой клавиатуру все обновится,
# И данные в локальных переменных умрут) В конце добавляем смайлик, вызываем get_necessary_corona_info и приводим answer
# К красивому виду, добавив \n
def keyboard_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    chat_id = update.effective_message.chat_id
    if data == BUTTON1 or data == BUTTON2:
        text = ""
        if data == BUTTON1:
            Location_Aspect["location"] = "Province/State"
            text = "Выберете критерий, по которому будет показан топ 5 провиниций/штатов с необходимой информацией!"
        elif data == BUTTON2:
            Location_Aspect["location"] = "Country/Region"
            text = "Выберете критерий, по которому будет показано топ 5 стран/регионов с необходимой информацией!"
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=aspect_keyboard(),
        )
    else:
        smile = ""
        if data == BUTTON3:
            Location_Aspect["aspect"] = "Confirmed"
            smile = u'\U0001F637'
        elif data == BUTTON4:
            Location_Aspect["aspect"] = "Deaths"
            smile = u'\U0001F635'
        elif data == BUTTON5:
            Location_Aspect["aspect"] = "Recovered"
            smile = u'\U0001F607'
        answer = download_actual_file()
        answer.append(Location_Aspect["aspect"] + ':' + smile)
        get_necessary_corona_info(Location_Aspect["location"], Location_Aspect["aspect"], answer)
        context.bot.send_message(
            chat_id=chat_id,
            text='\n'.join(answer),
        )

    # Define a few command handlers. These usually take the two arguments update and
    # context. Error handlers also receive the raised TelegramError object in error.
# Когда мы вводим /corono_stats, то эта функция выводит текствовое сообщение с запросом местоположения и клаву.
# Дальше мы попадаем в keyboard_handler, смотреть выше
def corono_stats(update: Updater, context: CallbackContext):
    chat_id = update.message.chat_id
    smile = u'\U0001F608'
    text = "Выберете местоположения вируса COVID-19 " + smile
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=location_keyboard(),
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
           "Введите команду /time, чтобы увидеть время, пройденное с последнего вашего сообщения.",
           "Введите команду /date, чтобы увидеть текущую дату и время.",
           "Введите команду /fact, чтобы увидеть самый залайканный пост на cat-fact.herokuapp.com",
           "Введите команду /corono_stats, чтобы увидеть актуальную статистику по короновирусу."]
    update.message.reply_text('\n'.join(tmp))

@update_log
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    chat_id = update.message.chat_id
    text = update.message.text
    context.bot.send_message(
        chat_id=chat_id,
        text=text,
    )

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
                print(str(i) , str(period))
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
    updater.dispatcher.add_handler(CommandHandler('corono_stats', corono_stats))
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