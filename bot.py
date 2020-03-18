#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import logging
import requests
from datetime import timedelta, datetime
from setup import PROXY, TOKEN
from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

LOG_HISTORY = list()


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

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

@update_log
def start(update: Update, context: CallbackContext):
    """Send a message when the command /start is issued."""
    update.message.reply_text(f'Привет, {update.effective_user.first_name}!')

@update_log
def chat_help(update: Update, context: CallbackContext):
    """Send a message when the command /help is issued."""
    tmp = ["Введи команду /start для начала.",
           "Введите команду /history, чтобы увидеть последние 5 действий.",
           "Введите команду /time, чтобы увидеть время, пройденное с последнего вашего сообщения.",
           "Введите команду /date, чтобы увидеть текущую дату и время.",
           "Введите команду /fact, чтобы увидеть самый залайканный пост на cat-fact.herokuapp.com"]
    update.message.reply_text('\n'.join(tmp))

@update_log
def echo(update: Update, context: CallbackContext):
    """Echo the user message."""
    update.message.reply_text(update.message.text)

@update_log
def error(update: Update, context: CallbackContext):
    """Log Errors caused by Updates."""
    logger.warning(f'Update {update} caused error {context.error}')

@update_log
def elapsed_time(update: Updater, context: CallbackContext):
    user = update.effective_user.first_name
    period = timedelta(0)
    if len(LOG_HISTORY) > 1:
        for i in range(len(LOG_HISTORY) - 2, -1, -1):
            if LOG_HISTORY[i]["user"] == user:
                time_delta = timedelta(hours=3, minutes=0, seconds=0)
                period = LOG_HISTORY[i]["date"] + time_delta
                period = datetime.now() - period
                print(str(i) , str(period))
                break;
    update.message.reply_text(f"Прошло {period.seconds // 3600} часов, {(period.seconds % 3600) // 60} минут, {(period.seconds % 3600) % 60} секунд с последнего вашего сообщения.")

@update_log
def date(update: Updater, context: CallbackContext):
    now = datetime.now()
    update.message.reply_text(f"Дата: {now.day}.{now.month}.{now.year}\nВремя: {now.hour}:{now.minute}")

@update_log 
def fact(update: Updater, context: CallbackContext):
  r = requests.get(r"https://cat-fact.herokuapp.com/facts")
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
            update.message.reply_text("\n".join(answer))
            handle.write("\n".join(answer) + '\n')

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