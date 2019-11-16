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

import pymongo
from bson.objectid import ObjectId

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jugidb"]
registered_users = mydb["users"]
registered_wariors = mydb["wariors"]
battle      = mydb["battle"]
competition = mydb["competition"]
settings    = mydb["settings"]
pending_messages = mydb["pending_messages"]

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

WARIORS_ARR = [] # Зарегистрированные жители пустоши
for x in registered_wariors.find():
    WARIORS_ARR.append(wariors.importWarior(x))

SETTINGS_ARR = [] # Зарегистрированные настройки
for setting in settings.find():
    SETTINGS_ARR.append(setting)

def getSetting(code: str):
    """ Получение настройки """
    result = settings.find_one({'code': code})
    if (result):
        return result.get('value') 

ADMIN_ARR = []
for adm in list(getSetting('ADMINISTRATOR')):
    ADMIN_ARR.append(adm.get('login'))

def isAdmin(login: str):
    for adm in list(ADMIN_ARR):
        if login.lower() == adm.lower(): return True
    return False

def isOurUserName(name: str):
    for user in list(USERS_ARR):
        if name.lower() == user.getName().lower(): return True
    return False

def isOurUserLogin(login: str):
    for user in list(USERS_ARR):
        if login.lower() == user.getLogin().lower(): 
            return True
    return False

def isOurBandUserLogin(login: str):
    for user in list(USERS_ARR):
        if login.lower() == user.getLogin().lower():
            for band in getSetting('OUR_BAND'):
                if user.getBand() and band.get('band').lower() == user.getBand().lower():
                    return True
            break
    return False

def getUserByLogin(login: str):
    for user in list(USERS_ARR):
        if login.lower() == user.getLogin().lower(): return user
    return None

def getUserByName(name: str):
    for user in list(USERS_ARR):
        if name.lower() == user.getName().lower(): return user
    return None

def updateUser(newuser: users.User):
    newvalues = { "$set": json.loads(newuser.toJSON()) }
    registered_users.update_one({"login": f"{newuser.getLogin()}"}, newvalues)

    USERS_ARR = []
    for x in registered_users.find():
        USERS_ARR.append(users.importUser(x))

def setSetting(login: str, code: str, value: str):
    if (isAdmin(login)):
        pass
    else: return False

    """ Сохранение настройки """
    myquery = { "code": code }
    newvalues = { "$set": { "value": json.loads(value) } }
    u = settings.update_one(myquery, newvalues)

    SETTINGS_ARR = [] # Зарегистрированные настройки
    for setting in settings.find():
        SETTINGS_ARR.append(setting)
    return True

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(config.TOKEN)

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
    if not isOurBandUserLogin(inline_query.from_user.username):
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
                band = ''
                if warior.getBand(): 
                    band = ' 🤟' + warior.getBand()
                    if warior.getBand() == 'NO_BAND':
                        band = ''

                r = types.InlineQueryResultArticle(id=i, title = warior.getName() + f'{band}',  input_message_content=types.InputTextMessageContent('Джу, профиль @'+warior.getName()), description=warior.getProfileSmall())
                result.append(r)
                i = i + 1
                #if i>4 : break
            bot.answer_inline_query(inline_query.id, result, cache_time=60)
    except Exception as e:
        print(e)

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    response = getResponseDialogFlow('start')
    if response:
        bot.send_message(message.chat.id, text=response)

def updateWarior(warior: wariors.Warior, message: Message):
        privateChat = ('private' in message.chat.type)
        findinUsers = False
        for user_in in list(USERS_ARR):
            if (user_in.getName() == warior.getName()):
                findinUsers = True

        findWariors = False
        for warior_in in list(WARIORS_ARR):
            if (warior_in.getName() == warior.getName()):
                findWariors = True

        if findWariors:
            # TODO Проверить, что нет более поздней версии бойца
            wariorToUpdate = wariors.getWarior(warior.getName(), registered_wariors)
            updatedWarior = wariors.mergeWariors(warior, wariorToUpdate)

            newvalues = { "$set": json.loads(updatedWarior.toJSON()) }
            registered_wariors.update_one({"name": f"{warior.getName()}"}, newvalues)
            
            if privateChat:
                if not findinUsers: 
                    if (updatedWarior and updatedWarior.photo):
                        bot.send_photo(message.chat.id, updatedWarior.photo, updatedWarior.getProfile())
                    else:
                        bot.reply_to(message, text=updatedWarior.getProfile())
            else:
                if not findinUsers:
                    bot.reply_to(message, text=getResponseDialogFlow('shot_message_zbs'))
        else:
            WARIORS_ARR.append(warior)
            registered_wariors.insert_one(json.loads(warior.toJSON()))
            if privateChat:
                if not findinUsers: 
                    bot.reply_to(message, text=getResponseDialogFlow('new_warior'))
                    bot.reply_to(message, text=warior.getProfile())
            else:
                bot.reply_to(message, text=getResponseDialogFlow('shot_message_zbs'))

