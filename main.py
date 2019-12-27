#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config
import users 
import wariors
import tools

import logging
import ssl

from aiohttp import web
from yandex_geocoder import Client

import telebot
from telebot import apihelper
from telebot import types
from telebot.types import Message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import apiai

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
registered_wariors = mydb["wariors"]
battle          = mydb["battle"]
competition     = mydb["competition"]
settings        = mydb["settings"]
pending_messages = mydb["pending_messages"]
plan_raids      = mydb["rades"]
report_raids    = mydb["report_raids"]

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(config.TOKEN)

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

WARIORS_ARR = [] # Зарегистрированные жители пустоши
for x in registered_wariors.find():
    WARIORS_ARR.append(wariors.importWarior(x))

SETTINGS_ARR = [] # Зарегистрированные настройки
for setting in settings.find():
    SETTINGS_ARR.append(setting)

def getSetting(code: str, name=None):
    """ Получение настройки """
    result = settings.find_one({'code': code})
    if (result):
        if name:
            for arr in result.get('value'):
                if arr['name'] == name:
                    return arr['value'] 
        else:
            return result.get('value')

ADMIN_ARR = []
for adm in list(getSetting('ADMINISTRATOR')):
    ADMIN_ARR.append(adm)

def isAdmin(login: str):
    for adm in list(ADMIN_ARR):
        if login.lower() == adm.get('login').lower(): return True
    return False

def getAdminChat(login: str):
    for adm in list(ADMIN_ARR):
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
    for goat in getSetting('GOATS_BANDS'):
        if goat['boss'] == login:
            return True
    return False

def isBandBoss(login: str):
    for goat in getSetting('GOATS_BANDS'):
        for band in goat['bands']:
            if band['boss'] == login:
                return True
    return False

def getMyBands(login: str):
    user = getUserByLogin(login)
    if not user:
        return None

    for goat in getSetting('GOATS_BANDS'):
        for band in goat['bands']:
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                return goat['bands']
    return None        

def getMyBandsName(login: str):
    user = getUserByLogin(login)
    if not user:
        return None
    
    for goat in getSetting('GOATS_BANDS'):
        find = False
        bands = []
        for band in goat['bands']:
            bands.append(band.get('name'))
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                find = True
        if find:
            return bands
    return None     

def getMyGoat(login: str):
    user = getUserByLogin(login)
    if not user:
        return None

    for goat in getSetting('GOATS_BANDS'):
        for band in goat['bands']:
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                return goat['name']

    return None 

def getGoatBands(goatName: str):
    for goat in getSetting('GOATS_BANDS'):
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

    for band in getSetting('BANDS_ACCESS_WARIORS'):
        if user.getBand() and band.get('band').lower() == user.getBand().lower():
            return True

    return False

def getUserByLogin(login: str):
    for user in list(USERS_ARR):
        try:
            if login.lower() == user.getLogin().lower(): return user
        except:
            pass
    return None

def getUserByName(name: str):
    for user in list(USERS_ARR):
        if name.lower().strip() == user.getName().lower().strip(): return user
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
    userIAm = getUserByLogin(login)
    if userIAm:
        if userIAm.getTimeBan():
            tz = config.SERVER_MSK_DIFF
            date_for = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
            if date_for.timestamp() < userIAm.getTimeBan():
                return True
            else:
                userIAm.setTimeBan(None)
                updateUser(userIAm)
    return False

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
    name = tools.deEmojify(name)
    for warior in list(WARIORS_ARR):
        if name == warior.getName() and fraction == warior.getFraction(): 
            return warior
    return None

def isKnownWarior(name: str, fraction: str):
    for warior in list(WARIORS_ARR):
        if warior.getName() and name.lower() == warior.getName().lower() and warior.getFraction() == fraction: 
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
    plan_for_date = 'План рейдов на ' + time.strftime("%d-%m-%Y", time.gmtime( raid_date.timestamp() )) + '\n'
    find = False
    for raid in plan_raids.find({
                                '$and' : 
                                [
                                    {
                                        'rade_date': {
                                        '$gte': (raid_date.replace(hour=0, minute=0, second=0, microsecond=0)).timestamp(),
                                        '$lt': (raid_date.replace(hour=23, minute=59, second=59, microsecond=0)).timestamp(),
                                        }},
                                    {
                                        'goat': goat
                                    }
                                ]
                            }):
        t = datetime.fromtimestamp(raid.get('rade_date') ) 
        plan_for_date = plan_for_date + str(t.hour).zfill(2)+':'+str(t.minute).zfill(2) + ' ' + raid.get('rade_text') + '\n'
        find = True

    if find == False:
        plan_for_date = plan_for_date + 'Нет запланированных рейдов'

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
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
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

def getResponseDialogFlow(text):
    if '' == text.strip():
        text = 'голос!'
    request = apiai.ApiAI(config.AI_TOKEN).text_request() # Токен API к Dialogflow
    request.lang = 'ru' # На каком языке будет послан запрос
    request.session_id = 'BatlabAIBot' # ID Сессии диалога (нужно, чтобы потом учить бота)
    request.query = text # Посылаем запрос к ИИ с сообщением от юзера
    
    # contextStr = '[{"name":"sss", "lifespan":1, "parameters":{"s": "1"}}]';
    # contextObj = json.loads(contextStr);
    # request.contexts = contextObj
    # print(request.contexts)
    responseJson = json.loads(request.getresponse().read().decode('utf-8'))
    response = responseJson['result']['fulfillment']['speech'] # Разбираем JSON и вытаскиваем ответ
    # Если есть ответ от бота - присылаем юзеру, если нет - бот его не понял
    return response

@bot.message_handler(content_types=['new_chat_members', 'left_chat_members'])
def send_welcome_and_dismiss(message):
    bot.send_chat_action(message.chat.id, 'typing')
    time.sleep(3)
    response = getResponseDialogFlow(message.content_type)
    if response:
        bot.send_message(message.chat.id, text=response)

