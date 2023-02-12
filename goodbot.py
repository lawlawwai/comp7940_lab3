## chatbot.py
import os

import telegram
from telegram import Location
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
# The messageHandler is used for all message updates
import configparser
import logging
from geopy.distance import geodesic
import random

praise_list = ['你很有責任感哦!', '你今天的表現令大家都很開心!', '你今天給了我很多的驚喜!', '你學的真快!', '你真棒!',
               '你真聰明!', '你的觀察力很強!', '你的想法很有創意!', '你的作品真棒!', '你很有想法哦!', '你真的很能幹哦!',
               '你真可愛!', '你真是個聰明的孩子!',
               '你做的非常好!', '你最近進步很大，繼續保持。', '你的眼睛真有神!']


def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token="6285599912:AAGZqru-oEEoFAyrFswuOamRT3ZWJaaFDZM", use_context=True)
    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as e
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher

    echo_handler = CommandHandler(['praise'], echo)
    dispatcher.add_handler(echo_handler)

    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    random_int = random.randint(0,len(praise_list)-1)
    reply_message = praise_list[random_int]
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


if __name__ == '__main__':
    main()