# Handle all other messages
@bot.message_handler(content_types=["photo"])
def get_message_photo(message):
    #write_json(message.json)
    if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
        ww = wariors.fromPhotoToWarioirs(message.forward_date, message.caption, message.photo[0].file_id)
        for warior in ww:
            updateWarior(warior, message)

# Handle all other messages
@bot.message_handler(content_types=["sticker"])
def get_message_stiker(message):
    #write_json(message.json)
    privateChat = ('private' in message.chat.type)
    if privateChat:
        bot.reply_to(message, text=message.sticker.file_id)

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
    if not isOurUserLogin(message.from_user.username):
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
    privateChat = ('private' in message.chat.type)
    callJugi = (privateChat 
                            or message.text.lower().startswith('джу') 
                            or (message.reply_to_message 
                                and message.reply_to_message.from_user.is_bot 
                                and message.reply_to_message.from_user.username in ('FriendsBrotherBot', 'JugiGanstaBot') )
                )

    findUser = isOurUserLogin(message.from_user.username)
    userIAm = getUserByLogin(message.from_user.username)

    if not findUser:
        r = random.random()
        if (r <= float(getSetting('PROBABILITY_I_DONT_NOW'))):
            bot.reply_to(message, text=getResponseDialogFlow('i_dont_know_you'))

    if (message.text.startswith('📟Пип-бой 3000') and 
            '/killdrone' not in message.text and 
            'ТОП ФРАКЦИЙ' not in message.text and 
            'СОДЕРЖИМОЕ РЮКЗАКА' not in message.text and 
            'ПРИПАСЫ В РЮКЗАКЕ' not in message.text and 
            'РЕСУРСЫ и ХЛАМ' not in message.text ):
        # write_json(message.json)
        if not findUser: 
            if privateChat:
                bot.reply_to(message, text=getResponseDialogFlow('getpip'))

        if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
            user = users.User(message.from_user.username, message.forward_date, message.text)
            if privateChat and (tools.deEmojify(message.from_user.first_name) != user.getName()):
                if not findUser: bot.reply_to(message, text=getResponseDialogFlow('change_name'))
                if not findUser: bot.send_chat_action(message.chat.id, 'typing')
                if not findUser: time.sleep(3)

            if findUser==False:   
                USERS_ARR.append(user)
                x = registered_users.insert_one(json.loads(user.toJSON()))
            else:
                updatedUser = users.updateUser(user, users.getUser(user.getLogin(), registered_users))
                updateUser(updatedUser)

            if privateChat:
                bot.reply_to(message, text=getResponseDialogFlow('setpip'))
            else:
                bot.reply_to(message, text=getResponseDialogFlow('shot_message_zbs'))

        else:
            bot.reply_to(message, text=getResponseDialogFlow('deceive'))
        
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and 'FIGHT!' in message.text):
        #write_json(message.json)
        ww = wariors.fromFightToWarioirs(message.forward_date, message, USERS_ARR, battle)
        if ww == None:
            bot.reply_to(message, text=getResponseDialogFlow('dublicate'))
            return
        for warior in ww:
            updateWarior(warior, message)
        return
    elif (message.forward_from and message.forward_from.username == 'WastelandWarsBot' and '/accept' in message.text and '/decline' in message.text):
        #write_json(message.json)
        if isOurBandUserLogin(message.from_user.username):
            warior = wariors.getWarior(message.text.split('👤')[1].split(' из ')[0], registered_wariors)
            if warior == None:
                bot.reply_to(message, text='Ничего о нем не знаю!', reply_markup=None)
            elif (warior and warior.photo):
                bot.send_photo(message.chat.id, warior.photo, warior.getProfile(), reply_markup=None)
            else:
                bot.reply_to(message, text=warior.getProfile(), reply_markup=None)
        else:
            bot.reply_to(message, text=getResponseDialogFlow('i_dont_know_you'), reply_markup=None)
        return
    if (isOurBandUserLogin(message.from_user.username)):
        

        #write_json(message.json)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)
        if not privateChat:
            markup.add('Джу, 📋 Отчет', 'Джу, Профиль')
        else:
            markup.add('📋 Отчет', '🤼 В ринг')
            markup.add('Профиль')
        
        if (callJugi and (message.text and ('анекдот' in message.text.lower() or 'тост' in message.text.lower()))) :
            type_joke = 11
            if ('анекдот' in message.text.lower()):
                type_joke = 11
            elif ('тост' in message.text.lower()):
                type_joke = 16  
            bot.send_chat_action(message.chat.id, 'typing')
            r = requests.get(f'{config.ANECDOT_URL}={type_joke}')
            bot.reply_to(message, r.text[12:-2], reply_markup=markup)
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # TO DO!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        elif (callJugi 
                    and message.text 
                    and ('залёт' in message.text.lower() or 'залет' in message.text.lower())
                ):
            pass

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
                bot.reply_to(message, reply_markup=markup, text="Из-за свой криворкукости ты вьебал статус самому себе. Теперь твой статус '" + message.text.split(login)[1].strip() + "'")
            else:
                registered_users.update_one({"login": f"{login}"}, newvalues)
                bot.reply_to(message, text='✅ Готово')
        
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # TO DO!
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
        elif ( callJugi and 'верси' in message.text.lower()):
            bot.reply_to(message, text=getResponseDialogFlow('last_version'), reply_markup=markup)

        elif (callJugi and 'бросить вызов @' in message.text.lower()):
            # if not privateChat:
            #     bot.reply_to(message, text=getResponseDialogFlow('shot_message_go_in_lk'))
            #     return

            login = message.text.lower().split('бросить вызов @')[1].split(' ')[0].strip()
            

            bot.reply_to(message, text=getResponseDialogFlow('shot_message_zbs'), reply_markup=markup)
            
        elif (callJugi and 'профиль @' in message.text.lower()):
            # if not privateChat:
            #     bot.reply_to(message, text=getResponseDialogFlow('shot_message_go_in_lk'), reply_markup=markup)
            #     return

            name = tools.deEmojify(message.text.lower().split('профиль @')[1].strip())
            login = message.text.lower().split('профиль @')[1].strip()
            if (isOurUserName(name) or isOurUserLogin(login)):
                user = getUserByLogin(login)
                if not user:
                    user = getUserByName(name)
                if user:
                    bot.reply_to(message, text=user.getProfile(), reply_markup=markup)

            for x in registered_wariors.find({'name':f'{name}'}):
                warior = wariors.importWarior(x)

                if (warior and warior.photo):
                    bot.send_photo(message.chat.id, warior.photo, warior.getProfile(), reply_markup=markup)
                else:
                    bot.reply_to(message, text=warior.getProfile(), reply_markup=markup)
        
        elif (callJugi and 'настройка @' in message.text):
            if not privateChat:
                bot.reply_to(message, text=getResponseDialogFlow('shot_message_go_in_lk'), reply_markup=markup)
                return
 
            settingCode = message.text.lower().split('настройка @')[1].split(' ')[0].strip()
            settingValue = message.text.lower().split('настройка @')[1].split(' ')[1].strip()
            if setSetting(message.from_user.username, settingCode, settingValue):
                bot.reply_to(message, text=getResponseDialogFlow('shot_message_zbs'), reply_markup=markup)
            else: 
                bot.reply_to(message, text=getResponseDialogFlow('shot_message_huinya'), reply_markup=markup)

        elif (callJugi and 'профиль' in message.text.lower()):
            user = users.getUser(message.from_user.username, registered_users)
            if user:
                warior = wariors.getWarior(user.getName(), registered_wariors)
                if (warior and warior.photo):
                    bot.send_photo(message.chat.id, warior.photo, user.getProfile(), reply_markup=markup)
                else:
                    bot.reply_to(message, text=user.getProfile(), reply_markup=markup)
                if (user.getRaid()):
                    msg = send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_raid'), reply_markup=markup)
            else:
                bot.reply_to(message, text='С твоим профилем какая-то беда... Звони в поддержку пип-боев!', reply_markup=markup)

        elif callJugi:
            text = message.text 
            if text.lower().startswith('джу'):
                text = message.text[3:]
            response = getResponseDialogFlow(text)
            if response:
                if (response.startswith('jugi:')):
                    #jugi:ping:Артхаус)
                    if 'ping' == response.split(':')[1]:
                        # Собираем всех пользоватлей с бандой Х
                        string = f'{tools.deEmojify(message.from_user.first_name)} просит собраться банду {response.split(":")[2]}:'
                        for registered_user in registered_users.find({"band": f"{response.split(':')[2][1:]}"}):
                            user = users.importUser(registered_user)
                            string = string + f'\n@{user.getLogin()}'
                        if ('@' in string):    
                            bot.reply_to(message, text=string, reply_markup=markup)
                        else:
                            bot.reply_to(message, text=getResponseDialogFlow('understand'), reply_markup=markup)
                    elif 'status' == response.split(':')[1]:
                        for registered_user in registered_users.find({"login": f'{message.from_user.username}'}):
                            user = users.importUser(registered_user)
                            if user.getStatus():
                                bot.reply_to(message, text=user.getStatus(), reply_markup=markup)
                            else:
                                bot.reply_to(message, text='У тебя пустой статус... Чё надо?... \nСпроси - "Джу, как установить статус?', reply_markup=markup)
                            break
                    elif 'capture' == response.split(':')[1]:
                            #   0    1        2       3     4
                            # jugi:capture:$bands:$Dangeon:$time
                            time_str = response.split(response.split(":")[3])[1][1:]
                            dt = parse(time_str)
                            time_str = str(dt.hour).zfill(2)+':'+str(dt.minute).zfill(2)

                            report = f'<b>Захват!</b> {response.split(":")[2]} {time_str} <b>{response.split(":")[3]}</b>\n'
                            for registered_user in registered_users.find({"band": f"{response.split(':')[2][1:]}"}):
                                user = users.importUser(registered_user)
                                report = report + f'\n@{user.getLogin()}'
                            report = report + '\n\n<b>Не опаздываем!</b>' 

                            markupinline = InlineKeyboardMarkup()
                            markupinline.row_width = 2
                            markupinline.add(InlineKeyboardButton("Иду!", callback_data="capture_yes"),
                            InlineKeyboardButton("Нахер!", callback_data="capture_no"))

                            msg = send_messages_big(message.chat.id, text=report, reply_markup=markupinline)
                            if not privateChat:
                                bot.pin_chat_message(message.chat.id, msg.message_id)
                    elif 'remind' == response.split(':')[1]:
                        # jugi:remind:2019-11-04T17:13:00+03:00
                        if not userIAm.getLocation():
                            bot.reply_to(message, text='Я не знаю из какого ты города. Напиши мне "Я из Одессы" или "Я из Москвы" и этого будет достаточно. Иначе, я буду думать, что ты живешь во временном поясе по Гринвичу, а это +3 часа к Москве, +2 к Киеву и т.д. И ты не сможешь просить меня напомнить о чем-либо!')
                            return
                        if not userIAm.getTimeZone():
                            bot.reply_to(message, text='Вроде, город знаю, а временную зону забыл. Напиши мне еще раз "Я из Одессы" или "Я из Москвы"!` ')
                            return
                                                
                        time_str = response.split(response.split(":")[1])[1][1:]
                        dt = parse(time_str)
                        tz = datetime.strptime(userIAm.getTimeZone(),"%H:%M:%S")
                        dt = dt - timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
                        if (dt.timestamp() < datetime.now().timestamp()):
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow('timeisout'), reply_markup=markup)
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
                        
                        msg = send_messages_big(message.chat.id, text=getResponseDialogFlow('shot_message_zbs'), reply_markup=markup)
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
                                bot.reply_to(message, text=getResponseDialogFlow('understand'), reply_markup=markup)
                            else:
                                # Display the current time in that time zone
                                timezone = pytz.timezone(timezone_str)
                                dt = datetime.utcnow()
                                userIAm.setLocation(response.split(':')[2])
                                userIAm.setTimeZone(str(timezone.utcoffset(dt)))
                                updateUser(userIAm)
                                bot.reply_to(message, text='Круто! Это ' + str(timezone.utcoffset(dt)) + ' к Гринвичу!', reply_markup=markup)

                        else:
                            bot.reply_to(message, text=getResponseDialogFlow('understand'), reply_markup=markup)
                    elif 'rating' == response.split(':')[1]:
                        report = ''
                        report = report + f'🏆ТОП 5 УБИЙЦ 🤟<b>{userIAm.getBand()}</b>\n'
                        report = report + '\n'
                        setting = getSetting('REPORT_KILLERS')
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
                                            "band": userIAm.getBand()   
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
                            if not isOurUserName(user_name): continue

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
                                            "band": userIAm.getBand()   
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
                            if not isOurUserName(user_name): continue
                            
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
                        
                        send_messages_big(message.chat.id, text=report, reply_markup=markup)
                else:
                    try:
                        bot.reply_to(message, text=response, reply_markup=markup)
                    except:
                        logger.info("Error!")
            else:
                bot.reply_to(message, text=getResponseDialogFlow('understand'), reply_markup=markup)
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

