## chatbot.py
import os

import telegram
from telegram import Location
from telegram.ext import Updater, MessageHandler, Filters
# The messageHandler is used for all message updates
import configparser
import logging
from geopy.distance import geodesic

def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as e
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)

    command_handler = MessageHandler(Filters.command, command)
    dispatcher.add_handler(command_handler)

    photo_handler = MessageHandler(Filters.photo, echo_photo)
    dispatcher.add_handler(photo_handler)

    location_handler = MessageHandler(Filters.location, echo_location)
    dispatcher.add_handler(location_handler)
    # To start the bot:
    # updater.start_polling()
    # updater.idle()
    TOKEN = (config['TELEGRAM']['ACCESS_TOKEN'])
    PORT = int(os.environ.get('PORT', '443'))
    HOOK_URL = 'comp7940lab3-prqeki.aws-eu-1.ccdns.co' + '/' + TOKEN
    updater.start_webhook(listen='0.0.0.0', port=PORT, url_path=TOKEN, webhook_url=HOOK_URL)
    updater.idle()




def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def command(update, context):
    command_input = update.message.text
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    if command_input=="/start":
        reply_message = "Welcome to lawlawwai bot!!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    elif command_input=="/help":
        reply_message = "Here is the function:\n1. echo: repeat you text in upper case.\n2. echo photo: send back the " \
                        "photo to you "
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def echo_photo(update, context):
    reply_message = update.message.photo[-1]
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=reply_message)

def echo_location(update, context):
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    longitude = update.message.location.longitude
    latitude = update.message.location.latitude
    saved_location = (22.323,114.167)
    current_location = (latitude,longitude)
    distance=geodesic(saved_location, current_location).m
    tg_current_location = Location(longitude,latitude)
    tg_save_location=Location(114.167,22.323)
    context.bot.send_location(chat_id=update.effective_chat.id, location=tg_current_location)
    context.bot.send_location(chat_id=update.effective_chat.id, location=tg_save_location)
    context.bot.send_message(chat_id=update.effective_chat.id, text=str(distance)+"m from the save point.")


if __name__ == '__main__':
    main()