# Handle all other messages
@bot.inline_handler(lambda query: query.query)
def default_query(inline_query):
    if not hasAccessToWariors(inline_query.from_user.username):
        r = types.InlineQueryResultArticle(id=0, title = 'Хрена надо? Ты не из наших банд!', input_message_content=types.InputTextMessageContent(getResponseDialogFlow('i_dont_know_you')), description=getResponseDialogFlow('i_dont_know_you'))
        bot.answer_inline_query(inline_query.id, [r], cache_time=3060)
        return
    
    try:
            result = []
            i = 0
            for x in registered_wariors.find({'$or':[
                    {'name':{'$regex':inline_query.query, '$options':'i'}},
                    {'band':{'$regex':inline_query.query, '$options':'i'}}]
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

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    response = getResponseDialogFlow('start')
    if response:
        bot.send_message(message.chat.id, text=response)

# Handle all other messages
@bot.message_handler(content_types=['document'])
def get_message_photo(message):
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то показать, но у него получилось лишь:\n' + getResponseDialogFlow('user_banned'))
        return

# Handle all other messages
@bot.message_handler(content_types=["photo"])
def get_message_photo(message):
    #write_json(message.json)

    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то показать, но у него получилось лишь:\n' + getResponseDialogFlow('user_banned'))
        return

    if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
        
        privateChat = ('private' in message.chat.type)
        ww = wariors.fromPhotoToWarioirs(message.forward_date, message.caption, message.photo[0].file_id)
        wariorShow = None
        for warior in ww:
            s = f'⏰{tools.getTimeEmoji(warior.getTimeUpdate())} ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(warior.getTimeUpdate()))
            print(warior.getName() + ' ' + s)
            update_warior(warior)
            if not isRegisteredUserName(warior.getName()):
                wariorShow = warior
        
        if privateChat:
            if not wariorShow == None: 
                if (wariorShow and wariorShow.photo):
                    bot.send_photo(message.chat.id, wariorShow.photo, wariorShow.getProfile())
                else:
                    send_messages_big(message.chat.id, text=wariorShow.getProfile())
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
    
# Handle all other messages
@bot.message_handler(content_types=["sticker"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то стикернуть, но у него получилось лишь:\n' + getResponseDialogFlow('user_banned'))
        return

    privateChat = ('private' in message.chat.type)
    if privateChat:
        send_messages_big(message.chat.id, text=message.sticker.file_id)

# Handle '/fight'
@bot.message_handler(commands=['fight'])
def send_welcome(message):
    privateChat = ('private' in message.chat.type)
    if not privateChat:
        return

    list_buttons = []
    isReady = True
    for cuser in competition.find({'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):
        if cuser.get('state') == 'WAIT':
            #list_buttons.append('💰 Ставка')
            list_buttons.append('🤼 В ринг')
            bot.send_message(message.chat.id, text='Ты сам еще не готов к бою!', reply_markup=getButtonsMenu(list_buttons) )
            return

    counter_rabbit = 0
    counter_urban = 0
    for cuser in competition.find({'state': 'READY'}):
        if (cuser.get('band') == '🎩 Городские'):
            counter_urban = counter_urban + 1
        if (cuser.get('band') == '🐇 Мертвые кролики'):
            counter_rabbit = counter_rabbit + 1

    if counter_urban >= 1 and counter_rabbit >= 1:
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
        
        myquery = {'state': 'READY'}
        newvalues = { '$set': { 'state': 'FIGHT' } }
        u = competition.update_many(myquery, newvalues)

        bot.send_message(message.chat.id, text='Бой скоро начнется!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
        bot.send_message(message.chat.id, text='Недостаточно бойцов в одной из банд!', reply_markup=getButtonsMenu(list_buttons) )

# '✅ Готово'
@bot.message_handler(func=lambda message: message.text and '✅ Готово' in message.text and message.chat.type == 'private', content_types=['text'])
def ok_message(message: Message):

    list_buttons = []
 
    isReady = True
    for cuser in competition.find({
                                    'login': message.from_user.username, 
                                    'state': 'WAIT'
                                    }):
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
        isReady = False

    if isReady:
        bot.send_message(message.chat.id, text='Ты готов к бою!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        myquery = {'login': message.from_user.username, 
                     'state': 'WAIT'}
        newvalues = { '$set': { 'state': 'READY' } }
        u = competition.update_one(myquery, newvalues)
        bot.send_message(message.chat.id, text='Готово...', reply_markup=getButtonsMenu(list_buttons) )


# 🎲'⚔ Нападение' '🛡 Защита' '😎 Провокация'
@bot.message_handler(func=lambda message: message.text and message.text in ('⚔ Нападение', '🛡 Защита', '😎 Провокация')  and message.chat.type == 'private', content_types=['text'])
def chose_strategy_message(message: Message):

    etalone = []
    etalone.append('⚔ Нападение')
    etalone.append('🛡 Защита')
    etalone.append('😎 Провокация')

    real = []

    list_buttons = []
 
    isReplay = False
    isReady = False
    isBand = False
    isStrategy = False
    lenStr = 0
    for cuser in competition.find({'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):
        isReplay = True
        if cuser.get('state') == 'READY':
            isReady = True
        
        if cuser.get('band'):
            isBand = True

        if cuser.get('strategy'):
            isStrategy = True
            lenStr = len(cuser.get('strategy'))
            real = cuser.get('strategy')

    if lenStr >= 3:
        if not isBand:
            list_buttons.append('⚖️ Банда')
            bot.send_message(message.chat.id, text='Выбери банду!', reply_markup=getButtonsMenu(list_buttons) )
        else:
            if isReady:
                #list_buttons.append('💰 Ставка')
                list_buttons.append('🤼 В ринг')
                bot.send_message(message.chat.id, text='Готово!', reply_markup=getButtonsMenu(list_buttons) )
            else:
                list_buttons.append('✅ Готово')
                bot.send_message(message.chat.id, text='Жми готово!', reply_markup=getButtonsMenu(list_buttons) )
    elif  lenStr == 0:
        for x in etalone:
            if x == message.text:
                pass
            else:
                list_buttons.append(x)
        real.append(message.text)
        
        myquery = {'login': message.from_user.username, 
                                    '$or': [
                                                {'state': 'WAIT'},
                                                {'state': 'READY'}]    
                                    }
        newvalues = { '$set': { 'strategy': real } }
        u = competition.update_one(myquery, newvalues)
        bot.send_message(message.chat.id, text='Дальше...', reply_markup=getButtonsMenu(list_buttons) )
    else: # 1 - 2
        real.append(message.text)
        myquery = {'login': message.from_user.username, 
                                    # 'chat': message.chat.id,   
                                    '$or': [
                                                {'state': 'WAIT'},
                                                {'state': 'READY'}]    
                                    }

        newvalues = { '$set': { 'strategy':  real} }
        u = competition.update_one(myquery, newvalues)

        for x in etalone:
            find = False
            for z in real:
                if z == x:
                    find = True;
                    break;
            if not find: list_buttons.append(x)
        if len(list_buttons) == 0:
            if not isBand:
                list_buttons.append('⚖️ Банда')
                bot.send_message(message.chat.id, text='Выбери банду!', reply_markup=getButtonsMenu(list_buttons) )
            else:
                if isReady:
                    #list_buttons.append('💰 Ставка')
                    list_buttons.append('🤼 В ринг')
                    bot.send_message(message.chat.id, text='Готово!', reply_markup=getButtonsMenu(list_buttons) ) 
                else:
                    list_buttons.append('✅ Готово')
                    bot.send_message(message.chat.id, text='Жми готово!', reply_markup=getButtonsMenu(list_buttons) )      
        else:
            bot.send_message(message.chat.id, text='Дальше... Еще...', reply_markup=getButtonsMenu(list_buttons) )        

# 🎲 Стратегия
@bot.message_handler(func=lambda message: message.text and '🎲 Стратегия' in message.text and message.chat.type == 'private', content_types=['text'])
def strategy_message(message: Message):
        
    list_buttons = []
 
    isReplay = False
    isReady = False
    for cuser in competition.find({'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):                                                
        isReplay = True
        if cuser.get('state') == 'READY':
            isReady = True

    if isReady:
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
    
        bot.send_message(message.chat.id, text='Ты готов к битве!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        list_buttons.append('⚔ Нападение')
        list_buttons.append('🛡 Защита')
        list_buttons.append('😎 Провокация')
        bot.send_message(message.chat.id, text='Выбирай', reply_markup=getButtonsMenu(list_buttons) )


# 🎩 Городские or 🐇 Мертвые кролики
@bot.message_handler(func=lambda message: message.text and message.text and message.text in ('🎩 Городские', '🐇 Мертвые кролики') and message.chat.type == 'private', content_types=['text'])
def my_band_message(message: Message):

    list_buttons = []
 
    isReplay = False
    isStrategy = False
    isReady = False
    for cuser in competition.find({'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):                                                
        isReplay = True
        if cuser.get('strategy'):
            isStrategy = True
        if cuser.get('state') == 'READY':
            isReady = True

    myquery = {'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }

    newvalues = { '$set': { 'band': message.text } }
    u = competition.update_one(myquery, newvalues)

    if not isStrategy:
        list_buttons.append('🎲 Стратегия')
        bot.send_message(message.chat.id, text='Определись со своими действиями в бою!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        if isReady:
            #list_buttons.append('💰 Ставка')
            list_buttons.append('🤼 В ринг')
        
            bot.send_message(message.chat.id, text='Ты готов к битве!', reply_markup=getButtonsMenu(list_buttons) )
        else:
            list_buttons.append('✅ Готово')
            bot.send_message(message.chat.id, text='Жми готов!', reply_markup=getButtonsMenu(list_buttons) )


# ⚖️ Банда
@bot.message_handler(func=lambda message: message.text and '⚖️ Банда' in message.text  and message.chat.type == 'private', content_types=['text'])
def band_message(message: Message):

    list_buttons = []
 
    isReplay = False
    isBand = False
    for cuser in competition.find({'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):                                                
        isReplay = True
        if cuser.get('band'):
            isBand = True
        break

    if not isReplay:
        list_buttons.append('⚔️ Записаться на бой')
        bot.send_message(message.chat.id, text='Ты не записан!', reply_markup=getButtonsMenu(list_buttons) )

    else:
        if not isBand:
            list_buttons.append('🎩 Городские')
            list_buttons.append('🐇 Мертвые кролики')
        if not cuser.get('strategy'):
            list_buttons.append('🎲 Стратегия')
            
        bot.send_message(message.chat.id, text='Выбирай!', reply_markup=getButtonsMenu(list_buttons) )


# '⚔️ Записаться на бой'
@bot.message_handler(func=lambda message: message.text and '⚔️ Записаться на бой' in message.text and message.chat.type == 'private', content_types=['text'])
def register_message(message: Message):
    
    list_buttons = []
    if not isRegisteredUserLogin(message.from_user.username):
        list_buttons.append('⚔️ Записаться на бой')
        list_buttons.append('🤼 В ринг')
        bot.send_message(message.chat.id, text='Я тебя не знаю! Брось мне свои пип-бой или иди нафиг!', reply_markup=getButtonsMenu(list_buttons))
        return

    isReplay = False
    for cuser in competition.find({'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'},
                                            {'state': 'FIGHT'}]   
                                }):                                                 
        if cuser.get('state') == 'READY':
            list_buttons.append('⚔️ Записаться на бой')
            list_buttons.append('🤼 В ринг')
            bot.send_message(message.chat.id, text='Бой еще не закончен!', reply_markup=getButtonsMenu(list_buttons) )
            return
        isReplay = True
        

    if not isReplay:
        u = getUserByLogin(message.from_user.username)
        competition.insert_one({'login': message.from_user.username, 
                                'chat': message.chat.id,
                                'date': datetime.now().timestamp(), 
                                'state': 'WAIT',
                                'name': u.getName(),
                                'health': u.getHealth(),
                                'damage': u.getDamage(),
                                'armor': u.getArmor(),
                                'accuracy': u.getAccuracy(),
                                'agility': u.getAgility(),
                                'charisma': u.getCharisma(),
                                'bm': u.getBm(),                                
                                'strategy': None,
                                'band': None,
                                'killedBy': None})

        list_buttons.append('⚖️ Банда')
        list_buttons.append('🎲 Стратегия')
        bot.send_message(message.chat.id, text=getResponseDialogFlow('sign_up_for_a_fight'), reply_markup=getButtonsMenu(list_buttons) )
    else:
        if not cuser.get('band'):
            list_buttons.append('⚖️ Банда')
        if not cuser.get('strategy'):
            list_buttons.append('🎲 Стратегия')

        bot.send_message(message.chat.id, text=getResponseDialogFlow('sign_up_replay'), reply_markup=getButtonsMenu(list_buttons) )

# Handle 🤼 В ринг
@bot.message_handler(func=lambda message: message.text and '🤼 В ринг' in message.text and message.chat.type == 'private', content_types=['text'])
def ring_message(message: Message):

    list_buttons = []

    isReplay = False
    isStrategy = False
    isReady = False
    isBand = False
    for cuser in competition.find({'login': message.from_user.username, 
                                # 'chat': message.chat.id,   
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'},
                                            {'state': 'FIGHT'}]   
                                }):                                                 
        isReplay = True
        if cuser.get('state') == 'READY':
            isReady = True

        if cuser.get('strategy'):
            isStrategy = True

        if cuser.get('band'):
            isBand = True

        if isStrategy and isBand and len(cuser.get('strategy')) >= 3 and cuser.get('state') == 'WAIT':
            list_buttons.append('✅ Готово')     

        if cuser.get('state') == 'WAIT':
            if not cuser.get('band'):
                list_buttons.append('⚖️ Банда')
            if not cuser.get('strategy') or len(cuser.get('strategy')) <3:
                list_buttons.append('🎲 Стратегия')
            break
            

    usersOnCompetition = '🤼 В ринге:\n\n'
    i = 0
    for cuser in competition.find({'$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'},
                                            {'state': 'FIGHT'}]
                                        }):
        i = i + 1
        band = cuser.get("band")
        state = cuser.get('state')
        if state == 'WAIT':
            state = '⏳'
        elif state == 'READY':
            state = '✅'
        elif state == 'FIGHT':
            state = '⚔'
        if not band:
            band = '❔'

        usersOnCompetition = usersOnCompetition + f'{i}.{state} {band[0:1]} {cuser.get("name")} 📯{cuser.get("bm")}\n'

    if i == 0:
        usersOnCompetition = 'Никого нет в ринге! Запишись первым!\n'
        list_buttons.append('⚔️ Записаться на бой')
    else:
        if (not isReplay):
            list_buttons.append('⚔️ Записаться на бой')
        list_buttons.append('🤼 В ринг')
        usersOnCompetition = usersOnCompetition + '\nНачать бой /fight\n' 
    
    usersOnCompetition = usersOnCompetition + '\n' 
    usersOnCompetition = usersOnCompetition + '⏰ ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(datetime.now().timestamp())) +'\n'

    bot.send_message(message.chat.id, text=usersOnCompetition, reply_markup=getButtonsMenu(list_buttons) ) 

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def main_message(message):
    #write_json(message.json)
    logger.info('message.from_user.username: '+message.from_user.username)
    logger.info('message.text: ' + message.text)

    black_list = getSetting('BLACK_LIST', message.from_user.username)
    if black_list:
        send_messages_big(message.chat.id, text=f'{message.from_user.username} заслужил пожизненный бан {black_list}', reply_markup=None)
        send_message_to_admin(f'⚠️Внимание! \n {message.from_user.username} написал Джу:\n\n {message.text}')
        return

    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        user = getUserByLogin(message.from_user.username)
        name = message.from_user.username
        if user:
            name = user.getName()
        send_messages_big(message.chat.id, text=f'{name} хотел что-то сказать, но у него получилось лишь:\n' + getResponseDialogFlow('user_banned'), reply_markup=None)
        return


    privateChat = ('private' in message.chat.type)
    callJugi = (privateChat 
                            or message.text.lower().startswith('джу') 
                            or (message.reply_to_message 
                                and message.reply_to_message.from_user.is_bot 
                                and message.reply_to_message.from_user.username in ('FriendsBrotherBot', 'JugiGanstaBot') )
                )

    findUser = isRegisteredUserLogin(message.from_user.username)
    userIAm = getUserByLogin(message.from_user.username)

    logger.info('findUser: ' + str(findUser))
    
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
    if not privateChat:
        markup.add('Джу, 📋 Отчет', 'Джу, 📜 Профиль', f'Джу, ⏰ план рейда')
    else:
        markup.add('📋 Отчет', '📜 Профиль', '🤼 В ринг', f'⏰ План рейда')



    if (message.text.startswith('📟Пип-бой 3000') and 
            '/killdrone' not in message.text and 
            'ТОП ФРАКЦИЙ' not in message.text and 
            'СОДЕРЖИМОЕ РЮКЗАКА' not in message.text and 
            'ПРИПАСЫ В РЮКЗАКЕ' not in message.text and 
            'РЕСУРСЫ и ХЛАМ' not in message.text ):
        if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
            if 'ТОП ИГРОКОВ:' in message.text:
                ww = wariors.fromTopToWariorsBM(message.forward_date, message, registered_wariors)
                for warior in ww:
                    update_warior(warior)
                send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
                return
            
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow('deceive'))
                return

            user = users.User(message.from_user.username, message.forward_date, message.text)
            if findUser==False:   
                x = registered_users.insert_one(json.loads(user.toJSON()))
                updateUser(None)
                send_message_to_admin(f'⚠️Внимание! Зарегистрировался новый пользователь.\n {user.getProfile()}')
            else:
                updatedUser = users.updateUser(user, users.getUser(user.getLogin(), registered_users))
                updateUser(updatedUser)
            if privateChat:
                send_messages_big(message.chat.id, text=getResponseDialogFlow('setpip'))
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow('deceive')) 
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'FIGHT!' in message.text):
        #write_json(message.json)
        ww = wariors.fromFightToWarioirs(message.forward_date, message, USERS_ARR, battle)
        if ww == None:
            send_messages_big(message.chat.id, text=getResponseDialogFlow('dublicate'))
            return
        for warior in ww:
            update_warior(warior)
        
        send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
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
            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_you_cant'))
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
            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_you_cant'))
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'Ты занял позицию для ' in message.text and 'Рейд начнётся через' in message.text):
        #write_json(message.json)
        if hasAccessToWariors(message.from_user.username):
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow('deceive'))
                return

            u = getUserByLogin(message.from_user.username)
            u.setRaidLocation(1)
            updateUser(u)
            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_you_cant'))
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'Панель банды.' in message.text):
        #write_json(message.json)
        if hasAccessToWariors(message.from_user.username):
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow('deceive'))
                return

            strings = message.text.split('\n')
            i = 0
            band = ''
            allrw = 0
            allcounter = 0
            onraidrw = 0
            onraidcounter = 0
            onraidReport = ''
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
                    if not isUsersBand(message.from_user.username, band):
                        send_messages_big(message.chat.id, text=f'Ты принес панель банды {band}\n' + getResponseDialogFlow('not_right_band'))
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
                        
                        if '👊' in strings[i]:
                            onraidrw = onraidrw + u.getRaidWeight()
                            u.setRaidLocation(km)
                            updateUser(u)
                            onraidcounter = onraidcounter + 1
                            onraidReport = onraidReport + f'{onraidcounter}.🏋️‍♂️{u.getRaidWeight()} {u.getName()} {spliter}{km}км\n'

                        else:
                            fuckupraidrw = fuckupraidrw + u.getRaidWeight()
                            fuckupraidcounter = fuckupraidcounter + 1
                            fuckupusers.append(u)
                            fuckupusersReport = fuckupusersReport + f'{fuckupraidcounter}.🏋️‍♂️{u.getRaidWeight()} {u.getName()} {spliter}{km}км\n' 
                    else:
                        aliancounter  = aliancounter + 1
                        alianusersReport = alianusersReport + f'{aliancounter}. {name} {spliter}{km}км\n'
                        
                i = i + 1
            
            report = report + f'🤘 <b>{band}</b>\n\n' 
            if onraidcounter > 0:
                report = report + f'🧘‍♂️ <b>на рейде</b>: <b>{onraidcounter}/{allcounter}</b>\n'
                report = report + onraidReport
                report = report + f'\n<b>Общий вес</b>: 🏋️‍♂️{onraidrw}/{allrw} <b>{str(int(onraidrw/allrw*100))}%</b>\n'
            report = report + '\n'
            if fuckupraidrw > 0:
                report = report + '🐢 <b>Бандиты в проёбе</b>:\n'
                report = report + fuckupusersReport
            report = report + '\n'
            if alianusersReport == '':
                pass
            else:
                report = report + '🐀 <b>Крысы в банде</b> (нет регистрации):\n'
                report = report + alianusersReport
            
            if onraidcounter > 0 or aliancounter > 0:
                bot.delete_message(message.chat.id, message.message_id)
                send_messages_big(message.chat.id, text=report)
                
                # ping_on_reade(fuckupusers, message.chat.id)
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow('no_one_on_rade'))
        else:
            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_you_cant'))
        return

    if not findUser:
        r = random.random()
        if (r <= float(getSetting('PROBABILITY','I_DONT_KNOW_YOU'))):
            send_messages_big(message.chat.id, text=getResponseDialogFlow('i_dont_know_you'))

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

        elif (callJugi 
                    and message.reply_to_message
                    and message.text 
                    and ('это залёт' in message.text.lower() or 'это залет' in message.text.lower())
                ):
            login = message.reply_to_message.from_user.username

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
            sec = int(randrange(int(getSetting('PROBABILITY','FUNY_BAN'))))
            tz = config.SERVER_MSK_DIFF
            ban_date = datetime.now() + timedelta(seconds=sec, hours=tz.hour)
            
            user.setTimeBan(ban_date.timestamp())
            report = f'{user.getName()} будет выписан бан! Злой Джу определил, что ⏰{sec} секунд(ы) будет достаточно!'
            updateUser(user)
            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs') + f'\n{report}')
    
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
            
        elif (callJugi and 'профиль @' in message.text.lower()):

            name = tools.deEmojify(message.text.split('@')[1].strip())
            if isAdmin(message.from_user.username):
                login = message.text.split('@')[1].strip()
                if (isRegisteredUserName(name) or isRegisteredUserLogin(login)):
                    user = getUserByLogin(login)
                    if not user:
                        user = getUserByName(name)
                    if user:
                        send_messages_big(message.chat.id, text=user.getProfile())
                else:
                    send_messages_big(message.chat.id, text=f'В базе зарегистрированнных бандитов {login} не найден')

            for x in registered_wariors.find({'name':f'{name}'}):
                warior = wariors.importWarior(x)
                if (warior and warior.photo):
                    try:
                        bot.send_photo(message.chat.id, warior.photo, warior.getProfile())
                    except:
                        send_messages_big(message.chat.id, text=warior.getProfile())
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile())
                    
        elif (callJugi and 'уволить @' in message.text.lower()):
            if not isGoatBoss(message.from_user.username):
                if not isAdmin(message.from_user.username):
                    send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_not_goat_boss'))
                    return

            login = message.text.split('@')[1].strip()
            user = getUserByLogin(login)
            if not user:
                send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                return

            if not isAdmin(message.from_user.username):
                if not isUsersBand(message.from_user.username, user.getBand()):
                    send_messages_big(message.chat.id, text=f'Бандит {login} не из банд твоего козла!')
                    return

            myquery = { "login": f"{login}" }
            doc = registered_users.delete_one(myquery)
            updateUser(None)
            
            myquery = { "name": f"{login}" }
            war = registered_wariors.delete_one(myquery)

            if doc.deleted_count == 0:
                send_messages_big(message.chat.id, text=f'{login} не найден в бандитах! Удалено {war.deleted_count} в дневнике боев!')
            else:                 
                send_messages_big(message.chat.id, text=f'{login} уволен нафиг! Удалено {doc.deleted_count} записей в дневнике бандитов и {war.deleted_count} в дневнике боев!')

        elif (callJugi and 'профиль' in message.text.lower()):
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
            response = getResponseDialogFlow(text)
            if response:
                if (response.startswith('jugi:')):
                    #jugi:ping:Артхаус
                    if 'ping' == response.split(':')[1]:
                        # Собираем всех пользоватлей с бандой Х
                        band = response.split(':')[2][1:]
                        if not isUsersBand(message.from_user.username, band):
                            send_messages_big(message.chat.id, text=f'Ты просил собраться банду{response.split(":")[2]}\n' + getResponseDialogFlow('not_right_band'))
                            return

                        first_string = f'{tools.deEmojify(message.from_user.first_name)} просит собраться банду\n<b>{response.split(":")[2]}</b>:\n'
                        usersarr = []
                        for registered_user in registered_users.find({"band": f"{band}"}):
                            user = users.importUser(registered_user)
                            registered_user.update({'weight': user.getRaidWeight()})
                            usersarr.append(registered_user)

                        # Пингуем
                        counter = 0
                        pingusers = []
                        report = f''
                        for pu in sorted(usersarr, key = lambda i: i['weight'], reverse=True):
                            counter = counter + 1
                            pingusers.append(pu)
                            report = report + f'{counter}. @{pu["login"]} 🏋️‍♂️{pu["weight"]} \n'
                            if counter % 5 == 0:
                                send_messages_big(message.chat.id, text=first_string + report)
                                pingusers = []
                                report = f''

                        if len(pingusers) > 0:
                            send_messages_big(message.chat.id, text=first_string + report)
                    elif 'planrade' == response.split(':')[1]:
                        # jugi:planrade:$date
                        goat = getMyGoat(message.from_user.username)

                        if response.split(response.split(":")[1])[1][1:].strip() == '*':
                            tz = config.SERVER_MSK_DIFF
                            plan_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
                            if plan_date.hour > 17:
                                raid_date = plan_date + timedelta(days=1)
                            else:
                                raid_date = plan_date
                        else:
                            raid_date = parse(response.split(response.split(":")[1])[1][1:])

                        plan_str = get_raid_plan(raid_date, goat)
                        msg = send_messages_big(message.chat.id, text=plan_str, reply_markup=markup)
                    elif 'onrade' == response.split(':')[1]:
                        # jugi:onrade:$goat
                        # if not isAdmin(message.from_user.username):
                        #     send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_not_admin'))
                        #     return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoat(message.from_user.username)

                        if not getMyGoat(message.from_user.username) == goatName:
                            send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow('shot_you_cant'))
                            return

                        for goat in getSetting('GOATS_BANDS'):
                            if goatName == goat.get('name'):
                                report = radeReport(goat)
                                send_messages_big(message.chat.id, text=report)
                    elif 'statistic' == response.split(':')[1]:
                        # jugi:statistic:*
                        if not isGoatBoss(message.from_user.username):
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_not_admin'))
                                return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoat(message.from_user.username)

                        if not getMyGoat(message.from_user.username) == goatName:
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow('shot_you_cant'))
                                return

                        report = statistic(goatName)
                        send_messages_big(message.chat.id, text=report) 
                    elif 'clearrade' == response.split(':')[1]:
                        # jugi:clearrade:*
                        if not isAdmin(message.from_user.username):
                            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_not_admin'))
                            return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoat(message.from_user.username)

                        if not getMyGoat(message.from_user.username) == goatName:
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow('shot_you_cant'))
                                return
                        registered_users.update_many(
                            {'band':{'$in':getGoatBands(goatName)}},
                            { '$set': { 'raidlocation': None} }
                        )

                        updateUser(None)
                        send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))        
                    elif 'ban' == response.split(':')[1] or 'unban' == response.split(':')[1]:
                        # if not isAdmin(message.from_user.username):
                        #     bot.reply_to(message, text=getResponseDialogFlow('shot_message_not_admin'))
                        #     return

                        # jugi:ban:@gggg на:2019-12-01T13:21:52/2019-12-01T13:31:52
                        ban = ('ban' == response.split(':')[1])
                        login = response.split(':')[2]
                        login = login.replace('@','').split(' ')[0].strip()
                        
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

                        time_str = response.split(response.split(':')[2])[1][1:]
                        date_for = None
                        if ban:
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
                            user.setTimeBan(date_for.timestamp())
                            report = f'{user.getName()} забанен нахрен до\n'+'⏰' + time.strftime("%H:%M:%S %d-%m-%Y", time.gmtime(date_for.timestamp()))
                        else:
                            user.setTimeBan(None)
                            report = f'{user.getName()} разбанен. Говори, дорогой!'
                        updateUser(user)

                        user = getUserByLogin(user.getLogin())
                        send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs') + f'\n{report}')
                    elif 'rade' == response.split(':')[1]:
                        if isGoatBoss(message.from_user.username) or isAdmin(message.from_user.username):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_not_goat_boss'))
                            return
                        
                        goat = getMyGoat(message.from_user.username)
                        #   0    1        2         3        4     
                        # jugi:rade:$radelocation:$bool:$date-time
                        raid_date = parse(response.split(response.split(":")[3])[1][1:])
                        if raid_date.hour not in (1, 9, 17):
                            send_messages_big(message.chat.id, text='Рейды проходят только в 1:00, 9:00, 17:00!\nУкажи правильное время!')
                            return 

                        # Проверка на будущую дату
                        tz = config.SERVER_MSK_DIFF
                        dt = raid_date - timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
                        if (dt.timestamp() < datetime.now().timestamp()):
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow('timeisout'))
                            return

                        rade_text = response.split(":")[2]
                        rade_location = int(response.split(":")[2].split('📍')[1].split('км')[0].strip())

                        if eval(response.split(":")[3]):
                            myquery = { 
                                        "rade_date": raid_date.timestamp(), 
                                        "goat": goat
                                    }
                            newvalues = { "$set": { 
                                            'rade_date': raid_date.timestamp(),
                                            'rade_text': rade_text,
                                            'rade_location': rade_location,
                                            'state': 'WAIT',
                                            'chat_id': message.chat.id,
                                            'login': message.from_user.username,
                                            'goat': goat
                                        } } 
                            u = plan_raids.update_one(myquery, newvalues)

                            if u.matched_count == 0:
                                plan_raids.insert_one({ 
                                    'create_date': datetime.now().timestamp(), 
                                    'rade_date': raid_date.timestamp(),
                                    'rade_text': rade_text,
                                    'rade_location': rade_location,
                                    'state': 'WAIT',
                                    'chat_id': message.chat.id,
                                    'login': message.from_user.username,
                                    'goat': goat})
                        else:
                            plan_raids.delete_one({
                                            'rade_date': raid_date.timestamp(),
                                            })

                        plan_str = get_raid_plan(raid_date, goat)
                        msg = send_messages_big(message.chat.id, text=plan_str)                                 
                    elif 'getchat' == response.split(':')[1]:
                        send_messages_big(message.chat.id, text=f'Id чата {message.chat.id}')
                    elif 'capture' == response.split(':')[1]:
                            #   0    1        2       3     4
                            # jugi:capture:$bands:$Dangeon:$time
                            band = response.split(':')[2][1:]
                            if not isUsersBand(message.from_user.username, band):
                                send_messages_big(message.chat.id, text=f'Ты пытался созвать на захват банду {response.split(":")[2]}\n' + getResponseDialogFlow('not_right_band'))
                                return  

                            time_str = response.split(response.split(":")[3])[1][1:]
                            dt = parse(time_str)
                            time_str = str(dt.hour).zfill(2)+':'+str(dt.minute).zfill(2)

                            first_string = f'<b>Захват!</b> {response.split(":")[2]} {time_str} <b>{response.split(":")[3]}</b>\n'
                            
                            usersarr = []
                            for registered_user in registered_users.find({"band": f"{band}"}):
                                user = users.importUser(registered_user)
                                registered_user.update({'weight': user.getRaidWeight()})
                                usersarr.append(registered_user)

                            # Пингуем
                            counter = 0
                            pingusers = []
                            report = f''
                            for pu in sorted(usersarr, key = lambda i: i['weight'], reverse=True):
                                counter = counter + 1
                                pingusers.append(pu)
                                report = report + f'{counter}. @{pu["login"]} 🏋️‍♂️{pu["weight"]} \n'
                                if counter % 5 == 0:
                                    send_messages_big(message.chat.id, text=first_string + report)
                                    pingusers = []
                                    report = f''

                            if len(pingusers) > 0:
                                send_messages_big(message.chat.id, text=first_string + report)

                            if not privateChat:
                                bot.pin_chat_message(message.chat.id, msg.message_id)
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
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow('timeisout'))
                            return

                        reply_message = None
                        if message.reply_to_message:
                            reply_message = message.reply_to_message.json

                        pending_messages.insert_one({ 
                            'chat_id': message.chat.id,
                            'reply_message': reply_message,
                            'create_date': datetime.now().timestamp(), 
                            'state': 'WAIT',
                            'pending_date': dt.timestamp(),
                            'dialog_flow_text': 'remindme',
                            'text': None})
                        
                        msg = send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'))
                    elif 'sticker' == response.split(':')[1]: 
                        #jugi:sticker:CAADAgADawgAAm4y2AABx_tlRP2FVS8WBA:Ми-ми-ми
                        photo = response.split(':')[2]
                        text = response.split(':')[3]
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
                                send_messages_big(message.chat.id, text=getResponseDialogFlow('understand'))
                            else:
                                # Display the current time in that time zone
                                timezone = pytz.timezone(timezone_str)
                                dt = datetime.utcnow()
                                userIAm.setLocation(response.split(':')[2])
                                userIAm.setTimeZone(str(timezone.utcoffset(dt)))
                                updateUser(userIAm)
                                send_messages_big(message.chat.id, text='Круто!\nЭто ' + str(timezone.utcoffset(dt)) + ' к Гринвичу!')

                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow('understand'))
                    elif 'rating' == response.split(':')[1]:
                        report = ''
                        report = report + f'🏆ТОП 5 УБИЙЦ 🐐<b>{getMyGoat(userIAm.getLogin())}</b>\n'
                        report = report + '\n'
                        setting = getSetting('REPORTS','KILLERS')
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
                            if not isRegisteredUserName(user_name): continue

                            i = i + 1
                            if i == 1:
                                emoji = '🥇 '
                            elif i == 2:
                                emoji = '🥈 '    
                            elif i == 3:
                                emoji = '🥉 '
                            else:
                                emoji = ''
                            
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
                            if not isRegisteredUserName(user_name): continue
                            
                            i = i + 1
                            if i == 1:
                                emoji = '👻 '
                            elif i == 2:
                                emoji = '💀️ '    
                            elif i == 3:
                                emoji = '☠️ '
                            else:
                                emoji = ''

                            if user_name == tools.deEmojify(message.from_user.first_name):
                                user_name = f'<b>{user_name}</b>'
                                findInLoser = i

                            if i <= 5: report = report + f'{i}. {emoji}{user_name}: {d.get("count")}\n' 
                             

                        if (i == 0): 
                            report = report + f'Мы бессмертны ✌️👻💀☠️\n'
                        else:
                            if (findInLoser > 5): report = report + f'\n🧸 Твое место - {findInLoser}!\n'
                        report = report + f'\n' 
                        report = report + '⏰ c ' + time.strftime("%d-%m-%Y", time.gmtime(from_date)) + ' по ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(to_date))
                        
                        send_messages_big(message.chat.id, text=report)
                else:
                    try:
                        
                        send_messages_big(message.chat.id, text=response, reply_markup=markup)
                    except:
                        logger.info("Error!")
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow('understand'))
        return
    else:
        logger.info(getResponseDialogFlow('you_dont_our_band_gangster'))
        return

