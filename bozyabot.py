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
from datetime import datetime

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
                send_messages_big(message.chat.id, text=getResponseDialogFlow('deceive'))
                return
            
            user = users.User(message.from_user.username, message.forward_date, message.text)
            
            if user == None:  
                if 'Подробности /me' in message.text or (not privateChat): 
                    send_messages_big(message.chat.id, text=getResponseDialogFlow('pip_me'))
                    return
                else:
                    user.setChat(message.chat.id)
                    user.setPing(True)
                    x = registered_users.insert_one(json.loads(user.toJSON()))
                    updateUser(None)
                    send_messages_big(message.chat.id, text=getResponseDialogFlow('registered'))
            else:
                updatedUser = users.updateUser(user, users.getUser(user.getLogin(), registered_users))
                updateUser(updatedUser)

            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow('deceive')) 
        return

    if message.forward_from and message.forward_from.username == 'WastelandWarsBot' and '❤️' in message.text and '🍗' in message.text and '🔋' in message.text and '👣' in message.text:
        if 'Сражение с' in message.text:
            user = getUserByLogin(message.from_user.username)
            if user == None:
                send_messages_big(message.chat.id, text=getResponseDialogFlow('no_user')) 
                return

            if getTimeEmoji(user.getTimeUpdate()) not in ('👶','👦'):
                send_messages_big(message.chat.id, text=getResponseDialogFlow('update_pip')) 
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
                    kr = int(s.split('🕳')[1].split(' ')[0].strip())
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
                report = 'Статистика сражений\n'
                report = report + f'<b>{mob_name}</b> {mob_class} на <b>{km}</b>км.\n\n'
                counter = 0
                win_counter = 0

                min_beaten = 1000000
                average_beaten = 0
                average_beaten_counter = 0
                max_beaten = 0
                max_beaten_user_armor = 0
                min_beaten_user_armor = 0

                min_damage = 1000000
                average_damage = 0
                average_damage_counter = 0
                max_damage = 0
                max_damage_user_damage = 0
                min_damage_user_damage = 0

                counter_kr = 0
                average_kr = 0
                counter_mat = 0
                average_mat = 0

                for one_mob in mob.find({'km':km, 'mob_name':mob_name, 'mob_class':mob_class}):
                    counter = counter + 1
                    if one_mob['win']:
                        win_counter = win_counter + 1

                    one_average_beaten = 0
                    one_counter_beaten = 0
                    for b in one_mob['beaten']:
                        one_counter_beaten = one_counter_beaten + 1
                        if b > max_beaten: 
                            max_beaten = b
                            max_beaten_user_armor = one_mob['user_armor']
                        if b < min_beaten: 
                            min_beaten = b
                            min_beaten_user_armor = one_mob['user_armor']
                        one_average_beaten = one_average_beaten + b

                    if one_counter_beaten > 0:
                        average_beaten = average_beaten + one_average_beaten / one_counter_beaten
                        average_beaten_counter = average_beaten_counter + 1


                    one_average_damage = 0
                    one_counter_damage = 0
                    for b in one_mob['damage']:
                        one_counter_damage = one_counter_damage + 1
                        if b > max_damage: 
                            max_damage = b
                            max_damage_user_damage = one_mob['user_damage']
                        if b < min_damage: 
                            min_damage = b
                            min_damage_user_damage = one_mob['user_damage']
                        one_average_damage = one_average_damage + b

                    if one_counter_beaten > 0:
                        average_beaten = average_beaten + one_average_beaten / one_counter_beaten
                        average_beaten_counter = average_beaten_counter + 1

                    if one_mob['kr'] > 0:
                        counter_kr = counter_kr + 1
                        average_kr = average_kr + one_mob['kr']
                    
                    if one_mob['mat'] > 0:
                        counter_mat = counter_mat + 1
                        average_mat = average_mat + one_mob['mat']

                if min_beaten == 1000000: 
                    min_beaten = 0
                if min_damage == 1000000: 
                    min_damage = 0

                if average_beaten_counter > 0:
                    average_beaten = int(average_beaten / average_beaten_counter)
                if counter_kr > 0:
                    average_kr = int(average_kr / counter_kr)
                if counter_mat > 0:
                    average_mat = int(average_mat / counter_mat)
                report = report + f'✊ Побед: <b>{win_counter}/{counter}</b>\n'
                report = report + f'💔 Урон бандитам:\n'
                report = report + f'      Min <b>{min_beaten}</b> при 🛡<b>{min_beaten_user_armor}</b>\n'
                report = report + f'      В среднем <b>{average_beaten}</b>\n'
                report = report + f'      Max <b>{max_beaten}</b> при 🛡<b>{max_beaten_user_armor}</b>\n'
                report = report + f'💥Получил от бандитов:\n'
                report = report + f'      Min <b>{min_damage}</b> при ⚔<b>{min_damage_user_damage}</b>\n'
                report = report + f'      В среднем <b>{average_damage}</b>\n'
                report = report + f'      Max <b>{max_damage}</b> при ⚔<b>{max_damage_user_damage}</b>\n' 
                report = report + f'В среднем добыто:\n'
                report = report + f'      🕳 {average_kr}\n'
                report = report + f'      📦 {average_mat}\n'
                send_messages_big(message.chat.id, text=report)
        return

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