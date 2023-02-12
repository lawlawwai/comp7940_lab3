import os
import re

import telegram
from telegram import Location
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
# The messageHandler is used for all message updates
import configparser
import logging
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

## global DB setting
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://datebot-f12cb-default-rtdb.firebaseio.com/'
    # 'storageBucket': 'datebot-f12cb.appspot.com'
})
ref = db.reference('/')
users_ref = ref.child('users')


def main():
    # Load your token and create an Updater for your Bot
    config = configparser.ConfigParser()
    config.read('config.ini')
    updater = Updater(token=(config['TELEGRAM']['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    # You can set this logging module, so you will know when and why things do not work as e
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    # register a dispatcher to handle message: here we register an echo dispatcher

    command_handler = CommandHandler(['start', 'help'], command)
    dispatcher.add_handler(command_handler)

    register_handler = CommandHandler(['register', 'm', 'f', 'caption'], register)
    dispatcher.add_handler(register_handler)

    info_handler = CommandHandler(['myinfo'], info)
    dispatcher.add_handler(info_handler)

    list_handler = CommandHandler(['list'], list)
    dispatcher.add_handler(list_handler)

    delete_handler = CommandHandler(['delete'], delete)
    dispatcher.add_handler(delete_handler)

    match_handler = MessageHandler(Filters.command, match)
    dispatcher.add_handler(match_handler)

    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)


    #
    # photo_handler = MessageHandler(Filters.photo, echo_photo)
    # dispatcher.add_handler(photo_handler)
    #
    # location_handler = MessageHandler(Filters.location, echo_location)
    # dispatcher.add_handler(location_handler)

    # test_handler = CommandHandler('test', test)

    # test_handler = MessageHandler(None, test)
    # dispatcher.add_handler(test_handler)

    # To start the bot:
    updater.start_polling()
    updater.idle()


# def event_router(update, context):
#     register(update, context)


def check_reg(id, context):
    if users_ref.child(id).get() is None:
        return users_ref.child(id).get()
    else:
        user_info = users_ref.child(id).get()
        if user_info.get('sex') == "" or user_info.get('sex') is None:
            context.bot.send_message(chat_id=id, text='Please use /M or /F to update user sex.')
            return None
        if user_info.get('caption') == "" or user_info.get('caption') is None:
            context.bot.send_message(chat_id=id, text='Please use /caption to update user caption.')
            return None
        return user_info


def check_match(id, match_id):
    if users_ref.child(id).child("match").get() == match_id and users_ref.child(match_id).child("match").get() == id:
        return True
    else:
        return False

def delete(update, context):
    id = str(update.effective_chat.id)
    match_id = users_ref.child(id).child("match").get()
    users_ref.child(id).update({
        'match': ""
    })
    users_ref.child(match_id).update({
        'match': ""
    })
    context.bot.send_message(chat_id=update.effective_chat.id, text="Deleted match")
    context.bot.send_message(chat_id=int(match_id), text=id+" deleted match")


def match(update, context):
    match_id = re.search("[0-9]{9,10}", update.message.text[1:])
    if match_id:
        id = str(update.effective_chat.id)
        if users_ref.child(str(id)).child('match').get() == match_id.group():
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="You have sent match request to " + match_id.group())
            return
        users_ref.child(str(id)).update({
            'match': match_id.group()
        })

        if check_match(id, match_id.group()):
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Match successfully, you are chatting with " + match_id.group())
            context.bot.send_message(chat_id=int(match_id.group()),
                                     text="Match successfully, you are chatting with " + id)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Sent match request to " + match_id.group())
            context.bot.send_message(chat_id=int(match_id.group()), text="Received match request from /" + id)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Input wrong command")


def list(update, context):
    oppo_sex = 'M'
    id = str(update.effective_chat.id)
    if users_ref.child(id).child("sex").get() == "M":
        oppo_sex = "F"
    snapshot = users_ref.order_by_child('sex').equal_to(oppo_sex).get()
    users_list = ""
    for key, val in snapshot.items():
        if key == id:
            continue
        if val.get("caption") is not None:
            users_list = users_list + "\nID: /" + key + " , Caption: " + val.get("caption")
    if users_list == "":
        users_list = "No user for matching"
    context.bot.send_message(chat_id=update.effective_chat.id, text=users_list)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Click the ID to match.")


def register(update, context):
    logging.info("Update: " + str(update))
    id = str(update.effective_chat.id)

    if users_ref.child(id).get() is None:
        users_ref.update({
            update.effective_chat.id: {"match": ""}
        })
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Registered user\nPlease use /M or /F to update sex\nUse /caption to update caption')
    else:
        if update.message.text == '/m':
            users_ref.child(str(id)).update({
                'sex': 'M'
            })
        elif update.message.text == '/f':
            users_ref.child(str(id)).update({
                'sex': 'F'
            })
        elif update.message.text[1:8] == "caption":
            users_ref.child(str(id)).update({
                'caption': update.message.text[9:]
            })
        context.bot.send_message(chat_id=update.effective_chat.id, text='Status updated.')


def info(update, context):
    logging.info("Update: " + str(update))
    id = str(update.effective_chat.id)
    user_info_dict = check_reg(id, context)
    if user_info_dict is None:
        return
    user_info_str = "User:\n"
    for k, v in user_info_dict.items():
        user_info_str = user_info_str + k + ":" + v + "\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=user_info_str)


def test(update, context):
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text='received')
    print(update.message)
    print(update.message.chat)
    context.bot.send_photo(chat_id=update.effective_chat.id,
                           photo='AgACAgUAAxkBAAIB6GPno8th9i0loEcIAdnu19H12D1SAALdtDEbCzE4VzSVKhi7ZlFrAQADAgADcwADLgQ')

def echo(update, context):
    reply_message = update.message.text
    logging.info("Update: " + str(update))
    id = str(update.effective_chat.id)
    match_id = users_ref.child(id).child("match").get()
    if check_match(id, match_id):
        context.bot.send_message(chat_id=int(match_id), text=reply_message)
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You don't have match yet. Please try to match first")


def command(update, context):
    command_input = update.message.text
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    if command_input == "/start":
        reply_message = "Welcome to lawlawwai bot!!"
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)
    elif command_input == "/help":
        reply_message = "Here is the function:\n1. echo: repeat you text in upper case.\n2. echo photo: send back the " \
                        "photo to you "
        context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


def echo_photo(update, context):
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    reply_message = update.message.photo[-1]
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=reply_message)


def echo_location(update, context):
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    longitude = update.message.location.longitude
    latitude = update.message.location.latitude
    tg_current_location = Location(longitude, latitude)
    context.bot.send_location(chat_id=update.effective_chat.id, location=tg_current_location)


if __name__ == '__main__':
    main()