def insert_dash(string, index, char):
    return string[:index] + char + string[index:]

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in ("capture_yes", "capture_no"):
        markupinline = InlineKeyboardMarkup()
        markupinline.row_width = 2
        markupinline.add(InlineKeyboardButton("Иду!", callback_data="capture_yes"),
        InlineKeyboardButton("Нахер!", callback_data="capture_no"))
        boldstring = []
        text = call.message.text

        # print(text)
        # for s in call.message.entities:
        #     print(s)
        #     if s.type == 'bold':
        #         print(s)
        #         print(text[s.offset : s.offset+s.length])
                
        #         boldstring.append(text[s.offset : s.offset+s.length])

        # for z in boldstring:
        #     print(z)
        #     print(z.decode('ascii') )
        #     #text = text.replace(z, f'<b>{z}</b>')

        if call.data == "capture_yes" :
            bot.answer_callback_query(call.id, "Ты записался в добровольцы!")
            text = text.replace(f'@{call.from_user.username}', f'<b>@{call.from_user.username}</b>')

        elif call.data == "capture_no":
            bot.answer_callback_query(call.id, "Сыкло!")
            text = text.replace(f'<b>@{call.from_user.username}</b>', f'@{call.from_user.username}')

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
    for adm in ADMIN_ARR:
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

