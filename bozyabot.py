import bozya_config

import logging
import ssl

import telebot
from telebot import apihelper
from telebot import types
from telebot.types import Message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import apiai

import sys
import json
from aiohttp import web
import requests

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(bozya_config.TOKEN)

def getResponseDialogFlow(text):
    if '' == text.strip():
        text = 'голос!'
    request = apiai.ApiAI(bozya_config.AI_TOKEN).text_request() # Токен API к Dialogflow
    request.lang = 'ru' # На каком языке будет послан запрос
    request.session_id = 'BatlabAIBot' # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.query = text # Посылаем запрос к ИИ с сообщением от юзера

    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
    # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
    return response

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def main_message(message):
    privateChat = ('private' in message.chat.type)
    callBozy = (privateChat 
                            or message.text.lower().startswith('бозя') 
                            or (message.reply_to_message 
                                and message.reply_to_message.from_user.is_bot 
                                and message.reply_to_message.from_user.username in ('BozyaBot') )
                )
    if callBozy:
        text = message.text 
        if text.lower().startswith('бозя'):
            text = message.text[4:]

        response = getResponseDialogFlow(text)
        bot.reply_to(message, text=response)

def main_loop():
    app = web.Application()
    # Process webhook calls
    async def handle(request):
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()


    app.router.add_post('/', handle)
    
    # Remove webhook, it fails sometimes the set if there is a previous webhook
    bot.remove_webhook()
    # Set webhook
    bot.set_webhook(url="https://{}/bot/{}".format(bozya_config.WEBHOOK_LISTEN, str(bozya_config.WEBHOOK_PORT)[3:1]))
    # Build ssl context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(bozya_config.WEBHOOK_SSL_CERT, bozya_config.WEBHOOK_SSL_PRIV)
    # Start aiohttp server
    web.run_app(
        app,
        host=bozya_config.WEBHOOK_LISTEN,
        port=bozya_config.WEBHOOK_PORT,
        ssl_context=context
    )

if __name__ == '__main__': 
    try:
        main_loop()
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)