#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config
import users 
import wariors
import tools
import speech
import dialogflow
import matplot

import logging
import ssl
from mem_top import mem_top

from aiohttp import web
from yandex_geocoder import Client
import pymorphy2

import telebot
from telebot import apihelper
from telebot import types
from telebot.types import Message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import time
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import timezonefinder, pytz

import threading
from multiprocessing import Process

import sys
import json
import requests

import random
from random import randrange

import pymongo
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jugidb"]
registered_users = mydb["users"]
tg_users        = mydb["tg_users"]
registered_wariors = mydb["wariors"]
battle          = mydb["battle"]
competition     = mydb["competition"]
settings        = mydb["settings"]
pending_messages = mydb["pending_messages"]
plan_raids      = mydb["rades"]
dungeons        = mydb["dungeons"]
report_raids    = mydb["report_raids"]
man_of_day      = mydb["man_of_day"]
pip_history     = mydb["pip_history"]


flexFlag = False
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(config.TOKEN)

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

TG_USERS_ARR = [] # Зарегистрированные пользователи
for x in tg_users.find():
    TG_USERS_ARR.append(x)

WARIORS_ARR = [] # Зарегистрированные жители пустоши
for x in registered_wariors.find():
    WARIORS_ARR.append(wariors.importWarior(x))

SETTINGS_ARR = [] # Зарегистрированные настройки
for setting in settings.find():
    SETTINGS_ARR.append(setting)

INFECT_PROBABILITY = 0
acc_koronavirus = '🦇 Коронавирус'

def getSetting(code: str, name=None, value=None):
    """ Получение настройки """
    result = settings.find_one({'code': code})
    if (result):
        if name:
            for arr in result.get('value'):
                if arr['name'] == name:
                    return arr['value'] 
        elif value:
            for arr in result.get('value'):
                if arr['value'] == value:
                    return arr['name'] 

        else:
            return result.get('value')

def check_and_register_tg_user(tg_login: str):
    user = getUserByLogin(tg_login)
    if user: 
        return
    else:
        if getTgUser(tg_login) == None:
            row = {}
            row.update({'createdate' :datetime.now().timestamp()})
            row.update({'login' : tg_login})
            row.update({'timeban' : None})
            newvalues = { "$set": row }
            tg_users.insert_one(row)

            TG_USERS_ARR.clear()
            for x in tg_users.find():
                TG_USERS_ARR.append(x)

def getTgUser(login: str):
    for user in list(TG_USERS_ARR):
        if login == user["login"]: 
            return user
    return None

def isAdmin(login: str):
    for adm in getSetting(code='ADMINISTRATOR'):
        if login.lower() == adm.get('login').lower(): return True
    return False

def getAdminChat(login: str):
    for adm in getSetting(code='ADMINISTRATOR'):
        if login.lower() == adm.get('login').lower(): return adm.get('chat')
    return None

def isRegisteredUserName(name: str):
    name = tools.deEmojify(name)

    for user in list(USERS_ARR):
        if name.lower() == user.getName().lower(): return True
    return False

def isRegisteredUserLogin(login: str):
    for user in list(USERS_ARR):
        try:
            if login.lower() == user.getLogin().lower(): 
                return True
        except:
            pass        
    return False

def isGoatBoss(login: str):
    for goat in getSetting(code='GOATS_BANDS'):
        for boss in goat['boss']:
            if boss == login:
                return True
    return False

def isBandBoss(login: str):
    for goat in getSetting(code='GOATS_BANDS'):
        for band in goat['bands']:
            if band['boss'] == login:
                return True
    return False

def getMyBands(login: str):
    user = getUserByLogin(login)
    if not user:
        return None

    for goat in getSetting(code='GOATS_BANDS'):
        for band in goat['bands']:
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                return goat['bands']
    return None        

def getMyBandsName(login: str):
    user = getUserByLogin(login)
    if not user:
        return None
    
    for goat in getSetting(code='GOATS_BANDS'):
        find = False
        bands = []
        for band in goat['bands']:
            bands.append(band.get('name'))
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                find = True
        if find:
            return bands
    return None

def isGoatSecretChat(login: str, secretchat: str):
    goat = getMyGoat(login)
    if goat:
        if goat['chats']['secret'] == secretchat:
            return True
        else:
            return False    
    else:
        return False
    return True

def getMyGoat(login: str):
    user = getUserByLogin(login)
    if not user:
        return None

    for goat in getSetting(code='GOATS_BANDS'):
        for band in goat['bands']:
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                return goat
    return None 

def getMyGoatName(login: str):
    user = getUserByLogin(login)
    if not user:
        return None

    for goat in getSetting(code='GOATS_BANDS'):
        for band in goat['bands']:
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                return goat['name']

    return None 

def getBandUsers(band: str):
    users = []
    for user in list(USERS_ARR):
        if user.getBand() and band.lower() == user.getBand().lower(): 
            users.append(user)
    return users

def getGoatBands(goatName: str):
    for goat in getSetting(code='GOATS_BANDS'):
        if goat.get('name') == goatName:
            bands = []
            for band in goat['bands']:
                bands.append(band.get('name'))
            return bands
    return None 

def isUsersBand(login: str, band: str):
    bands = getMyBands(login)
    if bands == None: 
        return False
    for b in bands:
        if b.get('name') == band:
            return True
    return False

def hasAccessToWariors(login: str):
    user = getUserByLogin(login)
    if not user:
        return False

    for band in getSetting(code='BANDS_ACCESS_WARIORS'):
        if user.getBand() and band.get('band').lower() == user.getBand().lower():
            return True

    return False

def getUserByLogin(login: str):
    for user in list(USERS_ARR):
        try:
            if login.lower() == user.getLogin().lower(): 
                return user
        except:
            pass
    return None

def getUserByName(name: str):
    for user in list(USERS_ARR):
        if tools.deEmojify(name).lower().strip() == user.getName().lower().strip(): return user
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

def isUserBan(login: str):
    tz = config.SERVER_MSK_DIFF
    date_for = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)

    userIAm = getUserByLogin(login)
    if userIAm:
        if userIAm.getTimeBan():
            if date_for.timestamp() < userIAm.getTimeBan():
                return True
            else:
                userIAm.setTimeBan(None)
                updateUser(userIAm)
    else:
        tg_user = getTgUser(login)
        if tg_user and tg_user['timeban']:
            if date_for.timestamp() < tg_user['timeban']:
                return True
            else:
                tg_user.update({'timeban' : None})
                newvalues = { "$set": tg_user }
                result = tg_users.update_one({
                    'login': login
                    }, newvalues)

                TG_USERS_ARR.clear()
                for x in tg_users.find():
                    TG_USERS_ARR.append(x)

    return False

def updateTgUser(tg_user):
    newvalues = { "$set": tg_user }
    result = tg_users.update_one({
        'login': tg_user["login"]
        }, newvalues)

    TG_USERS_ARR.clear()
    for x in tg_users.find():
        TG_USERS_ARR.append(x)

def getWariorFraction(string: str):
    if (string.startswith('⚙️')):
        return '⚙️Убежище 4'
    elif (string.startswith('🔪')):
        return '🔪Головорезы'
    elif (string.startswith('💣')):
        return '💣Мегатонна'
    elif (string.startswith('⚛️')):
        return '⚛️Республика'
    elif (string.startswith('👙')):
        return '👙Клуб бикини'

def getWariorByName(name: str, fraction: str):
    name = tools.deEmojify(name).strip()
    for warior in list(WARIORS_ARR):
        if name == warior.getName().strip() and fraction == warior.getFraction(): 
            return warior
    return None

def isKnownWarior(name: str, fraction: str):
    for warior in list(WARIORS_ARR):
        if warior.getName() and name.lower().strip() == warior.getName().lower().strip() and warior.getFraction() == fraction: 
            return True
    return False

def update_warior(warior: wariors.Warior):
    if warior == None:
        pass
    else:
        if isKnownWarior(warior.getName(), warior.getFraction()):
            wariorToUpdate = getWariorByName(warior.getName(), warior.getFraction())
            updatedWarior = wariors.mergeWariors(warior, wariorToUpdate)
            newvalues = { "$set": json.loads(updatedWarior.toJSON()) }
            z = registered_wariors.update_one({
                "name": f"{updatedWarior.getName()}", 
                "fraction": f"{updatedWarior.getFraction()}"
                }, newvalues)
        else:
            registered_wariors.insert_one(json.loads(warior.toJSON()))

    WARIORS_ARR.clear()
    for x in registered_wariors.find():
        WARIORS_ARR.append(wariors.importWarior(x))
        
def get_raid_plan(raid_date, goat):
    plan_for_date = f'План рейдов на {time.strftime("%d.%m.%Y", time.gmtime( raid_date.timestamp() ))}\n🐐<b>{goat}</b>\n\n'
    find = False
    time_str = None
    for raid in plan_raids.find({
                                '$and' : 
                                [
                                    {
                                        'rade_date': {
                                        '$gte': (datetime.now() + timedelta(minutes=180)).timestamp(),
                                        '$lt': (raid_date.replace(hour=23, minute=59, second=59, microsecond=0)).timestamp(),
                                        }
                                    },
                                    {
                                        'goat': goat
                                    }
                                ]
                            }):

        t = datetime.fromtimestamp(raid.get('rade_date') ) 
        if not (time_str == t):
            plan_for_date = plan_for_date + f'<b>Рейд в {str(t.hour).zfill(2)}:{str(t.minute).zfill(2)}</b>\n'
            time_str = t

        plan_for_date = plan_for_date + f'{raid.get("rade_text")}\n'
        users_onraid = raid.get("users")
        if users_onraid == None or len(users_onraid) == 0:
            plan_for_date = plan_for_date + f'    Никто не записался\n'
        else:
            i = 0
            for u in users_onraid:
                i = i + 1
                reg_usr = getUserByLogin(u)
                plan_for_date = plan_for_date + f'    {i}. {reg_usr.getName()}\n'
        
        find = True

    if find == False:
        plan_for_date = plan_for_date + '<b>Нет запланированных рейдов</b>'

    return plan_for_date

def setSetting(code: str, value: str):

    """ Сохранение настройки """
    myquery = { "code": code }
    newvalues = { "$set": { "value": json.dumps(value) } }
    u = settings.update_one(myquery, newvalues)

    SETTINGS_ARR.clear() # Зарегистрированные настройки
    for setting in settings.find():
        SETTINGS_ARR.append(setting)
    return True