def fight():
    #logger.info('Calculate fight')

    bands = ['🎩 Городские', '🐇 Мертвые кролики']
    figthers_rabbit = []
    figthers_urban = []
    fighters = [figthers_rabbit, figthers_urban]
    max_damage = 0
    min_damage = 10000000
    max_armor = 0
    findFighters = False
    for fighter in competition.find({'state': 'FIGHT'}):
        if fighter.get('band') == '🎩 Городские':
            figthers_urban.append(fighter)
        if fighter.get('band') == '🐇 Мертвые кролики':
            figthers_rabbit.append(fighter)
        if max_damage < int(str(fighter.get('damage')).split(' ')[0]): max_damage = int(str(fighter.get('damage')).split(' ')[0])
        if max_armor < int(str(fighter.get('armor')).split(' ')[0]): max_armor = int(str(fighter.get('armor')).split(' ')[0])
        if min_damage > int(str(fighter.get('damage')).split(' ')[0]): min_damage = int(str(fighter.get('damage')).split(' ')[0])
        findFighters = True

    if not findFighters:
        return

    # Какя банда начинает первой

    band1 = random.sample(fighters,  1)[0]
    fighters.remove(band1)
    band2 = random.sample(fighters,  1)[0]
 
    first = band1
    second = band2

    bot.send_message(fighter.get('chat'), text=f'Банда <b>{band1[0].get("band")}</b> воспользовалась неожиданностью и напала первой!', parse_mode='HTML')

    killed = []
    j = 0
    
    while True:
        j = j + 1
        doExit = False
        if len(first) == 0 or len(second) == 0:
            break

        f1 = random.sample(first,  1)[0]
        f2 = random.sample(second,  1)[0]         

        health1 = float(f1.get('health').split(' ')[0])
        health2 = float(f2.get('health').split(' ')[0])

        doBreak = False
        vs_log = '<b>⚔ ХОД БИТВЫ:</b>\n\n'
        vs_log = f'❤{f1.get("health")} <b>{f1.get("band")[0:1]} {f1.get("name")}</b>\nvs\n❤{f2.get("health")} <b>{f2.get("band")[0:1]} {f2.get("name")}</b>\n\n'
        damage = 0

        for i in range(0, 3):
            strategy1 = f1.get('strategy')[i]
            strategy2 = f2.get('strategy')[i]

            damage1 = float(str(f1.get('damage')).split(' ')[0])
            damage2 = float(str(f2.get('damage')).split(' ')[0])

            armor1 = float(str(f1.get('armor')).split(' ')[0])
            armor2 = float(str(f2.get('armor')).split(' ')[0])
            fight_str = ''


            # ⚔ 1024 vs ⚔ 800
            # 🛡 276  vs 🛡 300
            # ❤ 650  vs ❤ 500

            #1 - 1024

            #1 - 800


            if strategy1 == '⚔ Нападение':
                if strategy2 == '⚔ Нападение':
                    damage1 = damage1 * 1
                    damage2 = damage2 * 1
                    fight_str = '⚔⚔'
                if strategy2 == '🛡 Защита':
                    damage1 = damage1 * 1
                    armor2 = armor2 * 4
                    fight_str = '⚔🛡'
                if strategy2 == '😎 Провокация':
                    damage2 = damage2 * 0
                    fight_str = '⚔😎'
            if strategy1 == '🛡 Защита':
                if strategy2 == '⚔ Нападение':
                    armor1 = armor1 * 4
                    damage2 = damage2 * 1
                    fight_str = '🛡⚔'
                if strategy2 == '🛡 Защита':
                    armor1 = armor1 * 4
                    armor2 = armor2 * 4
                    fight_str = '🛡🛡'
                if strategy2 == '😎 Провокация':
                    armor2 = armor2 * 0  
                    fight_str = '🛡😎'
            if strategy1 == '😎 Провокация':
                if strategy2 == '⚔ Нападение':
                    damage2 = damage2 * 0
                    fight_str = '😎⚔'
                if strategy2 == '🛡 Защита':
                    armor2 = armor2 * 0
                    fight_str = '😎🛡'
                if strategy2 == '😎 Провокация':
                    armor1 = armor1 * random.random()  
                    armor2 = armor2 * random.random()  
                    damage1 = damage1 * random.random()  
                    damage2 = damage2 * random.random()  
                    fight_str = '😎😎'

            # health1 = health1 -  ( (Урон2-Защита1) / МахУрон) * МинУрон * 0.1)
            # health2 = health2 -  ( (Урон1-Защита2) / МахУрон) * МинУрон * 0.1)
            #
            # '⚔ Нападение', '🛡 Защита', '😎 Провокация'

            # print(f'{j} health1  = {health1} -  ( ({damage2}-{armor1}) / {max_damage}) * {min_damage} = {health1}: {(damage2-armor1)/max_damage*min_damage*0.1})')
            # print(f'{j} health2  = {health2} -  ( ({damage1}-{armor2}) / {max_damage}) * {min_damage} = {health1}: {(damage1-armor2)/max_damage*min_damage*0.1})')
            dmg1 = (damage2-armor1)/max_damage*min_damage*0.35
            dmg2 = (damage1-armor2)/max_damage*min_damage*0.35
            
            if int(dmg1) > int(dmg2):
                damage = dmg1-dmg2
                health2 = health2 - damage
                f2.update({'health': str(int(health2))})
                vs_log = vs_log + f'{fight_str} ❤{f2.get("health")} 💥{str(int(damage))} <b>{f1.get("band")[0:1]} {f1.get("name")}</b> {getResponseDialogFlow("you_win")}\n'
                if int(f2.get("health")) <= 0:
                    killed.append(f2)
                    second.remove(f2)
                    f2.update({'killedBy': f'{f1.get("band")[0:1]} {f1.get("name")}'})
                    break
            elif int(dmg1) == int(dmg2): 
                damage = 0
                vs_log = vs_log + f'{fight_str} {getResponseDialogFlow("draw_competition")}\n'
            else:
                damage = dmg2-dmg1
                health1 = health1 - damage
                f1.update({'health': str(int(health1))})
                vs_log = vs_log + f'{fight_str} ❤{f1.get("health")} 💥{str(int(damage))} <b>{f2.get("band")[0:1]} {f2.get("name")}</b> {getResponseDialogFlow("you_win")}\n'
                if int(f1.get("health")) <= 0:
                    killed.append(f1)
                    first.remove(f1)
                    f1.update({'killedBy': f'{f2.get("band")[0:1]} {f2.get("name")}'})
                    break

        if int(f1.get('health')) <= 0:
                vs_log = vs_log + f'\n'
                vs_log = vs_log + f'☠️ {f1.get("health")} <b>{f1.get("band")[0:1]} {f1.get("name")}</b> {getResponseDialogFlow("you_deadman")}\n'
        elif int(f2.get('health')) <= 0:
                vs_log = vs_log + f'\n'
                vs_log = vs_log + f'☠️ {f2.get("health")} <b>{f2.get("band")[0:1]} {f2.get("name")}</b> {getResponseDialogFlow("you_deadman")}\n'
        else:
                vs_log = vs_log + f'\n'
                vs_log = vs_log + f'{getResponseDialogFlow("draw_competition")}\n'

        send_messages_big(chat_id = f1.get('chat'), text=vs_log)
        send_messages_big(chat_id = f2.get('chat'), text=vs_log)
        time.sleep(5)

    fight_log = '<b>ИТОГИ БОЯ:</b>\n\n'
 
    winners = []
    if len(first) == 0:
        winners = second 
    if len(second) == 0:
        winners = first
    
    if (len(winners)>0):
        fight_log = fight_log + f'Победила банда <b>{winners[0].get("band")}</b>\n'
        m = 0
        for winFigther in winners:
            m = m + 1
            fight_log = fight_log + f'{m}. ❤{winFigther.get("health")} <b>{winFigther.get("band")[0:1]} {winFigther.get("name")}</b> \n'
    else:
        fight_log = fight_log + f'ВСЕ УМЕРЛИ!\n'

    fight_log = fight_log + f'\n'
    z = 0
    for deadman in killed:
        z = z+1
        fight_log = fight_log + f'{z}. ☠️{deadman.get("health")} <b>{deadman.get("band")[0:1]} {deadman.get("name")}</b> убит бойцом <b>{deadman.get("killedBy")}</b>\n'

    fight_log = fight_log + f'\n'
    fight_log = fight_log + '⏰ ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(datetime.now().timestamp())) +'\n'

    for fighter in competition.find({'state': 'FIGHT'}):
        send_messages_big(chat_id = fighter.get('chat'), text=fight_log)

    z = 0
    for deadman in killed:
        z = z+1
        myquery = { 'login': deadman.get('login'), 'state' : 'FIGHT'}
        newvalues = { '$set': { 'state': 'CANCEL', 'health': deadman.get('health'), 'killedBy': deadman.get('killedBy') } }
        u = competition.update_one(myquery, newvalues)

    for winner in winners:  
        myquery = { 'login': winner.get('login'), 'state' : 'FIGHT'}
        newvalues = { '$set': { 'state': 'CANCEL', 'health': winner.get('health') } }
        u = competition.update_one(myquery, newvalues)        

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
        if pending_message.get('dialog_flow_text'):
            text = getResponseDialogFlow(pending_message.get('dialog_flow_text'))
        
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
    fuckupusersReport = f'🐢 <b>Бандиты! {getResponseDialogFlow("rade_motivation")}</b>\n🤟<b>{fuckupusers[0].getBand()}</b>\n'
    for fu in fuckupusers:
        counter = counter + 1
        fusers.append(fu)
        fuckupusersReport = fuckupusersReport + f'{counter}. @{fu.getLogin()}\n' 
        if counter % 5 == 0:
            send_messages_big(chat_id, text=fuckupusersReport)
            fusers = []
            fuckupusersReport = f'🐢 <b>Бандиты! {getResponseDialogFlow("rade_motivation")}</b>\n🤟<b>{fuckupusers[0].getBand()}</b>\n'

    if len(fusers) > 0:
        send_messages_big(chat_id, text=fuckupusersReport)