def reply_to_big(message: str, text: str, reply_markup=None):
    strings = text.split('\n')
    tmp = ''
    msg = types.Message.de_json(message)

    for s in strings:
        if len(tmp + s) < 4000:
            tmp = tmp + s +'\n'
        else: 
            result = bot.reply_to(msg, text=tmp, parse_mode='HTML', reply_markup=reply_markup)
            tmp = s + '\n'

    result = bot.reply_to(msg, text=tmp, parse_mode='HTML', reply_markup=reply_markup)
    return result

def fight():
    logger.info('Calculate fight')

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
        if max_damage < int(fighter.get('damage').split(' ')[0]): max_damage = int(fighter.get('damage').split(' ')[0])
        if max_armor < int(fighter.get('armor').split(' ')[0]): max_armor = int(fighter.get('armor').split(' ')[0])
        if min_damage > int(fighter.get('damage').split(' ')[0]): min_damage = int(fighter.get('damage').split(' ')[0])
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

            damage1 = float(f1.get('damage').split(' ')[0])
            damage2 = float(f2.get('damage').split(' ')[0])

            armor1 = float(f1.get('armor').split(' ')[0])
            armor2 = float(f2.get('armor').split(' ')[0])
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
            reply_to_big(pending_message.get('reply_message'), text, None)
        else:
            send_messages_big(pending_message.get('chat_id'), text, None)
        ids.append(pending_message.get('_id')) 

    for id_str in ids:
        myquery = {"_id": ObjectId(id_str)}
        newvalues = { "$set": { "state": 'CANCEL'} }
        u = pending_messages.update_one(myquery, newvalues)

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
            if request.match_info.get('token') == bot.token:
                request_body_dict = await request.json()
                update = telebot.types.Update.de_json(request_body_dict)
                bot.process_new_updates([update])
                return web.Response()
            else:
                return web.Response(status=403)

        app.router.add_post('/{token}/', handle)
        
        # Remove webhook, it fails sometimes the set if there is a previous webhook
        bot.remove_webhook()
        # Set webhook
        bot.set_webhook(url=config.WEBHOOK_URL_BASE + config.WEBHOOK_URL_PATH,
                        certificate=open(config.WEBHOOK_SSL_CERT, 'r'))
        # Build ssl context
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)
        # Start aiohttp server
        web.run_app(
            app,
            host=config.WEBHOOK_LISTEN,
            port=config.WEBHOOK_PORT,
            ssl_context=context,
        )

if __name__ == '__main__': 
    try:
        proccess = Process(target=fight_job, args=())
        proccess.start() # Start new thread

        proccessPending_messages = Process(target=pending_job, args=())
        proccessPending_messages.start() # Start new thread

        main_loop()
        
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)