def getButtonsMenu(list_buttons):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    groups_names = []
    for group in list_buttons:
        groups_names.append(types.KeyboardButton(f'{group}'))
    markup.add(*groups_names)
    return markup

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def write_json(data, filename = "./pips.json"):
    with open(filename, 'a', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def getResponseDialogFlow(message, text: str, event=None):
    if not text or '' == text.strip():
        text = 'голос!'

    if message:
        user = getUserByLogin(message.from_user.username)
        return dialogflow.getResponseDialogFlow(message.from_user.username, text, event, user, message)
    else:
        return dialogflow.getResponseDialogFlow('system_user', text, event, None, message)

def getResponseHuificator(text):
    morph = pymorphy2.MorphAnalyzer()
    report = ''
    words = text.split(' ')
    for word in words:
        p = morph.parse(word.replace('-то','').replace('.','').replace(',','').replace('!','').replace('?','').replace('(','').replace(')','').replace(':',''))[0]
        if 'VERB' in p.tag:
            pass
        elif '-то' in word:
            pass
        elif 'NOUN' in p.tag or 'ADJF' in p.tag or 'ADVB' in p.tag:
            word = p.word + '-' + tools.huificate(word)
        report = report + word + ' '
    return report

def censored(message):
    bot.delete_message(message.chat.id, message.message_id)
    id = random.sample(getSetting(code='STICKERS',name='CENSORSHIP'), 1)[0]['value']
    if len(id) > 40:
        bot.send_photo(message.chat.id, id)
    else:
        bot.send_sticker(message.chat.id, id)
    send_messages_big(message.chat.id, text=getResponseDialogFlow(message ,'shot_censorship').fulfillment_text)

def getUserSettingsName():
    result = []
    for sett in getSetting(code='USER_SETTINGS'):
        result.append(sett["name"])
    return result

def getUserSetting(login: str, name: str):
    user = getUserByLogin(login)
    for sett in user.getSettings():
        if sett["name"] == name:
            return sett
    return None

def addToUserHistory(user: users.User):
    row = {}
    date = datetime.fromtimestamp(user.getTimeUpdate()).replace(hour=0, minute=0, second=0, microsecond=0).timestamp()
    row.update({'date'    :date})
    row.update({'login'   :user.getLogin()})
    row.update({'damage'  :user.getDamage()})   #⚔ 
    row.update({'armor'   :user.getArmor()})    #🛡
    row.update({'dzen'    :user.getDzen()})     #🏵
    row.update({'force'   :user.getForce()})    #💪
    row.update({'accuracy':user.getAccuracy()}) #🔫
    row.update({'health'  :user.getHealth()})   #❤
    row.update({'charisma':user.getCharisma()}) #🗣
    row.update({'agility' :user.getAgility()})  #🤸🏽‍
    row.update({'stamina' :user.getStamina()})  #🔋

    newvalues = { "$set": row }
    result = pip_history.update_one({'login': user.getLogin(), 'date': date}, newvalues)
    if result.matched_count < 1:
        pip_history.insert_one(row)

# Handle new_chat_members
@bot.message_handler(content_types=['new_chat_members', 'left_chat_members'])
def send_welcome_and_dismiss(message):
    response = getResponseDialogFlow(message, message.content_type).fulfillment_text
    if response:
        bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS',name='BOT_NEW_MEMBER'), 1)[0]['value'])
        bot.send_message(message.chat.id, text=response)
        
        goat = getMyGoat(message.from_user.username)
        if not isGoatSecretChat(message.from_user.username, message.chat.id):
            bot.send_photo(message.chat.id, random.sample(getSetting(code='STICKERS',name='NEW_MEMBER_IMG'), 1)[0]['value'])

# Handle inline_handler
@bot.inline_handler(lambda query: query.query)
def default_query(inline_query):
    if not hasAccessToWariors(inline_query.from_user.username):
        r = types.InlineQueryResultArticle(id=0, title = 'Хрена надо? Ты не из наших банд!', input_message_content=types.InputTextMessageContent(getResponseDialogFlow(inline_query.from_user.username, 'i_dont_know_you').fulfillment_text), description=getResponseDialogFlow(inline_query.from_user.username, 'i_dont_know_you').fulfillment_text)
        bot.answer_inline_query(inline_query.id, [r], cache_time=3060)
        return

    try:
            result = []
            i = 0
            for x in registered_wariors.find(
                {'$or':
                    [
                        {'name':
                            {'$regex':inline_query.query, '$options':'i'}
                        },
                        {'band':
                            {'$regex':inline_query.query, '$options':'i'}
                        }
                    ],
                    'timeUpdate':{'$gte': (datetime.now() - timedelta(days=28)).timestamp()  }
                }):
                warior = wariors.importWarior(x)
                r = types.InlineQueryResultArticle(id=i, title = f'{warior.getFractionSmall()}{warior.getName()}',  
                                                            input_message_content=types.InputTextMessageContent('Джу, профиль @'+warior.getName()), 
                                                            description=warior.getProfileInline())
                result.append(r)
                i = i + 1
            bot.answer_inline_query(inline_query.id, result, cache_time=30)
    except Exception as e:
        print(e)

@bot.message_handler(func=lambda message: message.text and ('📈 Статистика' == message.text))
def send_back_from_usset(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то наговорить, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return

    counter = pip_history.find({'login': message.from_user.username}).count()
    if counter == 0:
        bot.send_message(message.chat.id, text='Сбрось мне хоть один pip!')
        return
    N = 0
    if counter > 10:
        N = 10
    else:
        counter = 0
    cursor = pip_history.find({'login': message.from_user.username}).skip(counter - N)
    matplot.getPlot(cursor, message.from_user.username)
    img = open(config.PATH_IMAGE + f'plot_{message.from_user.username}.png', 'rb')
    bot.send_photo(message.chat.id, img)


@bot.message_handler(func=lambda message: message.text and ('Участвую 👨‍❤️‍👨!' in message.text or 'Сам ты пидор 👨‍❤️‍👨!' in message.text))
def send_back_from_usset(message):
    privateChat = ('private' in message.chat.type)
    if not privateChat:
        bot.send_message(message.chat.id, text='Иди в личный чат!')
        return

    user = getUserByLogin(message.from_user.username)
    setting = None
    for s in getSetting(code='USER_SETTINGS'):
        if s["name"] == '👨‍❤️‍👨Участник "Пидор дня"':
            setting = s

    if 'Участвую 👨‍❤️‍👨!' in message.text:
        setting.update({'value': True})
    elif 'Сам ты пидор 👨‍❤️‍👨!' in message.text:
        setting.update({'value': False})

    user.addSettings(setting)
    updateUser(user)

    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📋 Отчет', '📜 Профиль', f'⏰ План рейда', '📈 Статистика')
    bot.send_message(message.chat.id, text=user.getSettingsReport(), reply_markup=markup)

@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text in getUserSettingsName())
def send_settings(message):
    privateChat = ('private' in message.chat.type)
    if not privateChat:
        bot.send_message(message.chat.id, text='Иди в личный чат!')
        return

    if message.text == '👨‍❤️‍👨Участник "Пидор дня"':
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add('Участвую 👨‍❤️‍👨!', 'Сам ты пидор 👨‍❤️‍👨!')
        bot.send_message(message.chat.id, text='Розыгрыш в общем чате ровно в 9:00\nТвой выбор...', reply_markup=markup)

    if message.text == '🃏Мой герб':
        bot.send_message(message.chat.id, text='Отправь мне любой эмодзи. Только эмодзи может быть твоим гербом...')
        bot.register_next_step_handler(message, process_gerb_step)    

def process_gerb_step(message):
    if tools.isOneEmojify(message.text):
        for user in list(USERS_ARR):
            if user.getSettingValue('🃏Мой герб') and user.getSettingValue('🃏Мой герб') == message.text:
                bot.send_message(message.chat.id, text=f'Поздняк, этот герб уже забил за собой {user.getLogin()}')
                return

        user = getUserByLogin(message.from_user.username)
        setting = None
        for s in getSetting(code='USER_SETTINGS'):
            if s["name"] == '🃏Мой герб':
                setting = s
                setting.update({'value': message.text})
                user.addSettings(setting)
                updateUser(user)

                markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
                markup.add('📋 Отчет', '📜 Профиль', f'⏰ План рейда', '📈 Статистика')
                bot.send_message(message.chat.id, text=user.getSettingsReport(), reply_markup=markup)
                break
    else:
        bot.send_message(message.chat.id, text='Похоже, что ты меня не понял...')

@bot.message_handler(func=lambda message: message.text and 'Назад 📋🔚' in message.text)
def send_back_from_usset(message):
    privateChat = ('private' in message.chat.type)
    if not privateChat:
        bot.send_message(message.chat.id, text='Иди в личный чат!')
        return
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add('📋 Отчет', '📜 Профиль', f'⏰ План рейда', '📈 Статистика')
    bot.send_message(message.chat.id, text='Вернулся...', reply_markup=markup)

# Handle /usset
@bot.message_handler(commands=['usset'])
def send_usset(message):
    privateChat = ('private' in message.chat.type)
    if not privateChat:
        bot.send_message(message.chat.id, text='Иди в личный чат!')
        return

    buttons = getUserSettingsName()
    buttons.append('Назад 📋🔚')
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(*buttons)
    user = getUserByLogin(message.from_user.username)
    bot.send_message(message.chat.id, text=user.getSettingsReport(), reply_markup=markup)

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то стартовать, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return


    response = getResponseDialogFlow(message, 'start').fulfillment_text
    privateChat = ('private' in message.chat.type)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if not privateChat:
        markup.add('Джу, 📋 Отчет', f'Джу, ⏰ план рейда', '📈 Статистика')
    else:
        markup.add('📋 Отчет', '📜 Профиль', f'⏰ План рейда', '📈 Статистика')

    if response:
        bot.send_message(message.chat.id, text=response, reply_markup=markup)

# Handle document
@bot.message_handler(content_types=['document'])
def get_message_photo(message):
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то показать, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return

# Handle photo
@bot.message_handler(content_types=["photo"])
def get_message_photo(message):
    #write_json(message.json)
    
    privateChat = ('private' in message.chat.type)

    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то показать, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return

    if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
        ww = wariors.fromPhotoToWarioirs(message.forward_date, message.caption, message.photo[0].file_id)
        for warior in ww:
            row = {
                    "timeUpdate": message.forward_date, 
                    "name": f"{warior.getName()}", 
                    "fraction": f"{warior.getFraction()}",
                    'band': warior.getBand(), 
                    'goat': warior.getGoat(),
                    'photo': message.photo[0].file_id
                }
            newvalues = { "$set":  row}
            result = registered_wariors.update_one({
                "name": f"{warior.getName()}", 
                "fraction": f"{warior.getFraction()}"
                }, newvalues)
            if result.matched_count < 1:
                registered_wariors.insert_one(row)
            update_warior(None)
            wariorShow = warior
        
        if privateChat:
            wariorShow = getWariorByName(wariorShow.getName(), wariorShow.getFraction())
            if (wariorShow.photo):
                bot.send_photo(message.chat.id, wariorShow.photo, wariorShow.getProfile())
            else:
                send_messages_big(message.chat.id, text=wariorShow.getProfile())
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
    else:
        if privateChat:
            send_messages_big(message.chat.id, text=message.photo[len(message.photo)-1].file_id)
    
# Handle sticker
@bot.message_handler(content_types=["sticker"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то стикернуть, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return

    privateChat = ('private' in message.chat.type)
    if privateChat:
        send_messages_big(message.chat.id, text=message.sticker.file_id)

# Handle voice
@bot.message_handler(content_types=["video", "video_note"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то настримить, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return

# Handle voice
@bot.message_handler(content_types=["location"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то рассказать про свою локацию, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return

# Handle voice
@bot.message_handler(content_types=["voice"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то наговорить, но у него получилось лишь:\n' + getResponseDialogFlow(message, 'user_banned').fulfillment_text)
        return

    bot.send_chat_action(message.chat.id, 'typing')
    file_info = bot.get_file(message.voice.file_id)
    file = requests.get(
        'https://api.telegram.org/file/bot{0}/{1}'.format(config.TOKEN, file_info.file_path))

    try:
        # обращение к нашему новому модулю
        text = speech.speech_to_text(bytes=file.content)
    except speech.SpeechException:
        # Обработка случая, когда распознавание не удалось
        send_messages_big(message.chat.id, text=f'⚠️Внимание! 🗣 Произошла какая-то ошибка при разборе голосового сообщения!')
        pass
    else:
        # Бизнес-логика
        if text:
            name = message.from_user.username
            if message.forward_from:
                name = message.forward_from.username
            user = getUserByLogin(name)
            if user:
                name = user.getName()

            send_messages_big(message.chat.id, text=f'🗣<b>{name}</b>')
            send_messages_big(message.chat.id, text=text)
            
            message.text = text
            main_message(message)

            if (random.random() <= float(getSetting(code='PROBABILITY',name='EMOTIONS'))):
                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS',name='BOT_VOICE'), 1)[0]['value'])
        else:
            send_messages_big(message.chat.id, text=f'🗣<b>{message.from_user.username}</b> что-то сказал, но я ничего не понял!')

def koronavirus(logins, chat: str, probability = float(getSetting(code='PROBABILITY', name='KORONOVIRUS'))):
    if len(logins) < 1:
        return

    users_in_danger = []
    isKoronavirus = False
    
    if INFECT_PROBABILITY > 0:
        probability = INFECT_PROBABILITY
        isKoronavirus = True
    
    for user_login in logins:
        user = getUserByLogin(user_login)
        if user:
            users_in_danger.append(user)
            if user.isAccessoryItem(acc_koronavirus):
                isKoronavirus = True
    
    counter_infected = 0
    if isKoronavirus:
        for user in users_in_danger:
            if not user.isAccessoryItem(acc_koronavirus):
                if (random.random() <= probability):
                    user.addAccessory(acc_koronavirus)
                    updateUser(user)
                    counter_infected = counter_infected + 1
                    send_message_to_admin(f'⚠️🦇 Внимание! \n {user.getLogin()} заражен коронавирусом!')

    if counter_infected > 0:
        sec = int(randrange(int(getSetting(code='PROBABILITY', name='PANDING_WAIT_START_1')), int(getSetting(code='PROBABILITY', name='PANDING_WAIT_END_1'))))
        tz = config.SERVER_MSK_DIFF
        pending_date = datetime.now() + timedelta(seconds=sec, hours=tz.hour)

        pending_messages.insert_one({ 
            'chat_id': chat,
            'reply_message': None,
            'create_date': datetime.now().timestamp(),
            'user_id': logins[0],  
            'state': 'WAIT',
            'pending_date': pending_date.timestamp(),
            'dialog_flow_text': 'koronavirus_new_member',
            'text': f'Количество заразившихся {counter_infected}'})

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def main_message(message):
    #write_json(message.json)

    privateChat = ('private' in message.chat.type)
    logger.info(f'chat:{message.chat.id}:{privateChat}:{message.from_user.username} : {message.text}')

    if message.from_user.username == None:
        return

    black_list = getSetting(code='BLACK_LIST', name=message.from_user.username)
    if black_list:
        send_messages_big(message.chat.id, text=f'{message.from_user.username} заслужил пожизненный бан {black_list}', reply_markup=None)
        send_message_to_admin(f'⚠️Внимание! \n {message.from_user.username} написал Джу:\n\n {message.text}')
        return

    check_and_register_tg_user(message.from_user.username)

    if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
        may_be_infected = []
        may_be_infected.append(message.reply_to_message.from_user.username)
        may_be_infected.append(message.from_user.username)
        koronavirus(may_be_infected, message.chat.id)

    userIAm = getUserByLogin(message.from_user.username)
    if userIAm:
        if userIAm.isAccessoryItem(acc_koronavirus):
            global INFECT_PROBABILITY
            INFECT_PROBABILITY = float(getSetting(code='PROBABILITY', name='KORONOVIRUS'))
        else:
            if INFECT_PROBABILITY > 0.1:
                may_be_infected = []
                may_be_infected.append(message.from_user.username)
                koronavirus(may_be_infected, message.chat.id)
                INFECT_PROBABILITY = INFECT_PROBABILITY / 2
            else:
                INFECT_PROBABILITY = 0


    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        user = getUserByLogin(message.from_user.username)
        name = message.from_user.username
        if user:
            name = user.getName()
        send_messages_big(message.chat.id, text=f'{name} хотел что-то сказать, но у него получилось лишь:\n{getResponseDialogFlow(message, "user_banned").fulfillment_text}' )
        return
    
    callJugi = (privateChat 
                            or message.text.lower().startswith('джу') 
                            or (message.reply_to_message 
                                and message.reply_to_message.from_user.is_bot 
                                and message.reply_to_message.from_user.username in ('FriendsBrotherBot', 'JugiGanstaBot') )
                )
    findUser = not (userIAm == None)

    if message.forward_from_chat and message.forward_from_chat.username == 'wwkeeperhorn' and ' постиг ' in message.text:
        # ⚙️Машенька постиг 8-й 🏵Дзен !
        name = message.text.split(' постиг ')[0]
        name = name.replace('⚙️', '@').replace('🔪', '@').replace('💣', '@').replace('⚛️', '@').replace('👙', '@')
        name = name.split('@')[1].split(' ')[0].strip()
        num_dzen = message.text.split(' постиг ')[1].split('-й')[0]
        fraction = getWariorFraction(message.text)
        acc = f'🏵️ Грамота за {num_dzen}-й Дзен' 
        
        user = getUserByName(name)
        if user:
            if user.isAccessoryItem(acc):
                pass
            else:
                user.addAccessory(acc)
                updateUser(user)
                send_messages_big(message.chat.id, text=user.getName() + '!\n' + getResponseDialogFlow(message, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {acc}') 
        return


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

            if 'ТОП ИГРОКОВ:' in message.text:
                ww = wariors.fromTopToWariorsBM(message.forward_date, message, registered_wariors)
                for warior in ww:
                    update_warior(warior)
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
                return

            # if privateChat or (not isRegisteredUserLogin(message.from_user.username)) or isGoatSecretChat(message.from_user.username, message.chat.id):
            #     pass
            # else:
            #     censored(message)
            
            user = users.User(message.from_user.username, message.forward_date, message.text)
            
            if findUser==False:  
                if 'Подробности /me' in message.text or (not privateChat): 
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'pip_me').fulfillment_text)
                    return
                else:
                    acc = random.sample(getSetting(code='ACCESSORY', name='PIP_BOY'), 1)[0]["value"]
                    user.setChat(message.chat.id)
                    user.addAccessory(acc)
                    user.setPing(True)
                    x = registered_users.insert_one(json.loads(user.toJSON()))
                    updateUser(None)

                    send_messages_big(message.chat.id, text=f'Поздравляю! \nТебе выдали "{acc}" и вытолкнули за дверь!')
                    send_message_to_admin(f'⚠️Внимание! Зарегистрировался новый пользователь.\n {user.getProfile()}')
            else:
                updatedUser = users.updateUser(user, users.getUser(user.getLogin(), registered_users))
                updateUser(updatedUser)

            addToUserHistory(user)
                
            if privateChat:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'setpip').fulfillment_text)
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'deceive').fulfillment_text) 
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'FIGHT!' in message.text):
        # if privateChat or isGoatSecretChat(message.from_user.username, message.chat.id):
        #     pass
        # else:
        #     censored(message)

        ww = wariors.fromFightToWarioirs(message.forward_date, message, USERS_ARR, battle)
        if ww == None:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'dublicate').fulfillment_text)
            return
        for warior in ww:
            update_warior(warior)

        send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and '/accept' in message.text and '/decline' in message.text):
        #write_json(message.json)
        if hasAccessToWariors(message.from_user.username):
            fraction = getWariorFraction(message.text.split(' из ')[1].strip())
            warior = getWariorByName(message.text.split('👤')[1].split(' из ')[0], fraction)

            if warior == None:
                send_messages_big(message.chat.id, text='Ничего о нем не знаю!')
            elif (warior and warior.photo):
                bot.send_photo(message.chat.id, warior.photo, warior.getProfile())
            else:
                send_messages_big(message.chat.id, text=warior.getProfile())
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'Ты оценил обстановку вокруг.' in message.text and 'Рядом кто-то есть.' in message.text):
        #write_json(message.json)
        if hasAccessToWariors(message.from_user.username):
            strings = message.text.split('\n')
            i = 0
            find = False
            report = ''
            counter = 0
            report_goat_info = ''
            goats = []

            for s in strings:
                if '|' in strings[i]:
                    name = strings[i]
                    fraction = getWariorFraction(strings[i])
                    name = name.replace('⚙️', '@').replace('🔪', '@').replace('💣', '@').replace('⚛️', '@').replace('👙', '@')
                    name = name.split('@')[1].split('|')[0].strip()
                    warior = getWariorByName(name, fraction)
                    if warior:
                        if warior.getGoat():
                            findGoat = False
                            for g in goats:
                                if g['name'] == warior.getGoat():
                                   g.update({'counter': g['counter']+1})
                                   findGoat = True
                            
                            if not findGoat:
                                goat = {}
                                goat.update({'counter': 1})
                                goat.update({'name': warior.getGoat()})
                                goats.append(goat)

                        find = True
                        report = report + f'{warior.getProfileSmall()}\n'
                    else:
                        counter = counter + 1    
                if '...И еще' in strings[i]:
                    live = int(strings[i].split('...И еще')[1].split('выживших')[0].strip())
                    counter = counter + live
                i = i + 1
            if counter > 0:
                report = report + f'...И еще {str(counter)} выживших.'
            
            if len(goats) > 0:
                for goat in goats:
                    report_goat_info = report_goat_info + f'🐐 {goat["name"]}: <b>{goat["counter"]}</b>\n'
                report_goat_info = report_goat_info + '\n'

            if not find:
                send_messages_big(message.chat.id, text='Не нашел никого!')
            else:
                send_messages_big(message.chat.id, text=report_goat_info + report)
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'Ты уже записался.' in message.text):
        #write_json(message.json)
        if hasAccessToWariors(message.from_user.username):
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'deceive').fulfillment_text)
                return

            u = getUserByLogin(message.from_user.username)
            u.setRaidLocation(1)
            updateUser(u)
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'Ты занял позицию для ' in message.text and 'Рейд начнётся через' in message.text):
        #write_json(message.json)
        if hasAccessToWariors(message.from_user.username):
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'deceive').fulfillment_text)
                send_messages_big(message.chat.id, text='Шли мне свежее сообщение "Ты уже записался."')
                return

            u = getUserByLogin(message.from_user.username)
            u.setRaidLocation(1)
            updateUser(u)
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
        return
    elif (message.forward_from and 'Панель банды.' in message.text and message.forward_from.username == 'WastelandWarsBot'):
        #write_json(message.json)
        if hasAccessToWariors(message.from_user.username):

            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'deceive').fulfillment_text)
                return

            strings = message.text.split('\n')
            i = 0
            band = ''
            allrw = 0
            allcounter = 0
            onraidrw = 0
            onraidcounter = 0
            onraidReport = ''
            onraidusers = []

            report = 'Информация о рейдерах!\n'
            fuckupraidrw = 0
            fuckupraidcounter = 0
            fuckupusersReport = ''
            fuckupusers = []
            alianusersReport = ''
            aliancounter = 0

            # 🤘👊🏅
            for s in strings:
                if '🏅' in strings[i] and '🤘' in strings[i]:
                    band = strings[i].split('🤘')[1].split('🏅')[0].strip()
                    
                    if not isGoatBoss(message.from_user.username):
                        if not isUsersBand(message.from_user.username, band):
                            send_messages_big(message.chat.id, text=f'Ты принес панель банды {band}\n' + getResponseDialogFlow(message, 'not_right_band').fulfillment_text)
                            return
                    
                    registered_users.update_many(
                        {'band': band},
                        { '$set': { 'raidlocation': None} }
                    )
                    updateUser(None)

                if '👂' in strings[i]:
                    name = strings[i]
                    name = name.replace('⚙️', '@').replace('🔪', '@').replace('💣', '@').replace('⚛️', '@').replace('👙', '@')
                    name = name.split('@')[1].split('👂')[0].strip()
                    u = getUserByName(name)
                    
                    if u and (not u.getBand() == band):
                        u.setBand(band)

                    spliter = ''
                    km = ''
                    if '📍' in strings[i]:
                        km =  int(strings[i].split('📍')[1].split('km')[0].strip())
                        spliter = '📍'

                    elif '👟' in strings[i]:
                        km =  int(strings[i].split('👟')[1].split('km')[0].strip())
                        spliter = '👟'
                    else:
                        km =  int(strings[i].split('👊')[1].split('km')[0].strip())
                        spliter = '👊'


                    if u:
                        allrw = allrw + u.getRaidWeight()
                        allcounter = allcounter + 1
                        u.setWastelandLocation(km)
                        u.setMaxkm(km)
                        if '👊' in strings[i]:
                            onraidcounter = onraidcounter + 1
                            onraidrw = onraidrw + u.getRaidWeight()
                            u.setRaidLocation(km)
                            onraidusers.append(u)
                        else:
                            fuckupraidrw = fuckupraidrw + u.getRaidWeight()
                            fuckupusers.append(u)
                        updateUser(u)
                    else:
                        aliancounter  = aliancounter + 1
                        alianusersReport = alianusersReport + f'{aliancounter}. {name} {spliter}{km}км\n'
                    
                i = i + 1
            
            report = report + f'🤘 <b>{band}</b>\n\n' 
            if onraidcounter > 0:
                report = report + f'🧘‍♂️ <b>на рейде</b>: <b>{onraidcounter}/{allcounter}</b>\n'
                i = 1
                for onu in sorted(onraidusers, key = lambda i: i.getRaidWeight(), reverse=True):
                    report = report +  f'{i}.{onu.getFraction()[0:1]}{onu.getRaidWeight()} {onu.getName()} 👊{onu.getRaidLocation()}км\n'
                    i = i + 1
                report = report + f'\n<b>Общий вес</b>: 🏋️‍♂️{onraidrw}/{allrw} <b>{str(int(onraidrw/allrw*100))}%</b>\n'
            report = report + '\n'
            if fuckupraidrw > 0:
                report = report + '🐢 <b>Бандиты в проёбе</b>:\n'
                i = 1
                for offu in sorted(fuckupusers, key = lambda i: i.getRaidWeight(), reverse=True):
                    ping = ''
                    if not offu.isPing():
                        ping = '🔕' 
                    report = report +  f'{i}.{offu.getFraction()[0:1]}{offu.getRaidWeight()} {ping} {offu.getNameAndGerb()} 📍{offu.getWastelandLocation()}км\n'
                    i = i + 1
            report = report + '\n'
            if alianusersReport == '':
                pass
            else:
                report = report + '🐀 <b>Крысы в банде</b> (нет регистрации):\n'
                report = report + alianusersReport
            
            if privateChat or isGoatSecretChat(message.from_user.username, message.chat.id):
                bot.delete_message(message.chat.id, message.message_id)
                send_messages_big(message.chat.id, text=report)
            else:
                pass
                #censored(message)
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' 
                and 
                    (
                        (message.text.startswith('Теперь') and 'под контролем' in message.text)
                        or
                        (message.text.startswith('✊️Захват') and ('Захват начался!' in message.text or 'Вы автоматически отправитесь на совместную зачистку локации' in message.text)) 
                    )
                ):
        if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'deceive').fulfillment_text)
            return        
        
        band = ''
        dungeon_km = 0
        dungeon_name = ''
        usesrOnDungeon = []
        text = ''
        for s in message.text.split('\n'):
            #Теперь Гексагон под контролем 🤘АртхǁȺǁус
            if s.startswith('Теперь'): 
                band = s.split('🤘')[1].split('!')[0]
                dungeon_tmp = s.split('Теперь')[1].split('под контролем')[0].strip().lower()
                for d in getSetting(code='DUNGEONS'):
                    if dungeon_tmp in d['name'].lower():
                        dungeon_km = int(d['value'])
                        dungeon_name = d['name']     
                        break
                text = f'✊️Теперь <b>{dungeon_km}км {dungeon_name}</b>\nпод контролем 🤟<b>{band}</b>\n\nУдарный отряд\n'
       
            elif s.startswith('✊️Захват'):
                for d in getSetting(code='DUNGEONS'):
                    if tools.deEmojify(s.replace('✊️Захват ','')) in d['name'] :
                        dungeon_name = d['name']
                        dungeon_km = int(d['value'])
                        break
            elif s.startswith('🤘'):
                band = s.replace('🤘','')
                text = f'✊️Захват <b>{dungeon_name}</b>\n🤘{band}\n\n'
            elif 'в сборе.' in s:
                text = text + f'<b>{s}</b>' + '\n'
            elif s.startswith('👊'):
                name = s.split('👊')[1].split('❤️')[0].strip()
                user = getUserByName(name)
                if user:
                    usesrOnDungeon.append(user)
                else:
                    print(f'Не найден бандит {name}')
        
        i = 1
        for user in usesrOnDungeon:
            gerb = user.getSettingValue("🃏Мой герб")
            if gerb == None: gerb = ''

            text = text + f'  {i}. {gerb}<b>{user.getName()}</b>\n'
            i = i + 1

        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=text)

        goatName = getMyGoatName(usesrOnDungeon[0].getLogin()) 
        
        dresult = dungeons.aggregate([ 
            {   "$match": {
                        "band": band,
                        "dungeon_km": dungeon_km,
                        "state": "NEW"
                    } 
            },
            {   "$group": {
                "_id": "$date", 
                "count": {
                    "$sum": 1}}},
                
            {   "$sort" : { "count" : -1 } }
            ])
        
        date_arr = []
        for d in dresult:
            date_arr.append(d.get("_id"))

        if len(date_arr) == 0:
            tz = config.SERVER_MSK_DIFF
            dungeon_date = (datetime.now() + timedelta(hours=tz.hour)).timestamp()
            for user in usesrOnDungeon:
                row = {}
                row.update({'date': dungeon_date})
                row.update({'login': user.getLogin()})
                row.update({'band': band})
                row.update({'goat': goatName})
                row.update({'dungeon_km': dungeon_km})
                row.update({'dungeon': dungeon_name})
                row.update({'signedup': True})
                row.update({'invader': True})
                row.update({'state': 'CLOSED'})
                dungeons.insert_one(row)
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
            return
        elif len(date_arr) == 1:
            dungeon_date = date_arr[0]
            for user in usesrOnDungeon:
                row = {}
                row.update({'date': dungeon_date})
                row.update({'login': user.getLogin()})
                row.update({'band': band})
                row.update({'goat': goatName})
                row.update({'dungeon_km': dungeon_km})
                row.update({'dungeon': dungeon_name})
                row.update({'signedup': True})
                row.update({'invader': True})
                row.update({'state': 'CLOSED'})

                newvalues = { "$set": row }
                result = dungeons.update_one({
                    'login': user.getLogin(), 
                    'date': dungeon_date,
                    'band': band,
                    'goat': goatName,
                    'dungeon_km': dungeon_km
                    }, newvalues)
                if result.matched_count < 1:
                    dungeons.insert_one(row)
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
        else:
            markupinline = InlineKeyboardMarkup()
            
            for date in date_arr:
                dt = datetime.fromtimestamp(date)
                markupinline.add(
                    InlineKeyboardButton(f"{dt.hour}:{d.minute}", callback_data=f"commit_dungeon_time|{dt.timestamp()}|{band}|{dungeon_km}"),
                    InlineKeyboardButton(f"Готово ✅", callback_data=f"commit_dungeon_yes|{dt.timestamp()}|{band}|{dungeon_km}"),
                    InlineKeyboardButton(f"Закрыть ⛔", callback_data=f"commit_dungeon_no|{dt.timestamp()}|{band}|{dungeon_km}")
                )
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text, reply_markup=markupinline)

    if message.forward_from and message.forward_from.username == 'WastelandWarsBot' and '❤️' in message.text and '🍗' in message.text and '🔋' in message.text and '👣' in message.text:
        if hasAccessToWariors(message.from_user.username):
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                pass
            else:
                # сохраняем км, если он больше максимального
                km = int(message.text.split('👣')[1].split('км')[0])
                if userIAm.getMaxkm() < km:
                    userIAm.setMaxkm(km)
                    updateUser(userIAm)

    # Заменяем в сообщениях от ВВ все цифры 
    #     if not privateChat:
    #         if not isGoatSecretChat(message.from_user.username, message.chat.id):
    #             replacements =  {
    #                                 "0": str(random.randint(1,9)), 
    #                                 "1": str(random.randint(1,9)), 
    #                                 "2": str(random.randint(1,9)), 
    #                                 "3": str(random.randint(1,9)), 
    #                                 "4": str(random.randint(1,9)), 
    #                                 "5": str(random.randint(1,9)), 
    #                                 "6": str(random.randint(1,9)), 
    #                                 "7": str(random.randint(1,9)), 
    #                                 "8": str(random.randint(1,9)), 
    #                                 "9": str(random.randint(1,9)) 
    #                             }
    #             text = "".join([replacements.get(c, c) for c in message.text])
    #             bot.delete_message(message.chat.id, message.message_id)
    #             send_messages_big(message.chat.id, text=f'🗣 {userIAm.getName()} ({userIAm.getLogin()}):\n\n'+text)
    #             return
    #     return




    if 'gratz' in message.text.lower() or 'грац' in message.text.lower() or 'грац!' in message.text.lower() or  'лол' in message.text.lower() or 'lol' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='EMOTIONS'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_LOVE'), 1)[0]['value'])
            return
    if 'збс' in message.text.lower() or 'ура' in message.text.lower() or '))' in message.text.lower() or 'ахах' in message.text.lower() or 'ебать' in message.text.lower() or 'ебаать' in message.text.lower() or 'ебааать' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='EMOTIONS'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_LIKE'), 1)[0]['value'])
            return
    if 'пидорасы' == message.text.lower() or 'пидоры' == message.text.lower() or 'писец' == message.text.lower() or 'пиздец' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='EMOTIONS'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_DEAD'), 1)[0]['value'])
            return
    if 'тык' == message.text.lower() or 'тык!' == message.text.lower() or 'тык!)' == message.text.lower() or 'тык)' == message.text.lower() or ' тык' in message.text.lower() or ' тык' in message.text.lower():
        if not isGoatSecretChat(message.from_user.username, message.chat.id):
            if (random.random() <= float(getSetting(code='PROBABILITY', name='YES_STICKER'))):
                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_FINGER_TYK'), 1)[0]['value'])
                logger.info(mem_top())
                return
    if 'да' == message.text.lower() or 'да!' == message.text.lower() or 'да?' == message.text.lower() or 'да!)' == message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='YES_STICKER'))):
            if not isGoatSecretChat(message.from_user.username, message.chat.id):
                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_DA_PINDA'), 1)[0]['value'])
                return
    if 'нэт' == message.text.lower() or 'неа' == message.text.lower() or 'нет' == message.text.lower() or 'нет!' == message.text.lower() or 'нет?' == message.text.lower() or 'нет!)' == message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='NO_STICKER'))):
            if not isGoatSecretChat(message.from_user.username, message.chat.id):
                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_NO_PINDA'), 1)[0]['value'])
                return
    if 'а' == message.text.lower() or 'а!' == message.text.lower() or 'а?' == message.text.lower() or 'а!)' == message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='A_STICKER'))):
            if not isGoatSecretChat(message.from_user.username, message.chat.id):
                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_A_PINDA'), 1)[0]['value'])
                return
    if 'тебя буквально размазали' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='YES_STICKER'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_SALUTE'), 1)[0]['value'])
            return       
    if 'утречка' in message.text.lower() or 'добрым утром' in message.text.lower() or 'доброго утра' in message.text.lower() or 'доброго утречка' in message.text.lower() or 'доброе утро' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='MORNING_STICKER'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_MORNING'), 1)[0]['value'])
            return 
    if 'пойду спать' in message.text.lower() or 'я спать' in message.text.lower() or 'доброй ночи' in message.text.lower() or 'спокойной ночи' in message.text.lower() or 'спатки' in message.text.lower() or 'сладких снов' in message.text.lower() or 'добрых снов' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='NIGHT_STICKER'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_NIGHT'), 1)[0]['value'])
            return 

    # Хуификация
    if message.reply_to_message and 'хуифицируй' in message.text.lower():
        if not isGoatSecretChat(message.from_user.username, message.chat.id):
            phrases = message.reply_to_message.text.split('\n')
            text = ''
            for words in phrases:
                responce = getResponseHuificator(words)
                text = text + responce + '\n'
            reply_to_big(message.reply_to_message.json, text)
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
        return
    # Рассылка в чаты
    if privateChat and isGoatBoss(message.from_user.username) and message.reply_to_message:
        if message.text.lower().startswith('рассылка в'):
            if not isGoatBoss(message.from_user.username):
                if not isAdmin(message.from_user.username):
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                    return
            goat = getMyGoat(message.from_user.username)
            if goat:
                if 'нии' in message.text.lower():
                    if message.reply_to_message.sticker:
                        bot.send_sticker(goat['chats']['secret'], message.reply_to_message.sticker.file_id)
                    elif message.reply_to_message.photo:
                        bot.send_photo(goat['chats']['secret'], message.reply_to_message.photo[len(message.reply_to_message.photo)-1].file_id)
                    else:
                        send_messages_big(goat['chats']['secret'], message.reply_to_message.text)
                elif 'флуд' in message.text.lower():
                    if message.reply_to_message.sticker:
                        bot.send_sticker(goat['chats']['info'], message.reply_to_message.sticker.file_id)
                    elif message.reply_to_message.photo:
                        bot.send_photo(goat['chats']['info'], message.reply_to_message.photo[len(message.reply_to_message.photo)-1].file_id)
                    else:
                        send_messages_big(goat['chats']['info'], message.reply_to_message.text)   
                else:
                    send_messages_big(message.chat.id, 'Не понял! Нет такого чата!')

                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
                return
    
    if hasAccessToWariors(message.from_user.username):
        #write_json(message.json)
        if (callJugi and (message.text and ('анекдот' in message.text.lower() or 'тост' in message.text.lower()))) :
            type_joke = 11
            if ('анекдот' in message.text.lower()):
                type_joke = 11
            elif ('тост' in message.text.lower()):
                type_joke = 16  
            bot.send_chat_action(message.chat.id, 'typing')
            report = ''
            try:
                r = requests.get(f'{config.ANECDOT_URL}={type_joke}', verify=False, timeout=7)
                report = r.text[12:-2]
            except:
                report = 'Чёт я приуныл... Ничего в голову не идет... Давай позже.'
            
            send_messages_big(message.chat.id, report)
        elif (callJugi and ('это залёт' in message.text.lower() or 'это залет' in message.text.lower())
                    and message.reply_to_message
                    and message.text):
            login = message.reply_to_message.from_user.username

            if isGoatBoss(login) or isAdmin(login):
                login = message.from_user.username

            if isGoatSecretChat(message.from_user.username, message.chat.id):
                if not isGoatBoss(message.from_user.username):
                    login = message.from_user.username

            if config.BOT_LOGIN == login:
                login = message.from_user.username

            user = getUserByLogin(login)
            if not user:
                send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                return

            if not user.getBand():
                send_messages_big(message.chat.id, text=f'У бандита {login} нет банды!')
                return

            if not isUsersBand(message.from_user.username, user.getBand()):
                if not isAdmin(message.from_user.username):
                    send_messages_big(message.chat.id, text=f'Бандит {login} не из банд твоего козла!')
                    return
            
            sec = int(randrange(228, int(getSetting(code='PROBABILITY',name='FUNY_BAN'))))
            tz = config.SERVER_MSK_DIFF

            ban_date = datetime.now() + timedelta(seconds=sec, minutes=tz.minute, hours=tz.hour)

            if user.getTimeBan():
                ban_date = datetime.fromtimestamp(user.getTimeBan()) + timedelta(seconds=sec) 

            user.setTimeBan(ban_date.timestamp())
            report = f'{user.getName()} будет выписан бан! Злой Джу определил, что ⏰{sec} секунд(ы) будет достаточно!'
            updateUser(user)
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text + f'\n{report}')
        elif (callJugi and 'статус ' in message.text.lower() and ' @' in message.text):
            login = message.text.split('@')[1].split(' ')[0].strip()
            
            findLogin = False
            for x in registered_users.find({"login": f"{login}"}):
                findLogin = True

            if (isAdmin(message.from_user.username) or message.from_user.username == login):
                pass
            else:
                findLogin = False

            newvalues = { "$set": { "status": message.text.split(login)[1].strip() } }
            if not findLogin:
                registered_users.update_one({"login": f"{message.from_user.username}"}, newvalues)
                send_messages_big(message.chat.id, text="Из-за своей криворкукости ты вьебал статус самому себе. Теперь твой статус '" + message.text.split(login)[1].strip() + "'")
            else:
                registered_users.update_one({"login": f"{login}"}, newvalues)
                send_messages_big(message.chat.id, text='✅ Готово')
            
            updateUser(None)  
        elif (callJugi and 'статистика @' in message.text.lower()):
            if not isGoatBoss(message.from_user.username):
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                return

            login = tools.deEmojify(message.text.split('@')[1].strip())
            user = getUserByLogin(login)
            if user:
                counter = pip_history.find({'login': user.getLogin()}).count()
                if counter == 0:
                    bot.send_message(message.chat.id, text='Сбрось мне хоть один pip!')
                    return
               
                N = 0
                if counter > 10:
                    N = 10
                else:
                    counter = 0
                cursor = pip_history.find({'login': user.getLogin()}).skip(counter - N)
                matplot.getPlot(cursor, user.getLogin())
                img = open(config.PATH_IMAGE + f'plot_{user.getLogin()}.png', 'rb')
                bot.send_photo(message.chat.id, img)
            else:
                send_messages_big(message.chat.id, text=f'Не найден бандит {login}')
        elif (callJugi and 'профиль @' in message.text.lower()):
            updateUser(None)
            name = tools.deEmojify(message.text.split('@')[1].strip())
            if isGoatBoss(message.from_user.username):
                login = message.text.split('@')[1].strip()
                if isRegisteredUserName(name) or isRegisteredUserLogin(login):
                    user = getUserByLogin(login)
                    if not user:
                        user = getUserByName(name)

                    if user:
                        send_messages_big(message.chat.id, text=user.getProfile())
                else:
                    send_messages_big(message.chat.id, text=f'В базе зарегистрированнных бандитов {login} не найден')

            for x in registered_wariors.find({'name':f'{name}'}):
                print(f'find {name}')
                warior = wariors.importWarior(x)
                if (warior and warior.photo):
                    try:
                        bot.send_photo(message.chat.id, warior.photo, warior.getProfile())
                    except:
                        send_messages_big(message.chat.id, text=warior.getProfile())
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile())
        elif callJugi and ('уволить @' in message.text.lower() or 'удалить @' in message.text.lower()):
            if not isGoatBoss(message.from_user.username):
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                return

            login = message.text.split('@')[1].strip()
            user = getUserByLogin(login)
            if not user:
                send_messages_big(message.chat.id, text=f'Нет зарегистрированного бандита с логином {login}!')
                return

            if not isUsersBand(message.from_user.username, user.getBand()):
                send_messages_big(message.chat.id, text=f'Бандит {login} не из банд твоего козла!')
                return

            myquery = { "login": f"{user.getLogin()}" }
            doc = registered_users.delete_one(myquery)
            updateUser(None)

            if doc.deleted_count == 0:
                send_messages_big(message.chat.id, text=f'{login} не найден в бандитах!')
            else:                 
                send_messages_big(message.chat.id, text=f'{login} уволен нафиг!')
        elif (callJugi and 'профиль' in message.text.lower() ):
            if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                pass
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                return

            updateUser(None)
            user = users.getUser(message.from_user.username, registered_users)
            if user:
                warior = getWariorByName(user.getName(), user.getFraction())
                if (warior and warior.photo):
                    try:
                        bot.send_photo(message.chat.id, warior.photo, user.getProfile())
                    except:
                        send_messages_big(message.chat.id, text=user.getProfile())
                else:
                    send_messages_big(message.chat.id, text=user.getProfile())
            else:
                send_messages_big(message.chat.id, text='С твоим профилем какая-то беда... Звони в поддержку пип-боев!')
        elif callJugi:

            text = message.text 
            if text.lower().startswith('джу'):
                text = message.text[3:]

            result = getResponseDialogFlow(message, text)
            response = result.fulfillment_text
            parameters = result.parameters
            if response:
                if (response.startswith('jugi:')):
                    #jugi:ping:Артхаус
                    if 'ping' == response.split(':')[1]:
                        # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                        #     pass
                        # else:
                        #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                        #     return

                        # Собираем всех пользоватлей с бандой Х
                        band = response.split(':')[2]
                        if response.split(":")[2] == '*':
                            band = userIAm.getBand()
                        if band == 'all':
                            if not isGoatBoss(message.from_user.username):
                                if not isAdmin(message.from_user.username):
                                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                                    return
                        else:
                            if not isUsersBand(message.from_user.username, band):
                                send_messages_big(message.chat.id, text=f'Ты просил собраться банду 🤟{band}\n' + getResponseDialogFlow(message, 'not_right_band').fulfillment_text)
                                return

                        first_string = f'{tools.deEmojify(message.from_user.first_name)} просит собраться банду\n<b>🤟{band}</b>:\n'
                        usersarr = []

                        for registered_user in registered_users.find():
                            user = users.importUser(registered_user)
                            registered_user.update({'weight': user.getRaidWeight()})
                            registered_user.update({'ping': user.isPing()})
                            if band=='all':
                                if user.getBand() in getGoatBands(getMyGoatName(userIAm.getLogin())): 
                                    usersarr.append(registered_user)
                            else:
                                if user.getBand() == band: 
                                    usersarr.append(registered_user)

                        # Пингуем
                        counter = 0
                        pingusers = []
                        report = f''
                        for pu in sorted(usersarr, key = lambda i: i['weight'], reverse=True):
                            counter = counter + 1
                            pingusers.append(pu)
                            if pu["ping"] == True:
                                report = report + f'{counter}. @{pu["login"]} \n'
                            else:
                                report = report + f'{counter}. 🔕{pu["login"]} \n'
                            if counter % 5 == 0:
                                send_messages_big(message.chat.id, text=first_string + report)
                                pingusers = []
                                report = f''

                        if len(pingusers) > 0:
                            send_messages_big(message.chat.id, text=first_string + report)
                    elif 'setping' == response.split(':')[1]:
                        # jugi:setping:True:login
                        login = response.split(":")[3].replace('@','')
                        if login == '*':
                            login = message.from_user.username
                        else:
                            if not isGoatBoss(message.from_user.username):
                                if not isAdmin(message.from_user.username):
                                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                                    return
                                    
                        user = getUserByLogin(login)
                        if not user:
                            send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                            return 
                        
                        user.setPing(response.split(":")[2] == 'True')
                        updateUser(user)
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
                    elif 'birthday' == response.split(':')[1]:
                        # jugi:birthday:2020-02-02
                        userIAm.setBirthday(parse(response.split(':birthday:')[1]).timestamp())
                        updateUser(userIAm)
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)        
                    elif 'flex' == response.split(':')[1]:
                        pass
                        # jugi:flex:$bool
                        # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                        #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                        #     return

                        # if eval(response.split(':')[2]):
                        #     counter = int(randrange(int(getSetting(code='PROBABILITY', name='JUGI_FLEX'))))

                        #     send_messages_big(message.chat.id, f'Ща заебашу {counter} стикеров!')
                        #     bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_GO_FLEX'), 1)[0]['value'])
                            
                        #     global flexFlag
                        #     flexFlag = True
                        #     for i in range(0, counter):
                        #         if flexFlag:
                        #             bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_FLEX'), 1)[0]['value'])
                        #             time.sleep(random.randint(1000,3000) / 1000)
                        #         else:
                        #             send_messages_big(message.chat.id, text='Пипец ты кайфолом!')
                        #             bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_CRY'), 1)[0]['value'])
                        #             flexFlag = False
                        #             break
                        #     if flexFlag:
                        #         bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_END_FLEX'), 1)[0]['value'])
                        #         send_messages_big(message.chat.id, f'Хорошо, заебашил {counter} стикеров!')
                        #         flexFlag = False
                        # else:
                        #     flexFlag = False
                        #     send_messages_big(message.chat.id, text='Остановиливаю флекс нахОй!')
                        #     return
                    elif 'youbeautiful' == response.split(':')[1]:
                        # jugi:youbeautiful:text
                        photo = random.sample(getSetting(code='STICKERS', name='BOT_LOVE'), 1)[0]['value']
                        bot.send_sticker(message.chat.id, photo)
                        send_messages_big(message.chat.id, text=f'{response.split(":")[2]}')
                    elif 'youbadbot' == response.split(':')[1]:
                        # jugi:youbadbot
                        sec = int(randrange(288, int(getSetting(code='PROBABILITY', name='JUGI_BAD_BOT_BAN'))))
                        tz = config.SERVER_MSK_DIFF
                        ban_date = datetime.now() + timedelta(seconds=sec, hours=tz.hour)
                        userIAm.setTimeBan(ban_date.timestamp())

                        report = f'<b>{response.split(":")[2]}</b>\n<b>{userIAm.getName()}</b> выписан бан! ⏰{sec} секунд(ы) в тишине научат тебя хорошему поведению!'
                        updateUser(userIAm)

                        photo = random.sample(getSetting(code='STICKERS', name='BOT_FUCKOFF'), 1)[0]['value']
                        bot.send_sticker(message.chat.id, photo)
                        send_messages_big(message.chat.id, text=f'\n{report}')
                    elif 'planrade' == response.split(':')[1]:
                        # jugi:planrade:$date

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                            return

                        goat = getMyGoatName(message.from_user.username)

                        tz = config.SERVER_MSK_DIFF
                        plan_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
                        raid_date = plan_date

                        if response.split(response.split(":")[1])[1][1:].strip() == '*':
                            raid_date = raid_date.replace(minute=0, second=0, microsecond=0)

                            if plan_date.hour > 17 or plan_date.hour < 1:
                                if not plan_date.hour < 1:
                                    raid_date = raid_date + timedelta(days=1)
                                raid_date = raid_date.replace(hour=1)
                            elif plan_date.hour > 1 and plan_date.hour < 9:
                                raid_date = raid_date.replace(hour=9)
                            else:
                                raid_date = raid_date.replace(hour=17)
                        else:
                            raid_date = parse(response.split(response.split(":")[1])[1][1:])
                        
                        markupinline = InlineKeyboardMarkup()

                        for radeloc in plan_raids.find({
                                    'rade_date': { 
                                        '$gte' : plan_date.timestamp()
                                    }, 
                                    'goat': goat}): 
                            find = False
                            try:
                                users_onraid = radeloc['users']
                                for u in users_onraid:
                                    if u == message.from_user.username:
                                        find = True
                            except:
                                pass


                            
                            #if not find:
                            markupinline.add(InlineKeyboardButton(f"{radeloc['rade_text']}", callback_data=f"capture_{radeloc['rade_location']}_{raid_date.timestamp()}_{goat}"))
              
                        text = get_raid_plan(raid_date, goat)

                        msg = send_messages_big(message.chat.id, text=text, reply_markup=markupinline)
                    elif 'onrade' == response.split(':')[1]:

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                            return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoatName(message.from_user.username)

                        if not getMyGoatName(message.from_user.username) == goatName:
                            send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
                            return

                        for goat in getSetting(code='GOATS_BANDS'):
                            if goatName == goat.get('name'):
                                report = radeReport(goat)
                                send_messages_big(message.chat.id, text=report)
                    elif 'statistic' == response.split(':')[1]:
                        # jugi:statistic:*
                        if not isGoatBoss(message.from_user.username):
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                                return

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                            return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoatName(message.from_user.username)

                        if not getMyGoatName(message.from_user.username) == goatName:
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
                                return

                        report = statistic(goatName)
                        send_messages_big(message.chat.id, text=report) 
                    elif 'clearrade' == response.split(':')[1]:
                        # jugi:clearrade:*
                        if not isAdmin(message.from_user.username):
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_admin').fulfillment_text)
                            return

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                            return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoatName(message.from_user.username)

                        if not getMyGoatName(message.from_user.username) == goatName:
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow(message, 'shot_you_cant').fulfillment_text)
                                return
                        registered_users.update_many(
                            {'band':{'$in':getGoatBands(goatName)}},
                            { '$set': { 'raidlocation': None} }
                        )

                        updateUser(None)
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)        
                    elif 'totalizator' == response.split(':')[1]:
                        # jugin:totalizator:$any
                        pass
                    elif 'pickupaccessory' == response.split(':')[1]:
                        #jugi:pickupaccessory:$any

                        if not isGoatBoss(message.from_user.username):
                            if not isAdmin(message.from_user.username):
                                bot.reply_to(message, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                                return

                        login = response.split(':')[2].replace('@','').strip()         
                        user = getUserByLogin(login)

                        if not user:
                            send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                            return

                        markupinline = InlineKeyboardMarkup()

                        accessory = ''
                        if user.getAccessory() and len(user.getAccessory())>0:
                            i = 0
                            for acc in user.getAccessory():
                                accessory = accessory + f'▫️ {acc}\n'
                                markupinline.add(InlineKeyboardButton(f"{acc}", callback_data=f"pickupaccessory|{login}|{i}"))
                                i = i + 1
                        if not accessory == '':
                            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"pickupaccessory_exit|{login}"))
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message, None, 'shot_message_pickupaccessory').fulfillment_text + f'\n\n{accessory}\nЧто изьять?', reply_markup=markupinline)
                        else:
                            msg = send_messages_big(message.chat.id, text='У него ничего нет, он голодранец!' , reply_markup=markupinline)
                    elif 'toreward' == response.split(':')[1]:
                        #jugi:toreward:$any:$accessory
                        logger.info(response)
                        if not isGoatBoss(message.from_user.username):
                            if not isAdmin(message.from_user.username):
                                bot.reply_to(message, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                                return

                        login = response.split(':')[2].replace('@','').strip()
                        user = getUserByLogin(login)
                        if login.lower() == 'всем':
                            pass
                        else:
                            if not user:
                                send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                                return

                        if response.split(':')[3] == '*':  
                            markupinline = InlineKeyboardMarkup()
                            counter = 10
                            i = 1
                            for acc in getSetting(code='ACCESSORY', name='REWARDS'):
                                if user and user.getAccessory() and acc['value'] in user.getAccessory():
                                    continue    

                                markupinline.add(InlineKeyboardButton(f"{acc['value']}", callback_data=f"toreward|{login}|{acc['name']}"))
                                if i == counter :
                                    markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter}"))
                                    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit"))
                                    break
                                i = i + 1
                            if user:
                                msg = send_messages_big(message.chat.id, text=f'Аксессуары {user.getName()}:\n{user.getAccessoryReport()}' , reply_markup=markupinline)
                            else:
                                msg = send_messages_big(message.chat.id, text=f'Всем бандитам будет выдан...' , reply_markup=markupinline)

                        else:
                            acc = response.split(':')[3]
                            if user:
                                user.addAccessory(acc)
                                updateUser(user)
                                send_messages_big(message.chat.id, text=user.getName() + '!\n' + getResponseDialogFlow(message, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {acc}') 
                            else:
                                for user in list(USERS_ARR):
                                    user.addAccessory(acc)
                                    updateUser(user)
                                send_messages_big(message.chat.id, text='Бандиты!\n' + getResponseDialogFlow(message, 'new_accessory_all').fulfillment_text + f'\n\n▫️ {acc}') 
                    elif 'ban' == response.split(':')[1] or 'unban' == response.split(':')[1]:
                        # jugi:ban:@gggg на:2019-12-01T13:21:52/2019-12-01T13:31:52
                        logger.info(response)
                        ban = ('ban' == response.split(':')[1])
                        login = response.split(':')[2]
                        allUser = False

                        if login.lower() == 'всех':
                            allUser = True
                        else:
                            login = login.split('@')[1].split(' ')[0].strip()

                        if ban:
                            if not isGoatBoss(message.from_user.username):
                                bot.reply_to(message, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                                return
                        else:
                            if allUser:
                                if not isGoatBoss(message.from_user.username):
                                    bot.reply_to(message, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                                    return
                        
                        user = getUserByLogin(login)
                        if not allUser:
                            if not user:
                                send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                                return

                            if not user.getBand():
                                send_messages_big(message.chat.id, text=f'У бандита {login} нет банды!')
                                return

                            if not isUsersBand(message.from_user.username, user.getBand()):
                                if not isAdmin(message.from_user.username):
                                    send_messages_big(message.chat.id, text=f'Бандит {login} не из банд твоего козла!')
                                    return
                    
                        time_str = response.split(response.split(':')[2])[1][1:]
                        date_for = None
                        if ban:
                            if time_str == '*':
                                tz = config.SERVER_MSK_DIFF
                                date_for = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute+1, hours=tz.hour)
                            else:
                                if not '/' in time_str:
                                    send_messages_big(message.chat.id, text=f'Не определен период блокировки!')
                                    return
                                try:
                                    date_for = parse(time_str.split('/')[1].strip())
                                except:
                                    send_messages_big(message.chat.id, text=f'Не смог распознать дату блокировки!')
                                    return

                        report = ''
                        if ban:
                            if not allUser:
                                if user == None:
                                    tguser = getTgUser(login)
                                    tguser["timeban"] = date_for.timestamp()
                                    updateTgUser(tguser)
                                else:
                                    user.setTimeBan(date_for.timestamp())
                                    report = f'{user.getName()} забанен нахрен до\n'+'⏰' + time.strftime("%H:%M:%S %d-%m-%Y", time.gmtime(date_for.timestamp()))
                                    updateUser(user)
                            else:
                                for u in list(USERS_ARR):
                                    if u.getLogin() == message.from_user.username:
                                        pass
                                    else:
                                        u.setTimeBan(date_for.timestamp())
                                        updateUser(u)
                                for tguser in list(TG_USERS_ARR):
                                    if tguser["login"] == message.from_user.username:
                                        pass
                                    else:
                                        tguser["timeban"] = date_for.timestamp()
                                        updateTgUser(tguser)

                                report = f'Все забанены нахрен до\n'+'⏰' + time.strftime("%H:%M:%S %d-%m-%Y", time.gmtime(date_for.timestamp()))
                                
                        else:
                            if not allUser:
                                user.setTimeBan(None)
                                report = f'{user.getName()} разбанен. Говори, дорогой!'
                                updateUser(user)
                            else:
                                for u in list(USERS_ARR):
                                    u.setTimeBan(None)
                                    updateUser(u)
                                
                                for tguser in list(TG_USERS_ARR):
                                    tguser['timeBan'] = None
                                    updateTgUser(tguser)

                                report = f'Все разбанены. Говорите, дорогие мои!'

                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text + f'\n{report}')
                    elif 'requests' == response.split(':')[1]:
                        if not isAdmin(message.from_user.username):
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_admin').fulfillment_text)
                            return
                        #   0     1        2       3
                        # jugi:requests:$tables:$fields:$filters
                        try:
                            report = ''
                            send_messages_big(message.chat.id, text=f'{response}')
                            #filter_str = response.split(':'+response.split(":")[3]+':')[1]
                            filter_str = parameters.fields['filters'].string_value
                            send_messages_big(message.chat.id, text=f'{filter_str}')
                            jsonfind = json.loads(filter_str)
                            send_messages_big(message.chat.id, text=f'Do request...')
                            # fields = response.split(":")[3].replace(' и ', ',').split(',')

                            i = 1
                            for req in mydb[parameters.fields['tables'].string_value].find(jsonfind):
                                report = report + f'{i}. '
                                for field_name in parameters.fields['fields'].list_value:
                                    try:
                                        value = req[f'{field_name}']
                                        report = report + f'{value} '
                                    except: pass
                                report = report + '\n'
                                i = i + 1

                            if report == '':
                                send_messages_big(message.chat.id, text=f'Ничего не найдено!')
                            else:
                                send_messages_big(message.chat.id, text=f'{report}')
                        except Exception as e:
                            send_messages_big(message.chat.id, text=f'Ошибка!')
                            send_messages_big(message.chat.id, text=f'{e}')
                    elif 'rade' == response.split(':')[1]:
                        #   0    1           2            3          4          
                        # jugi:rade:Госпиталь 🚷 📍24км:True:2020-01-13T21:00:00
                        # print(f'isGoatBoss = {isGoatBoss(message.from_user.username)}')
                        # print(f'isAdmin = {isAdmin(message.from_user.username)}')
                        # print(response.split(f':{response.split(":")[3]:}')[1])
                        if isGoatBoss(message.from_user.username) or isAdmin(message.from_user.username):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_not_goat_boss').fulfillment_text)
                            return

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                            return
                        
                        goat = getMyGoatName(message.from_user.username)
                        #   0    1        2              3               4         5       6
                        # jugi:rade:$radelocation1:$radelocation2:$radelocation3:$bool:$date-time
                        
                        raid_date = parse(response.split(f':{response.split(":")[3]}:')[1])

                        if raid_date.hour not in (1, 9, 17):
                            send_messages_big(message.chat.id, text='Рейды проходят только в 1:00, 9:00, 17:00!\nУкажи правильное время!')
                            return 

                        # Проверка на будущую дату
                        tz = config.SERVER_MSK_DIFF
                        dt = raid_date - timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
                        if (dt.timestamp() < datetime.now().timestamp()):
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'timeisout').fulfillment_text)
                            return

                        markupinline = InlineKeyboardMarkup()

                        if eval(response.split(":")[3]):
                            
                            radeloc_arr = []
                            rlocs = response.split(":")[2].replace(' и ', ',').split(',')
                            for rloc in rlocs:
                                row = {}
                                rade_text = rloc
                                rade_location = int(rloc.split('📍')[1].split('км')[0].strip())
                                row.update({'rade_text': rade_text})
                                row.update({'rade_location': rade_location})
                                radeloc_arr.append(row)

                            row = {}
                            row.update({'rade_text': 'Не пойду никуда!'})
                            row.update({'rade_location': 0})
                            radeloc_arr.append(row)
                        
                        if eval(response.split(":")[3]):
                            for radeloc in radeloc_arr:                                
                                myquery = { 
                                            'rade_date': raid_date.timestamp(),
                                            'rade_location': radeloc['rade_location'],
                                            'goat': goat
                                        }
                                newvalues = { "$set": { 
                                                'rade_text': radeloc['rade_text'],
                                            } } 
                                u = plan_raids.update_one(myquery, newvalues)

                                users_onraid = []
                                if u.matched_count == 0:
                                    plan_raids.insert_one({ 
                                        'create_date': datetime.now().timestamp(), 
                                        'rade_date': raid_date.timestamp(),
                                        'rade_text': radeloc['rade_text'],
                                        'rade_location': radeloc['rade_location'],
                                        'state': 'WAIT',
                                        'chat_id': message.chat.id,
                                        'login': message.from_user.username,
                                        'goat': goat,
                                        'users': users_onraid})
                        else:
                            plan_raids.delete_many({
                                            'rade_date': raid_date.timestamp(),
                                            'goat': goat
                                            })

                        plan_str = get_raid_plan(raid_date, goat)

                        #markupinline.add(InlineKeyboardButton(f"{radeloc['rade_text']}", callback_data=f"capture_{radeloc['rade_location']}_{raid_date.timestamp()}_{goat}"))
                        for radeloc in plan_raids.find({
                                    'rade_date': raid_date.timestamp(),
                                    'goat': goat}): 
                            users_onraid = radeloc['users']
                            find = False
                            for u in users_onraid:
                                if u == message.from_user.username:
                                    find = True
                            
                            # if not find:
                            markupinline.add(InlineKeyboardButton(f"{radeloc['rade_text']}", callback_data=f"capture_{radeloc['rade_location']}_{raid_date.timestamp()}_{goat}"))
                                                    
                        msg = send_messages_big(message.chat.id, text=plan_str, reply_markup=markupinline)
                    elif 'getchat' == response.split(':')[1]:
                        send_messages_big(message.chat.id, text=f'Id чата {message.chat.id}')
                    elif 'capture' == response.split(':')[1]:
                            #   0    1        2       3     4
                            # jugi:capture:$bands:$Dangeon:$time
                            band = response.split(':')[2]
                            if response.split(":")[2] == '*':
                                band = userIAm.getBand()
                            
                            if not isUsersBand(message.from_user.username, band):
                                send_messages_big(message.chat.id, text=f'Ты пытался созвать на захват банду 🤟<b>{band}</b>\n' + getResponseDialogFlow(message, 'not_right_band').fulfillment_text)
                                return  

                            # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            #     pass
                            # else:
                            #     censored(message)
                            #     return

                            time_str = response.split(response.split(":")[3])[1][1:]
                            dt = parse(time_str)
                            time_str = str(dt.hour).zfill(2)+':'+str(dt.minute).zfill(2)
                            dungeon = response.split(":")[3]
                            dungeon_km = getSetting(code='DUNGEONS', name=dungeon)
                            text = f'✊️Захват <b>{dungeon_km}км {dungeon}\n🤟{band}\nв {time_str}</b>\n\n'

                            users_in_cupture = []
                            users_on_cupture = []
                            users_off_cupture = []
                            
                            report_yes = '<b>Записались на захват:</b>\n'
                            i = 0
                            for dun in dungeons.find({
                                'date': dt.timestamp(),
                                'band': band,
                                'dungeon_km': dungeon_km,
                                'signedup': True
                                }):
                                i = i + 1
                                user = getUserByLogin(dun['login'])
                                if dun['invader']:
                                    users_in_cupture.append(user)

                                if user:
                                    gerb = user.getSettingValue("🃏Мой герб")
                                    if gerb == None: gerb = ''
                                    users_on_cupture.append(user)
                                    report_yes = report_yes + f'  {i}. {gerb}{user.getName()}\n'
                                else:
                                    report_yes = report_yes + f'  {i}. {dun["login"]}\n'

                            if i == 0:
                                report_yes = report_yes + '  Никто не записался\n'

                            report_no = '<b>Отказались от захвата:</b>\n'
                            i = 0
                            for dun in dungeons.find({
                                'date': dt.timestamp(),
                                'band': band,
                                'dungeon_km': dungeon_km,
                                'signedup': False
                                }):
                                i = i + 1
                                user = getUserByLogin(dun['login'])
                                if user:
                                    gerb = user.getSettingValue("🃏Мой герб")
                                    if gerb == None: gerb = ''
                                    users_off_cupture.append(user)
                                    report_no = report_no + f'  {i}. {gerb}{user.getName()}\n'
                                else:
                                    report_no = report_no + f'  {i}. {dun["login"]}\n'

                            if i == 0:
                                report_no = report_no + '  Никто не отказался\n'

                            # Пингуем
                            counter = 0
                            report = f''
                            for user in getBandUsers(band):
                                counter = counter + 1
                                
                                if user.isPing():
                                    second_pref = ''
                                    pref = '@'

                                    if user in users_on_cupture:
                                        pref = '🏎'
                                    elif user in users_off_cupture:
                                        pref = '🚬'
                                    if user in users_in_cupture:
                                        pref = '🔥'
                                    
                                    if pref == '@':
                                        report = report + f'{counter}. {pref}{user.getLogin()}\n'
                                    else:
                                        report = report + f'{counter}. {pref} {user.getNameAndGerb()})\n'
                                else:
                                    report = report + f'{counter}. 🔕 {user.getNameAndGerb()}\n'

                                if counter % 5 == 0:
                                    send_messages_big(message.chat.id, text=text + report)
                                    report = f''
                            if not report == '':
                                send_messages_big(message.chat.id, text=report)

                            # делаем голосовалку
                            markupinline = InlineKeyboardMarkup()
                            markupinline.add(
                                InlineKeyboardButton(f"Ну нахер! ⛔", callback_data=f"dungeon_no|{dt.timestamp()}|{band}|{dungeon_km}"),
                                InlineKeyboardButton(f"Я в деле! ✅", callback_data=f"dungeon_yes|{dt.timestamp()}|{band}|{dungeon_km}")
                                )

                            text = text + report_yes + '\n' + report_no
                            send_messages_big(message.chat.id, text=text, reply_markup=markupinline)

                            # if not privateChat:
                            #     if len(pingusers) > 0:
                            #         msg = send_messages_big(message.chat.id, text=first_string + report)
                            #         bot.pin_chat_message(message.chat.id, msg.message_id)
                    elif 'remind' == response.split(':')[1]:
                        # jugi:remind:2019-11-04T17:12:00+02:00
                        if not userIAm.getLocation():
                            send_messages_big(message.chat.id, text='Я не знаю из какого ты города. Напиши мне "Я из Одессы" или "Я из Москвы" и этого будет достаточно. Иначе, я буду думать, что ты живешь во временном поясе по Гринвичу, а это +3 часа к Москве, +2 к Киеву и т.д. И ты не сможешь просить меня напомнить о чем-либо!')
                            return
                        if not userIAm.getTimeZone():
                            send_messages_big(message.chat.id, text='Вроде, город знаю, а временную зону забыл. Напиши мне еще раз "Я из Одессы" или "Я из Москвы"!` ')
                            return
                                                
                        time_str = response.split(response.split(":")[1])[1][1:]
                        dt = parse(time_str)
                        tz = datetime.strptime(userIAm.getTimeZone(),"%H:%M:%S")
                        dt = dt - timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
                        if (dt.timestamp() < datetime.now().timestamp()):
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'timeisout').fulfillment_text)
                            return

                        reply_message = None
                        if message.reply_to_message:
                            reply_message = message.reply_to_message.json

                        pending_messages.insert_one({ 
                            'chat_id': message.chat.id,
                            'reply_message': reply_message,
                            'create_date': datetime.now().timestamp(),
                            'user_id': message.from_user.username,  
                            'state': 'WAIT',
                            'pending_date': dt.timestamp(),
                            'dialog_flow_text': 'remindme',
                            'text': None})
                        
                        msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)
                    elif 'sticker' == response.split(':')[1]: 
                        # 0      1               2                          3        4
                        #jugi:sticker:CAADAgADawgAAm4y2AABx_tlRP2FVS8WBA:Ми-ми-ми:NEW_YEAR
                        
                        photo = response.split(':')[2]
                        if len(response.split(':')) > 4:
                            photo = random.sample(getSetting(code='STICKERS', name=response.split(':')[4]), 1)[0]['value']
                        text = response.split(':')[3]
                        if text:
                            bot.send_message(message.chat.id, text=text)   
                        
                        bot.send_sticker(message.chat.id, photo)   
                    elif 'tobeornottoby' == response.split(':')[1]:
                        #jugi:tobeornottoby
                        r = random.random()
                        if (r <= 0.5):
                            bot.send_message(message.chat.id, text='Быть, епта!')
                        else:
                            bot.send_message(message.chat.id, text='ХЗ, я бы не рискнул...')
                    elif 'setlocation' == response.split(':')[1]:
                        #jugi:setlocation:Москва
                        Client.PARAMS = {"format": "json", "apikey": config.YANDEX_GEOCODING_API_KEY}
                        location = Client.coordinates(response.split(':')[2])
                        if location:
                            tf = timezonefinder.TimezoneFinder()
                            timezone_str = tf.certain_timezone_at(lat=float(location[1]), lng=float(location[0]))
                            if timezone_str is None:
                                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'understand').fulfillment_text)
                            else:
                                # Display the current time in that time zone
                                timezone = pytz.timezone(timezone_str)
                                dt = datetime.utcnow()
                                userIAm.setLocation(response.split(':')[2])
                                userIAm.setTimeZone(str(timezone.utcoffset(dt)))
                                updateUser(userIAm)
                                send_messages_big(message.chat.id, text='Круто!\nЭто ' + str(timezone.utcoffset(dt)) + ' к Гринвичу!')

                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'understand').fulfillment_text)
                    elif 'rating' == response.split(':')[1]:
                        # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                        #     pass
                        # else:
                        #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_censorship').fulfillment_text)
                        #     return

                        report = ''
                        report = report + f'🏆ТОП 5 УБИЙЦ 🐐<b>{getMyGoatName(userIAm.getLogin())}</b>\n'
                        report = report + '\n'
                        setting = getSetting(code='REPORTS',name='KILLERS')
                        from_date = setting.get('from_date')
                        to_date = setting.get('to_date')

                        if (not from_date):
                            from_date = (datetime(2019, 1, 1)).timestamp() 

                        if (not to_date):
                            to_date = (datetime.now() + timedelta(minutes=180)).timestamp()

                        dresult = battle.aggregate([
                            {   "$match": {
                                    "$and" : [
                                        { 
                                            "date": {
                                                '$gte': from_date,
                                                '$lt': to_date
                                                    }       
                                        },
                                        {
                                            "band": {'$in': getMyBandsName(userIAm.getLogin())}   
                                        }]
                                }
                            }, 
                            {   "$group": {
                                "_id": "$winnerWarior", 
                                "count": {
                                    "$sum": 1}}},
                                
                            {   "$sort" : { "count" : -1 } }
                            ])

                        findInWinner = 0
                        i = 0
                        for d in dresult:
                            user_name = d.get("_id")   

                            user = getUserByName(user_name)
                            if user == None: continue

                            gerb = user.getSettingValue("🃏Мой герб")
                            if gerb == None: gerb = ''

                            i = i + 1
                            if i == 1:
                                emoji = f'🥇 - {gerb}'
                            elif i == 2:
                                emoji = f'🥈 - {gerb}'    
                            elif i == 3:
                                emoji = f'🥉 - {gerb}'
                            else:
                                emoji = f'{gerb}'
                            
                            if user_name == tools.deEmojify(message.from_user.first_name):
                                user_name = f'<b>{user_name}</b>'
                                findInWinner = i

                            if i <= 5: report = report + f'{i}. {emoji}{user_name}: {d.get("count")}\n' 

                        if (i == 0): 
                            report = report + f'Мир! Пис! ✌️🌷🐣\n'
                        else:
                            if (findInWinner > 5): report = report + f'\n👹 Твое место в рейтинге - {findInWinner}!\n'
                        #==========================================    
                        report = report + f'\n' 
                        report = report + f'⚰️ТОП 5 НЕУДАЧНИКОВ\n' 
                        report = report + '\n'
                        dresult = battle.aggregate([
                            {   "$match": {
                                    "$and" : [
                                        { 
                                            "date": {
                                                '$gte': from_date,
                                                '$lt': to_date
                                                    }       
                                        },
                                        {
                                            "band": {'$in': getMyBandsName(userIAm.getLogin())}    
                                        }]
                                } 
                            }, 
                            {   "$group": {
                                "_id": "$loseWarior", 
                                "count": {
                                    "$sum": 1}}},
                                
                            {   "$sort" : { "count" : -1 } }
                            ])

                        findInLoser = 0
                        i = 0
                        for d in dresult:
                            user_name = d.get("_id")  
                            user = getUserByName(user_name)
                            if user == None: continue

                            gerb = user.getSettingValue("🃏Мой герб")
                            if gerb == None: gerb = ''
                                
                            i = i + 1
                            if i == 1:
                                emoji = f'👻 - {gerb}'
                            elif i == 2:
                                emoji = f'💀️ - {gerb}'    
                            elif i == 3:
                                emoji = f'☠️ - {gerb}'
                            else:
                                emoji = f'{gerb}'

                            if user_name == tools.deEmojify(message.from_user.first_name):
                                user_name = f'<b>{user_name}</b>'
                                findInLoser = i

                            if i <= 5: report = report + f'{i}. {emoji}{user_name}: {d.get("count")}\n' 
                             

                        if (i == 0): 
                            report = report + f'Мы бессмертны ✌️👻💀☠️\n'
                        else:
                            if (findInLoser > 5): report = report + f'\n🧸 Твое место - {findInLoser}!\n'

                        report = report + f'\n' 
                        report = report + f'{report_man_of_day(message.from_user.username)}'
                        
                        report = report + f'\n' 
                        report = report + f'{report_koronavirus()}'

                        report = report + f'\n' 
                        report = report + '⏰ c ' + time.strftime("%d-%m-%Y", time.gmtime(from_date)) + ' по ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(to_date))
                        
                        send_messages_big(message.chat.id, text=report)
                else:
                    try:
                        send_messages_big(message.chat.id, text=response, reply_markup=None)
                    except:
                        logger.info("Error!")
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'understand').fulfillment_text)
        return
    else:
        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
            if (random.random() <= float(getSetting(code='PROBABILITY', name='I_DONT_KNOW_YOU'))):
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'you_dont_our_band_gangster').fulfillment_text)