def rade():
    tz = config.SERVER_MSK_DIFF
    now_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
    
    # 497065022 goat['chat'] Джу
    # goat['chat']

    logger.info('check rade time: now ' + str(now_date))
    
    if now_date.day == 28 and now_date.month == 12 and now_date.hour == 0 and now_date.minute in (0,1,2,3,4,5,6,7,8,9, 38,39,40) and now_date.second < 15:
        for goat in getSetting('GOATS_BANDS'):
            bot.send_message(goat['chat'], text='С новым годом!')
            getSetting('STICKERS','NEW_YEAR')
            bot.send_sticker(497065022, random.sample(getSetting('STICKERS','NEW_YEAR'), 1)[0]['value']) 

    if now_date.hour in (0, 8, 16) and now_date.minute in (0, 30, 50) and now_date.second < 15:
        
        updateUser(None)
        for goat in getSetting('GOATS_BANDS'):
            if getPlanedRaidLocation(goat['name'], planRaid = True)['rade_location']:
                report = radeReport(goat, True)
                send_messages_big(goat['chat'], text=f'<b>{str(60-now_date.minute)}</b> минут до рейда!\n' + report)

    if now_date.hour in (1, 9, 17) and now_date.minute == 0 and now_date.second < 15:
        logger.info('Rade time now!')
        updateUser(None)
        for goat in getSetting('GOATS_BANDS'):
            if getPlanedRaidLocation(goat['name'], planRaid = False)['rade_location']:
                report = radeReport(goat)
                send_messages_big(goat['chat'], text='<b>Результаты рейда</b>\n' + report)
                saveRaidResult(goat)
                statistic(goat['name'])

        for goat in getSetting('GOATS_BANDS'):
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
    goat_report.update({'chat': goat.get('chat')})
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
                report = report + f'{counter}. {u.getName()} 📍{location}км\n'
            report = report + f'\n'
        if ping:
            if planed_raid_location:
                ping_on_reade(bands.get("usersoffrade"), goat['chat'] )
    return report

def statistic(goatName: str):
    report = f'🐐<b>{goatName}</b>\n\n'
    report = report + f'🧘‍♂️ <b>Рейдеры</b>:\n'

    setting = getSetting('REPORTS','RAIDS')
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

# 20 secund
def fight_job():
    while True:
        fight()
        time.sleep(20)

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
        proccess = Process(target=fight_job, args=())
        proccess.start() # Start new thread

        proccessPending_messages = Process(target=pending_job, args=())
        proccessPending_messages.start() # Start new thread

        proccessRade = Process(target=rade_job, args=())
        proccessRade.start() # Start new thread 

        main_loop()      
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)