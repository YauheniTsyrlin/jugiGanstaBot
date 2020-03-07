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
from datetime import timedelta

import users
import pymongo
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["bozyadb"]
registered_users = mydb["users"]
mob = mydb["mob"]

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(bozya_config.TOKEN)

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

def getUserByLogin(login: str):
    for user in list(USERS_ARR):
        try:
            if login.lower() == user.getLogin().lower(): 
                return user
        except:
            pass
    return None

def updateUser(newuser: users.User):
    if newuser == None:
        pass
    else:
        newvalues = { "$set": json.loads(newuser.toJSON()) }
        z = registered_users.update_one({"login": f"{newuser.getLogin()}"}, newvalues)
    USERS_ARR.clear()
    for x in registered_users.find():
        USERS_ARR.append(users.importUser(x))

def getTimeEmoji(time):
    if time > (datetime.now() - timedelta(days=7)).timestamp():
        return '👶'
    elif time > (datetime.now() - timedelta(days=14)).timestamp():
        return '👦'
    elif time > (datetime.now() - timedelta(days=28)).timestamp():
        return '👨'
    elif time > (datetime.now() - timedelta(days=56)).timestamp():
        return '👨‍🦳'
    else:
        return '👴'

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
    if (message.text.startswith('📟Пип-бой 3000') and 
            '/killdrone' not in message.text and 
            'ТОП ФРАКЦИЙ' not in message.text and 
            'СОДЕРЖИМОЕ РЮКЗАКА' not in message.text and 
            'ПРИПАСЫ В РЮКЗАКЕ' not in message.text and 
            'РЕСУРСЫ и ХЛАМ' not in message.text ):

        if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
 
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'deceive').fulfillment_text)
                return
            
            user = users.User(message.from_user.username, message.forward_date, message.text)
            
            if user == None:  
                if 'Подробности /me' in message.text or (not privateChat): 
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'pip_me').fulfillment_text)
                    return
                else:
                    user.setChat(message.chat.id)
                    user.setPing(True)
                    x = registered_users.insert_one(json.loads(user.toJSON()))
                    updateUser(None)
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'registered').fulfillment_text)
            else:
                updatedUser = users.updateUser(user, users.getUser(user.getLogin(), registered_users))
                updateUser(updatedUser)

            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'deceive').fulfillment_text) 
        return

    if message.forward_from and message.forward_from.username == 'WastelandWarsBot' and '❤️' in message.text and '🍗' in message.text and '🔋' in message.text and '👣' in message.text:
        if 'Сражение с' in message.text:
            user = getUserByLogin(message.from_user.username)
            if user == None:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'no_user').fulfillment_text) 
                return

            if getTimeEmoji(user.getTimeUpdate()) not in ('👶','👦'):
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'update_pip').fulfillment_text) 
                return

            strings = message.text.split('\n')
            mob_name = ''
            mob_class = ''
            km = int(message.text.split('👣')[1].split('км')[0])
            kr = 0
            mat = 0
            damage = []
            beaten = []
            you_win = False
            for s in strings:
                if s.startswith('Сражение с'):
                    mob_name = s.split('Сражение с')[1].split('(')[0].strip()
                    mob_class = s.split('(')[1].split(')')[0].strip()
                if s.startswith('Получено:') and '🕳' in s and '📦' in s:
                    kr = int(s.split('🕳')[1].split(' ').strip())
                    mat = int(s.split('📦')[1].strip())
                if s.startswith('👤Ты') and '💥' in s:
                    damage.append(int(s.split('💥')[1].strip()))
                if 'нанес тебе удар' in s and '💔' in s:
                    beaten.append(int(s.split('💔')[1].strip()))
                if s.startswith('Ты одержал победу!'):
                    you_win = True

            if mob_name == '':
                pass
            else:
                row = {}
                row.update({'date': message.forward_date})
                row.update({'login': message.from_user.username})
                row.update({'mob_name': mob_name})
                row.update({'mob_class': mob_class})
                
                row.update({'km': km})
                row.update({'kr': kr})
                row.update({'mat': mat})
                row.update({'bm': user.getBm()})
                row.update({'damage': damage})
                row.update({'beaten': beaten})

                newvalues = { "$set": row }
                result = mob.update_one({
                    'login': message.forward_date, 
                    'date': message.forward_date,
                    'km': km
                    }, newvalues)
                if result.matched_count < 1:
                    mob.insert_one(row)

                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)

    if callBozy:
        text = message.text 
        if text.lower().startswith('бозя'):
            text = message.text[4:]

        
        response = getResponseDialogFlow(text)
        bot.reply_to(message, text=response)

def send_messages_big(chat_id: str, text: str, reply_markup=None):
    strings = text.split('\n')
    tmp = ''
    msg = None
    for s in strings:
        if len(tmp + s) < 4000:
            tmp = tmp + s +'\n'
        else: 
            msg = bot.send_message(chat_id, text=tmp, parse_mode='HTML', reply_markup=reply_markup)
            tmp = s + '\n'

    msg = bot.send_message(chat_id, text=tmp, parse_mode='HTML', reply_markup=reply_markup)
    return msg

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
    bot.set_webhook(url=f"https://{bozya_config.WEBHOOK_HOST}/bot/{str(bozya_config.WEBHOOK_PORT)[3:4]}")
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