def report_koronavirus():
    counter = 0
    for user in USERS_ARR:
        if user.isAccessoryItem(acc_koronavirus):
            counter = counter + 1

    report = f'🦇 Статистика зараженных: <b>{counter}</b>\n' 
    return report

def report_man_of_day(message_user_name: str):
    setting = getSetting(code='REPORTS',name='KILLERS')
    from_date = setting.get('from_date')
    to_date = setting.get('to_date')

    if (not from_date):
        from_date = (datetime(2019, 1, 1)).timestamp() 

    if (not to_date):
        to_date = (datetime.now() + timedelta(minutes=180)).timestamp()

    report = f'👨‍❤️‍👨ТОП 5 "Пидор дня"\n' 
    report = report + '\n'
    dresult = man_of_day.aggregate([
        {   "$match": {
                "$and" : [
                    { 
                        "date": {
                            '$gte': from_date,
                            '$lt': to_date
                                }       
                    }
                    ]
            } 
        }, 
        {   "$group": {
            "_id": "$login", 
            "count": {
                "$sum": 1}}},
            
        {   "$sort" : { "count" : -1 } }
        ])
    
    acc = '👑 "Пидор дня"'
    findInLoser = 0
    i = 0
    pidor_counter = 0
    pidor_user_now = None

    for d in dresult:
        user_login = d.get("_id")  
        user = getUserByLogin(user_login)
        i = i + 1
        if i == 1:
            emoji = '💝 - '
        elif i == 2:
            emoji = '💖 - '    
        elif i == 3:
            emoji = '❤️ - '
        else:
            emoji = ''
        
        user_name = user_login
        if user:
            user_name = f'{user.getNameAndGerb()}'
            if user.isAccessoryItem(acc):
                pidor_counter = i
                pidor_user_now = user
        else:
            user_name = user_login

        if message_user_name  == user_login:
            user_name = f'<b>{user_name}</b>'
            findInLoser = i

        if i <= 5: report = report + f'{i}. {emoji}{user_name}: <b>{d.get("count")}</b>\n' 

    if (i == 0): 
        report = report + f'В нашем козле нет пидоров!\n'
    else:
        if (findInLoser > 5): report = report + f'\n💔 Твое пидорье место - {findInLoser}!\n'
    
    if pidor_user_now:
        report = report + f'\nПидор дня <b>{pidor_user_now.getNameAndGerb()}</b> на {pidor_counter} месте\n'
    
    return report

@bot.callback_query_handler(func=lambda call: call.data.startswith("dungeon"))
def callback_query(call):
    #  logger.info(f'{call.from_user.username} {call.data}')
    #     0              1           2        3
    # dungeon_no|{dt.timestamp()}|{band}|{dungeon_km}

    if isUserBan(call.from_user.username):
       bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
       return


    band = call.data.split('|')[2]
    user = getUserByLogin(call.from_user.username)
    if not user.getBand() == band:
        bot.answer_callback_query(call.id, "Это не для твоей банды!")
        return

    dt = datetime.fromtimestamp(float(call.data.split('|')[1]))
    time_str = str(dt.hour).zfill(2)+':'+str(dt.minute).zfill(2)
    dungeon_km = call.data.split('|')[3]
    dungeon = getSetting(code='DUNGEONS', value=dungeon_km) 

    markupinline = InlineKeyboardMarkup()
    markupinline.add(
        InlineKeyboardButton(f"Ну нахер! ⛔", callback_data=f"dungeon_no|{dt.timestamp()}|{band}|{dungeon_km}"),
        InlineKeyboardButton(f"Я в деле! ✅", callback_data=f"dungeon_yes|{dt.timestamp()}|{band}|{dungeon_km}")
        )

    text = f'✊️Захват <b>{dungeon_km}км {dungeon}\n🤟{band}\nв {time_str}</b>\n\n'

    signedup = False
    if call.data.startswith("dungeon_yes"):
        signedup = True
        bot.answer_callback_query(call.id, "Красавчик!")
    elif call.data.startswith("dungeon_no"):
        bot.answer_callback_query(call.id, "Сыкло!")
        signedup = False

    row = {}
    row.update({'date': float(call.data.split('|')[1])})
    row.update({'login': call.from_user.username})
    row.update({'band': user.getBand()})
    row.update({'goat': getMyGoatName(call.from_user.username)})
    row.update({'dungeon_km': dungeon_km})
    row.update({'dungeon': dungeon})
    row.update({'signedup': signedup})
    row.update({'invader': False})
    row.update({'state': "NEW"})

    newvalues = { "$set": row }
    result = dungeons.update_one({
        'login': call.from_user.username, 
        'date': float(call.data.split('|')[1]),
        'band': user.getBand(),
        'dungeon_km': dungeon_km
        }, newvalues)
    if result.matched_count < 1:
        dungeons.insert_one(row)

    report_yes = '<b>Записались на захват:</b>\n'
    i = 0
    for dun in dungeons.find({
        'date': float(call.data.split('|')[1]),
        'band': user.getBand(),
        'dungeon_km': dungeon_km,
        'signedup': True
        }):
        i = i + 1
        user = getUserByLogin(dun['login'])
        if user:
            gerb = user.getSettingValue("🃏Мой герб")
            if gerb == None: gerb = ''
            report_yes = report_yes + f'  {i}. {gerb}{user.getName()}\n'
        else:
            report_yes = report_yes + f'  {i}. {dun["login"]}\n'

    if i == 0:
        report_yes = report_yes + '  Никто не записался\n'

    report_no = '<b>Отказались от захвата:</b>\n'
    i = 0
    for dun in dungeons.find({
        'date': float(call.data.split('|')[1]),
        'band': user.getBand(),
        'dungeon_km': dungeon_km,
        'signedup': False
        }):
        i = i + 1
        user = getUserByLogin(dun['login'])
        if user:
            gerb = user.getSettingValue("🃏Мой герб")
            if gerb == None: gerb = ''
            report_no = report_no + f'  {i}. {gerb}{user.getName()}\n'
        else:
            report_no = report_no + f'  {i}. {dun["login"]}\n'

    if i == 0:
        report_no = report_no + '  Никто не отказался\n'

    text = text + report_yes + '\n' + report_no
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
    # logger.info(f'{call.from_user.username} {text}')

@bot.callback_query_handler(func=lambda call: call.data.startswith("toreward"))
def callback_query(call):
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    if not isGoatBoss(call.from_user.username):
        if not isAdmin(call.from_user.username):
            bot.answer_callback_query(call.id, "Тебе не положено!")
            return

    if 'toreward_exit' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Раздача подарков завершена!', parse_mode='HTML')
        return

    if call.data.startswith("toreward_next"):
        #        0         1     2
        # toreward_next|{login}|10
        counter  = int(call.data.split('|')[2])
        login = call.data.split('|')[1]
        user = getUserByLogin(login)
        markupinline = InlineKeyboardMarkup()
        i = 1
        addExit = False
        for acc in getSetting(code='ACCESSORY',name='REWARDS'):
            if user and user.getAccessory() and acc['value'] in user.getAccessory():
                continue    

            if i <= counter:
                pass
            else:
                markupinline.add(InlineKeyboardButton(f"{acc['value']}", callback_data=f"toreward|{login}|{acc['name']}"))
                if i == counter + 10:
                    markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_back|{login}|{counter - 10}"), InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter + 10}"))
                    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit"))
                    addExit = True
                    break
            i = i + 1
        if not addExit:
            markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_back|{login}|{counter - 10}"))
            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit"))
        
        text=f'Всем бандитам будет что-то выдано! Просмотрено {counter} аксессуаров'
        if user:
            text=f'Аксессуары {user.getName()}:\n{user.getAccessoryReport()}'
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
        return

    if call.data.startswith("toreward_back"):
        # toreward_back|{login}|10"
        counter  = int(call.data.split('|')[2])
        login = call.data.split('|')[1]
        user = getUserByLogin(login)
        markupinline = InlineKeyboardMarkup()
        i = 1
        addExit = False
        for acc in getSetting(code='ACCESSORY',name='REWARDS'):
            if user.getAccessory() and acc['value'] in user.getAccessory():
                continue    

            if i <= counter:
                pass
            else:
                markupinline.add(InlineKeyboardButton(f"{acc['value']}", callback_data=f"toreward|{login}|{acc['name']}"))
                if i == counter + 10:
                    if counter == 0:
                        markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter + 10}"))
                    else:
                        markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_back|{login}|{counter - 10}"), InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter + 10}"))
                    
                    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit"))
                    addExit = True
                    break
            i = i + 1
        if not addExit:
            markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_next|{login}|{i+10}"))
            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit"))

        text=f'Аксессуары {user.getName()}:\n{user.getAccessoryReport()}'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
        return

    bot.answer_callback_query(call.id, "Ты сделал свой выбор")
    login = call.data.split('|')[1]
    user = getUserByLogin(login)
    
    for acc in getSetting(code='ACCESSORY', name='REWARDS'):
        if acc['name'] == call.data.split('|')[2]:
            if login.lower() == 'всем':
                for user in list(USERS_ARR):
                    user.addAccessory(acc['value'])
                    updateUser(user)
                send_messages_big(call.message.chat.id, text= 'Бандиты!\n' + getResponseDialogFlow(call.message, 'new_accessory_all').fulfillment_text + f'\n\n▫️ {acc["value"]}') 
                break
            else:
                user.addAccessory(acc['value'])
                updateUser(user)
                send_messages_big(call.message.chat.id, text=user.getName() + '!\n' + getResponseDialogFlow(call.message, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {acc["value"]}') 
                break

    markupinline = InlineKeyboardMarkup()
    counter = 10
    i = 1
    for acc in getSetting(code='ACCESSORY', name='REWARDS'):
        if user and user.getAccessory() and acc['value'] in user.getAccessory():
            continue    

        markupinline.add(InlineKeyboardButton(f"{acc['value']}", callback_data=f"toreward|{login}|{acc['name']}"))
        if i == counter :
            markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter}"))
            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit"))
            break
        i = i + 1
    if user:
        text=f'Аксессуары {user.getName()}:\n{user.getAccessoryReport()}'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pickupaccessory"))
def callback_query(call):
    # pickupaccessory|{login}|{acc}

    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    if not isGoatBoss(call.from_user.username):
        if not isAdmin(call.from_user.username):
            bot.answer_callback_query(call.id, "Тебе не положено!")
            return

    login = call.data.split('|')[1]
    user = getUserByLogin(login)
    markupinline = InlineKeyboardMarkup()

    accessory = ''
    if user.getAccessory() and len(user.getAccessory())>0:
        i = 0
        for acc in user.getAccessory():
            accessory = accessory + f'▫️ {acc}\n'
            i = i + 1
    text = 'У него больше ничего нет!'

    if 'pickupaccessory_exit' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Отъём завершен!\nОстались аксессуары:\n{accessory}', parse_mode='HTML')
        return

    acc = user.getAccessory()[int(call.data.split('|')[2])]
    bot.answer_callback_query(call.id, "Ты забрал это с полки...")
    
    user.removeAccessory(acc)
    updateUser(user)

    accessory = ''
    if user.getAccessory() and len(user.getAccessory())>0:
        i = 0
        for acc in user.getAccessory():
            accessory = accessory + f'▫️ {acc}\n'
            markupinline.add(InlineKeyboardButton(f"{acc}", callback_data=f"pickupaccessory|{login}|{i}"))
            i = i + 1
    text = 'У него больше ничего нет!'

    if not accessory == '':
        text = getResponseDialogFlow(call.message, None, 'shot_message_pickupaccessory').fulfillment_text + f'\n\n{accessory}\nЧто изьять?'
        
    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"pickupaccessory_exit|{login}"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

@bot.callback_query_handler(func=lambda call: call.data.startswith("capture_"))
def callback_query(call):
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return
    
    goat = call.data.split('_')[3]
    if not goat == getMyGoatName(call.from_user.username):
        bot.answer_callback_query(call.id, "Это план не твоего козла!")
        return

    raid_date = datetime.fromtimestamp(float(call.data.split('_')[2]))
    logger.info(f'raid_date: {raid_date}')
    raid_location = int(call.data.split('_')[1])
    logger.info(f'raid_location: {raid_location}')

    myquery = { 
                'rade_date': raid_date.timestamp(),
                'goat': goat
            }
            
    markupinline = InlineKeyboardMarkup()

    if call.data.startswith("capture_0"):
        bot.answer_callback_query(call.id, "Сыкло!")
    else:
        bot.answer_callback_query(call.id, "Ты записался в добровольцы!")


    users_onraid = []
    for row in plan_raids.find(myquery):
        users_onraid = row['users']
        if row['rade_location'] == raid_location:
            find_user = False
            for u in users_onraid:
                if call.from_user.username == u:
                    find_user = True
                    break
            if not find_user:
                users_onraid.append(call.from_user.username)
        else:
            for u in users_onraid:
                if call.from_user.username == u:
                    users_onraid.remove(call.from_user.username)
    
        newvalues = { "$set": { 
                        'users': users_onraid
                    }} 
        u = plan_raids.update_one({ 
                    'rade_date': raid_date.timestamp(),
                    'rade_location': row["rade_location"],
                    'goat': goat
                }, newvalues)

    for radeloc in plan_raids.find({
                'rade_date': raid_date.timestamp(),
                'goat': goat}): 
        users_onraid = radeloc['users']
        find = False
        for u in users_onraid:
            if u == call.from_user.username:
                find = True
        
        # if not find:
        markupinline.add(InlineKeyboardButton(f"{radeloc['rade_text']}", callback_data=f"capture_{radeloc['rade_location']}_{raid_date.timestamp()}_{goat}"))
                                
    text = get_raid_plan(raid_date, goat)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

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

def send_message_to_admin(text: str):
    for adm in getSetting(code='ADMINISTRATOR'):
        if adm.get('chat'):
            send_messages_big(adm.get('chat'), text)

def reply_to_big(message: str, text: str):
    strings = text.split('\n')
    tmp = ''
    msg = types.Message.de_json(message)

    for s in strings:
        if len(tmp + s) < 4000:
            tmp = tmp + s +'\n'
        else: 
            result = bot.reply_to(msg, text=tmp, parse_mode='HTML')
            tmp = s + '\n'

    result = bot.reply_to(msg, text=tmp, parse_mode='HTML')
    return result

def pending_message():
    ids = []
    for pending_message in pending_messages.find(
            {
                '$and' : [
                            {
                                'state': f'WAIT'   
                            }
                            ,
                            { 
                               'pending_date': {
                                   '$lt': datetime.now().timestamp()
                                       }       
                            }
                        ]
            }
        ):
        
        text = pending_message.get('text')
        if text == None:
            text = ''
        if pending_message.get('dialog_flow_text'):
            text = getResponseDialogFlow(None, pending_message.get('dialog_flow_text')).fulfillment_text + '\n' + text
        
        if pending_message.get('reply_message'):
            reply_to_big(pending_message.get('reply_message'), text)
        else:
            send_messages_big(pending_message.get('chat_id'), text, None)
        ids.append(pending_message.get('_id')) 

    for id_str in ids:
        myquery = {"_id": ObjectId(id_str)}
        newvalues = { "$set": { "state": 'CANCEL'} }
        u = pending_messages.update_one(myquery, newvalues)

def ping_on_reade(fuckupusers, chat_id):
    # Пингуем
    if len(fuckupusers) == 0:
        return

    counter = 0
    fusers = []
    fuckupusersReport = f'🐢 <b>Бандиты! {getResponseDialogFlow(None, "rade_motivation").fulfillment_text}</b>\n🤟<b>{fuckupusers[0].getBand()}</b>\n'
    for fu in fuckupusers:
        counter = counter + 1
        fusers.append(fu)
        if fu.isPing():
            fuckupusersReport = fuckupusersReport + f'{counter}. @{fu.getLogin()}\n'
        else:
            fuckupusersReport = fuckupusersReport + f'{counter}. 🔕{fu.getLogin()}\n'

        if counter % 5 == 0:
            send_messages_big(chat_id, text=fuckupusersReport)
            fusers = []
            fuckupusersReport = f'🐢 <b>Бандиты! {getResponseDialogFlow(None, "rade_motivation").fulfillment_text}</b>\n🤟<b>{fuckupusers[0].getBand()}</b>\n'

    if len(fusers) > 0:
        send_messages_big(chat_id, text=fuckupusersReport)

def rade():
    tz = config.SERVER_MSK_DIFF
    now_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)

    logger.info('check rade time: now ' + str(now_date))
    
    # Новый год!
    if now_date.day == 1 and now_date.month == 1 and now_date.hour == 0 and now_date.minute in (0,10,15,20,25,35,35,50) and now_date.second < 15:
        for goat in getSetting(code='GOATS_BANDS'):
            report = ''
            try:
                r = requests.get(f'{config.ANECDOT_URL}={16}', verify=False, timeout=7)
                report = r.text[12:-2]
            except:
                report = 'Чёт я приуныл... Ничего в голову не идет... С новым годом!'
            send_messages_big(goat['chats']['info'], report)
            bot.send_sticker(goat['chats']['info'], random.sample(getSetting(code='STICKERS', name='NEW_YEAR'), 1)[0]['value']) 

    # 14 февраля!
    if now_date.day == 14 and now_date.month == 2 and now_date.hour == 10 and now_date.minute in (0,10,15,20,25,35,35,50) and now_date.second < 15:
        for goat in getSetting(code='GOATS_BANDS'):
            report = ''
            try:
                r = requests.get(f'{config.ANECDOT_URL}={16}', verify=False, timeout=7)
                report = r.text[12:-2]
            except:
                report = 'Чёт я приуныл... Ничего в голову не идет... С новым годом!'
            send_messages_big(goat['chats']['info'], report)
            bot.send_sticker(goat['chats']['info'], random.sample(getSetting(code='STICKERS', name='LOVE_DAY'), 1)[0]['value']) 
    # День рождения
    if now_date.hour == 8 and now_date.minute == 0 and now_date.second < 15:
        updateUser(None)
        for user in USERS_ARR:
            if user.getBirthday():
                bday = time.gmtime(user.getBirthday())
                if now_date.day == bday.day and now_date.month == bday.month: 
                    send_messages_big(goat['chats']['info'], f'{user.getNameAndGerb()}!\n{getResponseDialogFlow(None, "happy_birthday").fulfillment_text}')

    # Пидор дня
    if now_date.hour == 9 and now_date.minute == 0 and now_date.second < 15:
        updateUser(None)
        user_in_game = []
        for user in USERS_ARR:
            usersettings = getUserSetting(user.getLogin(), '👨‍❤️‍👨Участник "Пидор дня"')
            if usersettings:
                user_in_game.append(user)

        winners = random.sample(user_in_game, 1)
        if len(winners)>0:
            userWin = winners[0]
            
            setting = getSetting(code='REPORTS',name='KILLERS')
            from_date = setting.get('from_date')
            to_date = setting.get('to_date')

            if (not from_date):
                from_date = (datetime(2019, 1, 1)).timestamp() 

            if (not to_date):
                to_date = (datetime.now() + timedelta(minutes=180)).timestamp()
                
            dresult = man_of_day.aggregate([
            {   "$match": {
                    "$and" : [
                        { 
                            "date": {
                                '$gte': from_date,
                                '$lt': to_date
                                    }       
                        }
                        ]
                } 
            }, 
            {   "$group": {
                "_id": "$login", 
                "count": {
                    "$sum": 1}}},
                
            {   "$sort" : { "count" : -1 } }
            ])

            old_pidors = []
            for d in dresult:
                user_login = d.get("_id")  
                user = getUserByLogin(user_login)
                if user:
                    old_pidors.append(user)

            pidor1 = None
            pidor2 = None
            if len(old_pidors)>1:
                pu = random.sample(old_pidors, 1)[0]
                pidor1 = pu.getNameAndGerb()
                old_pidors.remove(pu)
                pidor2 = random.sample(old_pidors, 1)[0].getNameAndGerb()
            else:
                pidor1 = random.sample(list(USERS_ARR), 1)[0].getNameAndGerb()
                pidor2 = random.sample(list(USERS_ARR), 1)[0].getNameAndGerb()

            text = f'🎊🎉🍾 Поздравляю!\nВ конкурсе "👨‍❤️‍💋‍👨 Пидор дня" сегодня побеждает...\n{userWin.getName()} (@{userWin.getLogin()})!!!\n\n👬 Два бывалых пидора, {pidor1} и {pidor2}, под вздохи толпы надевают на твою голову 👑 золотую корону и, ласково шлепая тебя по попе, сгоняют с помоста!\n🎁 Самое время поздравить сегодняшнего победителя!'
            chat = getMyGoat(userWin.getLogin())['chats']['info']
            send_messages_big(chat, text=text)

            acc = '👑 "Пидор дня"'
            for user in USERS_ARR:
                if acc in user.getAccessory():
                    user.removeAccessory(acc)
                    updateUser(user)
                    break
            
            userWin.addAccessory(acc)
            updateUser(userWin)
            send_messages_big(chat, text=userWin.getName() + '!\n' + getResponseDialogFlow(None, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {acc}') 
            row = {}
            row.update({'date':now_date.timestamp()})
            row.update({'login':userWin.getLogin()})
            row.update({'description':acc})
            man_of_day.insert_one(row)
            send_messages_big(chat, text=report_man_of_day('')) 

    if now_date.hour in (0, 8, 16) and now_date.minute in (0, 30, 50) and now_date.second < 15:
        updateUser(None)
        for goat in getSetting(code='GOATS_BANDS'):
            if getPlanedRaidLocation(goat['name'], planRaid = True)['rade_location']:
                report = radeReport(goat, True)
                send_messages_big(goat['chats']['secret'], text=f'<b>{str(60-now_date.minute)}</b> минут до рейда!\n' + report)

    if now_date.hour in (1, 9, 17) and now_date.minute == 0 and now_date.second < 15:
        logger.info('Rade time now!')
        updateUser(None)
        for goat in getSetting(code='GOATS_BANDS'):
            if getPlanedRaidLocation(goat['name'], planRaid = False)['rade_location']:
                report = radeReport(goat)
                send_messages_big(goat['chats']['secret'], text='<b>Результаты рейда</b>\n' + report)
                saveRaidResult(goat)
                statistic(goat['name'])

    if now_date.hour in (1, 9, 17) and now_date.minute == 5 and now_date.second < 15:
        logger.info('Clear raid info!')
        for goat in getSetting(code='GOATS_BANDS'):
            registered_users.update_many(
                {'band':{'$in':getGoatBands(goat.get('name'))}},
                { '$set': { 'raidlocation': None} }
            )
        updateUser(None)

def getPlanedRaidLocation(goatName: str, planRaid = True):
    tz = config.SERVER_MSK_DIFF
    raid_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
    hour = raid_date.hour

    if planRaid and raid_date.hour >= 17:
        raid_date = raid_date + timedelta(days=1)

    if raid_date.hour >=1 and raid_date.hour <9:
        hour = 9
        if not planRaid:
            hour = 1
    elif raid_date.hour >=9 and raid_date.hour <17:
        hour = 17
        if not planRaid:
            hour = 9
    if raid_date.hour >=17 or raid_date.hour <1:
        hour = 1
        if not planRaid:
            hour = 17

    raidNone = {}
    raidNone.update({'rade_date': (raid_date.replace(hour=hour, minute=0, second=0, microsecond=0)).timestamp()})
    raidNone.update({'rade_location': None})
    raidNone.update({'rade_text': None})

    for raid in plan_raids.find({
                                '$and' : 
                                [
                                    {
                                        'rade_date': {
                                        '$gte': (raid_date.replace(hour=0, minute=0, second=0, microsecond=0)).timestamp(),
                                        '$lt': (raid_date.replace(hour=23, minute=59, second=59, microsecond=0)).timestamp(),
                                        }},
                                    {
                                        'goat': goatName
                                    }
                                ]
                            }):
        if datetime.fromtimestamp(raid.get('rade_date')).hour == hour:
            return raid
    return raidNone

def saveRaidResult(goat):
    logger.info(f"saveRaidResult : {goat.get('name')}")
    raid = getPlanedRaidLocation(goat['name'], planRaid=False)
    location = raid.get('rade_location')
    raiddate = raid.get('rade_date')

    for band in goat.get('bands'):
        for user in list(USERS_ARR):
            # Обрабатываем по бандам
            if user.getBand() and user.getBand() == band.get('name'):
                row = {}
                row.update({'date': raiddate})
                row.update({'login': user.getLogin()})
                row.update({'band': band.get('name')})
                row.update({'goat': goat.get('name')})
                row.update({'planed_location': location})
                row.update({'planed_location_text': raid.get('rade_text')})
                row.update({'user_location': None})
                row.update({'on_raid': False})
                row.update({'on_planed_location': False})
                if user.getRaidLocation():
                    row.update({'on_raid': True}) 
                    row.update({'user_location': user.getRaidLocation()})    
                    if location and user.getRaidLocation() == location:
                        row.update({'planed_location': True})
                newvalues = { "$set": row }
                result = report_raids.update_one({"login": f"{user.getLogin()}", 'date': raiddate}, newvalues)
                if result.matched_count < 1:
                    report_raids.insert_one(row)

def radeReport(goat, ping=False):

    raidInfo = getPlanedRaidLocation(goat.get('name'))
    planed_raid_location = raidInfo['rade_location']
    planed_raid_location_text = raidInfo['rade_text']
    goat_report = {}
    goat_report.update({'name': goat.get('name')})
    goat_report.update({'chat': goat['chats']['secret']})
    goat_report.update({'bands': []})

    for band in goat.get('bands'):
        band_arr = {}
        band_arr.update({'name': band.get('name')})
        band_arr.update({'weight_all': 0})
        band_arr.update({'weight_on_rade': 0})
        band_arr.update({'counter_all': 0})
        band_arr.update({'counter_on_rade': 0})
        band_arr.update({'usersonrade': []})
        band_arr.update({'usersoffrade': []})


        for user in list(USERS_ARR):
            # Обрабатываем по козлам
            if user.getBand() and user.getBand() == band.get('name'):
                band_arr.update({'weight_all': band_arr.get('weight_all') + user.getRaidWeight()})
                band_arr.update({'counter_all': band_arr.get('counter_all') + 1}) 
                if user.getRaidLocation():
                    band_arr.update({'weight_on_rade': band_arr.get('weight_on_rade') + user.getRaidWeight()})
                    band_arr.update({'counter_on_rade': band_arr.get('counter_on_rade') + 1}) 
                    band_arr.get('usersonrade').append(user)
                else:
                    band_arr.get('usersoffrade').append(user)
        goat_report.get('bands').append(band_arr)

    report = f'🐐<b>{goat_report.get("name")}</b>\n'
    if planed_raid_location_text:
        report = report + f'{planed_raid_location_text}\n'
    report = report + '\n'
    
    for bands in goat_report.get('bands'):
        report = report + f'🤟<b>{bands.get("name")}</b>\n'
        if bands.get("weight_all") > 0:
            report = report + f'👤{bands.get("counter_on_rade")}/{bands.get("counter_all")} 🏋️‍♂️{bands.get("weight_on_rade")}/{bands.get("weight_all")} <b>{str(int(bands.get("weight_on_rade")/bands.get("weight_all")*100))}</b>%\n'
        else:
            report = report + f'👤{bands.get("counter_on_rade")}/{bands.get("counter_all")} 🏋️‍♂️<b>0</b>%\n'
        report = report + f'\n'

        if len(bands.get("usersonrade")):
            report = report + f'🧘‍♂️ <b>на рейде</b>:\n'
            counter = 0            
            for u in bands.get("usersonrade"):
                counter = counter + 1
                location = str(u.getRaidLocation())
                if u.getRaidLocation() == 1:
                    location = '?'
                if planed_raid_location:
                    if planed_raid_location == u.getRaidLocation():
                        location = '✔️' + location
                report = report + f'{counter}. {u.getNameAndGerb()} 📍{location}км\n'
            report = report + f'\n'
        if ping:
            if planed_raid_location:
                ping_on_reade(bands.get("usersoffrade"), goat['chats']['secret'] )
    return report

def statistic(goatName: str):
    report = f'🐐<b>{goatName}</b>\n\n'
    report = report + f'🧘‍♂️ <b>Рейдеры</b>:\n'

    setting = getSetting(code='REPORTS', name='RAIDS')
    from_date = setting.get('from_date')
    to_date = setting.get('to_date')

    if (not from_date):
        from_date = (datetime(2019, 1, 1)).timestamp() 

    if (not to_date):
        to_date = (datetime.now() + timedelta(minutes=180)).timestamp()

    dresult = report_raids.distinct('date', {"$and" : [
                    { 
                        "date": {
                            '$gte': from_date,
                            '$lt': to_date
                                }       
                    },
                    {
                        "band": {'$in': getGoatBands(goatName)}   
                    },
                    {
                        "planed_location": {'$ne':None}   
                    }
                ]})

    raid_counter = len(dresult)
    report =  f'👊<b>{raid_counter}</b> рейдов\n' + report

    dresult = report_raids.aggregate([
        {   "$match": {
                "$and" : [
                    { 
                        "date": {
                            '$gte': from_date,
                            '$lt': to_date
                                }       
                    },
                    {
                        "band": {'$in': getGoatBands(goatName)}   
                    },
                    {
                        "on_raid": True
                    },
                    {
                        "planed_location": {'$ne':None}   
                    }
                ]
            }
        }, 
        {   
            "$group": 
                {
                    "_id": "$login",
                    "count": 
                        {
                            "$sum": 1
                        }
                }
        },    
        {   
            "$sort" : { "count" : -1 } 
        }
    ])
    
    report_boss = ''
    for d in dresult:
        name = d.get("_id")
        user = getUserByLogin(name)
        count = d.get("count")

        if isGoatBoss(name):
            report_boss = f'😎 наш босс <b>{user.getName()}</b> посетил рейды {count} раз. Скажите за это ему "Спасибо!" при встрече.\n'
            continue
        
        if user:
            name = user.getName().strip()
        report = report + f'{count} {name}\n'


    dresult = report_raids.aggregate([
        {   "$match": {
                "$and" : [
                    { 
                        "date": {
                            '$gte': from_date,
                            '$lt': to_date
                                }       
                    },
                    {
                        "band": {'$in': getGoatBands(goatName)}   
                    },
                    {
                        "on_raid": False
                    },
                    {
                        "planed_location": {'$ne':None}   
                    }
                ]
            }
        }, 
        {   
            "$group": 
                {
                    "_id": "$login",
                    "count": 
                        {
                            "$sum": 1
                        }
                }
        },    
        {   
            "$sort" : { "count" : -1 } 
        }
    ])
    
    bad_raid_counter = raid_counter
    hrenraid = []

    report = report + f'\n🤬 <b>Хренейдеры</b>:\n'
    j = 0
    for d in dresult:
        name = d.get("_id")
        count = d.get("count")
        if j == 0:
            bad_raid_counter = count

        if isGoatBoss(name):
            report_boss = report_boss + f'Еще наш босс не был на некоторых рейдах, потому что был зянят переписью хренейдеров, забивших на общие цели! Это, надеюсь, всем понятно?!\n'
            report_boss = '\n'+report_boss
            continue
        user = getUserByLogin(name)
        login = name
        if user:
            name = user.getName().strip()

        if bad_raid_counter == count:
            hrenraid.append(f'@{login} {name}\n')
        else:
            report = report + f'{count} {name} \n'
        j = j + 1

    hrenraid_report = ''
    i = 0
    for s in hrenraid:
        if i == 0:
            hrenraid_report = f'\n🚪 <b>Кандидаты на выход</b>:\n'    
        
        hrenraid_report = hrenraid_report + s;
        i = i + 1

    report = report + hrenraid_report + report_boss + f'\n' 
    report = report + '⏰ c ' + time.strftime("%d-%m-%Y", time.gmtime(from_date)) + ' по ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(to_date))

    return report                                 

# 5 secund
def pending_job():
    while True:
        pending_message()
        time.sleep(5)

# 15 secund
def rade_job():
    while True:
        rade()
        time.sleep(15)


def flex_job(counter: int, chatid: str):
    send_messages_big(chatid, f'Ща заебашу {counter} стикеров!')
    bot.send_sticker(chatid, random.sample(getSetting(code='STICKERS', name='BOT_GO_FLEX'), 1)[0]['value'])
    for i in range(0, counter):
        bot.send_sticker(chatid, random.sample(getSetting(code='STICKERS', name='BOT_FLEX'), 1)[0]['value'])
        time.sleep(random.randint(500,2000) / 1000)
    bot.send_sticker(chatid, random.sample(getSetting(code='STICKERS', name='BOT_END_FLEX'), 1)[0]['value'])
    send_messages_big(chatid, f'Хорошо, заебашил {counter} стикеров!')

def main_loop():
    if (config.POLLING):
        bot.remove_webhook()
        bot.polling(none_stop=True)
        while 1:
            time.sleep(3)
    else:
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
        bot.set_webhook(url=f"https://{config.WEBHOOK_HOST}/bot/{str(config.WEBHOOK_PORT)[3:4]}")
        # Build ssl context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)
        # Start aiohttp server
        web.run_app(
            app,
            host=config.WEBHOOK_LISTEN,
            port=config.WEBHOOK_PORT,
            ssl_context=context
        )

if __name__ == '__main__': 
    try:
        # proccess = Process(target=fight_job, args=())
        # proccess.start() # Start new thread

        proccessPending_messages = Process(target=pending_job, args=())
        proccessPending_messages.start() # Start new thread

        proccessRade = Process(target=rade_job, args=())
        proccessRade.start() # Start new thread 

        main_loop()      
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)