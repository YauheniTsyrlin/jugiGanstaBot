#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config
import wariors

import tools
import speech
import users 
import matplot
import hashlib
import uuid

import logging
import ssl
from mem_top import mem_top
import traceback

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
mob             = mydb["mob"]
boss            = mydb["boss"]
messages        = mydb["messages"]
shelf           = mydb["shelf"]
workbench       = mydb["workbench"]
farm            = mydb["farm"]



flexFlag = False
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(config.TOKEN)

import dialogflow
import messager

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

def getSetting(code: str, name=None, value=None, id=None):
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
        elif id:
            for arr in result.get('value'):
                if arr['id'] == id:
                    return arr 
        else:
            return result.get('value')

GLOBAL_VARS = {
    'inventory': getSetting(code='ACCESSORY_ALL', id='ANIMALS')['value'] + getSetting(code='ACCESSORY_ALL', id='CURRENCY')['value'] + getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value'] + getSetting(code='ACCESSORY_ALL', id='PIP_BOY')['value'] + getSetting(code='ACCESSORY_ALL', id='REWARDS')['value'] + getSetting(code='ACCESSORY_ALL', id='THINGS')['value'] + getSetting(code='ACCESSORY_ALL', id='EDIBLE')['value'] + getSetting(code='ACCESSORY_ALL', id='TATU')['value'] + getSetting(code='ACCESSORY_ALL', id='CLOTHES')['value'] + getSetting(code='ACCESSORY_ALL', id='MARKS_OF_EXCELLENCE')['value'] + getSetting(code='ACCESSORY_ALL', id='POSITIONS')['value'] + getSetting(code='ACCESSORY_ALL', id='VIRUSES')['value'] + getSetting(code='ACCESSORY_ALL', id='PIP_BOY')['value'] ,
    'chat_id':
                {
                    'inventory':[]
                },
    'skill':
                {
                    'programmer': next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='programmer'), None),
                    'watchmaker':next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='watchmaker'), None),
                    'economist':next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='economist'), None),
                    'fighter':next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='fighter'), None),
                    'robotics':next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='robotics'), None),
                    'electrician':next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='electrician'), None),
                    'medic':next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None)
                },
    'fractions':  ['⚙️Убежище 4', '⚙️Убежище 11', '🔪Головорезы', '💣Мегатонна', '⚛️Республика', '👙Клуб бикини', '🔰Конкорд'],
    'bosses': ['Танкобот','Яо-гай','Супермутант-конг','Квантиум','Коготь смерти'],
    'fight_log_message' : ['отдал на съедение кротокрысам', 'одержал победу над', 'не оставил живого места от', 'гордо наступил на полудохлого', 'оставил бездыханное тело', 'сделал сиротами детишек', 'добил с пинка', 'добил лежачего', 'выписал пропуск в Вальхаллу', 'добил фаталити', 'стоит над поверженным', 'одержал победу над'],
    'eating_in_new_rino': ['опустошил бокал бурбона.', 'жадно ест сухари.'],
    'group_buttons': ['Джу, 📋 Отчет'],
    'private_buttons': ['📋 Отчет', '📜 Профиль', f'⏰ План рейда', '📈 Статистика', '🧺 Комиссионка'],
    'typeforexcenge': [ 'animals','clothes', 'food', 'decoration', 'things'], # обмен
    'typeforcomission': [ 'animals','clothes', 'food', 'decoration', 'things'], # продажа
    'profile':
    {
        'id': 'profile',
        'name': '📜 Профиль',
        'description': '📜 Здесь ты можешь посмотреть все свои атрибуты, навыки, вещи и подарки.',
        'buttons': [
            {
                'id': 'common',
                'name': '🏷 Общие',
                'description': '📜 Здесь ты можешь посмотреть общие атрибуты',
                'buttons': []              
            },
            {
                'id': 'сombat',
                'name': '📯 Боевая мощь',
                'description': '📯 Здесь ты можешь посмотреть свои боевые параметры',
                'buttons': []              
            },
            {
                'id': 'setting',
                'name': '📋 Настройки',
                'description': '📋  Здесь ты можешь посмотреть свои настройки',
                'buttons': []              
            },
            {
                'id': 'abilities',
                'name': '💡 Навыки',
                'description': '💡 Здесь ты можешь посмотреть свои навыки и должности',
                'buttons': []              
            },
            {
                'id': 'things',
                'name': '📦 Вещи',
                'description': '📦 Здесь ты можешь посмотреть все свои вещи',
                'buttons': []              
            },
            {
                'id': 'awards',
                'name': '🏵 Награды 🔩',
                'description': '🏵 Здесь ты можешь посмотреть свои 🏵 Награды, 🎁 Подарки и 🔩 Рейдовые болты',
                'buttons': []              
            }
       ]
    },
    'commission':
    {
        'id': 'trade',
        'name': '🧺 Комиссионка',
        'description': '🧺 Здесь ты можешь попытаться продать, обменять, сдать вещи из своего инвентаря или посмотреть, что продают другие бандиты.',
        'buttons': [
            
            {
                'id': 'onshelf',
                'name': '🛍️ Магазин',
                'description':'🛍️ Здесь можно посмотреть товара, которые бандиты выставили на продажу.',
                'buttons': []
            },
            {
                'id': 'workbench',
                'name': '⚙️ Верстак',
                'description':'⚙️ Здесь можно собрать новые вещи или разобрать на 📦 запчасти. Для этого надо положить на верстак какую-либо вещь из меню "📦 Мои вещи"',
                'buttons': []
            },
            {
                'id': 'exchange',
                'name': '📦 Мои вещи',
                'description':'📦 Здесь можно выставить свои товар на 🛍️ продажу, тупо сдать за 30% 🔘Crypto или положить на ⚙️ Верстак.',
                'buttons': [],
                'discont': 0.3
            },
            {
                'id': 'farm',
                'name': '🐐🌳 Ферма',
                'description':'🐐🌳 Здесь можно заниматься выращиванием 🐮 домашних животных и 🌳 садоводством.',
                'buttons': []
            }
        ]
    }
}

def addInventory(user: users.User, inv, check_skills=True):
    eco_skill = user.getInventoryThing(GLOBAL_VARS['skill']['economist'])
    if check_skills and eco_skill:
        power_skill = 0
        if eco_skill['storage'] >= eco_skill['min']:
            power_skill = (eco_skill['storage'] - eco_skill['min'])/(eco_skill['max'] - eco_skill['min'])
            r = random.random()
            if r <= eco_skill['probability']:
                # може
                inv['cost'] = inv['cost'] + int(inv['cost'] * power_skill * eco_skill['value'])
    
    quantity = None
    if 'quantity' in inv:
        quantity = inv['quantity']

    # Добавляем составные   объекты
    listInv = GLOBAL_VARS['inventory']    
    if 'composition' in inv:
        arr = []
        for com in inv['composition']:
           arr.append(com)

        comp_arr = []  
        inv.update({'composition': comp_arr})
        for com in arr:
            for i in range(0, com["counter"]):
                composit = list(filter(lambda x : x['id']==com['id'], listInv))[0].copy()
                composit.update({'uid':f'{uuid.uuid4()}'})
                if com["id"] == 'crypto':
                    composit["cost"] = com["counter"]
                    comp_arr.append(composit)
                    break
                comp_arr.append(composit)

    return user.addInventoryThing(inv)

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

def isPowerUser(login: str):
    for goat in getSetting(code='GOATS_BANDS'):
        for boss in goat['poweruser']:
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

def isGoatInfoChat(login: str, infochat: str):
    goat = getMyGoat(login)
    if goat:
        if goat['chats']['info'] == infochat:
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
    
    arr = []
    for x in registered_users.find():
        arr.append(users.importUser(x))

    global USERS_ARR
    USERS_ARR.clear() 
    USERS_ARR = USERS_ARR + arr 

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
    elif (string.startswith('🔰')):
        return '🔰Конкорд'
    else:
        f = [ele for ele in GLOBAL_VARS['fractions'] if(ele in string)]
        if len(f)>0:
            return f[-1]                       

def getWariorByName(name: str, fraction: str):
    name = tools.deEmojify(name).strip()
    for warior in list(WARIORS_ARR):
        if name == warior.getName().strip() and (fraction == None or fraction == warior.getFraction()): 
            return warior
    return None

def isKnownWarior(name: str, fraction: str):
    
    if getWariorByName(name, fraction):
        return True
    return False

def update_warior(warior: wariors.Warior):
    result = {
            'new': False,
            'bm_update': False
        }
    if warior == None:
        pass
    else:
        # logger.info(f'======= Ищем Бандита с именем {warior.getName()} {warior.getFraction()}')
        # if isKnownWarior(warior.getName(), warior.getFraction()):
        # logger.info(f'======= Это известный бандит')
        wariorToUpdate = getWariorByName(warior.getName(), warior.getFraction())
        if wariorToUpdate and warior and warior.getBm():
            try:
                if (wariorToUpdate.getBm() == None or wariorToUpdate.getBm() < warior.getBm()):      
                    result.update({'bm_update': True})
            except:
                pass

        updatedWarior = None
        if wariorToUpdate == None:
            updatedWarior = warior 
        else:
            updatedWarior = wariors.mergeWariors(warior, wariorToUpdate)
        # updatedWarior Текущий пользователь
        # warior Новый пользователь

        newvalues = { "$set": json.loads(updatedWarior.toJSON()) }
        resultupdata = registered_wariors.update_one({
            "name": f"{updatedWarior.getName()}", 
            "fraction": f"{updatedWarior.getFraction()}"
            }, newvalues)
        if resultupdata.matched_count < 1:
            # logger.info(f'======= НЕ нашли бандита')
            result.update({'new': True})
            result.update({'bm_update': True})
            res = registered_wariors.insert_one(json.loads(warior.toJSON()))
            send_message_to_admin(f'🔫 Новый бандит:\n{warior.getProfile()}')

    
    arr = []
    for x in registered_wariors.find():
        arr.append(wariors.importWarior(x))
    
    global WARIORS_ARR
    WARIORS_ARR.clear() 
    WARIORS_ARR = WARIORS_ARR + arr 
    
    return result

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

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None, limit=None, step=None, back_button=None, exit_button=None, forward_button=None ):
    if limit==None: 
        limit=len(buttons)
        step = 0 
    menu = [ buttons [i:i + n_cols] for i in range(step*limit, (step+1)*limit if (step+1)*limit <= len(buttons) else len(buttons), n_cols) ]
    
    if back_button or exit_button or forward_button: 
        if step==0 and len(buttons) <= limit:
            manage_buttons = [exit_button]
        elif step==0:
            if exit_button and forward_button:
                manage_buttons = [exit_button, forward_button]
            elif exit_button and not forward_button:
                manage_buttons = [exit_button]
            if not exit_button and forward_button:
                manage_buttons = [forward_button]
            if not exit_button and not forward_button:
                manage_buttons = []
        elif (step+1)*limit >= len(buttons):
            manage_buttons = [back_button, exit_button]
        else:
            stepNext = step + 1
            menuBtnNext = [ buttons [i:i + n_cols] for i in range(stepNext*limit, (stepNext+1)*limit if (stepNext+1)*limit <= len(buttons) else len(buttons), n_cols) ]
            manage_buttons = [back_button, exit_button, forward_button]
        menu = menu + [manage_buttons [i:i + 3] for i in range(0, len(manage_buttons), 3)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

def write_json(data, filename = "./pips.json"):
    with open(filename, 'a', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def getResponseDialogFlow(login, text: str, event=None, context_param=None):
    if not text or '' == text.strip():
        text = 'голос!'

    user = getUserByLogin(login)
    return dialogflow.getResponseDialogFlow(login, text, event, user, context_param=context_param)

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
    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username ,'shot_censorship').fulfillment_text)

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

def checkInfected(logins, chat_id):
    chat = f'chat_{chat_id}' 
    viruses = getSetting(code='ACCESSORY_ALL', id='VIRUSES')["value"]
    try: 
        for z in GLOBAL_VARS[chat]['inventory']:
            pass
        for m in GLOBAL_VARS[chat]['medics']:
            pass
    except: 
        GLOBAL_VARS.update({chat: {'inventory': [], 'medics': []} })

    for vir in list(filter(lambda x : (not x == None) and x['type'] == 'disease', GLOBAL_VARS[chat]['inventory'])):
        if vir['property']['contagiousness'] < 0.005:
            GLOBAL_VARS[chat]['inventory'].remove(vir)
        else:
            vir['property'].update({'contagiousness':  vir['property']['contagiousness'] * vir['property']['halflife']})
    
    # Добавляем новые вирусы, если есть у бандитов
    for user_login in logins:
        user = getUserByLogin(user_login)
        if user:
            for vir in list(filter(lambda x : x['property']['contagiousness'] > 0, viruses)):
                # #################
                # vir.update({'login': user.getLogin()}) 
                # GLOBAL_VARS[chat]['inventory'].append(vir)
                # #################
                if user.getInventoryThingCount(vir) > 0:
                    vir.update({'login': user.getLogin()})  
                    GLOBAL_VARS[chat]['inventory'].append(vir)

def infect(logins, chat_id):
    chat = f'chat_{chat_id}' 
    if len(logins) < 1:
        return

    users_in_danger = []
    for user_login in logins:
        user = getUserByLogin(user_login)
        if user:
            # TODO Вставить проверку на иммунитет, иммунитет получаешь если переболел 'immunity'
            users_in_danger.append(user)

    for vir in list(filter(lambda x : x['type'] == 'disease', GLOBAL_VARS[chat]['inventory'])):
        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='VIRUSES')['value']) if x['id']==vir['id']), None)

        for user in users_in_danger:
            if user.isInventoryThing(vir):
                pass
            else:
                r = random.random()
                c = vir['property']['contagiousness']
                # send_message_to_admin(f'{user.getLogin()} может заразиться вирусом {vir["name"]}...\n{r<=c} {r} меньше или равно {c} {user.getLogin()} {vir["name"]}')
                # logger.info(f'{r<=c} {r} меньше или равно {c} {user.getLogin()} {vir["name"]}')
                if (r <= c):

                    for protected_thing in list(filter(lambda x : 'protection' in x, user.getInventory())):
                        safe_mask = False  
                        for protection in list(filter(lambda x : x['type'] == 'disease', protected_thing['protection'])):
                            if protection['id'] == vir['id'] and protection['type'] == vir['type']:
                                p = random.random()
                                # send_message_to_admin(f'⚠️🦇 Внимание! \n вероятность {p}, защита {protection["value"]}')
                                if p < protection['value']:
                                    # send_message_to_admin(f'⚠️🦇 Внимание! \n value = {protected_thing["wear"]["value"]}, one_use = {protected_thing["wear"]["one_use"]}')
                                    if protected_thing['wear']['value'] - protected_thing['wear']['one_use'] > 0:
                                        protected_thing['wear'].update({'value':  protected_thing['wear']['value'] - protected_thing['wear']['one_use']})
                                        updateUser(user)
                                        safe_mask = True
                                        # Маска уберегла
                                        text = f'{user.getNameAndGerb()} использовал {protected_thing["name"]}\nчтобы не заразиться {vir["name"]}!'
                                        sec = 5
                                        pending_date = datetime.now() + timedelta(seconds=sec)
                                        pending_messages.insert_one({ 
                                            'chat_id': chat_id,
                                            'reply_message': None,
                                            'create_date': datetime.now().timestamp(),
                                            'user_id': user.getLogin(),
                                            'state': 'WAIT',
                                            'pending_date': pending_date.timestamp(),
                                            'dialog_flow_text': None,
                                            'dialog_flow_context': None,
                                            'text': text})

                                        send_message_to_admin(f'🦇 Вирус!\n у {user.getLogin()} {protected_thing["name"]} спасла от {vir["name"]}')
                                        break
                                    else:
                                        user.removeInventoryThing(protected_thing)
                                        updateUser(user)
                                        text = f'{user.getNameAndGerb()}, у тебя испортилась вещь из инвентаря:\n▫️ {protected_thing["name"]}'
                                        sec = 5
                                        pending_date = datetime.now() + timedelta(seconds=sec)
                                        pending_messages.insert_one({ 
                                            'chat_id': chat_id,
                                            'reply_message': None,
                                            'create_date': datetime.now().timestamp(),
                                            'user_id': user.getLogin(),  
                                            'state': 'WAIT',
                                            'pending_date': pending_date.timestamp(),
                                            'dialog_flow_text': None,
                                            'dialog_flow_context': None,
                                            'text': text})
                                        send_message_to_admin(f'🦇 Вирус!\n у {user.getLogin()} порвалась {protected_thing["name"]}')
                                        break

                        if safe_mask:
                            break            

                    addInventory(user, elem)
                    updateUser(user)
                    infect_user = getUserByLogin(vir['login'])

                    #sec = int(randrange(int(getSetting(code='PROBABILITY', name='PANDING_WAIT_START_1')), int(getSetting(code='PROBABILITY', name='PANDING_WAIT_END_1'))))
                    sec = 10
                    pending_date = datetime.now() + timedelta(seconds=sec)
                    pending_messages.insert_one({ 
                        'chat_id': chat_id,
                        'reply_message': None,
                        'create_date': datetime.now().timestamp(),
                        'user_id': user.getLogin(),  
                        'state': 'WAIT',
                        'pending_date': pending_date.timestamp(),
                        'dialog_flow_text': 'virus_new_member',
                        'dialog_flow_context': None,
                        'text': f'▫️ {infect_user.getNameAndGerb()} заразил тебя {vir["name"]}'})
                    send_message_to_admin(f'🦇 Вирус!\n {user.getLogin()} заражен вирусом {vir["name"]} с вероятностью {vir["property"]["contagiousness"]}')

def checkCure(logins, chat_id):
    chat = f'chat_{chat_id}' 
    medicskill = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None) 
    
    # Удаляем информацию о всех предыдущих медиках
    GLOBAL_VARS[chat]['medics'].clear()
      
    for user_login in logins:
        user = getUserByLogin(user_login)
        if user:
            if user.getInventoryThingCount(medicskill)>0:
                GLOBAL_VARS[chat]['medics'].append(user)

def cure(logins, chat_id):
    chat = f'chat_{chat_id}' 
    if len(logins) < 1:
        return
    users_in_danger = []
    viruses = getSetting(code='ACCESSORY_ALL', id='VIRUSES')["value"]
    medicskill = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None) 
    # medical_mask = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='CLOTHES')['value']) if x['id']=='medical_mask'), None) 
    
    for user_login in logins:
        user = getUserByLogin(user_login)
        if user:
            for vir in viruses:
                if user.getInventoryThingCount(vir) > 0:
                    users_in_danger.append(user)

    for medic in GLOBAL_VARS[chat]['medics']:
        # сила умения
        skill = medic.getInventoryThing(medicskill)
        power_skill = 0
        if skill['storage'] >= skill['min']:
            power_skill = (skill['storage'] - skill['min'])/(skill['max'] - skill['min'])

        for infected in users_in_danger:
            if power_skill == 0:
                # медик не готов лечить
                break

            for vir in viruses:
                if infected.getInventoryThingCount(vir) > 0:
                    r = random.random()
                    if (r <= (vir['property']['treatability'] + power_skill)/2):
                        infected.removeInventoryThing(vir)
                        mask_text = ''

                        protected_clothes = None
                        for protected_thing in list(filter(lambda x : 'protection' in x, getSetting(code='ACCESSORY_ALL', id='CLOTHES')["value"])):
                            for protection in list(filter(lambda x : x['type'] == 'disease', protected_thing['protection'])):
                                if protection['id'] == vir['id'] and protection['type'] == vir['type']:
                                    protected_clothes = protected_thing
                        
                        if protected_clothes and not infected.isInventoryThing(protected_clothes):
                            addInventory(infected, protected_clothes)
                            mask_text = f'\n▫️ +{protected_clothes["name"]}'

                        send_message_to_admin(f'❤️ Доктор!\n {infected.getLogin()} вылечен {medic.getLogin()} от {vir["name"]}!')
                        updateUser(infected)
                        sec = int(randrange(int(getSetting(code='PROBABILITY', name='PANDING_WAIT_START_2')), int(getSetting(code='PROBABILITY', name='PANDING_WAIT_END_2'))))
                        pending_date = datetime.now() + timedelta(seconds=sec)
                        text = f'Врач {medic.getNameAndGerb()} вылечил бандита {infected.getNameAndGerb()} от:\n▫️ {vir["name"]}{mask_text}'
                        if medic.getLogin() == infected.getLogin():
                            text = f'{medic.getNameAndGerb()} вылечил сам себя от:\n▫️ {vir["name"]}{mask_text}'

                        pending_messages.insert_one({ 
                            'chat_id': chat_id,
                            'reply_message': None,
                            'create_date': datetime.now().timestamp(),
                            'user_id': infected.getLogin(),  
                            'state': 'WAIT',
                            'pending_date': pending_date.timestamp(),
                            'dialog_flow_text': 'virus_minus_member',
                            'dialog_flow_context': None,
                            'text': text})

def getMobHash(mob_name: str, mob_class: str):
    stringforhash = mob_name + mob_class
    hashstr = f'{int(hashlib.sha256(stringforhash.encode("utf-8")).hexdigest(), 16) % 10**8}'  
    return hashstr

def getMobByHash(hashstr: str):
    dresult = mob.aggregate([ 
    {   "$match": {
                "kr": {"$gte": 0}
            } 
    },
    {   "$group": {
        "_id": { "mob_name":"$mob_name", "mob_class":"$mob_class"}, 
        "count": {
            "$sum": 1}}},
        
    {   "$sort" : { "count" : -1 } }
    ])
    
    for d in dresult:
        mob_name = d["_id"]["mob_name"] 
        mob_class = d["_id"]["mob_class"] 
        hashstr_in_bd = getMobHash(mob_name, mob_class)
        if hashstr == hashstr_in_bd:
            mobinbd = {'mob_name':mob_name, 'mob_class': mob_class}
            return mobinbd

    return None

def getMobDetailReport(mob_name: str, mob_class: str):
    hashstr = getMobHash(mob_name, mob_class)
    return 'В разработке...'

def getMobReport(mob_name: str, mob_class: str, dark_zone=False):
    hashstr = getMobHash(mob_name, mob_class)

    report = f"{'🔆' if not dark_zone else '🚷'}<b>Статистика сражений</b>\n"
    report = report + f'<b>{mob_name}</b> {mob_class}\n\n'
    # report = report + f'Подробнее {hashstr}\n\n'

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
    health = None

    habitat = {}
    for one_mob in mob.find({'mob_name':mob_name, 'mob_class': mob_class, 'dark_zone':dark_zone}):
        #send_messages_big(497065022, text=f'{one_mob}')
        try:
            if one_mob['health'] and (health == None or one_mob['health'] < health):
                health = one_mob['health']
        except: pass

        counter = counter + 1
        if one_mob['win']:
            win_counter = win_counter + 1
        
        habitat.update({f'{one_mob["km"]}':True})
        
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

        if one_counter_damage > 0:
            average_damage = average_damage + one_average_damage / one_counter_damage
            average_damage_counter = average_damage_counter + 1

        if one_mob['kr'] > 0:
            counter_kr = counter_kr + 1
            average_kr = average_kr + one_mob['kr']
        try:
            if one_mob['mat'] > 0:
                counter_mat = counter_mat + 1
                average_mat = average_mat + one_mob['mat']
        except: pass

    if min_beaten == 1000000: 
        min_beaten = 0
    if min_damage == 1000000: 
        min_damage = 0

    if average_beaten_counter > 0:
        average_beaten = int(average_beaten / average_beaten_counter)
    if average_damage_counter > 0:
        average_damage = int(average_damage / average_damage_counter)
    if counter_kr > 0:
        average_kr = int(average_kr / counter_kr)
    if counter_mat > 0:
        average_mat = int(average_mat / counter_mat)
   
    habitat_str = ''
 
    for h in sorted(habitat):
        if habitat_str == '':
            habitat_str = habitat_str + h
        else:
            habitat_str = habitat_str + ', '+ h

    if habitat_str == '':
        report = report + f"👣 Еще ни разу не встречали в {'🔆' if not dark_zone else '🚷'}\n"
    else:
        report = report + f'👣 Встречается: <b>{habitat_str}</b> км\n'

        if health > 0:
            report = report + f'❤️ Здоровье: <b>{health}</b>\n'

        report = report + f'✊ Побед: <b>{win_counter}/{counter}</b>\n'
        report = report + f'💔 <b>Урон бандитам</b>:\n'
        report = report + f'      Min <b>{min_beaten}</b> при 🛡<b>{min_beaten_user_armor}</b>\n'
        report = report + f'      В среднем <b>{average_beaten}</b>\n'
        report = report + f'      Max <b>{max_beaten}</b> при 🛡<b>{max_beaten_user_armor}</b>\n'
        report = report + f'💥 <b>Получил от бандитов</b>:\n'
        report = report + f'      Min <b>{min_damage}</b> при ⚔<b>{min_damage_user_damage}</b>\n'
        report = report + f'      В среднем <b>{average_damage}</b>\n'
        report = report + f'      Max <b>{max_damage}</b> при ⚔<b>{max_damage_user_damage}</b>\n' 
        report = report + f'💰 <b>В среднем добыто</b>:\n'
        report = report + f'      🕳 <b>{average_kr}</b>\n'
        report = report + f'      📦 <b>{average_mat}</b>\n'

    all_counter = mob.find().count()
    report = report + f'\n'
    report = report + f'Всего записей в базе <b>{all_counter}</b>\n'
    
    return report

def getBossReport(boss_name: str):
    report = f"⚜️<b>Статистика по боссам</b>\n"
    report = report + f'<b>{boss_name}</b>\n\n'
    #counter_all_boss = boss.find({'boss_name': boss_name}).count()*4

    for bo in boss.find({'boss_name': boss_name}):
        report = report + f'❤️ Здоровье: <b>{bo["health"]}</b>\n'
        report = report + f'💀 Убил: <b>{len(bo["killed"])}</b>\n'
        if len(bo["beaten"]) > 0:
            report = report + f'💔 <b>Урон бандитам</b>:\n'
            report = report + f'      Min <b>{min(bo["beaten"])}</b> '
            report = report + f'Avr <b>{int(sum(bo["beaten"]) / len(bo["beaten"]))}</b> '
            report = report + f'Max <b>{max(bo["beaten"])}</b>\n'
        if len(bo["damage"]) > 0:
            report = report + f'💥 <b>Получил от бандитов</b>:\n'
            report = report + f'      Min <b>{min(bo["damage"])}</b> '
            report = report + f'Avr <b>{int(sum(bo["damage"]) / len(bo["damage"]))}</b> '
            report = report + f'Max <b>{max(bo["damage"])}</b>\n'
        if len(bo["kr"]) > 0:
            report = report + f'💰 <b>В среднем добыто</b>:\n'
            report = report + f'      🕳 <b>{int(sum(bo["kr"]) / len(bo["kr"]))}</b>\n'
            report = report + f'      📦 <b>{int(sum(bo["mat"]) / len(bo["mat"]))}</b>\n'

        report = report + f'\n'
        last_date = max(bo["forward_date"])

        tz = config.SERVER_MSK_DIFF
        date = (datetime.fromtimestamp(last_date).replace(second=0) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp()

        try:
            report = report + f'📋 <b>Записались {bo["onboss"]}</b>\n'
        except: pass
        report = report + f'⏰ Замечен {time.strftime("%d.%m.%Y %H:%M", time.gmtime(date))} МСК'

    return report 

def getBossByHash(hashstr: str):
    dresult = boss.aggregate([ 
    {   "$group": {
        "_id": { "boss_name":"$boss_name"}, 
        "count": {
            "$sum": 1}}},
        
    {   "$sort" : { "count" : -1 } }
    ])
    
    for d in dresult:
        boss_name = d["_id"]["boss_name"] 
        hashstr_in_bd = getMobHash(boss_name, 'boss')
        if hashstr == hashstr_in_bd:
            return {'boss_name': boss_name}

    return None

def dzen_rewards(user, num_dzen, message):
    chat = message.chat.id

    goat = getMyGoat(user.getLogin())
    if goat:
        chat = goat['chats']['secret']
    for i in range(1, num_dzen+1):
        elem =   {
                    'id': f'marks_of_dzen_{i}',
                    'name': f'🏵️ Грамота за {i}-й Дзен',
                    'cost': 0,
                    'type': 'marks_of_excellence',
                    'quantity': 1000
                }

        if user.isInventoryThing(elem):
            pass
        else:
            if addInventory(user, elem):
                updateUser(user)
                send_messages_big(chat, text=user.getNameAndGerb() + '!\n' + getResponseDialogFlow(message.from_user.username, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {elem["name"]} 🔘{elem["cost"]}') 
            else:
                send_messages_big(message.chat.id, text=user.getNameAndGerb() + '!\n' + getResponseDialogFlow(message.from_user.username, 'new_accessory_not_in_stock').fulfillment_text + f'\n\n▫️ {elem["name"]} 🔘{elem["cost"]}') 

def check_things(text, chat, time_over, userIAm, elem, counterSkill=0):
    count = counterSkill
    if 'Найдено:' in text:
        text = text.split('Найдено:')[0]+'\nНайдено: ' + text.replace('\n', '').split('Найдено:')[1]
    if text:
        for s in text.split('\n'):
            for thing in elem['subjects_to_find']:
                if (s.startswith('Получено:') or s.startswith('Найдено:') or s.startswith('Бонус:') or (s.startswith('💰')) ) and thing in s:
                    if ' x' in s or ' ×' in s:
                        for x in [' x', ' ×']:
                            if x in s:
                                count = count + int(s.replace('/buy_trash','').split(x)[1].split(',')[0].strip())
                    else: count = count + 1
    minimum = 1
    if 'subjects_quantum' in elem:
        minimum = elem['subjects_quantum']

    if count >= minimum:
        if not time_over:
            logger.info(f'ADD')
            addInventory(userIAm, elem)
            updateUser(userIAm)
            text = f'{userIAm.getNameAndGerb()}, ты нашел:\n▫️ {elem["name"]}'
            send_messages_big(chat, text=text)
        else:
            send_messages_big(chat, text=getResponseDialogFlow(userIAm.getLogin(), elem["dialog_old_text"]).fulfillment_text)
    elif count > 1 and count < minimum:
        send_messages_big(chat, text=getResponseDialogFlow(userIAm.getLogin(), 'dialog_few_things').fulfillment_text)


def check_skills(text, chat, time_over, userIAm, elem, counterSkill=0):
    count = counterSkill
    if text:
        for s in text.split('\n'):
            for skill_sign in elem['subjects_of_study']:
                if (s.startswith('Получено:') or s.startswith('Бонус:') or (s.startswith('💰')) ) and skill_sign in s or (s == 'FIGHT!' and skill_sign in s):
                    if ' x' in s or ' ×' in s:
                        for x in [' x', ' ×']:
                            if x in s:
                                count = count + int(s.replace('/buy_trash','').split(x)[1].strip())
                    else: count = count + 1

    if count > 0:
        if not time_over:
            # Проверяем на увеличители или уменшители умения
            for thing in list(filter(lambda x : 'skill' in x and 'training' in x['skill'], userIAm.getInventory())):
                if elem['id']==thing['skill']['training']['id']:
                    r = random.random()
                    if r < thing['skill']['training']['probability']:
                        # Немножко ломаем предмет
                        new_value = thing['wear']['value'] - thing['wear']['one_use']
                        isBroken = new_value <= 0
                        if isBroken:
                            userIAm.removeInventoryThing(thing)
                            text = f'{userIAm.getNameAndGerb()}, у тебя испотилась вещь из инвентаря:\n▫️ {thing["name"]}'
                            send_messages_big(chat, text=text)
                            send_message_to_admin(f'🗑️ Сломалось\n{text}')
                        else:
                            thing['wear'].update({'value': new_value})
                            text = f'{userIAm.getNameAndGerb()}\n{getResponseDialogFlow(None, thing["skill"]["training"]["dialog_text"]).fulfillment_text}\n▫️ {thing["name"]} <b>{int(new_value*100)}%</b>'
                            send_messages_big(chat, text=text)
                            send_message_to_admin(f'🔧 Использован предмет\n{text}')
                        
                        count = count + thing['skill']['training']['value']
            if count <= 0:
                updateUser(userIAm)
                return
            if not userIAm.isInventoryThing(elem):
                elem.update({'storage': elem['storage'] + count})
                addInventory(userIAm, elem)
                percent = int((elem['storage'])*100/elem['max'])
                send_messages_big(chat, text=f'Ты начал изучение умения:\n▫️ {elem["name"]} {percent}%') 
                send_message_to_admin(f'💡 Начато изучение умения:\n▫️ {userIAm.getNameAndGerb()} (@{userIAm.getLogin()})\n▫️ {elem["name"]} {percent}%')
            else:
                elem = userIAm.getInventoryThing(elem)
                text = ''
                count = elem['storage'] + count
                if count >= elem['max']:
                    count = elem['max']
                    if elem['flags']['congratulation_max']:
                        send_messages_big(chat, text=f'Ты уже достиг всего в этом умении\n▫️ {elem["name"]} {100}%')
                        return

                # проверяем, а не поздравляли ли мы его за достижение минимума?
                if count >= elem['min'] and not elem['flags']['congratulation_min']:
                    elem['flags'].update({'congratulation_min': True})
                    send_messages_big(chat, text=f'Поздравляю 🥳! Твоё умение {elem["name"]} стало приносить пользу 😎.')
                    
                    # Корочка
                    present = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id=elem['flags']['present_min']['type'])['value']) if x['id']==elem['flags']['present_min']['id']), None)
                    if present and not userIAm.isInventoryThing(present):
                        addInventory(userIAm, present)
                        send_messages_big(chat, text=userIAm.getNameAndGerb() + '!\n' + getResponseDialogFlow(userIAm.getLogin(), 'new_accessory_add').fulfillment_text + f'\n\n▫️ {present["name"]}') 
                    # Должность

                    position = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='POSITIONS')['value']) if x['id']==elem['flags']['position_min']), None)
                    if position and not userIAm.isInventoryThing(position):
                        addInventory(userIAm, position)
                        send_messages_big(chat, text=userIAm.getNameAndGerb() + '!\n' + getResponseDialogFlow(userIAm.getLogin(), 'new_position_add').fulfillment_text + f'\n\n▫️ {position["name"]}') 
                
                # проверяем, а не поздравляли ли мы его за достижение максимума?
                if count >= elem['max'] and not elem['flags']['congratulation_max']:
                    elem['flags'].update({'congratulation_max': True})
                    send_messages_big(chat, text=f'Поздравляю 🥳! Ты стал профессионалом 🤩 в умение {elem["name"]}!')

                    # Корочка
                    present = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id=elem['flags']['present_max']['type'])['value']) if x['id']==elem['flags']['present_max']['id']), None)
                    if present and not userIAm.isInventoryThing(present):
                        addInventory(userIAm, present)
                        send_messages_big(chat, text=userIAm.getNameAndGerb() + '!\n' + getResponseDialogFlow(userIAm.getLogin(), 'new_accessory_add').fulfillment_text + f'\n\n▫️ {present["name"]}') 
                    # Должность
                    position = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='POSITIONS')['value']) if x['id']==elem['flags']['position_max']), None)
                    if position and not userIAm.isInventoryThing(position):
                        addInventory(userIAm, position)
                        old_position = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='POSITIONS')['value']) if x['id']==elem['flags']['position_min']), None)
                        userIAm.removeInventoryThing(old_position)
                        send_messages_big(chat, text=userIAm.getNameAndGerb() + '!\n' + getResponseDialogFlow(userIAm.getLogin(), 'new_position_add').fulfillment_text + f'\n\n▫️ {position["name"]}') 
                
                elem.update({'storage': count})
                percent = int(count*100/elem['max'])

                send_message_to_admin(f'💡 Изучение умения:\n▫️ {userIAm.getNameAndGerb()} (@{userIAm.getLogin()})\n▫️ {elem["name"]} <b>{percent}</b>% {int(elem["storage"])}/{elem["max"]}')
                send_messages_big(chat, text=f'▫️ {elem["name"]} {percent}%')

            updateUser(userIAm)
        else:
            send_messages_big(chat, text=getResponseDialogFlow(userIAm.getLogin(), elem["dialog_old_text"]).fulfillment_text)

def getInvCompositionIn(thing):
    result = []
    listInv = GLOBAL_VARS['inventory']
    for inventory in listInv:
        if 'composition' in inventory:
            for com in inventory['composition']:
                if thing['id'] == com['id']:
                    if inventory not in result:
                        result.append(inventory)
    return result

# Handle new_chat_members
@bot.message_handler(content_types=['new_chat_members', 'left_chat_members'])
def send_welcome_and_dismiss(message):
    response = getResponseDialogFlow(message.from_user.username, message.content_type).fulfillment_text
    if response:
        bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_NEW_MEMBER'), 1)[0]['value'])
        bot.send_message(message.chat.id, text=response)
        
        goat = getMyGoat(message.from_user.username)
        if not isGoatSecretChat(message.from_user.username, message.chat.id):
            bot.send_photo(message.chat.id, random.sample(getSetting(code='STICKERS', name='NEW_MEMBER_IMG'), 1)[0]['value'])

# Handle inline_handler
@bot.inline_handler(lambda query: query.query)
def default_query(inline_query):
    if not hasAccessToWariors(inline_query.from_user.username):
        r = types.InlineQueryResultArticle(id=0, title = 'Хрена надо? Ты не из наших банд!', input_message_content=types.InputTextMessageContent(getResponseDialogFlow(inline_query.from_user.username, 'i_dont_know_you').fulfillment_text), description=getResponseDialogFlow(inline_query.from_user.username, 'i_dont_know_you').fulfillment_text)
        bot.answer_inline_query(inline_query.id, [r], cache_time=300)
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
                    ]
                    #, 'timeUpdate':{'$gte': (datetime.now() - timedelta(days=28)).timestamp()  }
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

# ================================== Профиль ====================================
@bot.message_handler(func=lambda message: message.text and '📜 Профиль' == message.text and 'private' in message.chat.type)
def send_profile(message):
    user = users.getUser(message.from_user.username, registered_users)
    
    buttons = []
    button_parent = GLOBAL_VARS['profile']
    description = ''
    for d in button_parent['buttons']:
        name = f"{d['name']}"
        if d['id'] == 'common':
            name = '✳️ ' + name
            description = d['description']
        buttons.append(InlineKeyboardButton(f"{name}", callback_data=f"{button_parent['id']}|{d['id']}"))

    markup = InlineKeyboardMarkup(row_width=2)
    for row in build_menu(buttons=buttons, n_cols=3):
        markup.row(*row)  

    text=f'{description}\n{user.getProfile("common")}'
    # bot.send_photo(message.chat.id, warior.photo, warior.getProfile(userIAm.getTimeZone()))
    # bot.send_photo(message.chat.id, 'AgACAgIAAxkBAAI0nV6vzZEm2z3EHL4n_sEt2g3rHNnDAAI5rTEbRKKASdcXJDj7bh-oNmtMkS4AAwEAAwIAA20AA-wNAwABGQQ', caption=text, parse_mode='HTML', reply_markup=markup)
    # bot.send_photo(message.chat.id, 'CAACAgIAAxkBAAECbHRer8Y-iIWhSbwOsyDVXM6C0HjBBwACRgADswIBAAFr0mTVWxNP3BkE', caption=text, parse_mode='HTML', reply_markup=markup)
    bot.send_message(message.chat.id, text=text, parse_mode='HTML', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(GLOBAL_VARS['profile']['id']))
def select_profile(call):
    # bot.answer_callback_query(call.id, call.data)
    privateChat = ('private' in call.message.chat.type)
    if (privateChat):
        pass
    else:
        send_messages_big(call.message.chat.id, text=getResponseDialogFlow(call.from_user.username, 'shot_censorship').fulfillment_text)
        return
    
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return
    
    user = users.getUser(call.from_user.username, registered_users)
    button_parent_id = call.data.split('|')[0]
    button_id = call.data.split('|')[1]

    buttons = []
    button_parent = GLOBAL_VARS['profile']
    description = ''
    for d in button_parent['buttons']:
        name = f"{d['name']}"
        if d['id'] == button_id:
            name = '✳️ ' + name
            description = d['description']
        buttons.append(InlineKeyboardButton(f"{name}", callback_data=f"{button_parent_id}|{d['id']}"))

    markup = InlineKeyboardMarkup(row_width=2)
    for row in build_menu(buttons=buttons, n_cols=3):
        markup.row(*row)  

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'{description}\n{user.getProfile(button_id)}', parse_mode='HTML', reply_markup=markup)

# ================================== Комиссионка ==================================== and 'private' == message.chat.type
@bot.message_handler(func=lambda message: message.text and ('🧺 Комиссионка' == message.text) )
def send_baraholka(message):
    # if not isAdmin(message.from_user.username):
    #     send_welcome(message)
    #     return

    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то наговорить, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return

    buttons = []
    button = GLOBAL_VARS['commission']
    for d in button['buttons']:
        buttons.append(InlineKeyboardButton(f"{d['name']}", callback_data=f"{button['id']}|{d['id']}"))

    markup = InlineKeyboardMarkup(row_width=2)
    exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit")
    for row in build_menu(buttons=buttons, n_cols=3, exit_button=exit_button):
        markup.row(*row)  
    
    bot.send_message(message.chat.id, text=f'{button["description"]}', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(GLOBAL_VARS['commission']['id']))
def select_baraholka(call):
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    markupinline = InlineKeyboardMarkup(row_width=2)
    button_parent = call.data.split('|')[0]
    button_id = call.data.split('|')[1]

    if button_id == 'exit':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='🧺 Удачи, до новых встреч!', reply_markup=markupinline)
        return

    button = list(filter(lambda x : x['id'] == button_id, GLOBAL_VARS['commission']['buttons']))[0]
    buttons = []
    user = getUserByLogin(call.from_user.username)
    step = 0
    stepexit = 0
    
    if button_id in ['farm']:
        
        inventors = []
        for inv in farm.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inventors.append(inv['inventory'])
        
        unic_inv = []
        for inv in inventors:
            counter = len(list(filter(lambda x : x['id'] == inv['id'], inventors)))
            btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button['id']}|selectinvent|{step}|{inv['uid']}|{stepexit}")
            if counter > 1:
                btn = InlineKeyboardButton(f"💰{counter} {inv['name']}", callback_data=f"{button['id']}|selectgroup|{step}|{inv['id']}|{stepexit}")

            if inv['id'] not in unic_inv:
                unic_inv.append(inv['id'])
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)

        return

    if button_id in ['onshelf']:
        for invonshelf in shelf.find({'state': {'$ne': 'CANCEL'}}):
            inv = invonshelf['inventory']
            request = invonshelf['request']
            if request == None:
                request = []
            cost = inv['cost']
            findMyRequest = False
            for req in request:
                if req['login'] == user.getLogin():
                    cost = req['cost']
                    findMyRequest = True
                    break

            itsMy = call.from_user.username == invonshelf['login']
            btn = InlineKeyboardButton(f"{'👤 ' if itsMy else ('📝 ' if findMyRequest else '')}🔘{cost} {inv['name']}", callback_data=f"{button['id']}|selectinvent|{step}|{inv['uid']}")
            buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)

        return

    if button_id in ['workbench']:
        inventories_on = []
        for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inv = invonworkbench['inventory']
            inventories_on.append(inv)
            btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button['id']}|selectinvent|{step}|{inv['uid']}")
            buttons.append(btn)

        # Добавление кнопки Собрать 🔧
        collect = False
        for inv in list(filter(lambda x : 'composition' in x, GLOBAL_VARS['inventory'])):
            collect = False
            if inv['type'] == 'animals': continue
            for composit in inv['composition']:
                counter = len(list(filter(lambda x : x['id'] == composit['id'], inventories_on)))
                if counter >= composit['counter']:
                    collect = True
                else:
                    collect = False
                    break
            if collect:
                break


        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button['id']}|forward|{step+1}")
        
        header_buttons = []
        if collect:
            collect_btn = InlineKeyboardButton(f"Собрать 🔧", callback_data=f"{button['id']}|collect|{step}")
            header_buttons.append(collect_btn)

        if len(buttons)>0:
            selectall = InlineKeyboardButton(f"Забрать всё 💰", callback_data=f"{button['id']}|pickupall|{step}") 
            header_buttons.append(selectall) 

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, header_buttons=header_buttons, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)
        return

    if button_id in ['exchange']:
        inventors = []
        for inv in user.getInventoryType(GLOBAL_VARS['typeforcomission']):
            inventories = user.getInventoryThings({'id': inv['id']})
            btn = InlineKeyboardButton(f"🔘{inv['cost']} {inv['name']}", callback_data=f"{button['id']}|selectinvent|{step}|{inv['uid']}")
            if len(inventories) > 1:
                btn = InlineKeyboardButton(f"💰{len(inventories)} {inv['name']}", callback_data=f"{button['id']}|selectgroup|{step}|{inv['id']}")

            if inv['id'] not in inventors:
                inventors.append(inv['id'])
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith('farm'))
def select_farm(call):
    # bot.answer_callback_query(call.id, call.data)
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    markupinline = InlineKeyboardMarkup(row_width=2)
    button_parent_id = call.data.split('|')[0]
    button_parent = list(filter(lambda x : x['id'] == button_parent_id, GLOBAL_VARS['commission']['buttons']))[0]
    button_id = call.data.split('|')[1]
    buttons = []
    user = getUserByLogin(call.from_user.username)

    if button_id == 'exit':
        button = GLOBAL_VARS['commission']
        for d in button['buttons']:
            buttons.append(InlineKeyboardButton(f"{d['name']}", callback_data=f"{button['id']}|{d['id']}"))

        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit")
        for row in build_menu(buttons=buttons, n_cols=3, exit_button = exit_button):
            markupinline.row(*row)  
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)
        return

    if button_id in ['forward', 'back', 'selectgroupexit', 'selectexit']:
        step = int(call.data.split('|')[2])
        inventors = []
        for inv in farm.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inventors.append(inv['inventory'])
        
        unic_inv = []
        for inv in inventors:
            counter = len(list(filter(lambda x : x['id'] == inv['id'], inventors)))
            btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{step}|{inv['uid']}|{step}")
            if counter > 1:
                btn = InlineKeyboardButton(f"💰{counter} {inv['name']}", callback_data=f"{button_parent['id']}|selectgroup|{step}|{inv['id']}|{step}")

            if inv['id'] not in unic_inv:
                unic_inv.append(inv['id'])
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button_parent['description'], reply_markup=markupinline)
        return

    if button_id in ['selectgroupforward', 'selectgroupback', 'selectgroup']:
        stepinventory = int(call.data.split('|')[2])
        inv_id = call.data.split('|')[3]
        stepexit = call.data.split('|')[4]

        user = getUserByLogin(call.from_user.username)
        
        inventory = None
        inventories = []
        for inv in farm.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}, 'inventory.id': inv_id}):
            inventory = inv['inventory']
            inventories.append(inventory)

        if button_id in ['selectgroup']:
            stepinventory = 0
        
        selectall = InlineKeyboardButton(f"Выбрать все 💰", callback_data=f"{button_parent['id']}|selectall|{stepinventory}|{inventory['id']}|{stepexit}") 
        
        for inv in inventories: 
            btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{stepinventory}|{inv['uid']}|{stepexit}")
            buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|selectgroupback|{stepinventory-1}|{inventory['id']}|{stepexit}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectgroupexit|{stepexit}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|selectgroupforward|{stepinventory+1}|{inventory['id']}|{stepexit}")

    
        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=stepinventory, header_buttons=[selectall], back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row) 

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n▫️ {inventory['name']}\n▫️ {len(inventories)} шт.", reply_markup=markupinline)
        return

    if button_id in ['selectinvent', 'selectall']:
        inv_uid = call.data.split('|')[3]
        stepinventory = int(call.data.split('|')[2])
        stepexit = call.data.split('|')[4]
        user = getUserByLogin(call.from_user.username)
        filterInv = 'uid'
        if button_id in ['selectall']:
            filterInv = 'id'
        
        inventory = None
        inventories = []
        for inv in farm.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}, f'inventory.{filterInv}': inv_uid}):
            inventory = inv['inventory']
            inventories.append(inventory)

        pickup = InlineKeyboardButton(f"Забрать 📤", callback_data=f"{button_parent['id']}|{'pickup' if (filterInv == 'uid') else 'pickupall'}|{stepinventory}|{inventory[filterInv]}|{stepexit}")
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{stepinventory}")

        for row in build_menu(buttons=buttons, n_cols=3, limit=6, step=0, header_buttons=[exit_button, pickup], back_button=None, exit_button=None, forward_button=None):
            markupinline.row(*row) 

        count_str = f'▫️ {len(inventories)} шт.\n' if len(inventories) > 1 else ''  
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n\n{count_str}{users.getThingInfo(inventory)}", reply_markup=markupinline)
        return

    if button_id in ['pickup', 'pickupall']:
        stepinventory = int(call.data.split('|')[2])
        inv_uid = call.data.split('|')[3]
        user = getUserByLogin(call.from_user.username)
        inventory = None # user.getInventoryThing({'uid': inv_uid})
        u = 'uid'
        if button_id in ['pickupall']:
            u = 'id'

        for invonfarm in farm.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}, f'inventory.{u}': inv_uid}):
            user.addInventoryThing(invonfarm['inventory'])
        updateUser(user)

        newvalues = { "$set": {'state': 'CANCEL'} }
        result = farm.update_many(
            {
                'login': user.getLogin(), 
                'state': {'$ne': 'CANCEL'}, 
                f'inventory.{u}': inv_uid
            }, newvalues)

        # selectexit
        step = int(call.data.split('|')[2])
        inventors = []
        for inv in farm.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inventors.append(inv['inventory'])
        
        unic_inv = []
        for inv in inventors:
            counter = len(list(filter(lambda x : x['id'] == inv['id'], inventors)))
            btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{step}|{inv['uid']}|{step}")
            if counter > 1:
                btn = InlineKeyboardButton(f"💰{counter} {inv['name']}", callback_data=f"{button_parent['id']}|selectgroup|{step}|{inv['id']}|{step}")

            if inv['id'] not in unic_inv:
                unic_inv.append(inv['id'])
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button_parent['description'], reply_markup=markupinline)
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith('onshelf'))
def select_shelf(call):
    # bot.answer_callback_query(call.id, call.data)
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    markupinline = InlineKeyboardMarkup(row_width=2)
    button_parent_id = call.data.split('|')[0]
    button_parent = list(filter(lambda x : x['id'] == button_parent_id, GLOBAL_VARS['commission']['buttons']))[0]
    button_id = call.data.split('|')[1]
    buttons = []
    user = getUserByLogin(call.from_user.username)

    if button_id == 'exit':
        button = GLOBAL_VARS['commission']
        for d in button['buttons']:
            buttons.append(InlineKeyboardButton(f"{d['name']}", callback_data=f"{button['id']}|{d['id']}"))

        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit")
        for row in build_menu(buttons=buttons, n_cols=3, exit_button = exit_button):
            markupinline.row(*row)  
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)
        return

    if button_id in ['forward', 'back', 'selectexit']:
        step = int(call.data.split('|')[2])

        for invonshelf in shelf.find({'state': {'$ne': 'CANCEL'}}):
            inv = invonshelf['inventory']
            request = invonshelf['request']
            cost = inv['cost']
            findMyRequest = False
            if request == None:
                request = []
            for req in request:
                if req['login'] == user.getLogin():
                    cost = req['cost']
                    findMyRequest = True
                    break

            itsMy = call.from_user.username == invonshelf['login']
            btn = InlineKeyboardButton(f"{'👤 ' if itsMy else ('📝 ' if findMyRequest else '')}🔘{cost} {inv['name']}", callback_data=f"{button_parent_id}|selectinvent|{step}|{inv['uid']}")
            buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button_parent['description'], reply_markup=markupinline)
        return

    if button_id in ['decrease', 'order', 'add', 'selectinvent']:
        # {button_parent['id']}|selectinvent|{stepinventory}|{inv['uid']}
        inv_uid = call.data.split('|')[3]
        stepinventory = int(call.data.split('|')[2])
        user = getUserByLogin(call.from_user.username)
        
        inventory = None # user.getInventoryThing({'uid': inv_uid})
        invonshelf  = None
        your_request = ''

        # Валюта у продавца
        crypto = user.getInventoryThing({'id': 'crypto'})
        if crypto == None:
            crypto = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='CURRENCY')['value']) if x['id']=='crypto'), None).copy()
            user.addInventoryThing(crypto)
        
        for invonshelf in shelf.find({'state': {'$ne': 'CANCEL'}}):
            itsMy = False
            if invonshelf['inventory']['uid'] == inv_uid:
                inventory = invonshelf['inventory']
                break

        if inventory == None:
            bot.answer_callback_query(call.id, f'Этой вещи уже нет в магазине.')
            return
        
        request = invonshelf['request']
        if request == None:
            request = []

        best_request = ''
        best = None
        if len(request)>0:
            best = max(request, key=lambda x: x['cost'])
            best_request = f'\n▫️ 📈 Лучшее предложение: 🔘{best["cost"]}' 

        for req in request:
            if req['login'] == user.getLogin():
                your_request = f'\n▫️ {user.getGerb()} Твое предложение: 🔘{req["cost"]}' 

        userseller = getUserByLogin(invonshelf['login'])
        itsMy = call.from_user.username == invonshelf['login']
        if itsMy:
            for req in sorted(request, key = lambda i: i['cost'], reverse=True):
                userRequester = getUserByLogin(req["login"])
                cost = req['cost']
                if userRequester:
                    #s = f"{button_parent['id']}|request|{stepinventory}|{inventory['uid']}|{userRequester.getLogin()}"
                    #logger.info(str(len(s)) + '|' + s )
                    btn = InlineKeyboardButton(f"🔘{cost} {userRequester.getNameAndGerb()}", callback_data=f"{button_parent['id']}|request|{stepinventory}|{inventory['uid'][:16]}|{userRequester.getLogin()}")
                    buttons.append(btn)


            pickup = InlineKeyboardButton(f"Забрать 📤", callback_data=f"{button_parent['id']}|pickup|{stepinventory}|{inventory['uid']}")
            buttons.append(pickup)
        else:
            cost = inventory['cost']
            if best:
                cost = best['cost']
            for req in request:
                if req['login'] == user.getLogin():
                    cost = req['cost']
                    break 

            if not button_id == 'selectinvent':
                cost = int(call.data.split('|')[4])
                if cost <= 0:
                    bot.answer_callback_query(call.id, "Дешевле не бывает!")
                    return

            decrease  = InlineKeyboardButton(f"-5% 🔻", callback_data=f"{button_parent['id']}|decrease|{stepinventory}|{inventory['uid']}|{cost-1 if cost*0.05 <= 1 else int(cost-cost*0.05)}")
            buttons.append(decrease)

            order = InlineKeyboardButton(f"{cost} 📝", callback_data=f"{button_parent['id']}|order|{stepinventory}|{inventory['uid']}|{cost}")
            buttons.append(order)

            add = InlineKeyboardButton(f"+5% 🔺", callback_data=f"{button_parent['id']}|add|{stepinventory}|{inventory['uid']}|{cost+1 if cost*0.05 <= 1 else int(cost+cost*0.05)}")
            buttons.append(add)

        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{stepinventory}")
        step = 0
        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|selectback|{step-1}") 
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|selectforward|{step+1}")

        # TODO limit=16! Нужно сделать обработку вперед / назад
        for row in build_menu(buttons=buttons, n_cols=3, limit=16, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  


        if button_id == 'order':
            findMyReq = False
            for req in request:
                if req['login'] == user.getLogin():
                    req['cost'] = cost
                    findMyReq = True
                    break

            if not findMyReq:
                req = {'login': user.getLogin(), 'cost': cost}
                request.append(req)

            newvalues = { "$set": {'request': request} }
            result = shelf.update_one(
                {
                    '$or': 
                        [
                            {'state': 'NEW'},
                            {'state': None}
                        ],
                    'inventory.uid' : inventory['uid']
                }, newvalues)
            
            if result.matched_count < 1:
                bot.answer_callback_query(call.id, f'Что пошло не так.')
                return
            your_request = f'\n▫️ {user.getGerb()} Твое предложение: 🔘{cost}'
            
            send_messages_big(userseller.getChat(), text=f'🛍️👋 Магазин!\n{user.getNameAndGerb()} (@{user.getLogin()}) сделал предложение в магазине!\n▫️ 🔘{cost} {inventory["name"]}')
            bot.answer_callback_query(call.id, f'Заявка подана!')
        


        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n\n{userseller.getNameAndGerb()} (@{userseller.getLogin()})\n{users.getThingInfo(inventory)}{best_request}{your_request}\n▫️ {user.getGerb()} Твой кошелек: 🔘{crypto['cost']}", reply_markup=markupinline)
        return

    if button_id in ['pickup', 'request']:
        # {button_parent['id']}|pickup|{stepinventory}|{inventory['uid']}
        # {button_parent['id']}|request|{stepinventory}|{inventory['uid']}|{userRequester.getLogin()}
        inv_uid = call.data.split('|')[3]
        stepinventory = int(call.data.split('|')[2])
        user = getUserByLogin(call.from_user.username)
        inventory = None # user.getInventoryThing({'uid': inv_uid})
        invonshelf = None

        for invonshelf in shelf.find({'state': {'$ne': 'CANCEL'}}):
            itsMy = False
            if inv_uid in invonshelf['inventory']['uid']:
                inventory = invonshelf['inventory']
                break

        if inventory == None:
            bot.answer_callback_query(call.id, f'Этой вещи уже нет в магазине.')
            return
        
        userseller = getUserByLogin(invonshelf['login'])
        itsMy = call.from_user.username == invonshelf['login']

        if button_id == 'pickup':
            newvalues = { "$set": {'state': 'CANCEL'} }
            result = shelf.update_one(
                {
                    'state': 'NEW',
                    'inventory.uid' : inventory['uid']
                }, newvalues)
            
            if result.matched_count < 1:
                bot.answer_callback_query(call.id, f'Что пошло не так.')
                return

            userseller.addInventoryThing(inventory)
            updateUser(userseller)
            for req in invonshelf['request']:
                requester = user.getUserByLogin(req['login'])
                if requester:
                    send_messages_big(requester.getChat(), text=f'🛍️❌ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) забрал из магазина\n▫️ 🔘{cost} {inventory["name"]}!\nТвоя заявка аннулирована!')

        elif button_id == 'request':
            # Есть ли покупатель
            buyer = getUserByLogin(call.data.split('|')[4])
            if not buyer: 
                bot.answer_callback_query(call.id, f'Не найден покупатель')
                return
            
            request = None
            for request in invonshelf['request']:
                if request['login'] == buyer.getLogin():
                    break

            # Есть ли заявка от покупателя
            if not request:
                bot.answer_callback_query(call.id, f'Не найдена заявка')
                return
            
            # Есть ли деньги у покупателя
            cryptoBuyer = buyer.getInventoryThing({'id': 'crypto'})
            if cryptoBuyer == None or cryptoBuyer['cost'] - request['cost'] < 0:
                
                if cryptoBuyer == None:
                    cryptoBuyer = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='CURRENCY')['value']) if x['id']=='crypto'), None).copy()
                    buyer.addInventoryThing(cryptoBuyer)
                    updateUser(buyer)

                newRequests = invonshelf['request']
                newRequests.remove(request)
                invonshelf.update({'request': newRequests}) 

                newvalues = { "$set": {'request': newRequests} }
                result = shelf.update_one(
                    {
                        '$or': 
                        [
                            {'state': 'NEW'},
                            {'state': None}
                        ],
                        'inventory.uid' : inventory['uid']
                    }, newvalues)

                if result.matched_count < 1:
                    bot.answer_callback_query(call.id, f'Не смогли обновить заявки')
                    return

                # print(f'🛍️❌ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) хотел тебе продать {inventory["name"]}, но у тебя нет 🔘{inventory["cost"]}. Твоя заявка аннулирована :\n▫️ 🔘{inventory["cost"]} {inventory["name"]}')
                text = f'🛍️❌ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) хотел тебе продать {inventory["name"]}, но у тебя нет 🔘{inventory["cost"]}. Твоя заявка аннулирована :\n▫️ 🔘{inventory["cost"]} {inventory["name"]}'
                send_messages_big(buyer.getChat(), text=text)
                bot.answer_callback_query(call.id, f'У него нет столько бабла!')
                send_message_to_admin(f'🛍️❌ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) хотел {buyer.getNameAndGerb()} (@{buyer.getLogin()}) продать {inventory["name"]}, но у него нет 🔘{inventory["cost"]}. Заявка аннулирована :\n▫️ 🔘{inventory["cost"]} {inventory["name"]}')

                # Перерисовываем кнопки без этой заявки
                for request in newRequests:
                    userRequester = getUserByLogin(request["login"])
                    cost = request['cost']
                    if userRequester:
                        btn = InlineKeyboardButton(f"🔘{cost} {userRequester.getNameAndGerb()}", callback_data=f"{button_parent['id']}|request|{stepinventory}|{inventory['uid'][:16]}|{userRequester.getLogin()}")
                        buttons.append(btn)


                pickup = InlineKeyboardButton(f"Забрать 📤", callback_data=f"{button_parent['id']}|pickup|{stepinventory}|{inventory['uid']}")
                buttons.append(pickup)
                exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{stepinventory}")

                step = 0
                for row in build_menu(buttons=buttons, n_cols=3, limit=6, step=step, back_button=None, exit_button=exit_button, forward_button=None):
                    markupinline.row(*row) 

                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n\n{userseller.getNameAndGerb()} (@{userseller.getLogin()})\n{users.getThingInfo(inventory)}", reply_markup=markupinline)
                return

            # Валюта у продавца
            cryptoSeller = userseller.getInventoryThing({'id': 'crypto'})
            if cryptoSeller == None:
                cryptoSeller = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='CURRENCY')['value']) if x['id']=='crypto'), None).copy()
                userseller.addInventoryThing(cryptoSeller)

            # Добавили валюту продавцу
            cryptoSeller.update({'cost': cryptoSeller['cost'] + request['cost']})
            userseller.updateInventoryThing(cryptoSeller)

            # Забрали валюту у покупателя
            cryptoBuyer.update({'cost': cryptoBuyer['cost'] - request['cost']})
            buyer.updateInventoryThing(cryptoBuyer)
            
            # Добавили вещь в инвентарь покупателя
            inventory['cost'] = request['cost']
            buyer.addInventoryThing(inventory)
            
            # Закрываем заявку               
            newvalues = { "$set": {'state': 'CANCEL'} }
            result = shelf.update_one(
                {
                    '$or': 
                        [
                            {'state': 'NEW'},
                            {'state': None}
                        ],
                    'inventory.uid' : inventory['uid']
                }, newvalues)
            
            if result.matched_count < 1:
                bot.answer_callback_query(call.id, f'Что пошло не так.')
                return

            # Уведомляем всех остальных о закрытии заявки
            for req in invonshelf['request']:
                requester = getUserByLogin(req['login'])
                if requester:
                    if not (requester.getLogin() == buyer.getLogin()):
                        # print(f'🛍️❌ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) продал {buyer.getNameAndGerb()} (@{buyer.getLogin()})\n▫️ 🔘{inventory["cost"]} {inventory["name"]}!\nТвоя заявка аннулирована!')
                        send_messages_big(requester.getChat(), text=f'🛍️❌ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) продал {buyer.getNameAndGerb()} (@{buyer.getLogin()})\n▫️ {inventory["name"]} за 🔘{inventory["cost"]}!\nТвоя заявка аннулирована!')

            # Обновляем покупателя и продавца
            updateUser(buyer)
            updateUser(userseller)
            
            send_messages_big(userseller.getChat(), text=f'🛍️✔️ Магазин!\nТы продал:\n▫️ 🔘{inventory["cost"]} {inventory["name"]}')
            # print(f'🛍️✔️ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) продал тебе:\n▫️ 🔘{inventory["cost"]} {inventory["name"]}')
            send_messages_big(buyer.getChat(), text=f'🛍️✔️ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) продал тебе:\n▫️ 🔘{inventory["cost"]} {inventory["name"]}')
            text = f'🛍️✔️ Магазин!\n{userseller.getNameAndGerb()} (@{userseller.getLogin()}) продал {buyer.getNameAndGerb()} (@{buyer.getLogin()}):\n▫️ 🔘{inventory["cost"]} {inventory["name"]}'
            send_message_to_admin(text)

        # selectexit
        step = int(call.data.split('|')[2])
        for invonshelf in shelf.find({'state': {'$ne': 'CANCEL'}}):
            inv = invonshelf['inventory']
            itsMy = call.from_user.username == invonshelf['login']
            btn = InlineKeyboardButton(f"{'👤 ' if itsMy else ''}🔘{inv['cost']} {inv['name']}", callback_data=f"{button_parent_id}|selectinvent|{step}|{inv['uid']}")
            buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button_parent['description'], reply_markup=markupinline)
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith('workbench'))
def select_workbench(call):
    
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    markupinline = InlineKeyboardMarkup(row_width=2)
    button_parent_id = call.data.split('|')[0]
    button_parent = list(filter(lambda x : x['id'] == button_parent_id, GLOBAL_VARS['commission']['buttons']))[0]
    button_id = call.data.split('|')[1]
    buttons = []
    user = getUserByLogin(call.from_user.username)

    if button_id == 'exit':
        button = GLOBAL_VARS['commission']
        for d in button['buttons']:
            buttons.append(InlineKeyboardButton(f"{d['name']}", callback_data=f"{button['id']}|{d['id']}"))

        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit")
        for row in build_menu(buttons=buttons, n_cols=3, exit_button = exit_button):
            markupinline.row(*row)  
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)
        return

    if button_id in ['forward', 'back', 'selectexit']:
        step = int(call.data.split('|')[2])
        inventories_on = []
        for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inv = invonworkbench['inventory']
            
            inventories_on.append(inv)
            btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button_parent_id}|selectinvent|{step}|{inv['uid']}")
            buttons.append(btn)

        # Добавление кнопки Собрать 🔧
        collect = False
        for inv in list(filter(lambda x : 'composition' in x, GLOBAL_VARS['inventory'])):
            collect = False
            if inv['type'] == 'animals': continue
            for composit in inv['composition']:
                counter = len(list(filter(lambda x : x['id'] == composit['id'], inventories_on)))
                if counter >= composit['counter']:
                    collect = True
                else:
                    collect = False
                    break
            if collect:
                break

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        header_buttons = []
        if len(buttons)>0:
            selectall = InlineKeyboardButton(f"Забрать всё 💰", callback_data=f"{button_parent['id']}|pickupall|{step}") 
            header_buttons.append(selectall) 

        if collect:
            collect_btn = InlineKeyboardButton(f"Собрать 🔧", callback_data=f"{button_parent['id']}|collect|{0}")
            header_buttons.append(collect_btn)

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, header_buttons=header_buttons, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button_parent['description'], reply_markup=markupinline)
        return

    if button_id in ['selectinvent']:
        # {button_parent['id']}|selectinvent|{stepinventory}|{inv['uid']}
        inv_uid = call.data.split('|')[3]
        stepinventory = int(call.data.split('|')[2])
        step = 0
        user = getUserByLogin(call.from_user.username)
        
        inventory = None # user.getInventoryThing({'uid': inv_uid})

        for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            if invonworkbench['inventory']['uid'] == inv_uid:
                inventory = invonworkbench['inventory']
                break

        if inventory == None:
            bot.answer_callback_query(call.id, f'Этой вещи уже нет на верстаке.')
            return
        
        userseller = getUserByLogin(invonworkbench['login'])

        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{stepinventory}")
        buttons.append(exit_button)

        if 'composition' in inventory:
            doit = 'Разобрать 🛠️'
            if inventory['type'] == 'animals':
                doit = 'Зарезать 🔪'
            splitup = InlineKeyboardButton(f"{doit} {len(inventory['composition'])} ", callback_data=f"{button_parent['id']}|splitup|{stepinventory}|{inventory['uid']}")
            buttons.append(splitup)

        pickup = InlineKeyboardButton(f"Забрать 📤", callback_data=f"{button_parent['id']}|pickup|{stepinventory}|{inventory['uid']}")
        buttons.append(pickup)

        for row in build_menu(buttons=buttons, n_cols=3, limit=6, step=step, back_button=None, exit_button=None, forward_button=None):
            markupinline.row(*row) 

        part_of_composition = '▫️ 🔬 Часть чего-то' if len(getInvCompositionIn(inventory))>0 else ''
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n\n{userseller.getNameAndGerb()} (@{userseller.getLogin()})\n{users.getThingInfo(inventory)}{part_of_composition}", reply_markup=markupinline)
        return

    if button_id in ['collect', 'collectback', 'collectforward']:
        # {button_parent['id']}|collect|{step}}
        step = int(call.data.split('|')[2])
        inventories_on = []
        for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inv = invonworkbench['inventory']
            inventories_on.append(inv)

        for inv in list(filter(lambda x : 'composition' in x, GLOBAL_VARS['inventory'])):
            collect = False
            if inv['type'] == 'animals': continue
            for composit in inv['composition']:
                counter = len(list(filter(lambda x : x['id'] == composit['id'], inventories_on)))
                if counter >= composit['counter']:
                    collect = True
                else:
                    collect = False
                    break
            if collect:
                btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button_parent_id}|selectcollect|{0}|{inv['id']}")
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|collectback|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|collectforward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\nЭти вещи ты можешь собрать.", reply_markup=markupinline)
        return

    if button_id in ['selectcollect']:
        step = int(call.data.split('|')[2])
        ivn_id = call.data.split('|')[3]
        inventory = list(filter(lambda x : x['id'] == ivn_id, GLOBAL_VARS['inventory']))[0].copy()

        inventories_on = []
        for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inv = invonworkbench['inventory']
            inventories_on.append(inv)

        arr = []
        for com in inventory['composition']:
            arr.append(com)
        
        comp_arr = []  
        inventory.update({'composition': comp_arr})

        for composit in arr:
            for i in range(0, composit['counter']):
                for inv in inventories_on:
                    if inv['id'] == composit['id']:
                        comp_arr.append(inv)
                        inventories_on.remove(inv)

                        newvalues = { "$set": {'state': 'CANCEL'} }
                        result = workbench.update_one(
                            {
                                'state': 'NEW',
                                'inventory.uid' : inv['uid']
                            }, newvalues)
                        
                        if result.matched_count < 1:
                            bot.answer_callback_query(call.id, f'Что пошло не так.')
                            return
                        break
        
        if 'uid' not in inventory:
            inventory.update({'uid': f'{uuid.uuid4()}'})

        row = {
                'date': (datetime.now()).timestamp(),
                'login': user.getLogin(),
                'band' : user.getBand(),
                'goat' : getMyGoatName(user.getLogin()),
                'state': 'NEW',
                'inventory'  : inventory
        }
        newvalues = { "$set": row }

        result = workbench.update_one(
            {
                'state': 'NEW',
                'inventory.uid' : inventory['uid']
            }, newvalues)
        if result.matched_count < 1:
            workbench.insert_one(row)

        send_message_to_admin(text=f'🛠️ Собрано на верстаке:\n▫️ {user.getNameAndGerb()} {user.getLogin()}\n▫️ {inventory["name"]} 🔘{inventory["cost"]}')
            
        # user.addInventoryThing(inventory) 
        # updateUser(user)               
        # bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n\n{users.getThingInfo(inventory)}", reply_markup=markupinline)
        
        # Рисуекм кнопки назад и т.д.
        step = int(call.data.split('|')[2])
        inventories_on = []
        for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inv = invonworkbench['inventory']
            inventories_on.append(inv)

        for inv in list(filter(lambda x : 'composition' in x, GLOBAL_VARS['inventory'])):
            collect = False
            if inv['type'] == 'animals': continue
            for composit in inv['composition']:
                counter = len(list(filter(lambda x : x['id'] == composit['id'], inventories_on)))
                if counter >= composit['counter']:
                    collect = True
                else:
                    collect = False
                    break
            if collect:
                btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button_parent_id}|selectcollect|{0}|{inv['id']}")
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|collectback|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|collectforward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n<b>Ты собрал:</b>\n{users.getThingInfo(inventory)}", reply_markup=markupinline, parse_mode='HTML')

        return

    if button_id in ['pickup', 'pickupall', 'splitup']:
        # {button_parent['id']}|pickup|{stepinventory}|{inventory['uid']}

        stepinventory = int(call.data.split('|')[2])
        user = getUserByLogin(call.from_user.username)
        inventory = None # user.getInventoryThing({'uid': inv_uid})

        if button_id in ['pickupall']:
            for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
                user.addInventoryThing(invonworkbench['inventory'])
            updateUser(user)

            newvalues = { "$set": {'state': 'CANCEL'} }
            result = workbench.update_many(
                {
                    'state': 'NEW',
                    'login' : user.getLogin()
                }, newvalues)
        else:
            inv_uid = call.data.split('|')[3]
            for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
                if invonworkbench['inventory']['uid'] == inv_uid:
                    inventory = invonworkbench['inventory']
                    break

            if inventory == None:
                bot.answer_callback_query(call.id, f'Этой вещи уже нет на верстаке.')
                return
            
            userseller = getUserByLogin(invonworkbench['login'])

            newvalues = { "$set": {'state': 'CANCEL'} }
            result = workbench.update_one(
                {
                    'state': 'NEW',
                    'inventory.uid' : inventory['uid']
                }, newvalues)
            
            if result.matched_count < 1:
                bot.answer_callback_query(call.id, f'Что пошло не так.')
                return

            if button_id in ['pickup']:
                userseller.addInventoryThing(inventory)
                updateUser(userseller)
                bot.answer_callback_query(call.id, f'Забрали')

            elif button_id in ['splitup']:
                
                for comp in inventory['composition']:

                    # Добавляем составные   объекты
                    listInv = GLOBAL_VARS['inventory']    
                    if 'composition' in comp:
                        arr = []
                        flagSplitComposition = False
                        for com in comp['composition']:
                            arr.append(com)
                            if 'counter' in com: flagSplitComposition = True

                        if flagSplitComposition:
                            comp_arr = []  
                            comp.update({'composition': comp_arr})
                            for com in arr:
                                for i in range(0, com["counter"]):
                                    composit = list(filter(lambda x : x['id']==com['id'], listInv))[0].copy()
                                    composit.update({'uid':f'{uuid.uuid4()}'})
                                    if com["id"] == 'crypto':
                                        composit["cost"] = com["counter"]
                                        comp_arr.append(composit)
                                        break
                                    comp_arr.append(composit)

                    row = {
                            'date': (datetime.now()).timestamp(),
                            'login': userseller.getLogin(),
                            'band' : userseller.getBand(),
                            'goat' : getMyGoatName(userseller.getLogin()),
                            'state': 'NEW',
                            'inventory'  : comp
                    }
                    newvalues = { "$set": row }
                    result = workbench.update_one(
                        {
                            'state': 'NEW',
                            'inventory.uid' : comp['uid']
                        }, newvalues)
                    if result.matched_count < 1:
                        workbench.insert_one(row)
                    send_message_to_admin(text=f'🔨 Разобрано\n▫️ {userseller.getNameAndGerb()} (@{userseller.getLogin()})\n▫️ {inventory["name"]}')
            
                bot.answer_callback_query(call.id, f'Разобрали')
        
        # selectexit
        step = int(call.data.split('|')[2])
        inventories_on = []
        for invonworkbench in workbench.find({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'}}):
            inv = invonworkbench['inventory']
            inventories_on.append(inv)
            btn = InlineKeyboardButton(f"{inv['name']}", callback_data=f"{button_parent_id}|selectinvent|{step}|{inv['uid']}")
            buttons.append(btn)

        # Добавление кнопки Собрать 🔧
        collect = False
        for inv in list(filter(lambda x : 'composition' in x, GLOBAL_VARS['inventory'])):
            collect = False
            for composit in inv['composition']:
                counter = len(list(filter(lambda x : x['id'] == composit['id'], inventories_on)))
                if counter >= composit['counter']:
                    collect = True
                else:
                    collect = False
                    break
            if collect:
                break

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        header_buttons = []
        if len(buttons)>0:
            selectall = InlineKeyboardButton(f"Забрать всё 💰", callback_data=f"{button_parent['id']}|pickupall|{step}") 
            header_buttons.append(selectall) 

        if collect:
            collect_btn = InlineKeyboardButton(f"Собрать 🔧", callback_data=f"{button_parent['id']}|collect|{0}")
            header_buttons.append(collect_btn)

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, header_buttons=header_buttons, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button_parent['description'], reply_markup=markupinline)
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith('exchange'))
def select_exchange(call):
    # bot.answer_callback_query(call.id, call.data)
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    markupinline = InlineKeyboardMarkup(row_width=2)
    button_parent_id = call.data.split('|')[0]
    button_parent = list(filter(lambda x : x['id'] == button_parent_id, GLOBAL_VARS['commission']['buttons']))[0]
    button_id = call.data.split('|')[1]
    buttons = []

    if button_id == 'exit':
        button = GLOBAL_VARS['commission']
        for d in button['buttons']:
            buttons.append(InlineKeyboardButton(f"{d['name']}", callback_data=f"{button['id']}|{d['id']}"))

        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button['id']}|exit")
        for row in build_menu(buttons=buttons, n_cols=3, exit_button = exit_button):
            markupinline.row(*row)  
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button['description'], reply_markup=markupinline)
        return

    if button_id in ['forward', 'back', 'selectexit']:
        step = int(call.data.split('|')[2])
        user = getUserByLogin(call.from_user.username)
        inventors = []
        for inv in user.getInventoryType(GLOBAL_VARS['typeforcomission']):
            inventories = user.getInventoryThings({'id': inv['id']})
            btn = InlineKeyboardButton(f"🔘{inv['cost']} {inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{step}|{inv['uid']}")
            if len(inventories) > 1:
                btn = InlineKeyboardButton(f"💰{len(inventories)} {inv['name']}", callback_data=f"{button_parent['id']}|selectgroup|{step}|{inv['id']}")

            if inv['id'] not in inventors:
                inventors.append(inv['id'])
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=button_parent['description'], reply_markup=markupinline)
        return

    if button_id in ['selectgroupexit', '']:
        step = int(call.data.split('|')[2])
        user = getUserByLogin(call.from_user.username)
        inventories_arr = []
        for inv in user.getInventoryType(GLOBAL_VARS['typeforcomission']):
            
            inventories = user.getInventoryThings({'id': inv['id']})
            btn = InlineKeyboardButton(f"🔘{inv['cost']} {inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{step}|{inv['uid']}")
            if len(inventories) > 1:
                btn = InlineKeyboardButton(f"{len(inventories)} {inv['name']}", callback_data=f"{button_parent['id']}|selectgroup|{step}|{inv['id']}")

            if inv['id'] not in inventories_arr:
                inventories_arr.append(inv['id'])
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = button_parent['description'], reply_markup=markupinline)
        return

    if button_id in ['selectgroupforward', 'selectgroupback', 'selectgroup']:
        stepinventory = int(call.data.split('|')[2])
        
        inv_id = call.data.split('|')[3]
        user = getUserByLogin(call.from_user.username)
        step = 0
        inventory = user.getInventoryThing({'id': inv_id})

        if button_id in ['selectgroup']:
            stepinventory = 0
        
        
        inventories = user.getInventoryThings({'id': inv_id})
        for inv in inventories: 
            btn = InlineKeyboardButton(f"🔘{inv['cost']} {inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{stepinventory}|{inv['uid']}")
            buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|selectgroupback|{stepinventory-1}|{inventory['id']}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectgroupexit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|selectgroupforward|{stepinventory+1}|{inventory['id']}")
        selectall = InlineKeyboardButton(f"Выбрать все 💰", callback_data=f"{button_parent['id']}|selectall|{stepinventory}|{inventory['id']}") 
        
    
        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=stepinventory, header_buttons=[selectall], back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row) 

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n▫️ {inventory['name']}\n▫️ {len(inventories)} шт.", reply_markup=markupinline)
        return

    if button_id in ['selectinvent', 'selectall']:
        # {button_parent['id']}|selectinvent|{stepinventory}|{inv['uid']}
        inv_uid = call.data.split('|')[3]
        stepinventory = int(call.data.split('|')[2])
        step = 0
        user = getUserByLogin(call.from_user.username)
        filterInv = {'uid': inv_uid}
        if button_id in ['selectall']:
            filterInv = {'id': inv_uid}
        inventory = user.getInventoryThing(filterInv)

        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{stepinventory}")
        if button_id in ['selectinvent']:
            toshelf = InlineKeyboardButton(f"🛍️ На продажу", callback_data=f"{button_parent['id']}|toshelf|{stepinventory}|{inventory['uid']}")
            sell = InlineKeyboardButton(f"🔘 {int(inventory['cost']*button_parent['discont'])} Получить", callback_data=f"{button_parent['id']}|getcrypto|{stepinventory}|{inventory['uid']}")
            buttons.append(toshelf)
            buttons.append(sell)

        toworkbench = InlineKeyboardButton(f"⚙️ На верстак", callback_data=f"{button_parent['id']}|toworkbench|{stepinventory}|{inventory['uid']}")
        if button_id in ['selectall']:
            toworkbench = InlineKeyboardButton(f"⚙️ На верстак", callback_data=f"{button_parent['id']}|toworkbenchall|{stepinventory}|{inventory['id']}")
        buttons.append(toworkbench)

        if inventory['type'] in ['animals']:
            tofarm = InlineKeyboardButton(f"🐮 На ферму", callback_data=f"{button_parent['id']}|tofarm|{stepinventory}|{inventory['uid']}")
            if button_id in ['selectall']:
                tofarm = InlineKeyboardButton(f"🐮 На ферму", callback_data=f"{button_parent['id']}|tofarmall|{stepinventory}|{inventory['id']}")
            buttons.append(tofarm)
        
        for row in build_menu(buttons=buttons, n_cols=3, limit=6, step=step, back_button=None, exit_button=exit_button, forward_button=None):
            markupinline.row(*row) 

        part_of_composition = '▫️ 🔬 Часть чего-то' if len(getInvCompositionIn(inventory))>0 else ''
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n\n{user.getInventoryThingInfo({'uid': inv_uid})}{part_of_composition}", reply_markup=markupinline)
    
        # bot.answer_callback_query(call.id, f'selectinvent: {call.data}')
        return

    if button_id in ['getcrypto', 'toshelf', 'toworkbench', 'toworkbenchall', 'tofarm', 'tofarmall']:
        # {button_parent['id']}|getcrypto|{stepinventory}|{inventory['uid']}
        inv_uid = call.data.split('|')[3]
        stepinventory = int(call.data.split('|')[2])
        step = 0
        user = getUserByLogin(call.from_user.username)

        filterInv = {'uid': inv_uid}
        if button_id in ['toworkbenchall', 'tofarmall']:
            filterInv = {'id': inv_uid}
        inventory = user.getInventoryThing(filterInv)

        if inventory['id'] == 'crown_pidor':
            goat = getMyGoat(call.from_user.username)
            send_messages_big(goat['chats']['info'], text=f'Внимание! Вы представляете!? {user.getNameAndGerb()} (@{user.getLogin()}) хотел сдать 👑 золотую корону с гравировкой "Pidor of the day". Ну настоящий пидорский поступок!\nА ну-ка, наваляйте ему хорошенько!')
            bot.answer_callback_query(call.id, f'Ну ты и пидор! Попытаться сдать корону - это запредельно!')
            return

        if button_id in ['getcrypto']:
            cost = int(inventory["cost"]*button_parent['discont'])
            crypto = user.getInventoryThing({'id': 'crypto'})
            if crypto == None:
                crypto = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='CURRENCY')['value']) if x['id']=='crypto'), None).copy()
                crypto.update({'cost': cost})
                addInventory(user, crypto)
            else:
                crypto.update({'cost': crypto['cost']+cost})
                user.updateInventoryThing(crypto)
            user.removeInventoryThing(inventory)
            updateUser(user)
            send_message_to_admin(text=f'♻️ Сдано за {int(button_parent["discont"]*100)}% 💴!\n▫️ {user.getNameAndGerb()} (@{user.getLogin()})\n▫️ {inventory["name"]} 🔘{cost}')
            bot.answer_callback_query(call.id, f'Сдано за 🔘 {cost}')

        elif button_id in ['toshelf']:
            counter_inv = shelf.count_documents({'login': user.getLogin(), 'state': {'$ne': 'CANCEL'} })
            if counter_inv >= 2:
                bot.answer_callback_query(call.id, f'Тебе можно держать в магазине только {counter_inv} шт.')
                return
            request = []
            row = {
                    'date': (datetime.now()).timestamp(),
                    'login': user.getLogin(),
                    'band' : user.getBand(),
                    'goat' : getMyGoatName(user.getLogin()),
                    'state': 'NEW',
                    'inventory'  : inventory,
                    'request' : request
            }
            newvalues = { "$set": row }
            result = shelf.update_one(
                {
                    'state': 'NEW',
                    'inventory.uid' : inventory['uid']
                }, newvalues)
            if result.matched_count < 1:
                shelf.insert_one(row)
            
            user.removeInventoryThing(inventory)
            updateUser(user)
            send_message_to_admin(text=f'🛍️ Выставили на продажу!\n▫️ {user.getNameAndGerb()} (@{user.getLogin()})\n▫️ {inventory["name"]} 🔘{inventory["cost"]}')
            bot.answer_callback_query(call.id, f'Выставлено на продажу')

        elif button_id in ['toworkbench', 'toworkbenchall']:
            for inventory in user.getInventoryThings(filterInv):
                row = {
                        'date': (datetime.now()).timestamp(),
                        'login': user.getLogin(),
                        'band' : user.getBand(),
                        'goat' : getMyGoatName(user.getLogin()),
                        'state': 'NEW',
                        'inventory'  : inventory
                }
                newvalues = { "$set": row }

                result = workbench.update_one(
                    {
                        'state': 'NEW',
                        'inventory.uid' : inventory['uid']
                    }, newvalues)
                if result.matched_count < 1:
                    workbench.insert_one(row)
            
                user.removeInventoryThing(inventory)

            updateUser(user)
            send_message_to_admin(text=f'⚙️ Положено на верстак!\n▫️ {user.getNameAndGerb()} (@{user.getLogin()})\n▫️ {inventory["name"]}')
            bot.answer_callback_query(call.id, f'Положено на верстак')

        elif button_id in ['tofarm', 'tofarmall']:
            for inventory in user.getInventoryThings(filterInv):
                row = {
                        'date': (datetime.now()).timestamp(),
                        'login': user.getLogin(),
                        'band' : user.getBand(),
                        'goat' : getMyGoatName(user.getLogin()),
                        'state': 'NEW',
                        'inventory'  : inventory
                }
                newvalues = { "$set": row }

                result = workbench.update_one(
                    {
                        'state': 'NEW',
                        'inventory.uid' : inventory['uid']
                    }, newvalues)
                if result.matched_count < 1:
                    farm.insert_one(row)
            
                user.removeInventoryThing(inventory)

            updateUser(user)
            send_message_to_admin(text=f'🐮 Переведен на ферму!\n▫️ {user.getNameAndGerb()} (@{user.getLogin()})\n▫️ {inventory["name"]}')
            bot.answer_callback_query(call.id, f'Переведен на ферму')

        # Возвращаемся как selectexit
        step = int(call.data.split('|')[2])
        user = getUserByLogin(call.from_user.username)
                    
        inventors = []
        for inv in user.getInventoryType(GLOBAL_VARS['typeforcomission']):
            inventories = user.getInventoryThings({'id': inv['id']})
            btn = InlineKeyboardButton(f"🔘{inv['cost']} {inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{step}|{inv['uid']}")
            if len(inventories) > 1:
                btn = InlineKeyboardButton(f"💰{len(inventories)} {inv['name']}", callback_data=f"{button_parent['id']}|selectgroup|{step}|{inv['id']}")

            if inv['id'] not in inventors:
                inventors.append(inv['id'])
                buttons.append(btn)

        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|back|{step-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|exit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|forward|{step+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row)  

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = button_parent['description'], reply_markup=markupinline)
        
        return

    if button_id in ['select']:
        bot.answer_callback_query(call.id, call.data)
        step = int(call.data.split('|')[2])
        stepinventory = 0
        user = getUserByLogin(call.from_user.username)
        inv_id = call.data.split('|')[3]
        inventories = user.getInventoryThings({'id': inv_id})
        inventory = user.getInventoryThing({'id': inv_id})
        
        inventories_arr = []
        for inv in user.getInventoryType(GLOBAL_VARS['typeforcomission']):
            inventories = user.getInventoryThings({'id': inv['id']})

            btn = InlineKeyboardButton(f"🔘{inv['cost']} {inv['name']}", callback_data=f"{button_parent['id']}|selectinvent|{stepinventory}|{inv['uid']}")
            if len(inventories) > 1:
                btn = InlineKeyboardButton(f"💰{len(inventories)} {inv['name']}", callback_data=f"{button_parent['id']}|selectgroup|{step}|{inv['id']}")

            if inv['id'] not in inventories_arr:
                inventories_arr.append(inv['id'])
                buttons.append(btn)
        
        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"{button_parent['id']}|selectback|{stepinventory-1}") 
        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"{button_parent['id']}|selectexit|{step}")
        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"{button_parent['id']}|selectforward|{stepinventory+1}")

        for row in build_menu(buttons=buttons, n_cols=2, limit=6, step=stepinventory, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
            markupinline.row(*row) 

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{button_parent['description']}\n{inventory['name']}", reply_markup=markupinline)
        
        return    
# ============================================================================

@bot.message_handler(func=lambda message: message.text and ('📈 Статистика' == message.text))
def send_back_from_usset(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то наговорить, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
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
    for row in build_menu(buttons=GLOBAL_VARS['private_buttons'], n_cols=3):
        markup.row(*row)  
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
    
    if message.text == '🧠Играю в "П"артизана':
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        markup.add('Да ✅', 'Нет ❌')
        bot.send_message(message.chat.id, text='Твой выбор...', reply_markup=markup)
        bot.register_next_step_handler(message, process_partizan_step)   

def process_partizan_step(message):
    if message.text == 'Да ✅' or message.text == 'Нет ❌':
        user = getUserByLogin(message.from_user.username)
        setting = getSetting(code='USER_SETTINGS', id='partizan')
        if message.text == 'Да ✅':
            setting.update({'value': True})
        else:
            setting.update({'value': False})
        user.addSettings(setting)
        updateUser(user)

        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        for row in build_menu(buttons=GLOBAL_VARS['private_buttons'], n_cols=3):
            markup.row(*row)  
        bot.send_message(message.chat.id, text=user.getSettingsReport(), reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text='Похоже, что ты меня не понял...')

def process_gerb_step(message):
    if tools.isOneEmojify(message.text):
        goat_bands = getGoatBands(getMyGoatName(message.from_user.username))
        for user in list( filter(lambda x : x.getBand() and x.getBand() in goat_bands, USERS_ARR) ):
            if user.getSettingValue(name='🃏Мой герб') and user.getSettingValue(name='🃏Мой герб') == message.text:
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
                for row in build_menu(buttons=GLOBAL_VARS['private_buttons'], n_cols=3):
                    markup.row(*row)  
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
    for row in build_menu(buttons=GLOBAL_VARS['private_buttons'], n_cols=3):
        markup.row(*row)  
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

# Handle '/mob'
@bot.message_handler(func=lambda message: message.text and message.text.startswith('/mob'))
def send_mob_report(message):
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то стартовать, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return
    
    hashstr = message.text
    dresult = mob.aggregate([ 
    {   "$match": {
                "kr": {"$gte": 0}
            } 
    },
    {   "$group": {
        "_id": { "mob_name":"$mob_name", "mob_class":"$mob_class"}, 
        "count": {
            "$sum": 1}}},
        
    {   "$sort" : { "count" : -1 } }
    ])
    
    for d in dresult:
        mob_name = d["_id"]["mob_name"] 
        mob_class = d["_id"]["mob_class"] 
        s = mob_name + mob_class
        hashstr_in_bd = getMobHash(mob_name, mob_class)
        if hashstr == hashstr_in_bd:
            send_messages_big(message.chat.id, text=getMobDetailReport(mob_name, mob_class))
            return

    send_messages_big(message.chat.id, text=f'Не нашел ничего!')

# Handle '/door' 
@bot.message_handler(commands=['door','314door','pi_door', '3.14159265359_door'])
def send_welcome(message):
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то стартовать, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return

    if (random.random() <= float(getSetting(code='PROBABILITY', name='DOOR_STICKER'))):
        bot.send_photo(message.chat.id, random.sample(getSetting(code='STICKERS', name='DOOR'), 1)[0]['value'])
        return   

# Handle '/test'
@bot.message_handler(commands=['test'])
def send_welcome(message):
    if not isAdmin(message.from_user.username):
        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
        return

    try:
        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'bolt_congratulation_bolt_1', context_param={'bolt':'🎫🍼 Билет на гигантскую бутылку'}).fulfillment_text)
    except:
        send_message_to_admin(f'⚠️🤬 Сломался тест!')

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то стартовать, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return


    response = getResponseDialogFlow(message.from_user.username, 'start').fulfillment_text
    privateChat = ('private' in message.chat.type)
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if not privateChat:
        for row in build_menu(buttons=GLOBAL_VARS['group_buttons'], n_cols=3):
            markup.row(*row)  
    else:
        for row in build_menu(buttons=GLOBAL_VARS['private_buttons'], n_cols=3):
            markup.row(*row)  

    if response:
        bot.send_message(message.chat.id, text=response, reply_markup=markup)

# Handle document
@bot.message_handler(content_types=['document'])
def get_message_photo(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то показать, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return

# Handle photo
@bot.message_handler(content_types=["photo"])
def get_message_photo(message):
    #write_json(message.json)
    privateChat = ('private' in message.chat.type)
    logger.info(f'chat:{message.chat.id}:{"private" if privateChat else "Group"}:{message.from_user.username}:{datetime.fromtimestamp(message.forward_date) if message.forward_date else ""}:{message.text}')
    
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то показать, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return

    if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
        ww = wariors.fromPhotoToWarioirs(message.forward_date, message.caption, message.photo[0].file_id)
        for warior in ww:
            update_warior(warior)
            # Отедельно обновляем Банду
            if warior.getBand() == None:
                newvalues = { "$set": {'band': None} }
                resultupdata = registered_wariors.update_one({
                    "name": f"{warior.getName()}", 
                    "fraction": f"{warior.getFraction()}"
                    }, newvalues)
                update_warior(None)
                    
            wariorShow = getWariorByName(warior.getName(), warior.getFraction())
            markupinline = None
            
            user = getUserByName(wariorShow.getName())
            if not privateChat and user and (not user.getLogin() == message.from_user.username) and user.getBand() and user.getBand() in getGoatBands(getMyGoatName(message.from_user.username)):
                buttons = []
                buttons.append(InlineKeyboardButton(f'@{user.getLogin()}', callback_data=f"ping_user|{user.getLogin()}"))
                markupinline = InlineKeyboardMarkup(row_width=2)
                for row in build_menu(buttons=buttons, n_cols=2):
                    markupinline.row(*row) 
            userIAm = getUserByLogin(message.from_user.username)
            
            if hasAccessToWariors(message.from_user.username):
                send_messages_big(message.chat.id, text=wariorShow.getProfile(userIAm.getTimeZone()), reply_markup=markupinline)
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)

    else:
        if privateChat:
            send_messages_big(message.chat.id, text=message.photo[len(message.photo)-1].file_id)
    
# Handle sticker
@bot.message_handler(content_types=["sticker"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то стикернуть, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
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
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то настримить, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return

# Handle voice
@bot.message_handler(content_types=["location"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то рассказать про свою локацию, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
        return

# Handle voice
@bot.message_handler(content_types=["voice"])
def get_message_stiker(message):
    #write_json(message.json)
    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        send_messages_big(message.chat.id, text=f'{message.from_user.username} хотел что-то наговорить, но у него получилось лишь:\n' + getResponseDialogFlow(message.from_user.username, 'user_banned').fulfillment_text)
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

# Handle all other messages
@bot.message_handler(func=lambda message: True, content_types=['text'])
def main_message(message):
    # message.from_user.username = "Brodskey"
    # write_json(message.json)
    chat = message.chat.id
    privateChat = ('private' in message.chat.type)
    logger.info(f'chat:{message.chat.id}:{"private" if privateChat else "Group"}:{message.from_user.username}:{datetime.fromtimestamp(message.forward_date) if message.forward_date else ""}:{message.text}')
    if message.from_user.username == None: return
    
    # Проверка на присутствие в черном списке
    black_list = getSetting(code='BLACK_LIST', name=message.from_user.username)
    if black_list:
        send_messages_big(message.chat.id, text=f'{message.from_user.username} заслужил пожизненный бан {black_list}', reply_markup=None)
        send_message_to_admin(f'⚠️Внимание! \n {message.from_user.username} написал Джу:\n\n {message.text}')
        return

    check_and_register_tg_user(message.from_user.username)
    userIAm = getUserByLogin(message.from_user.username)

    if not privateChat and userIAm and isGoatInfoChat(message.from_user.username, message.chat.id):
        # Собрали группу бандитов
        may_be_cured_or_infected = []
        may_be_cured_or_infected.append(message.from_user.username)
        if message.reply_to_message and not message.reply_to_message.from_user.is_bot:
            may_be_cured_or_infected.append(message.reply_to_message.from_user.username)

        # Определили заражение
        checkInfected(may_be_cured_or_infected, message.chat.id)
        # Заражаем бандитов
        infect(may_be_cured_or_infected, message.chat.id)
        # Определили способных лечить
        checkCure(may_be_cured_or_infected, message.chat.id)
        # лечим бандитов
        cure(may_be_cured_or_infected, message.chat.id)

    if isUserBan(message.from_user.username):
        bot.delete_message(message.chat.id, message.message_id)
        user = getUserByLogin(message.from_user.username)
        name = message.from_user.username
        if user:
            name = user.getName()
        send_messages_big(message.chat.id, text=f'{name} хотел что-то сказать, но у него получилось лишь:\n{getResponseDialogFlow(message.from_user.username, "user_banned").fulfillment_text}' )
        return
    
    callJugi = (privateChat or message.text.lower().startswith('джу') or (message.reply_to_message and message.reply_to_message.from_user.is_bot and message.reply_to_message.from_user.username in ('FriendsBrotherBot', 'JugiGanstaBot') ))
    findUser = not (userIAm == None)

    # Форварды от Рупора Пустоши
    if message.forward_from_chat and (message.forward_from_chat.username == 'wwkeeperhorn' or message.forward_from_chat.username == 'tolyIya') and ' постиг ' in message.text:
        # ⚙️Машенька постиг 8-й 🏵Дзен !
        name = message.text.split(' постиг ')[0]
        name = name.replace('⚙️', '#@#').replace('🔪', '#@#').replace('💣', '#@#').replace('⚛️', '#@#').replace('👙', '#@#').replace('🔰', '#@#')
        name = name.split('#@#')[1].split('постиг')[0].strip()
        num_dzen = int(message.text.split(' постиг ')[1].split('-й')[0])
        fraction = getWariorFraction(message.text)
        # acc = f'🏵️ Грамота за {num_dzen}-й Дзен' 
        user = getUserByName(name)
        if user:
            dzen_rewards(user, num_dzen, message)
            return

    # Форварды от WastelandWarsBot
    if (message.forward_from and message.forward_from.username == 'WastelandWarsBot'):
        time_over = message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp()
        # Вычисление коэффициента времени фарма
        farm_k = 0
        if userIAm:
            for thing in userIAm.getInventoryType(['things']):
                try:
                    if 'skill' in thing and 'storage' in thing['skill'] and thing['skill']['storage']['id'] == 'watchmaker':
                        skill = userIAm.getInventoryThing({'id':'watchmaker','type':'skill'})
                        if skill == None:
                            skill = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']==thing['skill']['storage']['id']), None) 

                        storage = skill['storage'] + thing['skill']['storage']['value'] 
                        if storage >= skill['min']:
                            power_skill = (storage - skill['min'])/(skill['max'] - skill['min'])
                            farm_k = int(power_skill * 10 / 1)
                            logger.info(f'Коэффициент времени фарма: +{farm_k} мин.')
                        newValue = thing['wear']['value'] - thing['wear']['one_use']
                        if newValue < 0:
                            userIAm.removeInventoryThing(thing)
                            text = f'{user.getNameAndGerb()}, у тебя испортилась вещь из инвентаря:\n▫️ {thing["name"]}'
                        else:
                            thing['wear'].update({'value': newValue})
                        updateUser(userIAm)
                except:
                    traceback.print_exc()
        time_farm_over = message.forward_date < (datetime.now() - timedelta(minutes= 5+farm_k)).timestamp()

        if (message.text.startswith('📟Пип-бой 3000')):
            if ('/killdrone' in message.text or 
                'ТОП ФРАКЦИЙ' in message.text or 
                'СОДЕРЖИМОЕ РЮКЗАКА' in message.text or 
                'ПРИПАСЫ В РЮКЗАКЕ' in message.text or 
                '🏆ТОП КОЗЛОВ:' in message.text or
                'РЕСУРСЫ и ХЛАМ' in message.text or
                '🔧РЕСУРСЫ И ХЛАМ' in message.text or
                '🏆ТОП МАГНАТОВ' in message.text):
                return

            if 'ТОП ИГРОКОВ:' in message.text:
                filter_message = {"forward_date": message.forward_date, "forward_from_username": message.forward_from.username, 'text': message.text}
                new_Message = messager.new_message(message, filter_message)

                if new_Message:
                    if time_farm_over:
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text)
                        return

                    ww = wariors.fromTopToWariorsBM(message.forward_date, message, registered_wariors)
                    countLearnSkill = 0
                    for warior in ww:
                        res = update_warior(warior)
                        # logger.info(f'{res} : {warior.getName()}')
                        if warior.getName() == userIAm.getName() and warior.getFraction() == userIAm.getFraction():
                            pass #logger.info(f'Это Я, пропускаем')
                        else: 
                            if res['bm_update']:
                                logger.info(f'Обновился BM {res} : {warior.getName()}')
                                countLearnSkill = countLearnSkill + 1

                    # Учимся умению "Экономист"
                    logger.info(f'Обновился BM у {countLearnSkill} бандитов')
                    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='economist'), None)
                    if countLearnSkill > 0:
                        check_skills(None, message.chat.id, False, userIAm, elem, counterSkill=countLearnSkill)
                    else:
                        send_messages_big(chat, text=getResponseDialogFlow(None, elem["dialog_old_text"]).fulfillment_text)
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
                else:
                    send_messages_big(chat, text=getResponseDialogFlow(message.from_user.username, 'duplicate').fulfillment_text) 
                return

            if time_over:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text)
                return

            user = users.User(message.from_user.username, message.forward_date, message.text)
            if findUser==False:  
                if 'Подробности /me' in message.text or (not privateChat): 
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'pip_me').fulfillment_text)
                    return
                else:
                    # bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_2'), None)

                    elem = random.sample(getSetting(code='ACCESSORY_ALL', id='PIP_BOY')["value"], 1)[0]
                    user.setChat(message.chat.id)
                    addInventory(user, elem)
                    user.setPing(True)

                    newRank = None
                    for rank in getSetting(code='RANK', id='MILITARY')['value']:
                        if rank['bm'] < user.getBm():
                            newRank = rank  
                    user.setRank(newRank)
                    dzen_rewards(user, user.getDzen(), message)

                    x = registered_users.insert_one(json.loads(user.toJSON()))
                    updateUser(None)

                    send_messages_big(message.chat.id, text=f'Поздравляю! \nТебе выдали {elem["name"]} и вытолкнули за дверь!')
                    send_message_to_admin(f'👤 Новый пользователь:\n{user.getProfile()}')
            else:
                updatedUser = users.updateUser(user, users.getUser(user.getLogin(), registered_users))
                dzen_rewards(updatedUser, updatedUser.getDzen(), message)
                updateUser(updatedUser)
            addToUserHistory(user)
            if privateChat:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'setpip').fulfillment_text)
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
            
            return
        elif ('FIGHT!' in message.text):
            filter_message = {"forward_date": message.forward_date, "forward_from_username": message.forward_from.username, 'text': message.text}
            new_Message = messager.new_message(message, filter_message)
            if new_Message:                     
                ww = wariors.fromFightToWarioirs(message.forward_date, message, USERS_ARR, battle)
                # Переделать так, чтобы учитывало, что может быть два бойца из нашего козла.
                # Выдавать только за свои бои.

                ourBandUser = None
                for warior in ww:
                    if ourBandUser == None:
                        ourBandUser = getUserByName(warior.getName())
                    update_warior(warior)
            
                if ourBandUser:
                    
                    if ourBandUser.getLogin() == message.from_user.username:
                        # Учимся умению "Боец"
                        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='fighter'), None)
                        check_skills(None, message.chat.id, False, userIAm, elem, counterSkill=1)

                    for w in battle.find({
                        # 'login': message.from_user.username, 
                        'date': message.forward_date}):
                        if w['winnerWarior'] == ourBandUser.getName():
                            for war in ww:
                                # Вручаем скальп за машинку
                                if war.getName() == w['loseWarior']:
                                    loser = getWariorByName(war.getName(), war.getFraction())

                                    if loser:
                                        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']=='scalp_of_banditos'), None).copy() 
                                        k = 1
                                        if loser.getGoat():
                                            k = 2
                                            if loser.getGoat() == 'Δeus Σx Machina':
                                                elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']=='scalp_deus'), None).copy() 
                                                k =3
                                        if loser.getName() == '{^_^}': 
                                            elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']=='scalp_of_zak'), None).copy() 
                                            k = 5

                                        if loser.getName() == 'Очко гуся': 
                                            elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']=='scalp_goose'), None).copy() 
                                            k = 4

                                        if loser.getName() == 'Fateev': 
                                            elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']=='scalp_ass'), None).copy() 
                                            k = 4

                                        elem.update({"cost": elem["cost"] * k})

                                        if addInventory(ourBandUser, elem):
                                            updateUser(ourBandUser)
                                            send_messages_big(message.chat.id, text = f'Тебе выдали:\n▫️ {elem["name"]} 🔘{elem["cost"]}') 
                                        else:
                                            send_messages_big(message.chat.id, text=ourBandUser.getNameAndGerb() + '!\n' + getResponseDialogFlow(message.from_user.username, 'new_accessory_not_in_stock').fulfillment_text + f'\n\n▫️ {elem["name"]} 🔘{elem["cost"]}') 

                            if (random.random() <= float(getSetting(code='PROBABILITY', name='YOU_WIN'))):
                                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_SALUTE'), 1)[0]['value'])
                        else:
                            if (random.random() <= float(getSetting(code='PROBABILITY', name='YOU_LOSER'))):
                                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_CRY'), 1)[0]['value'])
                        break
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
            else:
                send_messages_big(chat, text=getResponseDialogFlow(message.from_user.username, 'duplicate').fulfillment_text) 

            return
        elif ( len([ele for ele in GLOBAL_VARS['eating_in_new_rino'] if(ele in message.text)])>0):
            #write_json(message.json)
            if hasAccessToWariors(message.from_user.username):
                fraction = getWariorFraction(message.text)
                name = message.text
                name = name.replace('⚙️', '#@#').replace('🔪', '#@#').replace('💣', '#@#').replace('⚛️', '#@#').replace('👙', '#@#').replace('🔰', '#@#')
                for fr in GLOBAL_VARS['eating_in_new_rino']:
                    if fr in message.text:
                        name = name.split('#@#')[1].split(fr)[0].strip()
                name = tools.deEmojify(name)
                warior = getWariorByName(name, fraction)

                if warior == None:
                    send_messages_big(message.chat.id, text='Ничего о нем не знаю!')
                elif (warior and warior.photo):
                    bot.send_photo(message.chat.id, warior.photo, warior.getProfile(userIAm.getTimeZone()))
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile(userIAm.getTimeZone()))
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            return
        elif ('Тренировки не прошли даром:' in message.text and 'Ты забрал часть его припасов' in message.text):
            #write_json(message.json)
            if hasAccessToWariors(message.from_user.username):

                warior = None
                fractions =                [ele for ele in GLOBAL_VARS['eating_in_new_rino'] if(ele in message.text)]                        
                for s in message.text.split('\n'):
                    if s.startswith('Ты забрал часть его припасов у 👤'):
                        fraction = getWariorFraction(s)
                        name = s.split('Ты забрал часть его припасов у 👤')[1].split(' из ' + fraction)[0].strip()
                        name = tools.deEmojify(name)
                        warior = getWariorByName(name, fraction)
                        break

                if warior == None:
                    send_messages_big(message.chat.id, text='Ничего о нем не знаю!')
                elif (warior and warior.photo):
                    bot.send_photo(message.chat.id, warior.photo, warior.getProfile(userIAm.getTimeZone()))
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile(userIAm.getTimeZone()))
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            return
        elif ('Рядом с тобой другой выживший.' in message.text and 'Для ответа используй' in message.text):
            #write_json(message.json)
            if hasAccessToWariors(message.from_user.username):
                warior = getWariorByName(message.text.split(':')[0].strip(), None)

                if warior == None:
                    send_messages_big(message.chat.id, text='Ничего о нем не знаю!')
                elif (warior and warior.photo):
                    bot.send_photo(message.chat.id, warior.photo, warior.getProfile(userIAm.getTimeZone()))
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile(userIAm.getTimeZone()))
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            return
        elif ('/accept' in message.text and '/decline' in message.text):
            #write_json(message.json)
            if hasAccessToWariors(message.from_user.username):
                fraction = getWariorFraction(message.text.split(' из ')[1].strip())
                warior = getWariorByName(message.text.split('👤')[1].split(' из ')[0], fraction)

                if warior == None:
                    send_messages_big(message.chat.id, text='Ничего о нем не знаю!')
                elif (warior and warior.photo):
                    bot.send_photo(message.chat.id, warior.photo, warior.getProfile(userIAm.getTimeZone()))
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile(userIAm.getTimeZone()))
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            return
        elif ('Ты оценил обстановку вокруг.' in message.text and 'Рядом кто-то есть.' in message.text):
            #write_json(message.json)

            if hasAccessToWariors(message.from_user.username):
                goat_bands = getGoatBands(getMyGoatName(message.from_user.username))
                k_bm = []
                bm = []
                for user in list(filter(lambda x : x.getBand() in goat_bands, USERS_ARR)):
                    k_bm.append(user.getHealth()/user.getBm())
                    userBm = user.getBm()
                    if userBm and userBm > 0:
                        bm.append(user.getBm())                
                average_k_bm =(sum(k_bm)/len(k_bm))
                average_bm =int(sum(bm)/len(bm))

                # 🚷/👣52 км.
                message.text = message.text + f'{userIAm.getFractionSmall()}{userIAm.getName()} | 👤\n'
                strings = message.text.split('\n')
                i = 0
                find = False
                report = ''
                counter = 0
                report_goat_info = ''
                goats = []
                km = 0
                dark_zone = False
                user_in_dark_zone = []

                goat_wild = {}
                wild_goat = 'Дикие бандиты'
                goat_wild.update({'counter': 0})
                goat_wild.update({'bm': 0})
                goat_wild.update({'name': wild_goat})
                wariors_arr = []
                goat_wild.update({'wariors':wariors_arr})
                goats.append(goat_wild)
                km = ""

                findwariors = {}

                for s in strings:
                    if ('👣' in s or '🚷' in s) and ' км' in s:
                        km = f'<b>{s}</b>\n'
                        report_goat_info = report_goat_info + km
                    if s.startswith('🚷'):
                        dark_zone = True
                    if '|' in strings[i]:
                        name = strings[i]
                        fraction = getWariorFraction(strings[i])
                        name = name.replace('⚙️', '#@#').replace('🔪', '#@#').replace('💣', '#@#').replace('⚛️', '#@#').replace('👙', '#@#').replace('🔰', '#@#')
                        name = name.split('#@#')[1].split('|')[0].strip()
                        name = tools.deEmojify(name)
                        warior = getWariorByName(name, fraction)
                        atac_ref = strings[i].split('| 👤')[1].split(';')[0].strip().replace('u_', 'p_')
                        
                        user = getUserByName(name)
                        if user and (not user.getFraction() == fraction):
                            user == None

                        if user:
                            
                            if dark_zone and (not time_over) and (not userIAm.getLogin()==user.getLogin()) and (not privateChat) :
                                user_in_dark_zone.append(user.getLogin())  
                            # Обновляем Bm у нашего бойца                            
                            if warior:
                                warior.setBm(user.getBm())
                                warior.setKills(0)
                                warior.setMissed(0)
                                warior.setHithimself(0)
                                update_warior(warior)

                        if warior:
                            if not user or (not getMyGoatName(user.getLogin()) == getMyGoatName(userIAm.getLogin())): 
                                findwariors.update({warior.getName(): atac_ref})
                            if warior.getGoat():
                                findGoat = False
                                for g in goats:
                                    if g['name'] == warior.getGoat():
                                        g.update({'counter': g['counter']+1})
                                        wariors_arr = g['wariors']
                                        wariors_arr.append(warior)
                                        g.update({'wariors': wariors_arr})
                                        bm = g['bm'] + warior.getBm(average_k_bm, average_bm)
                                        g.update({'bm': bm})
                                        findGoat = True
                                
                                if not findGoat:
                                    g = {}
                                    g.update({'counter': 1})
                                    g.update({'name': warior.getGoat()})
                                    wariors_arr = []
                                    wariors_arr.append(warior)
                                    g.update({'wariors': wariors_arr})
                                    bm = warior.getBm(average_k_bm, average_bm)
                                    g.update({'bm': bm})                                    
                                    goats.append(g)
                            else:
                                for g in goats:
                                    if g['name'] == wild_goat:
                                        g.update({'counter': g['counter']+1})
                                        wariors_arr = g['wariors']
                                        wariors_arr.append(warior)
                                        g.update({'wariors': wariors_arr})
                                        bm = g['bm'] + warior.getBm(average_k_bm, average_bm)
                                        g.update({'bm': bm})     


                            find = True
                            # report = report + f'{warior.getProfileSmall()}\n'
                        else:
                            counter = counter + 1    
                    if '...И еще' in strings[i]:
                        live = int(strings[i].split('...И еще')[1].split('выживших')[0].strip())
                        counter = counter + live
                    i = i + 1

                    buttons = []
                    for d in user_in_dark_zone:
                        buttons.append(InlineKeyboardButton(f'@{d}', callback_data=f"ping_user|{d}"))

                    markupinline = InlineKeyboardMarkup(row_width=2)
                    for row in build_menu(buttons=buttons, n_cols=2):
                        markupinline.row(*row)   

                # logger.info(goats)

                if len(goats) > 0:
                    for goat in list(filter(lambda x : len(x['wariors']) > 0, goats)):
                        emoji = '🐐 '
                        if goat['name'] == wild_goat:
                            emoji = ''
                        report_goat_info = report_goat_info + f'{emoji}<b>{goat["name"]}</b>: <b>{goat["counter"]}</b>\n\n'
                        for w in sorted(goat['wariors'], key = lambda i: i.getBm(average_k_bm, average_bm), reverse=True):
                            report_goat_info = report_goat_info + f'{w.getProfileVerySmall()}'
                            if w.getName() in findwariors: 
                                report_goat_info = report_goat_info + f'    <a href="http://t.me/share/url?url={findwariors[w.getName()]}">🔪Напасть</a>\n\n'
                                # report_goat_info = report_goat_info + f'    <a href="https://t.me/FriendsBrotherBot/url={findwariors[w.getName()]}">🔪Напасть</a>\n\n'
                            else:
                                report_goat_info = report_goat_info + '\n'

                    report_goat_info = report_goat_info + '\n'

                    report_goat_info = report_goat_info + f'{km}'
                    for goat in sorted(list(filter(lambda x : len(x['wariors']) > 0, goats)), key = lambda i: i['bm'], reverse=True):
                        emoji = '🐐 '
                        if goat['name'] == wild_goat:
                            emoji = ''
                        kubik = '▫️' 
                        if goat['name'] == getMyGoatName(message.from_user.username):
                            kubik = '▪️'
                        report_goat_info = report_goat_info + f'{kubik} {emoji}<b>{goat["name"]}</b>: <b>{goat["counter"]}</b> 📯{goat["bm"]}\n'


                if counter > 0:
                    report_goat_info = report_goat_info + f'...И еще <b>{str(counter)}</b> выживших.'

                if not find:
                    send_messages_big(message.chat.id, text='Не нашел никого!')
                else:
                    send_messages_big(message.chat.id, text=report + report_goat_info, reply_markup=markupinline)
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            return
        elif ('Ты либо очень смел, либо очень глуп, раз переступил порог ⚡️Купола Грома.' in message.text):
            if hasAccessToWariors(message.from_user.username):

                strings = message.text.split('\n')
                start = False
                report = ''

                for s in strings:
                    if 'Сейчас Купол Грома пуст, но ты можешь позвать сюда кого-нибудь из своих знакомых' in message.text:
                        break

                    if start: 
                        if s.startswith('⚔️'):
                            continue

                        fraction = s.split('(')[1].split(')')[0].strip()
                        pref = ''
                        band = ''
                        if '(Без банды' in s:
                            pref = '(Без банды'
                        elif '🤘' in s:
                            pref = '🤘'
                            band = s.split('🤘')[1].strip()
                        name = s.split(')')[1].split(pref)[0].strip()
                        fraction_full = getWariorFraction(fraction)
                        warior = getWariorByName(name, fraction_full)
                        if warior:
                            report = report + f'{warior.getProfileSmall()}\n'
                        else:
                            if band == '':
                                report = report + f'┌{fraction} {name}\n└...\n'
                            else:
                                report = report + f'┌{fraction} {name}\n├🤘{band}\n└...\n'
                            
                    
                    if 'ТОП Купола /tdtop' in s:
                        start = True
                if report == '':
                    send_messages_big(message.chat.id, text='Никого не нашел!')
                else:
                    report = '<b>⚡️Купола Грома.</b>\n\n' + report
                    send_messages_big(message.chat.id, text=report)
            return
        # elif ('Ты уже записался.' in message.text):
            # #write_json(message.json)
            # if hasAccessToWariors(message.from_user.username):
            #     if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
            #         send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text)
            #         return

            #     u = getUserByLogin(message.from_user.username)
            #     u.setRaidLocation(1)
            #     updateUser(u)
            #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
            # else:
            #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            # return
        elif ('Ты занял позицию для ' in message.text and 'Рейд начнётся через' in message.text):
            #write_json(message.json)
            if hasAccessToWariors(message.from_user.username):
                
                filter_message = {"username": message.from_user.username, "forward_date": message.forward_date, "forward_from_username": message.forward_from.username, 'text': message.text}
                new_Message = messager.new_message(message, filter_message)                
                if not new_Message:
                    send_messages_big(chat, text=getResponseDialogFlow(message.from_user.username, 'duplicate').fulfillment_text) 
                    return

                # if message.forward_date < (datetime.now() - timedelta(minutes=30)).timestamp():
                #     #send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text)
                #     send_messages_big(message.chat.id, text='Шли мне свежее сообщение "Ты уже записался."')
                #     return

                # if '7ч.' in message.text.split('Рейд начнётся через ⏱')[1]:
                #     send_messages_big(message.chat.id, text='Это захват на следующий рейд. Сбрось мне его позже!')
                #     return

                user = getUserByLogin(message.from_user.username)
                user.setRaidLocation(1)

                try:
                    ticket = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']=='redeemed_raid_ticket'), None)             
                    date_stamp = getRaidTimeText(message.text.split("Рейд начнётся через ⏱")[1], message.forward_date)
                    date_str = time.strftime("%d.%m %H:%M", time.gmtime( date_stamp ))
                    addInventory(user, ticket)
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text + 
                        f'\nВ специальном паркомате на рейдовой точке ты взял талончик на рейд:\n▫️  {ticket["name"]} {date_str}')
                    tz = config.SERVER_MSK_DIFF
                    date_stamp = (datetime.fromtimestamp(date_stamp) - timedelta(hours=tz.hour)).timestamp()
                    saveUserRaidResult(user, date_stamp, 1)

                except:
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
                    send_message_to_admin(f'⚠️🤬 {message.from_user.username}\nСломался "Ты занял позицию"!')

                updateUser(user)
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            return
        elif ('Панель банды.' in message.text):
            #write_json(message.json)
            if hasAccessToWariors(message.from_user.username):
                if message.forward_date < (datetime.now() - timedelta(minutes=1)).timestamp():
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text)
                    return 

                raidDate = getRaidTimeText("", message.forward_date)
                logger.info(f'Панель банды от {message.forward_date}: {datetime.fromtimestamp(message.forward_date)}.\nВремя следующего рейда: {datetime.fromtimestamp(raidDate)}')
                tz = config.SERVER_MSK_DIFF
                

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
                        
                        if not isPowerUser(message.from_user.username):
                            if not isUsersBand(message.from_user.username, band):
                                send_messages_big(message.chat.id, text=f'Ты принес панель банды {band}\n' + getResponseDialogFlow(message.from_user.username, 'not_right_band').fulfillment_text)
                                return

                    if '👂' in strings[i]:
                        name = strings[i]
                        name = name.replace('⚙️', '#@#').replace('🔪', '#@#').replace('💣', '#@#').replace('⚛️', '#@#').replace('👙', '#@#').replace('🔰', '#@#')
                        name = name.split('#@#')[1].split('👂')[0].strip()
                        u = getUserByName(name)

                        if u and (not u.getBand() == band):
                            u.setBand(band)
                            logger.info(f'change band: {band}')

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
                                saveUserRaidResult(u, (datetime.fromtimestamp(raidDate) - timedelta(hours=tz.hour)).timestamp(), km)

                            else:
                                fuckupraidrw = fuckupraidrw + u.getRaidWeight()
                                fuckupusers.append(u)
                                u.setRaidLocation(0)
                                saveUserRaidResult(u, (datetime.fromtimestamp(raidDate) - timedelta(hours=tz.hour)).timestamp(), 0)
                            updateUser(u)
                        else:
                            aliancounter  = aliancounter + 1
                            alianusersReport = alianusersReport + f'{aliancounter}. {name} {spliter}{km}км\n'
                    i = i + 1

                send_message_to_admin(f'🤘 Панель банды <b>{band}</b>\n▫️ {getUserByLogin(message.from_user.username).getNameAndGerb()}\n▫️ {message.forward_date}: {datetime.fromtimestamp(message.forward_date)}\n▫️ ⏰ Время рейда: {datetime.fromtimestamp(raidDate)}')
                report = report + f'🤘 <b>{band}</b>\n\n' 
                if onraidcounter > 0:
                    report = report + f'🧘‍♂️ <b>на рейде</b>: <b>{onraidcounter}/{allcounter}</b>\n'
                    i = 1
                    for onu in sorted(onraidusers, key = lambda i: i.getRaidWeight(), reverse=True):
                        report = report +  f'{i}.{onu.getFraction()[0:1]}{onu.getRaidWeight()} {onu.getNameAndGerb()} 👊{onu.getRaidLocation()}км\n'
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
                   censored(message)
            else:
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
            return
        elif ((message.text.startswith('Теперь') and 'под контролем' in message.text) or (message.text.startswith('✊️Захват') and ('Захват начался!' in message.text or 'Вы автоматически отправитесь на совместную зачистку локации' in message.text))):
            if message.forward_date < (datetime.now() - timedelta(minutes=5)).timestamp():
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text)
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
                text = text + f'  {i}. <b>{user.getNameAndGerb()}</b>\n'
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
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
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
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
            else:
                markupinline = InlineKeyboardMarkup()
                
                for date in date_arr:
                    dt = datetime.fromtimestamp(date)
                    markupinline.add(
                        InlineKeyboardButton(f"{dt.hour}:{d.minute}", callback_data=f"commit_dungeon_time|{dt.timestamp()}|{band}|{dungeon_km}"),
                        InlineKeyboardButton(f"Готово ✅", callback_data=f"commit_dungeon_yes|{dt.timestamp()}|{band}|{dungeon_km}"),
                        InlineKeyboardButton(f"Закрыть ⛔", callback_data=f"commit_dungeon_no|{dt.timestamp()}|{band}|{dungeon_km}")
                    )
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text, reply_markup=markupinline)
        elif (message.text.startswith('ХОД БИТВЫ:') or 'Ты присоединился к группе, которая собирается атаковать' in message.text or message.text.startswith('Победа!') or (message.text.startswith('⚜️Боссы.') and '❌Нацарапать крестик' in message.text)):
            if hasAccessToWariors(message.from_user.username):
        
                if userIAm == None:
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'no_user').fulfillment_text) 
                    return

                if userIAm.getTimeUpdate() < (datetime.now() - timedelta(days=30)).timestamp():
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'update_pip').fulfillment_text) 
                    return

                if message.forward_date < (datetime.now() - timedelta(days=1)).timestamp():
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'old_forward').fulfillment_text) 
                    return
                    
                counter = 0
                onboss = 0
                health = 0
                damage = []
                beaten = []
                killed = []
                kr = []
                mat = []
                name = ''
                forward_date = [message.forward_date]
                if message.text.startswith('Победа!'):
                    for s in message.text.split('\n'):
                        if s.startswith('🔥'):
                            name = s.split('🔥')[1].split('(')[0].strip()
                        if s.startswith('Получено:') and '🕳' in s and '📦' in s:
                            kr = [int(s.split('🕳')[1].split(' ')[0].strip())]
                            mat = [int(s.split('📦')[1].strip())]
                        if s.startswith('💀'):
                            killed.append(s.split('💀')[1].strip())
                    onboss = 0
                elif (message.text.startswith('⚜️Боссы.') and '❌Нацарапать крестик' in message.text):
                    name = message.text.split('\n')[3].strip()
                    onboss = int(message.text.split('\n')[7].split('/')[0].strip())
                elif 'Ты присоединился к группе, которая собирается атаковать' in message.text:
                    name = message.text.split('Ты присоединился к группе, которая собирается атаковать')[1].split('.')[0].strip()
                    onboss = 4 - int(message.text.split('Для битвы нужно еще')[1].split('человек')[0].strip())
                elif message.text.startswith('ХОД БИТВЫ:'):
                    for s in message.text.split('\n'):
                        counter = counter + 1
                        if counter == 2 and not (s == ''):
                            return
                        if counter >=3:
                            if '❤️' in s and health == 0:
                                health = int(s.split('❤️')[1].strip())
                                name = s.split('❤️')[0].strip()
                            if '💔-' in s:
                                beaten.append(int(s.split('💔-')[1].strip()))
                            if '💥' in s:
                                damage.append(int(s.split('💥')[1].strip())) 
                            if '☠️' in s:
                                killed.append(s.split('☠️')[1].strip())
                    onboss = 0

                if name == '':
                    pass
                else:
                    dublicate = False
                    row = {}
                    row.update({'date': message.forward_date})
                    row.update({'boss_name': name})
                    row.update({'health': health})
                    row.update({'damage': damage})
                    row.update({'beaten': beaten})
                    row.update({'killed': killed})
                    row.update({'kr': kr})
                    row.update({'mat': mat})
                    row.update({'onboss': onboss})
                    row.update({'forward_date': forward_date})
                    

                    for bo in boss.find({'boss_name': name}):
                        if bo['date'] > row['date']:
                            row.update({'date': bo['date']})
                        
                        if row['health'] > bo['health']:
                            pass
                        else:
                            row.update({'health': bo['health']})

                        damage = bo['damage'] + damage
                        row.update({'damage': damage})

                        beaten = bo['beaten'] + beaten
                        row.update({'beaten': beaten})
                        
                        killed = bo['killed']+ killed
                        row.update({'killed': killed})
                        
                        kr = bo['kr'] + kr
                        row.update({'kr': kr})
                        
                        mat = bo['mat']+ mat
                        row.update({'mat': mat})

                        if message.forward_date in bo['forward_date']:
                            pass
                            dublicate = True
                        else:
                            forward_date = bo['forward_date'] + forward_date
                            row.update({'forward_date': forward_date})

                    if not dublicate:
                        newvalues = { "$set": row }
                        result = boss.update_one({
                            'boss_name': name
                            }, newvalues)
                        #logger.info(f'UPDATE {newvalues}')
                        if result.matched_count < 1:
                            boss.insert_one(row)
                            #logger.info(f'insert_one {row}')

                    dresult = boss.aggregate([ 
                        {   "$group": {
                            "_id": { "boss_name":"$boss_name" }, 
                            "count": {
                                "$sum": 1}}},
                            
                        {   "$sort" : { "count" : -1 } }
                        ])
                    
                    buttons = []
                    for d in sorted(dresult, key = lambda i: tools.deEmojify(i["_id"]["boss_name"]), reverse=False):
                        boss_name = d["_id"]["boss_name"] 
                        #if boss_name == name: continue
                        hashstr = getMobHash(boss_name, 'boss')
                        boss_name_small = boss_name
                        for n_boss in GLOBAL_VARS['bosses']:
                            boss_name_small = boss_name_small.replace(n_boss, '') 
                        buttons.append(InlineKeyboardButton(boss_name_small, callback_data=f"boss_info|{hashstr}"))

                    markupinline = InlineKeyboardMarkup(row_width=3)
                    for row in build_menu(buttons=buttons, n_cols=3):
                        markupinline.row(*row)   


                    #if privateChat or isGoatSecretChat(message.from_user.username, message.chat.id):
                    report = getBossReport(name)
                    send_messages_big(message.chat.id, text=report, reply_markup=markupinline)
                    #else:
                    #    send_messages_big(message.chat.id, text=getResponseDialogFlow(message, 'shot_message_zbs').fulfillment_text)

                if name == '':
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
            return
        elif ('❤️' in message.text and '🍗' in message.text and '🔋' in message.text and '👣' in message.text) or ('Экзекутос предатель, Рагнароса разбудили слишком рано, насекомое победило, правосудие свершилось. Хорошо, что никто не руинил и ты успел победить до того, как Рагна упал сам.' in message.text):
            if hasAccessToWariors(message.from_user.username):
                if not time_over:
                    # сохраняем км, если он больше максимального
                    if '👣' in message.text: 
                        km = int(message.text.split('👣')[1].split('км')[0])
                        if userIAm.getMaxkm() < km:
                            userIAm.setMaxkm(km)
                            updateUser(userIAm)
                filter_message = {"forward_date": message.forward_date, "forward_from_username": message.forward_from.username, 'text': message.text}
                new_Message = messager.new_message(message, filter_message) 
                if new_Message:

                    # Учимся умению "⏰ Часовщик"
                    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='watchmaker'), None).copy()
                    check_skills(message.text, message.chat.id, time_farm_over, userIAm, elem)
                    # Учимся умению "Робототехник"
                    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='robotics'), None).copy()
                    check_skills(message.text, message.chat.id, time_farm_over, userIAm, elem)
                    # Учимся умению "Электрик"
                    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='electrician'), None).copy()
                    check_skills(message.text, message.chat.id, time_farm_over, userIAm, elem)
                    # Учимся умению "Программист"
                    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='programmer'), None).copy()
                    check_skills(message.text, message.chat.id, time_farm_over, userIAm, elem)
                     # Учимся умению "Медик"
                    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None).copy()
                    check_skills(message.text, message.chat.id, time_farm_over, userIAm, elem)

                    for inv in list(filter(lambda x : 'subjects_to_find' in x, GLOBAL_VARS['inventory'])):
                        check_things(message.text, message.chat.id, time_farm_over, userIAm, inv.copy())


                
                else:
                    send_messages_big(chat, text=getResponseDialogFlow(message.from_user.username, 'duplicate').fulfillment_text) 


                if 'Во время вылазки на тебя напал' in message.text:
                    if userIAm == None:
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'no_user').fulfillment_text) 
                        return

                    strings = message.text.split('\n')
                    mob_name = ''
                    mob_class = ''
                    dark_zone = False
                    for s in strings:
                        if s.startswith('🚷'):
                            dark_zone = True
                        if s.startswith('Во время вылазки на тебя напал'):
                            mob_name = s.split('Во время вылазки на тебя напал')[1].split('(')[0].strip()
                            mob_class = s.split('(')[1].split(')')[0].strip()
                            break

                    if mob_name == '':
                        pass
                    else:
                        report = getMobReport(mob_name, mob_class, dark_zone)
                        hashstr = getMobHash(mob_name, mob_class)
                        mobindb = getMobByHash(hashstr)
                        markupinline = None
                        if mobindb:
                            markupinline = InlineKeyboardMarkup()
                            markupinline.add(
                                InlineKeyboardButton('🔆' if dark_zone else '🚷', callback_data=f"mob_info|{hashstr}|{not dark_zone}")
                                )
                
                        send_messages_big(message.chat.id, text=report, reply_markup=markupinline)
                    return
                if 'Сражение с' in message.text:
                    if message.text.startswith('📯'):
                        return # Пропускаем мобов из данжей

                    if userIAm == None:
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'no_user').fulfillment_text) 
                        return

                    if userIAm.getTimeUpdate() < (datetime.now() - timedelta(days=30)).timestamp():
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'update_pip').fulfillment_text) 
                        return

                    if message.forward_date < (datetime.now() - timedelta(days=1)).timestamp():
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'old_forward').fulfillment_text) 
                        return

                    strings = message.text.split('\n')
                    mob_name = ''
                    mob_class = ''
                    km = int(message.text.split('👣')[1].split('км')[0])
                    kr = 0
                    mat = 0
                    health = 0
                    damage = []
                    beaten = []
                    you_win = False
                    dark_zone = False
                    for s in strings:
                        if s.startswith('👊'):
                            send_messages_big(message.chat.id, text='Это моб из митспина, не записываю...')
                            return
                        if s.startswith('🚷') or s.startswith('📯🚷'):
                            dark_zone = True
                        if s.startswith('Сражение с'):
                            mob_name = s.split('Сражение с')[1].split('(')[0].strip()
                            mob_class = s.split('(')[1].split(')')[0].strip()
                        if s.startswith('Получено:') and '🕳' in s and '📦' in s:
                            kr = int(s.split('🕳')[1].split(' ')[0].strip())
                            mat = int(s.split('📦')[1].strip())
                        if s.startswith('👤Ты') and '💥' in s:
                            damage.append(int(s.split('💥')[1].strip()))
                        if 'нанес тебе удар' in s and '💔' in s:
                            beaten.append(-1*int(s.split('💔')[1].strip()))
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
                        row.update({'dark_zone': dark_zone})
                        row.update({'kr': kr})
                        row.update({'mat': mat})
                        row.update({'bm': userIAm.getBm()})
                        row.update({'user_damage': userIAm.getDamage()})
                        row.update({'user_armor': userIAm.getArmor()})
                        row.update({'damage': damage})
                        row.update({'beaten': beaten})
                        row.update({'win': you_win})
                        row.update({'health': sum(damage) if you_win else None})
                        

                        newvalues = { "$set": row }
                        result = mob.update_one({
                            'date': message.forward_date,
                            'login': message.from_user.username, 
                            'km': km,
                            'dark_zone': dark_zone
                            }, newvalues)
                        if result.matched_count < 1:
                            mob.insert_one(row)

                        if privateChat or isGoatSecretChat(message.from_user.username, message.chat.id):
                            report = getMobReport(mob_name, mob_class, dark_zone)
                            hashstr = getMobHash(mob_name, mob_class)
                            markupinline = InlineKeyboardMarkup()
                            markupinline.add(
                                InlineKeyboardButton('🔆' if dark_zone else '🚷', callback_data=f"mob_info|{hashstr}|{not dark_zone}")
                                )
                    
                            send_messages_big(message.chat.id, text=report, reply_markup=markupinline)
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
                return
        elif (message.text.startswith('Неподалеку ты заметил другого выжившего.') or message.text.startswith('Неподалеку ты заметил какую-то потасовку.')):
            #arr = ['отдал на съедение кротокрысам', 'одержал победу над', 'не оставил живого места от', 'гордо наступил на полудохлого', 'оставил бездыханное тело', 'сделал сиротами детишек', 'добил с пинка', 'добил лежачего', 'выписал пропуск в Вальхаллу', 'добил фаталити', 'стоит над поверженным', 'одержал победу над']
            counter = 0
            name = ''
            fraction = ''
            for s in message.text.split('\n'):
                counter = counter + 1
                if counter > 1:
                    for a in GLOBAL_VARS['fight_log_message']:
                        if a in s:
                            name = s.split(a)[0].strip()
                            name = name.replace('⚙️', '#@#').replace('🔪', '#@#').replace('💣', '#@#').replace('⚛️', '#@#').replace('👙', '#@#').replace('🔰', '#@#')
                            name = name.split('#@#')[1].strip()
                            name = tools.deEmojify(name)
                            fraction = getWariorFraction(s)
                            break
            if name == '':
                pass
            else:
                warior = getWariorByName(name, fraction)
                if warior == None:
                    send_messages_big(message.chat.id, text='Ничего о нем не знаю!')
                elif (warior and warior.photo):
                    bot.send_photo(message.chat.id, warior.photo, warior.getProfile(userIAm.getTimeZone()))
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile(userIAm.getTimeZone()))
            return
        elif (message.text.startswith('Рейд в 17:00') or message.text.startswith('Рейд в 9:00') or message.text.startswith('Рейд в 01:00')):
            
            # if message.forward_date < (datetime.now() - timedelta(minutes=30)).timestamp():
            #     #send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text)
            #     send_messages_big(message.chat.id, text='Поздняк! У тебя было 30 минут, чтобы прислать это. Статистика уже собрана и отправлена в библиотеку пустоши!')
            #     return
            
            tz = config.SERVER_MSK_DIFF
            date = (datetime.fromtimestamp(message.forward_date).replace(minute=0, second=0) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp()
            raid = getPlanedRaidLocation(getMyGoatName(message.from_user.username), planRaid = False)

            if raid['rade_location']:
                if raid['rade_date'] == date:
                    u = getUserByLogin(message.from_user.username)
                    u.setRaidLocation(1)
                    updateUser(u)
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
                    return
                else:
                    send_messages_big(message.chat.id, text='К чему ты это мне прислал?')
            return   
        else:
            return 
            #send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'deceive').fulfillment_text) 
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
            if (random.random() <= float(getSetting(code='PROBABILITY', name='FINGER_TYK'))):
                bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_FINGER_TYK'), 1)[0]['value'])
                #logger.info(mem_top())
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
    if 'утречка' in message.text.lower() or 'добрым утром' in message.text.lower() or 'доброго утра' in message.text.lower() or 'доброго утречка' in message.text.lower() or 'доброе утро' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='MORNING_STICKER'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_MORNING'), 1)[0]['value'])
            return 
    if 'пойду спать' in message.text.lower() or 'я спать' in message.text.lower() or 'доброй ночи' in message.text.lower() or 'спокойной ночи' in message.text.lower() or 'спатки' in message.text.lower() or 'сладких снов' in message.text.lower() or 'добрых снов' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='NIGHT_STICKER'))):
            bot.send_sticker(message.chat.id, random.sample(getSetting(code='STICKERS', name='BOT_NIGHT'), 1)[0]['value'])
            return 
    if '🚪' in message.text.lower():
        if (random.random() <= float(getSetting(code='PROBABILITY', name='DOOR_STICKER'))):
            bot.send_photo(message.chat.id, random.sample(getSetting(code='STICKERS', name='DOOR'), 1)[0]['value'])
            return   
    #if '+' == message.text.lower() and message.reply_to_message:
        # if 'kirill_burthday' not in GLOBAL_VARS:
        #      kirill_burthday = []
        #      GLOBAL_VARS.update({'kirill_burthday':kirill_burthday})

        # if message.from_user.username not in GLOBAL_VARS['kirill_burthday']:
        #     kirill_burthday = GLOBAL_VARS['kirill_burthday']
        #     kirill_burthday.append(message.from_user.username)
        #     elem = random.sample(GLOBAL_VARS['inventory'], 1)[0]
        #     addInventory(userIAm, elem)
        #     updateUser(userIAm)
        #     send_messages_big(message.chat.id, text=userIAm.getNameAndGerb() + '!\n' + getResponseDialogFlow(message.from_user.username, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {elem["name"]}') 
        # else:
        #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'duplicate').fulfillment_text) 
        
        # for login in GLOBAL_VARS['kirill_burthday']:
        #     logger.info(f'{login} ===============')
        # return

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
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
        return
    # Рассылка в чаты
    if privateChat and isGoatBoss(message.from_user.username) and message.reply_to_message:
        if message.text.lower().startswith('рассылка в'):
            if not isGoatBoss(message.from_user.username):
                if not isAdmin(message.from_user.username):
                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
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

                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
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
            report = f'{user.getNameAndGerb()} будет выписан бан! Злой Джу определил, что ⏰{sec} секунд(ы) будет достаточно!'
            updateUser(user)
            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text + f'\n{report}')
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
            if not isPowerUser(message.from_user.username):
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
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
                        if isAdmin(message.from_user.username) or getMyGoatName(message.from_user.username) == getMyGoatName(user.getLogin()):
                            send_messages_big(message.chat.id, text=user.getProfile('All'))
                else:
                    send_messages_big(message.chat.id, text=f'В базе зарегистрированнных бандитов {login} не найден')

            for x in registered_wariors.find({'name':f'{name}'}):
                warior = wariors.importWarior(x)
                if (warior and warior.photo):
                    try:
                        bot.send_photo(message.chat.id, warior.photo, warior.getProfile(userIAm.getTimeZone()))
                    except:
                        send_messages_big(message.chat.id, text=warior.getProfile(userIAm.getTimeZone()))
                else:
                    send_messages_big(message.chat.id, text=warior.getProfile(userIAm.getTimeZone()))
        elif callJugi and ('уволить @' in message.text.lower() or 'удалить @' in message.text.lower()): 
            if not isGoatBoss(message.from_user.username):
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
                return

            login = message.text.split('@')[1].strip()
            user = getUserByLogin(login)
            if not user:
                send_messages_big(message.chat.id, text=f'Нет зарегистрированного бандита с логином {login}!')
                return

            if not isUsersBand(message.from_user.username, user.getBand()):
                if not isAdmin(message.from_user.username):
                    send_messages_big(message.chat.id, text=f'Бандит {login} не из банд твоего козла!')
                    return

            myquery = { "login": f"{user.getLogin()}" }
            doc = registered_users.delete_one(myquery)
            updateUser(None)

            if doc.deleted_count == 0:
                send_messages_big(message.chat.id, text=f'{login} не найден в бандитах!')
            else:                 
                send_messages_big(message.chat.id, text=f'{login} уволен нафиг!')
        # elif (callJugi and 'профиль' in message.text.lower() ):
            # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
            #     pass
            # else:
            #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
            #     return

            # updateUser(None)
            # user = users.getUser(message.from_user.username, registered_users)
            # if user:
            #     warior = getWariorByName(user.getName(), user.getFraction())
            #     if (warior and warior.photo):
            #         try:
            #             bot.send_photo(message.chat.id, warior.photo, user.getProfile(), parse_mode='HTML')
            #         except:
            #             send_messages_big(message.chat.id, text=user.getProfile())
            #     else:
            #         send_messages_big(message.chat.id, text=user.getProfile())
            # else:
            #     send_messages_big(message.chat.id, text='С твоим профилем какая-то беда... Звони в поддержку пип-боев!')
        elif callJugi:

            text = message.text 
            if text.lower().startswith('джу'):
                text = message.text[3:]

            result = getResponseDialogFlow(message.from_user.username, text)
            # logger.info(f'getResponseDialogFlow: {result}')
            response = result.fulfillment_text
            parameters = result.parameters
            if response:
                if (response.startswith('jugi:')):
                    #jugi:ping:Артхаус:bm
                    if 'ping' == response.split(':')[1]:
                        # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                        #     pass
                        # else:
                        #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
                        #     return

                        # Собираем всех пользоватлей с бандой Х
                        band = response.split(':')[2]
                        if response.split(":")[2] == '*':
                            band = userIAm.getBand()
                        bm = eval(response.split(":")[3])
                        if band == 'all' or bm:
                            if not isGoatBoss(message.from_user.username):
                                if not isAdmin(message.from_user.username):
                                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
                                    return
                        else:
                            if not isUsersBand(message.from_user.username, band):
                                send_messages_big(message.chat.id, text=f'Ты просил собраться банду 🤟{band}\n' + getResponseDialogFlow(message.from_user.username, 'not_right_band').fulfillment_text)
                                return

                        first_string = f'{tools.deEmojify(message.from_user.first_name)} просит собраться банду\n<b>🤟{band}</b>:\n'
                        usersarr = []

                        for registered_user in registered_users.find():
                            user = users.importUser(registered_user)
                            registered_user.update({'weight': user.getRaidWeight()})
                            registered_user.update({'bm': user.getBm()})
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
                        for pu in sorted(usersarr, key = lambda i: i['bm'], reverse=True):
                            counter = counter + 1
                            pingusers.append(pu)
                            user = getUserByLogin(pu["login"])
                            if pu["ping"] == True:
                                report = report + f'{counter}. @{pu["login"]} {user.getNameAndGerb()} {"📯"+ str(user.getBm()) if bm else ""} {"🏵"+str(user.getDzen()) if bm and user.getDzen()>0 else ""}\n'
                            else:
                                report = report + f'{counter}. 🔕{pu["login"]} {user.getNameAndGerb()} {"📯"+ str(user.getBm()) if bm else ""} {"🏵"+str(user.getDzen()) if bm and user.getDzen()>0 else ""}\n'
                            if counter % 5 == 0:
                                send_messages_big(message.chat.id, text=first_string + report)
                                pingusers = []
                                report = f''

                        if len(pingusers) > 0:
                            send_messages_big(message.chat.id, text=first_string + report)
                    elif 'letsgame' == response.split(':')[1]:
                        #jugi:letsgame:partizan
                        if response.split(":")[2] == 'partizan':
                            if not (message.from_user.username == 'Lena_Lenochka_32'):
                                #if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text='Тебе это не положено! \nПозови ЛеДонну и убери свои шаловливые руки от клавиатуры!')
                                return

                            counter = 0
                            usersarr = []
                            goat_bands = getGoatBands(getMyGoatName(message.from_user.username))
                            for user in list(filter(lambda x : x.getBand() in goat_bands, USERS_ARR)):
                                if user.isPing():
                                    if user.getSettingValue(id='partizan'):
                                        counter = counter + 1
                                        usersarr.append(user)

                            first_string = 'Бандиты с 🧠!\nСобираемся на игру!\n\n'
                            report = ''

                            if counter > 0:
                                # Пингуем
                                counter = 0
                                pingusers = []
                                report = f''
                                for user in usersarr:
                                    counter = counter + 1
                                    pingusers.append(user)
                                    if user.isPing():
                                        report = report + f'{counter}. @{user.getLogin()} {user.getNameAndGerb()}\n' 
                                    else:
                                        report = report + f'{counter}. 🔕{user.getLogin()} {user.getNameAndGerb()}\n'
                                    if counter % 5 == 0:
                                        send_messages_big(message.chat.id, text=first_string + report)
                                        pingusers = []
                                        report = f''

                                if len(pingusers) > 0:
                                    send_messages_big(message.chat.id, text=first_string + report)

                            else:
                                send_messages_big(message.chat.id, text=f'Никто не записался...')

                        else: 
                            send_messages_big(message.chat.id, text='Я не знаю игру с названием {response.split(":")[2]}')
                    elif 'need_doctor' == response.split(':')[1]:
                        # jugi:need_doctor
                        markupinline = InlineKeyboardMarkup()
                        medic = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None) 
                        
                        buttons = []
                        step = 0
                        for user in list(filter(lambda x : x.getInventoryThingCount(medic) > 0, USERS_ARR)):
                            skill = user.getInventoryThing(medic)
                            if skill['storage'] >= skill['min']:
                                buttons.append(InlineKeyboardButton(f"{user.getNameAndGerb()}", callback_data=f"need_doctor|get|{step}|{user.getLogin()}"))
                        
                        back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"need_doctor|back|{step}|{userIAm.getLogin()}|")
                        exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"need_doctor|exit|{step}|{userIAm.getLogin()}|")
                        forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"need_doctor|forward|{step}|{userIAm.getLogin()}|")

                        for row in build_menu(buttons=buttons, n_cols=3, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
                            markupinline.row(*row)  

                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text, reply_markup=markupinline)
                    elif 'setping' == response.split(':')[1]:
                        # jugi:setping:True:login
                        login = response.split(":")[3].replace('@','')
                        if login == '*':
                            login = message.from_user.username
                        else:
                            if not isGoatBoss(message.from_user.username):
                                if not isAdmin(message.from_user.username):
                                    send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
                                    return
                                    
                        user = getUserByLogin(login)
                        if not user:
                            send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                            return 
                        
                        user.setPing(response.split(":")[2] == 'True')
                        updateUser(user)
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
                    elif 'birthday' == response.split(':')[1]:
                        # jugi:birthday:2020-02-02
                        userIAm.setBirthday(parse(response.split(':birthday:')[1]).timestamp())
                        updateUser(userIAm)
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)        
                    # elif 'flex' == response.split(':')[1]:
                        # pass
                        # jugi:flex:$bool
                        # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                        #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
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

                        report = f'<b>{response.split(":")[2]}</b>\n<b>{userIAm.getNameAndGerb()}</b> выписан бан! ⏰{sec} секунд(ы) в тишине научат тебя хорошему поведению!'
                        updateUser(userIAm)

                        photo = random.sample(getSetting(code='STICKERS', name='BOT_FUCKOFF'), 1)[0]['value']
                        bot.send_sticker(message.chat.id, photo)
                        send_messages_big(message.chat.id, text=f'\n{report}')
                    elif 'planrade' == response.split(':')[1]:
                        # jugi:planrade:$date

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
                            return

                        goat = getMyGoatName(message.from_user.username)

                        tz = config.SERVER_MSK_DIFF
                        raid_date = None# (datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp()

                        # if response.split(response.split(":")[1])[1][1:].strip() == '*':
                        #     logger.info('=========1 ============')
                        #     raid_date = getPlanedRaidLocation(goat, planRaid = True)['rade_date']
                        # else:
                        #     logger.info('=========2 ============')
                        #     raid_date = parse(response.split(response.split(":")[1])[1][1:]).timestamp()
                        #     raid_date = (datetime.fromtimestamp(raid_date)).timestamp()
                        raid_date = getPlanedRaidLocation(goat, planRaid = True)['rade_date']
                        logger.info(datetime.fromtimestamp(raid_date))
                        
                        markupinline = InlineKeyboardMarkup()

                        for radeloc in plan_raids.find({
                                    'rade_date': raid_date, 
                                    'goat': goat}): 
                            markupinline.add(InlineKeyboardButton(f"{radeloc['rade_text']}", callback_data=f"capture_{radeloc['rade_location']}_{raid_date}_{goat}"))
              
                        text = get_raid_plan(raid_date, goat, message.from_user.username if privateChat else None)

                        if privateChat and isGoatBoss(message.from_user.username):
                            markupinline.add(InlineKeyboardButton(f"Раздача пинов", callback_data=f"capture_pin_{raid_date}_{goat}"))

                        msg = send_messages_big(message.chat.id, text=text, reply_markup=markupinline)
                    elif 'onrade' == response.split(':')[1]:

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
                            return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoatName(message.from_user.username)

                        if not getMyGoatName(message.from_user.username) == goatName:
                            send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
                            return

                        for goat in getSetting(code='GOATS_BANDS'):
                            if goatName == goat.get('name'):
                                report = radeReport(goat)
                                send_messages_big(message.chat.id, text=report)
                    elif 'statistic' == response.split(':')[1]:
                        # jugi:statistic:*
                        if not isGoatBoss(message.from_user.username):
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
                                return

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
                            return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoatName(message.from_user.username)

                        if not getMyGoatName(message.from_user.username) == goatName:
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
                                return

                        report = statistic(goatName)
                        send_messages_big(message.chat.id, text=report) 
                    elif 'clearrade' == response.split(':')[1]:
                        # jugi:clearrade:*
                        if not isAdmin(message.from_user.username):
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_admin').fulfillment_text)
                            return

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
                            return

                        goatName = response.split(':')[2].strip()
                        if goatName == '*':
                            goatName = getMyGoatName(message.from_user.username)

                        if not getMyGoatName(message.from_user.username) == goatName:
                            if not isAdmin(message.from_user.username):
                                send_messages_big(message.chat.id, text='Не твой козёл!\n' + getResponseDialogFlow(message.from_user.username, 'shot_you_cant').fulfillment_text)
                                return
                        registered_users.update_many(
                            {'band':{'$in':getGoatBands(goatName)}},
                            { '$set': { 'raidlocation': 0} }
                        )

                        updateUser(None)
                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)        
                    elif 'totalizator' == response.split(':')[1]:
                        # jugin:totalizator:$any
                        pass
                    elif 'pickupaccessory' == response.split(':')[1]:
                        #jugi:pickupaccessory:$any

                        if not isGoatBoss(message.from_user.username):
                            if not isAdmin(message.from_user.username):
                                bot.reply_to(message, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
                                return

                        login = response.split(':')[2].replace('@','').strip()         
                        user = getUserByLogin(login)

                        if not user:
                            send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                            return

                        markupinline = InlineKeyboardMarkup()

                        counter = 0
                        elems = []
                        for elem in user.getInventory():
                            try:
                                if elem['id'] in elems:
                                    continue
                                elems.append(elem['id'])
                                markupinline.add(InlineKeyboardButton(f"{elem['name']}", callback_data=f"pickup|{login}|{elem['id'][:100]}"))
                                counter = counter + 1 
                            except: pass
                        if counter > 0:
                            inventory_category = getSetting(code='INVENTORY_CATEGORY')
                            report = user.getInventoryReport(inventory_category)

                            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"pickup_exit|{login}"))
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, None, 'shot_message_pickupaccessory').fulfillment_text + f'\n\n{report}\nЧто изьять?', reply_markup=markupinline)
                        else:
                            msg = send_messages_big(message.chat.id, text='У него ничего нет, он голодранец!' , reply_markup=markupinline)
                    elif 'setrank' == response.split(':')[1]:
                        #jugi:setrank:$any
                        
                        # if not isGoatBoss(message.from_user.username):
                        if not isAdmin(message.from_user.username):
                            bot.reply_to(message, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_admin').fulfillment_text)
                            return

                        login = response.split(':')[2].replace('@','').strip()
                        user = getUserByLogin(login)
                        if login.lower() == 'всем':
                            send_messages_big(message.chat.id, text=f'Укажи логин бандита "@..."!')
                            return
                        else:
                            if not user:
                                send_messages_big(message.chat.id, text=f'Нет бандита с логином {login}!')
                                return

                        markupinline = InlineKeyboardMarkup()
                        counter = 10
                        i = 1
                        for rank in getSetting(code='RANK', id='MILITARY')['value']:
                            if user and user.getRankId() == rank['id']:
                                continue    

                            markupinline.add(InlineKeyboardButton(f"{rank['name']}", callback_data=f"setrank|{login}|{rank['id']}"))
                            if i == counter :
                                markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"setrank_next|{login}|{counter}"))
                                break
                            i = i + 1
                        markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"setrank_exit"))
                        if user:
                            text = f'Звание {user.getNameAndGerb()}: {user.getRankName()}'
                            msg = send_messages_big(message.chat.id, text=text, reply_markup=markupinline)
                    elif 'toreward' == response.split(':')[1]:
                        #jugi:toreward:$any:$accessory
                        
                        # if not isAdmin(message.from_user.username):
                            # bot.reply_to(message, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_admin').fulfillment_text)
                            # return


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
                            listInv = list(GLOBAL_VARS['inventory'])
                            if not isAdmin(message.from_user.username):
                                listInv = userIAm.getInventoryType(GLOBAL_VARS['typeforexcenge'])

                            checker = []
                            for elem in listInv:
                                if elem['id'] in checker:
                                    continue
                                checker.append(elem['id'])
                                if user and user.isMaxInventoryThing(elem, USERS_ARR):
                                    continue
                                # if user and user.isInventoryThing(elem):
                                #     continue    
                                s = f"toreward|{login}|{elem['id']}|{userIAm.getLogin()}"
                                if len(s)>64:
                                    logger.info(f"ERROR: callback_data more 64b: {elem['id']}")
                                    continue

                                markupinline.add(InlineKeyboardButton(f"{elem['name']}", callback_data=f"toreward|{login}|{elem['id']}|{userIAm.getLogin()}"))

                                if i == counter :
                                    markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter}|{userIAm.getLogin()}"))
                                    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))
                                    break
                                i = i + 1
                            
                            if len(listInv)<10:
                                markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))

                            if user:
                                inventory_category = [{'id':'food', 'name':'🍗 Еда'},
                                                    {'id':'decoration', 'name':'🎁 Подарки'},
                                                    {'id':'things', 'name':'📦 Вещи'}]

                                report = user.getInventoryReport(inventory_category)
                                msg = send_messages_big(message.chat.id, text=f'{user.getNameAndGerb()}:\n{report}', reply_markup=markupinline)
                            else:
                                msg = send_messages_big(message.chat.id, text=f'Всем бандитам будет выдан...' , reply_markup=markupinline)

                        else:
                            send_messages_big(message.chat.id, text='Нет выдачи по одному Подарку') 
                        return
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
                            if not isPowerUser(message.from_user.username):
                                bot.reply_to(message, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
                                return
                        else:
                            if allUser:
                                if not isPowerUser(message.from_user.username):
                                    bot.reply_to(message, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
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
                                    report = f'{user.getNameAndGerb()} забанен нахрен до\n'+'⏰' + time.strftime("%H:%M:%S %d-%m-%Y", time.gmtime(date_for.timestamp()))
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
                                report = f'{user.getNameAndGerb()} разбанен. Говори, дорогой!'
                                updateUser(user)
                            else:
                                for u in list(USERS_ARR):
                                    u.setTimeBan(None)
                                    updateUser(u)
                                
                                for tguser in list(TG_USERS_ARR):
                                    tguser['timeBan'] = None
                                    updateTgUser(tguser)

                                report = f'Все разбанены. Говорите, дорогие мои!'

                        send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text + f'\n{report}')
                    elif 'requests' == response.split(':')[1]:
                        if not isAdmin(message.from_user.username):
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_admin').fulfillment_text)
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
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_not_goat_boss').fulfillment_text)
                            return

                        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                            pass
                        else:
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
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
                        
                        if (raid_date.timestamp() < datetime.now().timestamp()):
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'timeisout').fulfillment_text)
                            return

                        logger.info(f'Дата нового рейда {dt} {dt.timestamp()}   ')
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
                                            'rade_date': dt.timestamp(),
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
                                        'rade_date': dt.timestamp(),
                                        'rade_text': radeloc['rade_text'],
                                        'rade_location': radeloc['rade_location'],
                                        'state': 'WAIT',
                                        'chat_id': message.chat.id,
                                        'login': message.from_user.username,
                                        'goat': goat,
                                        'users': users_onraid})
                        else:
                            plan_raids.delete_many({
                                            'rade_date': dt.timestamp(),
                                            'goat': goat
                                            })

                        plan_str = get_raid_plan(dt.timestamp(), goat, message.from_user.username if privateChat else None)

                        #markupinline.add(InlineKeyboardButton(f"{radeloc['rade_text']}", callback_data=f"capture_{radeloc['rade_location']}_{raid_date.timestamp()}_{goat}"))
                        for radeloc in plan_raids.find({
                                    'rade_date': dt.timestamp(),
                                    'goat': goat}): 
                            users_onraid = radeloc['users']
                            find = False
                            for u in users_onraid:
                                if u == message.from_user.username:
                                    find = True
                            
                            # if not find:
                            markupinline.add(InlineKeyboardButton(f"{radeloc['rade_text']}", callback_data=f"capture_{radeloc['rade_location']}_{dt.timestamp()}_{goat}"))

                        if privateChat and isGoatBoss(message.from_user.username):
                            markupinline.add(InlineKeyboardButton(f"Раздача пинов", callback_data=f"capture_pin_{dt.timestamp()}_{goat}"))

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
                                send_messages_big(message.chat.id, text=f'Ты пытался созвать на захват банду 🤟<b>{band}</b>\n' + getResponseDialogFlow(message.from_user.username, 'not_right_band').fulfillment_text)
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
                                    users_on_cupture.append(user)
                                    report_yes = report_yes + f'  {i}. {user.getNameAndGerb()}\n'
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
                                    users_off_cupture.append(user)
                                    report_no = report_no + f'  {i}. {user.getNameAndGerb()}\n'
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
                            msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'timeisout').fulfillment_text)
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
                            'dialog_flow_context': None,
                            'text': None})
                        
                        msg = send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text)
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
                    elif 'coffee' == response.split(':')[1]:
                        #jugi:setlocation:Москва
                        coffee = next((x for i, x in enumerate(listInv) if x['id']=='coffee'), None).copy()
                        addInventory(userIAm, coffee)                  
                        updateUser(userIAm)
                        send_messages_big(message.chat.id, text=f'Ты получил:▫️ {coffee["name"]}\n')
                        
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
                            send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'understand').fulfillment_text)
                    elif 'rating' == response.split(':')[1]:
                        # if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
                        #     pass
                        # else:
                        #     send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_censorship').fulfillment_text)
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

                            gerb = user.getSettingValue(name="🃏Мой герб")
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

                            gerb = user.getSettingValue(name="🃏Мой герб")
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
                        report = report + f'{report_koronavirus(getMyGoat(userIAm.getLogin()))}'
                        report = report + f'{report_medics(getMyGoat(userIAm.getLogin()))}'

                        report = report + f'\n' 
                        report = report + '⏰ c ' + time.strftime("%d-%m-%Y", time.gmtime(from_date)) + ' по ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(to_date))
                        
                        send_messages_big(message.chat.id, text=report)
                else:
                    try:
                        if privateChat:
                            send_messages_big(message.chat.id, text=response)
                        else:
                            reply_to_big(message.json, text=response)
                    except:
                        logger.info("Error!")
            else:
                reply_to_big(message.json, text=getResponseDialogFlow(message.from_user.username, 'understand').fulfillment_text)
        return
    else:
        if (privateChat or isGoatSecretChat(message.from_user.username, message.chat.id)):
            if (random.random() <= float(getSetting(code='PROBABILITY', name='I_DONT_KNOW_YOU'))):
                send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'you_dont_our_band_gangster').fulfillment_text)

def report_koronavirus(goat):
    viruses = getSetting(code='ACCESSORY_ALL', id='VIRUSES')["value"]
    counter = 0
    goat_bands = getGoatBands(goat['name'])
    report = ''
    for vir in viruses:
        vir_report = f'▫️ {vir["name"]}'
        vir_count = 0
        users_count = 0
        for user in list(filter(lambda x : x.getBand() in goat_bands, USERS_ARR)):
            users_count = users_count + 1
            if user.getInventoryThingCount(vir):
                vir_count = vir_count + 1
        if vir_count > 0:
            report = report + vir_report + f': <b>{vir_count}/{users_count}</b>\n'
    if report == '':
        report = '🦠 У нас нет зараженных\n'
    else:
        report = f'🦠 Статистика зараженных:\n{report}\n'
    return report 

def report_medics(goat):
    counter = 0
    counter_cerificate = 0
    medic = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None) 

    goat_bands = getGoatBands(goat['name'])
    for user in list(filter(lambda x : x.getBand() in goat_bands, USERS_ARR)):
        if user.getInventoryThingCount(medic) > 0 :
            counter = counter + 1
            skill = user.getInventoryThing(medic)
            if skill['storage'] >= skill['min']:
                counter_cerificate = counter_cerificate + 1
    report = f'💉 Сертифицированных врачей: <b>{counter_cerificate}/{counter}</b>\n' 
    return report

def report_man_of_day(message_user_name: str):
    setting = getSetting(code='REPORTS',name='KILLERS')
    from_date = setting.get('from_date')
    to_date = setting.get('to_date')

    goatName = getMyGoatName(message_user_name)

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
    
    goat_users = []
    for d in dresult:
        user = getUserByLogin(d.get("_id"))
        if user:
            if goatName == getMyGoatName(user.getLogin()):
                goat_users.append({'user': user, 'count': d.get("count")})


    # acc = '👑 "Пидор дня"'
    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='REWARDS')['value']) if x['id']=='crown_pidor'), None).copy()

    findInLoser = 0
    i = 0
    pidor_counter = 0
    pidor_user_now = None

    for user_dict in goat_users:
        i = i + 1
        if i == 1:
            emoji = '💝 - '
        elif i == 2:
            emoji = '💖 - '    
        elif i == 3:
            emoji = '❤️ - '
        else:
            emoji = ''
        user = user_dict['user']

        user_name = f'{user.getNameAndGerb()}'
        if user.isInventoryThing(elem):
            pidor_counter = i
            pidor_user_now = user


        if message_user_name  == user.getLogin():
            user_name = f'<b>{user_name}</b>'
            findInLoser = i

        if i <= 5: report = report + f'{i}. {emoji}{user_name}: <b>{user_dict["count"]}</b>\n' 

    if (i == 0): 
        report = report + f'В нашем козле нет пидоров!\n'
    else:
        if (findInLoser > 5): report = report + f'\n💔 Твое пидорье место: <b>{findInLoser}</b>!\n'
    
    if pidor_user_now:
        report = report + f'\nПидор дня <b>{pidor_user_now.getNameAndGerb()}</b> на {pidor_counter} месте\n'
    
    return report

@bot.callback_query_handler(func=lambda call: call.data.startswith("need_doctor"))
def callback_query(call):
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return
    
    login = call.data.split('|')[3]
    step = int(call.data.split('|')[2])
    user = getUserByLogin(call.from_user.username)

    markupinline = InlineKeyboardMarkup()
    medic = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None) 
    
    buttons = []
    for user in list(filter(lambda x : x.getInventoryThingCount(medic) > 0, USERS_ARR)):
        skill = user.getInventoryThing(medic)
        if skill['storage'] >= skill['min']:
            buttons.append(InlineKeyboardButton(f"{user.getNameAndGerb()}", callback_data=f"need_doctor|get|{step}|{user.getLogin()}"))

    if call.data.split('|')[1] == 'exit':
        if login == call.from_user.username:
            bot.answer_callback_query(call.id, f"Вышел!")
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='На сегодня хватит!', parse_mode='HTML')
            return
        else:
            bot.answer_callback_query(call.id, f"Куда ты лезешь?")

    elif call.data.split('|')[1] == 'back':
        if login == call.from_user.username:
            step = step - 1 
        else:
            bot.answer_callback_query(call.id, f"Куда ты лезешь?")
    elif call.data.split('|')[1] == 'forward':
        if login == call.from_user.username:
            step = step + 1
        else:
            bot.answer_callback_query(call.id, f"Куда ты лезешь?")
    else:
        pass
    
    bot.answer_callback_query(call.id, f"Шаг {step}!")

    back_button = InlineKeyboardButton(f"Назад 🔙", callback_data=f"need_doctor|back|{step}|{login}|")
    exit_button = InlineKeyboardButton(f"Выйти ❌", callback_data=f"need_doctor|exit|{step}|{login}|")
    forward_button = InlineKeyboardButton(f"Далее 🔜", callback_data=f"need_doctor|forward|{step}|{login}|")

    for row in build_menu(buttons=buttons, n_cols=3, limit=6, step=step, back_button=back_button, exit_button=exit_button, forward_button=forward_button):
        markupinline.row(*row)  
    
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=getResponseDialogFlow(call.message.from_user.username, 'shot_message_zbs').fulfillment_text, parse_mode='HTML', reply_markup=markupinline)

@bot.callback_query_handler(func=lambda call: call.data.startswith("ping_user"))
def callback_query(call):
    # logger.info(f'{call.from_user.username} {call.data}')
    #  0         1      2
    # ping_user|{d}

    if isUserBan(call.from_user.username):
       bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
       return

    login = call.data.split('|')[1]
    hwois = f'🗣 <b>{call.from_user.username}</b>'
    user = getUserByLogin(call.from_user.username)
    if user:
        hwois = f'🗣 <b>{user.getLogin()}</b>'

    if login == call.from_user.username:
        bot.answer_callback_query(call.id, f"Понял!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        send_messages_big(call.message.chat.id, text=f'{hwois}\n👌Благодарю!🙏')
        return



    text = f'{hwois}\n@{login}, родной!\nТы в опасности!'
    bot.answer_callback_query(call.id, f"{login} предупрежден!")
    send_messages_big(call.message.chat.id, text=text)

@bot.callback_query_handler(func=lambda call: call.data.startswith("boss_info"))
def callback_query(call):
    # logger.info(f'{call.from_user.username} {call.data}')
    #     0              1           2        
    # boss_info|{hashstr}

    if isUserBan(call.from_user.username):
       bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
       return
 
    hashstr = call.data.split('|')[1]
    bossinbd = getBossByHash(hashstr)

    dresult = boss.aggregate([ 
        {   "$group": {
            "_id": { "boss_name":"$boss_name" }, 
            "count": {
                "$sum": 1}}},
            
        {   "$sort" : { "count" : -1 } }
        ])
    
    
    buttons = []
    for d in sorted(dresult, key = lambda i: tools.deEmojify(i["_id"]["boss_name"]), reverse=False):
        boss_name = d["_id"]["boss_name"] 
        #if boss_name == bossinbd['boss_name']: continue
        hashstr = getMobHash(boss_name, 'boss')
        boss_name_small = boss_name
        for n_boss in GLOBAL_VARS['bosses']:
            boss_name_small = boss_name_small.replace(n_boss, '') 
        buttons.append(InlineKeyboardButton(boss_name_small, callback_data=f"boss_info|{hashstr}"))

    markupinline = InlineKeyboardMarkup(row_width=3)
    for row in build_menu(buttons=buttons, n_cols=3):
        markupinline.row(*row)    

    text = getBossReport(bossinbd['boss_name'])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

@bot.callback_query_handler(func=lambda call: call.data.startswith("mob_info"))
def callback_query(call):
    # logger.info(f'{call.from_user.username} {call.data}')
    #     0              1           2        
    # mob_info|{hashstr}|{not dark_zone}

    if isUserBan(call.from_user.username):
       bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
       return
 
    hashstr = call.data.split('|')[1]
    dark_zone = eval(call.data.split('|')[2])
    mobinbd = getMobByHash(hashstr)
    markupinline = InlineKeyboardMarkup()
    markupinline.add(
        InlineKeyboardButton('🔆' if dark_zone else '🚷', callback_data=f"mob_info|{hashstr}|{not dark_zone}")
        )

    text = getMobReport(mobinbd['mob_name'], mobinbd['mob_class'], dark_zone)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

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
            report_yes = report_yes + f'  {i}. {user.getNameAndGerb()}\n'
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
            report_no = report_no + f'  {i}. {user.getNameAndGerb()}\n'
        else:
            report_no = report_no + f'  {i}. {dun["login"]}\n'

    if i == 0:
        report_no = report_no + '  Никто не отказался\n'

    text = text + report_yes + '\n' + report_no
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
    # logger.info(f'{call.from_user.username} {text}')

@bot.callback_query_handler(func=lambda call: call.data.startswith("setrank"))
def callback_query(call):
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    if not isGoatBoss(call.from_user.username):
        if not isAdmin(call.from_user.username):
            bot.answer_callback_query(call.id, "Тебе не положено!")
            return

    if 'setrank_exit' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Присвоение звания завершено!', parse_mode='HTML')
        return

    if call.data.startswith("setrank_next"):
        #        0         1     2
        counter  = int(call.data.split('|')[2])
        login = call.data.split('|')[1]
        user = getUserByLogin(login)
        markupinline = InlineKeyboardMarkup()
        i = 1
        addExit = False
        for rank in getSetting(code='RANK', id='MILITARY')['value']:
            if user and user.getRankId() == rank['id']:
                continue    

            if i <= counter:
                pass
            else:
                markupinline.add(InlineKeyboardButton(f"{rank['name']}", callback_data=f"setrank|{login}|{rank['id']}"))
                if i == counter + 10:
                    markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"setrank_back|{login}|{counter - 10}"), InlineKeyboardButton(f"Далее 🔜", callback_data=f"setrank_next|{login}|{counter + 10}"))
                    addExit = True
                    break
            i = i + 1
        if not addExit:
            markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"setrank_back|{login}|{counter - 10}"))
        
        markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"setrank_exit"))
        
        if user:
            text=f'Звание {user.getNameAndGerb()}: {user.getRankName()}'
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
        return

    if call.data.startswith("setrank_back"):
        counter  = int(call.data.split('|')[2])
        login = call.data.split('|')[1]
        user = getUserByLogin(login)
        markupinline = InlineKeyboardMarkup()
        i = 1
        addExit = False
        for rank in getSetting(code='RANK', id='MILITARY')['value']:
            if user.getRankId() == rank['id']:
                continue    

            if i <= counter:
                pass
            else:
                markupinline.add(InlineKeyboardButton(f"{rank['name']}", callback_data=f"setrank|{login}|{rank['id']}"))
                if i == counter + 10:
                    if counter == 0:
                        markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"setrank_next|{login}|{counter + 10}"))
                    else:
                        markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"setrank_back|{login}|{counter - 10}"), InlineKeyboardButton(f"Далее 🔜", callback_data=f"setrank_next|{login}|{counter + 10}"))
                    
                    #markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"setrank_exit"))
                    addExit = True
                    break
            i = i + 1
        if not addExit:
            markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"setrank_next|{login}|{i+10}"))
        markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"setrank_exit"))

        text=f'Звание {user.getNameAndGerb()}: {user.getRankName()}'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
        return

    bot.answer_callback_query(call.id, "Ты сделал свой выбор")
    login = call.data.split('|')[1]
    user = getUserByLogin(login)
    
    for rank in getSetting(code='RANK', id='MILITARY')['value']:
        if rank['id'] == call.data.split('|')[2]:
            rank.update({'update':'hand'})
            user.setRank(rank)
            updateUser(user)
            send_messages_big(call.message.chat.id, text=user.getNameAndGerb() + '!\n' + getResponseDialogFlow(call.message.from_user.username, 'set_new_rank').fulfillment_text + f'\n\n▫️ {rank["name"]}') 
            break

    markupinline = InlineKeyboardMarkup()
    counter = 10
    i = 1
    for rank in getSetting(code='RANK', id='MILITARY')['value']:
        if user and user.getRankId() == rank['id']:
            continue    

        markupinline.add(InlineKeyboardButton(f"{rank['name']}", callback_data=f"setrank|{login}|{rank['id']}"))
        if i == counter :
            markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"setrank_next|{login}|{counter}"))
            #markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"setrank_exit"))
            break
        i = i + 1

    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"setrank_exit"))
    
    if user:
        text=f'Звание {user.getNameAndGerb()}: {user.getRankName()}'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

@bot.callback_query_handler(func=lambda call: call.data.startswith("toreward"))
def callback_query(call):
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    if not call.from_user.username == call.data.split('|')[3]:
        bot.answer_callback_query(call.id, f"Это может сделать только {call.data.split('|')[3]}!")
        return

    userIAm = getUserByLogin(call.from_user.username)

    # if not isGoatBoss(call.from_user.username):
    #     if not isAdmin(call.from_user.username):
    #         bot.answer_callback_query(call.id, "Тебе не положено!")
    #         return

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

        listInv = list(GLOBAL_VARS['inventory'])
        if not isAdmin(call.from_user.username):
            listInv = userIAm.getInventoryType(GLOBAL_VARS['typeforexcenge'])

        checker = []
        for elem in listInv:
            if elem['id'] in checker:
                continue
            checker.append(elem['id'])
            if user and user.isMaxInventoryThing(elem, USERS_ARR):
                continue
            # if user and user.isInventoryThing(elem):
            #     continue    

            if i <= counter:
                pass
            else:
                s = f"toreward|{login}|{elem['id']}|{userIAm.getLogin()}"
                if len(s)>64:
                    logger.info(f"ERROR: callback_data more 64b: {elem['id']}")
                    continue
                markupinline.add(InlineKeyboardButton(f"{elem['name']}", callback_data=f"toreward|{login}|{elem['id']}|{userIAm.getLogin()}"))
                if i == counter + 10:
                    markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_back|{login}|{counter - 10}|{userIAm.getLogin()}"), InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter + 10}|{userIAm.getLogin()}"))
                    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))
                    addExit = True
                    break
            i = i + 1
        if not addExit:
            markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_back|{login}|{counter - 10}|{userIAm.getLogin()}"))
            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))
        
        text=f'Всем бандитам будет что-то выдано! Просмотрено {counter} аксессуаров'
        if user:
            inventory_category = [{'id':'food', 'name':'🍗 Еда'},
                                    {'id':'decoration', 'name':'🎁 Подарки'},
                                    {'id':'things', 'name':'📦 Вещи'}]
            report = user.getInventoryReport(inventory_category)
            text=f'{user.getNameAndGerb()}:\n{report}'
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
        return

    if call.data.startswith("toreward_back"):
        # toreward_back|{login}|10"
        counter  = int(call.data.split('|')[2])
        login = call.data.split('|')[1]
        user = getUserByLogin(login)
        markupinline = InlineKeyboardMarkup()
        i = 1

        listInv = list(GLOBAL_VARS['inventory'])
        if not isAdmin(call.from_user.username):
            listInv = userIAm.getInventoryType(GLOBAL_VARS['typeforexcenge'])

        addExit = False
        checker = []
        for elem in listInv:
            if elem['id'] in checker:
                continue
            checker.append(elem['id'])
            if user and user.isMaxInventoryThing(elem, USERS_ARR):
                continue
            # if user and user.isInventoryThing(elem):
            #     continue    

            if i <= counter:
                pass
            else:
                s = f"toreward|{login}|{elem['id']}|{userIAm.getLogin()}"
                if len(s)>64:
                    logger.info(f"ERROR: callback_data more 64b: {elem['id']}")
                    continue
                markupinline.add(InlineKeyboardButton(f"{elem['name']}", callback_data=f"toreward|{login}|{elem['id']}|{userIAm.getLogin()}"))
                if i == counter + 10:
                    if counter == 0:
                        markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter + 10}|{userIAm.getLogin()}"))
                    else:
                        markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_back|{login}|{counter - 10}|{userIAm.getLogin()}"), InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter + 10}|{userIAm.getLogin()}"))
                    
                    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))
                    addExit = True
                    break
            i = i + 1
        if not addExit:
            markupinline.add(InlineKeyboardButton(f"Назад 🔙", callback_data=f"toreward_next|{login}|{i+10}|{userIAm.getLogin()}"))
            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))

        inventory_category = [{'id':'food', 'name':'🍗 Еда'},
                                {'id':'decoration', 'name':'🎁 Подарки'},
                                {'id':'things', 'name':'📦 Вещи'}]
        report = user.getInventoryReport(inventory_category)
        text=f'{user.getNameAndGerb()}:\n{report}'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)
        return


    login = call.data.split('|')[1]
    user = getUserByLogin(login)
    userIAm = getUserByLogin(call.from_user.username)

    listInv = list(GLOBAL_VARS['inventory'])
    if not isAdmin(call.from_user.username):
        listInv = userIAm.getInventoryType(GLOBAL_VARS['typeforexcenge'])

    for elem in listInv:
        inv = elem.copy()
        if inv['id'] == call.data.split('|')[2]:
            bot.answer_callback_query(call.id, "Ты сделал свой выбор")
            if login.lower() == 'всем':
                if isAdmin(call.from_user.username):
                    for useradd in list(USERS_ARR):
                        addInventory(useradd, inv, False)
                        updateUser(useradd)
                    send_messages_big(call.message.chat.id, text= 'Бандиты!\n' + getResponseDialogFlow(call.message.from_user.username, 'new_accessory_all').fulfillment_text + f'\n\n▫️ {inv["name"]}') 
                else:
                    send_messages_big(call.message.chat.id, text= getResponseDialogFlow(call.message.from_user.username, 'shot_message_not_admin').fulfillment_text) 
            else:
                if isAdmin(call.from_user.username): 
                    addInventory(user, inv, False)
                else:
                    userIAm.removeInventoryThing(inv)
                    user.addInventoryThing(inv)
                    updateUser(userIAm)

                updateUser(user)
                send_messages_big(call.message.chat.id, text=f'{userIAm.getNameAndGerb()} передал {user.getNameAndGerb()}\n\n▫️ {inv["name"]}') 

            break

    listInv = list(GLOBAL_VARS['inventory'])
    if not isAdmin(call.from_user.username):
        listInv = userIAm.getInventoryType(GLOBAL_VARS['typeforexcenge'])

    markupinline = InlineKeyboardMarkup()
    counter = 10
    i = 1
    checker = []
    for elem in listInv:
        if elem['id'] in checker:
            continue
        checker.append(elem['id'])
        if user and user.isMaxInventoryThing(elem, USERS_ARR):
            continue
        # if user and user.isInventoryThing(elem):
        #     continue    

        markupinline.add(InlineKeyboardButton(f"{elem['name']}", callback_data=f"toreward|{login}|{elem['id']}|{userIAm.getLogin()}"))
        if i == counter :
            markupinline.add(InlineKeyboardButton(f"Далее 🔜", callback_data=f"toreward_next|{login}|{counter}|{userIAm.getLogin()}"))
            markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))
            break
        i = i + 1
    
    if len(listInv)<10:
        markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"toreward_exit|||{userIAm.getLogin()}"))

    if user:
        inventory_category = [{'id':'animals', 'name':'🐮 Животные'},
                        {'id':'food', 'name':'🍗 Еда'},
                        {'id':'decoration', 'name':'🎁 Подарки'},
                        {'id':'things', 'name':'📦 Вещи'}]
        report = user.getInventoryReport(inventory_category)
        text=f'{user.getNameAndGerb()}:\n{report}'
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pickup"))
def callback_query(call):
    # pickupaccessory|{login}|{acc}
    logger.info(call.data)
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    if not isGoatBoss(call.from_user.username):
        if not isAdmin(call.from_user.username):
            bot.answer_callback_query(call.id, "Тебе не положено!")
            return

    login  = call.data.split('|')[1]

    user = getUserByLogin(login)
    markupinline = InlineKeyboardMarkup()

    inventory_category = getSetting(code='INVENTORY_CATEGORY')
    report = user.getInventoryReport(inventory_category)
    if report == '':
        report = 'У него больше ничего нет!'

    if 'pickup_exit' in call.data:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Отъём завершен!\nОстались аксессуары:\n{report}', parse_mode='HTML')
        return

    elemId = call.data.split('|')[2]
    elem = user.getInventoryThing({'id':f'{elemId}'})

    #if elem['type'] in ('skill', 'disease', 'tatu'):
    if elem['type'] in ('disease', 'tatu'):
        bot.answer_callback_query(call.id, "Это нельзя забрать!")
        return    

    bot.answer_callback_query(call.id, "Ты забрал это ...")
    user.removeInventoryThing(elem)
    updateUser(user)

    elems = []
    for elem in user.getInventory():
        if elem['id'] in elems:
            continue
        elems.append(elem['id'])
        markupinline.add(InlineKeyboardButton(f"{elem['name']}", callback_data=f"pickup|{login}|{elem['id']}"))

    text = 'У него больше нечего забрать!'
    report = user.getInventoryReport(inventory_category)
    if not report == '':
           text = f'{report}\nЧто изьять?'
        
    markupinline.add(InlineKeyboardButton(f"Выйти ❌", callback_data=f"pickup_exit|{login}"))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, parse_mode='HTML', reply_markup=markupinline)

@bot.callback_query_handler(func=lambda call: call.data.startswith("pinraid_"))
def callback_query(call):
    privateChat = ('private' in call.message.chat.type)
    # pinonraid_actions_{goat}_{band}_{raid_date.timestamp()}
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return

    markupinline = InlineKeyboardMarkup()
    buttons = []
    goat = ''
    band = ''
    raid_date = None
    exit_button = None
    selected_name = ''
    liga = ''
    
    if call.data.startswith('pinraid_band'):
        goat = call.data.split('_')[2]
        band = call.data.split('_')[3]
        raid_date = datetime.fromtimestamp(float(call.data.split('_')[4]))

        # bot.answer_callback_query(call.id, f"Банда {band}")

        for user in list(filter(lambda x : x.getBand() == band, USERS_ARR)):
            planed_location = None
            for report in report_raids.find({'login': user.getLogin(), 'date': raid_date.timestamp()}):
                try:
                    planed_location = report['planed_location']
                except: pass
            planed_location_str = ''
            if planed_location:
                planed_location_str = f'📍{planed_location} ' if planed_location > 0 else ''
            buttons.append(InlineKeyboardButton(f"{planed_location_str}{user.getNameAndGerb()}", callback_data=f"pinraid_user_{raid_date.timestamp()}_{band}_{user.getLogin()}"))
        
        all_banditos=InlineKeyboardButton(f"👥 Все бандиты", callback_data=f"pinraid_user_{raid_date.timestamp()}_{band}_allbanditos")
        buttons.append(all_banditos)
        exit_button = InlineKeyboardButton(f"Вернуться ❌", callback_data=f"capture_pin_{raid_date.timestamp()}_{goat}")
    
    if call.data.startswith('pinraid_user'):
        #   0      1               2             3       4
        # pinraid_user_{raid_date.timestamp()}_{band}_allbanditos
        raid_date = datetime.fromtimestamp(float(call.data.split('_')[2]))
        user_login = call.data.split("_"+call.data.split('_')[3]+"_")[1]
        if user_login == 'allbanditos':
            for user in list(filter(lambda x : x.getBand() == call.data.split('_')[3], USERS_ARR)):
                selected_name = '👥 Все бандиты'
                goatRow = getMyGoat(user.getLogin())
                band = user.getBand()
                goat = goatRow['name']
                liga = goatRow['liga']
                break
        else:
            user = getUserByLogin(user_login)
            selected_name = f'{user.getNameAndGerb()} @{user.getLogin()}' 
            
            band = user.getBand()
            goatRow = getMyGoat(user_login)
            goat = goatRow['name']
            liga = goatRow['liga']
        
        for loc in getSetting(code='RAIDLOCATIONS'):
            if loc['liga'] == liga:
                buttons.append(InlineKeyboardButton(f"{loc['name']}", callback_data=f"pinraid_loc_{raid_date.timestamp()}_{loc['id']}_{band}_{user_login}"))
        
        exit_button = InlineKeyboardButton(f"Вернуться ❌", callback_data=f"pinraid_band_{goat}_{band}_{raid_date.timestamp()}")

    if call.data.startswith('pinraid_loc'):
        #   0      1            2                   3       4       5
        # pinraid_loc_{raid_date.timestamp()}_{loc['id']}_{band}_{user_login}
        raid_date = datetime.fromtimestamp(float(call.data.split('_')[2]))
        loc_id = int(call.data.split('_')[3]) 
        band = call.data.split('_')[4]
        user_login = call.data.split('_'+call.data.split('_')[4]+'_')[1]
        
        if user_login == 'allbanditos':
            for user in list(filter(lambda x : x.getBand() == band, USERS_ARR)):
                saveUserRaidResult(user, raid_date.timestamp(), location=None, planed_location=loc_id)
        else:
            user = getUserByLogin(user_login)
            saveUserRaidResult(user, raid_date.timestamp(), location=None, planed_location=loc_id)


        for user in list(filter(lambda x : x.getBand() == band, USERS_ARR)):
            planed_location = None
            for report in report_raids.find({'login': user.getLogin(), 'date': raid_date.timestamp()}):
                try:
                    planed_location = report['planed_location']
                except: pass
            planed_location_str = ''
            if planed_location:
                planed_location_str = f'📍{planed_location} ' if planed_location > 0 else ''

            buttons.append(InlineKeyboardButton(f"{planed_location_str}{user.getNameAndGerb()}", callback_data=f"pinraid_user_{raid_date.timestamp()}_{band}_{user.getLogin()}"))
            if goat == '':
                goat = getMyGoatName(user.getLogin())

        all_banditos=InlineKeyboardButton(f"👥 Все бандиты", callback_data=f"pinraid_user_{raid_date.timestamp()}_{band}_allbanditos")
        buttons.append(all_banditos)
        exit_button = InlineKeyboardButton(f"Вернуться ❌", callback_data=f"capture_pin_{raid_date.timestamp()}_{goat}")

    if call.data.startswith('pinraid_repeat'):
        tz = config.SERVER_MSK_DIFF
        raid_date = datetime.fromtimestamp(float(call.data.split('_')[2]))
        bands = getGoatBands(call.data.split('_')[3])
        goat = call.data.split('_')[3]
        counter = 0
        for user in list(filter(lambda x : x.getBand() in bands, USERS_ARR)):        
            counter_r = report_raids.find({'login': user.getLogin()}).count()
            cursor = report_raids.find({'login': user.getLogin()}).skip(counter_r - 1)
            
            for rep in cursor:
                row = {}
                row.update({'planed_location': rep['planed_location']})
                row.update({'notified': False})
                newvalues = { "$set": row }
                result = report_raids.update_one({"login": f"{user.getLogin()}", 'date': raid_date.timestamp()}, newvalues)
                if result.matched_count < 1:
                    row.update({'date': raid_date.timestamp() })
                    row.update({'login': user.getLogin()})
                    row.update({'band': user.getBand()})
                    row.update({'goat': getMyGoatName(user.getLogin())})
                    row.update({'user_location': 0})
                    row.update({'on_raid': False})
                    row.update({'planed_location': rep['planed_location']})
                    row.update({'notified': False})
                    report_raids.insert_one(row)
        
        buttons = []
        for band in getGoatBands(goat):
            counter_100 = registered_users.find({'band': band}).count()
            counter_now = report_raids.find({'band': band, 'date': raid_date.timestamp(), 'planed_location': {'$ne': None} }).count()
            percent = 0
            if counter_100 > 0:
                percent = counter_now/counter_100*100
            buttons.append(InlineKeyboardButton(f"🤘{band} {int(percent)}%", callback_data=f"pinraid_band_{goat}_{band}_{raid_date.timestamp()}"))                        
        
        counter_not_notified = report_raids.find({'band': {'$in': getGoatBands(goat)}, 'date': raid_date.timestamp(), 'notified': False, 'planed_location': {'$gt': 0} }).count()

        if counter_not_notified > 0:
            buttons.append(InlineKeyboardButton(f"Отправить 📩", callback_data=f"pinraid_pin_{raid_date.timestamp()}_{goat}"))
        
        if report_raids.count_documents({'band': {'$in': getGoatBands(goat)}, 'date': raid_date.timestamp(), 'planed_location': {'$gt': 0} })  == 0:
            buttons.append(InlineKeyboardButton(f"Повторить 🔄", callback_data=f"pinraid_repeat_{raid_date.timestamp()}_{goat}"))
    
        exit_button = InlineKeyboardButton(f"Вернуться ❌", callback_data=f"capture_plan_{raid_date.timestamp()}_{goat}")
        
        for row in build_menu(buttons=buttons, n_cols=2, exit_button=exit_button):
            markupinline.row(*row)  
            
        text = get_raid_plan(raid_date.timestamp(), goat, call.from_user.username if privateChat else None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'🤘Выбери банду\n{text}', parse_mode='HTML', reply_markup=markupinline)
        return

    if call.data.startswith('pinraid_pin'):
        #    0     1          2                  3
        # pinraid_pin_{raid_date.timestamp()}_{goat}
        tz = config.SERVER_MSK_DIFF
        raid_date = datetime.fromtimestamp(float(call.data.split('_')[2]))
        bands = getGoatBands(call.data.split('_')[3])
        goat = call.data.split('_')[3]
        counter = 0
        for user in list(filter(lambda x : x.getBand() in bands, USERS_ARR)):
            planed_location = None
            for report in report_raids.find({'login': user.getLogin(), 'date': raid_date.timestamp(), 'notified': False}):
                try:
                    planed_location = report['planed_location']
                except: pass
            planed_location_str = ''
            if planed_location:
                date_str = time.strftime("%H:%M %d.%m", time.gmtime((raid_date + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp())) 
                planed_location_str = f'Твой пин ⏱ <b>{date_str}</b> -> 📍<b>{planed_location}км</b>' if planed_location > 0 else ''
                try:
                    if planed_location > 0:
                        logger.info(f'Отправляем пин {user.getLogin()}')
                        send_messages_big(user.getChat(), text=planed_location_str)
                        bot.send_sticker(user.getChat(), random.sample(getSetting(code='STICKERS', name='GOTORAID'), 1)[0]['value'])
                        counter = counter + 1
                    newvalues = { "$set": { 'notified': True} }
                    result = report_raids.update_one({'login': user.getLogin(), 'date': raid_date.timestamp()}, newvalues)
                        
                except:
                    logger.info(f'ERROR: Не смогли отправить пин {user.getLogin()}')
        if counter > 0:
            bot.answer_callback_query(call.id, f"Пины отправлены {counter} бандитам!")

            buttons = []
            for band in getGoatBands(goat):
                counter_100 = registered_users.find({'band': band}).count()
                counter_now = report_raids.find({'band': band, 'date': raid_date.timestamp(), 'planed_location': {'$ne': None} }).count()
                percent = 0
                if counter_100 > 0:
                    percent = counter_now/counter_100*100
                buttons.append(InlineKeyboardButton(f"🤘{band} {int(percent)}%", callback_data=f"pinraid_band_{goat}_{band}_{raid_date.timestamp()}"))                        
            
            counter_not_notified = report_raids.find({'band': {'$in': getGoatBands(goat)}, 'date': raid_date.timestamp(), 'notified': False, 'planed_location': {'$gt': 0} }).count_documents() 

            if counter_not_notified > 0:
                buttons.append(InlineKeyboardButton(f"Отправить 📩", callback_data=f"pinraid_pin_{raid_date.timestamp()}_{goat}"))
            
            if report_raids.count_documents({'band': {'$in': getGoatBands(goat)}, 'date': raid_date.timestamp(), 'planed_location': {'$gt': 0} }) == 0:
                buttons.append(InlineKeyboardButton(f"Повторить 🔄", callback_data=f"pinraid_repeat_{raid_date.timestamp()}_{goat}"))
        
            exit_button = InlineKeyboardButton(f"Вернуться ❌", callback_data=f"capture_plan_{raid_date.timestamp()}_{goat}")
            
            for row in build_menu(buttons=buttons, n_cols=2, exit_button=exit_button):
                markupinline.row(*row)  
                
            text = get_raid_plan(raid_date.timestamp(), goat, call.from_user.username if privateChat else None)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'🤘Выбери банду\n{text}', parse_mode='HTML', reply_markup=markupinline)

        else:
            bot.answer_callback_query(call.id, f"Некому отправлять пины!")
        return

    for row in build_menu(buttons=buttons, n_cols=2, exit_button=exit_button):
        markupinline.row(*row)  

    text = get_raid_plan(raid_date.timestamp(), goat, call.from_user.username if privateChat else None)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'🤘 <b>{band}</b> <b>{selected_name}</b>\n{text}', parse_mode='HTML', reply_markup=markupinline)
    return

@bot.callback_query_handler(func=lambda call: call.data.startswith("capture_"))
def callback_query(call):
    privateChat = ('private' in call.message.chat.type)
    if isUserBan(call.from_user.username):
        bot.answer_callback_query(call.id, "У тебя ядрёный бан, дружище!")
        return
    
    goat = call.data.split('_')[3]
    if not goat == getMyGoatName(call.from_user.username):
        bot.answer_callback_query(call.id, "Это план не твоего козла!")
        return

    markupinline = InlineKeyboardMarkup()
    raid_date = datetime.fromtimestamp(float(call.data.split('_')[2]))

    if call.data.startswith("capture_plan"):
        bot.answer_callback_query(call.id, "План рейда!")
        plan_str = get_raid_plan(raid_date.timestamp(), goat, call.from_user.username if privateChat else None)
        markupinline.add(InlineKeyboardButton(f"Раздача пинов", callback_data=f"capture_pin_{raid_date.timestamp()}_{goat}"))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=plan_str, parse_mode='HTML', reply_markup=markupinline)

        return

    if call.data.startswith("capture_pin"):
        bot.answer_callback_query(call.id, "Раздача личных пинов!")
        
        buttons = []
        for band in getGoatBands(goat):
            counter_100 = registered_users.count_documents({'band': band})
            counter_now = report_raids.count_documents({'band': band, 'date': raid_date.timestamp(), 'planed_location': {'$ne': None} })
            percent = 0
            if counter_100 > 0:
                percent = counter_now/counter_100*100
            buttons.append(InlineKeyboardButton(f"🤘{band} {int(percent)}%", callback_data=f"pinraid_band_{goat}_{band}_{raid_date.timestamp()}"))                        
        
        counter_not_notified = report_raids.count_documents({'band': {'$in': getGoatBands(goat)}, 'date': raid_date.timestamp(), 'notified': False, 'planed_location': {'$gt': 0}  })

        if counter_not_notified > 0:
            buttons.append(InlineKeyboardButton(f"Отправить 📩", callback_data=f"pinraid_pin_{raid_date.timestamp()}_{goat}"))

        if report_raids.count_documents({'band': {'$in': getGoatBands(goat)}, 'date': raid_date.timestamp(), 'planed_location': {'$gt': 0} })  == 0:
            buttons.append(InlineKeyboardButton(f"Повторить 🔄", callback_data=f"pinraid_repeat_{raid_date.timestamp()}_{goat}"))
        
        exit_button = InlineKeyboardButton(f"Вернуться ❌", callback_data=f"capture_plan_{raid_date.timestamp()}_{goat}")
        
        for row in build_menu(buttons=buttons, n_cols=2, exit_button=exit_button):
            markupinline.row(*row)  
            
        text = get_raid_plan(raid_date.timestamp(), goat, call.from_user.username if privateChat else None)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'🤘Выбери банду\n{text}', parse_mode='HTML', reply_markup=markupinline)
        return

    raid_location = int(call.data.split('_')[1])
    myquery = { 
                'rade_date': raid_date.timestamp(),
                'goat': goat
            }

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
    
    if privateChat and isGoatBoss(call.from_user.username):
        markupinline.add(InlineKeyboardButton(f"Раздача пинов", callback_data=f"capture_pin_{raid_date.timestamp()}_{goat}"))
       
    text = get_raid_plan(raid_date.timestamp(), goat, call.from_user.username if privateChat else None)
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
            text = getResponseDialogFlow(pending_message['user_id'], pending_message.get('dialog_flow_text'), context_param=pending_message.get('dialog_flow_context')).fulfillment_text + '\n' + text
        
        try:
            if pending_message.get('reply_message'):
                reply_to_big(pending_message.get('reply_message'), text)
            else:
                send_messages_big(pending_message.get('chat_id'), text, None)
        except:
            send_message_to_admin(f'⚠️ Ошибка оправки отложенного сообщения в чат {pending_message.get("chat_id")}\n\n{text}')
                
        ids.append(pending_message.get('_id')) 

    for id_str in ids:
        myquery = {"_id": ObjectId(id_str)}
        newvalues = { "$set": { "state": 'CANCEL'} }
        u = pending_messages.update_one(myquery, newvalues)

def isUserVotedRaid(login, raidInfo, goatName):
    find = False
    for radeloc in plan_raids.find({
                'rade_date': raidInfo['rade_date'],
                'goat': goatName}): 
        users_onraid = radeloc['users']
        for u in users_onraid:
            if u == login:
                find = True
                break
    return find        

def ping_on_raid(fuckupusers, chat_id, raidInfo, goatName):
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
            if (fu.getRaidLocation() and fu.getRaidLocation() > 0) or isUserVotedRaid(fu.getLogin(), raidInfo, goatName): 
                fuckupusersReport = fuckupusersReport + f'{counter}. {fu.getNameAndGerb()}\n'
            else:
                fuckupusersReport = fuckupusersReport + f'{counter}. @{fu.getLogin()}\n'
        else:
            fuckupusersReport = fuckupusersReport + f'{counter}. 🔕{fu.getNameAndGerb()}\n'

        if counter % 5 == 0:
            send_messages_big(chat_id, text=fuckupusersReport)
            fusers = []
            fuckupusersReport = f'🐢 <b>Бандиты! {getResponseDialogFlow(None, "rade_motivation").fulfillment_text}</b>\n🤟<b>{fuckupusers[0].getBand()}</b>\n'

    if len(fusers) > 0:
        send_messages_big(chat_id, text=fuckupusersReport)

def get_raid_plan(raid_date, goat, login):
    tz = config.SERVER_MSK_DIFF
    planed_location_str = ''
    # Вставляем информацию о пине на рейд
    if login:
        user = getUserByLogin(login)
        if user:
            planed_location = None
            for report in report_raids.find({'login': user.getLogin(), 'date': raid_date}):
                try:
                    planed_location = report['planed_location']
                except: pass
            if planed_location and planed_location > 0:
                date_str = time.strftime("%H:%M %d.%m", time.gmtime(( datetime.fromtimestamp(raid_date) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp())) 
                planed_location_str = f'Твой пин ⏱ <b>{date_str}</b>  -> 📍<b>{planed_location}км</b>\n' if planed_location > 0 else ''     
    
    plan_for_date = f'Ближайший рейд ⏱ <b>{time.strftime("%H:%M %d.%m", time.gmtime( (datetime.fromtimestamp(raid_date) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp() ))}</b>\n🐐<b>{goat}</b>\n\n'
    find = False
    time_str = None
    for raid in plan_raids.find({
                                '$and' : 
                                [
                                    {
                                        'rade_date': raid_date
                                    },
                                    {
                                        'goat': goat
                                    }
                                ]
                            }):

        t = datetime.fromtimestamp(raid.get('rade_date') ) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
        if not (time_str == t):
            plan_for_date = plan_for_date + f'<b>Рейд в {str(t.hour).zfill(2)}:{str(t.minute).zfill(2)}</b>\n'
            time_str = t

        plan_for_date = plan_for_date + f'<b>{raid.get("rade_text")}</b>\n'
        users_onraid = raid.get("users")
        if users_onraid == None or len(users_onraid) == 0:
            plan_for_date = plan_for_date + f'    Никто не записался\n'
        else:
            i = 0
            for u in users_onraid:
                i = i + 1
                reg_usr = getUserByLogin(u)
                if reg_usr.getLogin() == login:
                    plan_for_date = plan_for_date + f'    {i}. <b>{reg_usr.getNameAndGerb()}</b>\n'
                else:
                    plan_for_date = plan_for_date + f'    {i}. {reg_usr.getNameAndGerb()}\n'
        
        find = True

    if find == False:
        plan_for_date = plan_for_date + '<b>Нет запланированных рейдов</b>'

    return plan_for_date + f'\n{planed_location_str}'

def rade():
    tz = config.SERVER_MSK_DIFF
    now_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)

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
                report = 'Чёт я приуныл... Ничего в голову не идет... С днем всех влюблённых!'
            send_messages_big(goat['chats']['info'], report)
            bot.send_sticker(goat['chats']['info'], random.sample(getSetting(code='STICKERS', name='LOVE_DAY'), 1)[0]['value']) 
    
    # 8 марта!
    if now_date.day == 8 and now_date.month == 3 and now_date.hour == 9 and now_date.minute in (0,10,15,20,25,35,40,45,50,55) and now_date.second < 15:
        for goat in getSetting(code='GOATS_BANDS'):
            report = 'Девашки! Я ваз лублу!'
            send_messages_big(goat['chats']['info'], report)
            bot.send_sticker(goat['chats']['info'], random.sample(getSetting(code='STICKERS', name='8_MARCH'), 1)[0]['value']) 
    
    # День рождения
    if now_date.hour == 10 and now_date.minute == 0 and now_date.second < 15:
        
            updateUser(None)
            for goat in getSetting(code='GOATS_BANDS'):
                goat_bands = getGoatBands(goat['name'])
                for user in list(filter(lambda x : x.getBand() in goat_bands, USERS_ARR)):
                    try:
                        if user.getBirthday():
                            bday = datetime.fromtimestamp(user.getBirthday())
                            if now_date.day == bday.day and now_date.month == bday.month: 
                                msg = send_messages_big(goat['chats']['info'], f'{user.getNameAndGerb()} (@{user.getLogin()})!\n{getResponseDialogFlow(user.getLogin(), "happy_birthday").fulfillment_text}')
                                bot.pin_chat_message(goat['chats']['info'], msg.message_id )
                    except:
                        send_message_to_admin(f'⚠️🤬 Сломались при расчете дня рождения {user.getLogin()}!')

    # Присвоение званий
    if now_date.hour == 10 and now_date.minute == 1   and now_date.second < 15:
        logger.info('Присвоение званий!')
        try:
            report = ''
            updateUser(None)

            for goat in getSetting(code='GOATS_BANDS'):
                goat_bands = getGoatBands(goat['name'])
                
                for user in list(filter(lambda x : x.getBand() in goat_bands, USERS_ARR)):
                    if user.getRank() == None or user.getRank()['update'] == 'auto':
                        newRank = None
                        for rank in getSetting(code='RANK', id='MILITARY')['value']:
                            newRank = rank
                            if user.getBm() < rank['bm']:
                                break 
                        if not user.getRank() == None and newRank['id'] == user.getRank()['id']:
                            pass
                        else:
                            report = report + f'{newRank["bm"]} бандит {user.getNameAndGerb()} теперь {newRank["name"]}\n'
                            user.setRank(newRank)
                            updateUser(user)
                            time.sleep(1)
                            send_messages_big(goat['chats']['secret'], f'{user.getNameAndGerb()}!\n{getResponseDialogFlow(user.getLogin(), "set_new_rank").fulfillment_text}\n▫️  {newRank["name"]}')
                if report == '':
                    pass
                else:
                    send_message_to_admin(f"{goat['name']}\n\n{report}")
                report = ''
        except:
            send_message_to_admin(f'⚠️🤬 Сломалось Присвоение званий!')

    # Пидор дня
    if now_date.hour == 11 and now_date.minute == 11 and now_date.second < 15:
        
        logger.info('Pidor of the day!')
        updateUser(None)
        
        for goat in getSetting(code='GOATS_BANDS'):
            try:
                getPidorOfTheDay(goat, now_date)
            except:
                send_message_to_admin(f'⚠️🤬 Сломался Pidor of the day!\n▫️ {goat["name"]}')

    # Предупреждение о рейде за час, полчаса, 10 минут
    if now_date.hour in (0, 8, 16) and now_date.minute in (0, 30, 50) and now_date.second < 15:
        updateUser(None)
        for goat in getSetting(code='GOATS_BANDS'):
            try:
                # send_message_to_admin(f'⚠️ Предупреждение {goat["name"]}!')
                if getPlanedRaidLocation(goat['name'], planRaid = True)['rade_location']:
                    report = radeReport(goat, True)
                    # send_messages_big(497065022, text=f'<b>{str(60-now_date.minute)}</b> минут до рейда!\n' + report)
                    send_messages_big(goat['chats']['secret'], text=f'<b>{str(60-now_date.minute)}</b> минут до рейда!\n' + report)
            except:
                send_message_to_admin(f'⚠️🤬 Сломалось Предупреждение о рейде!')

    # Предварительные Отчет по рейду
    if now_date.hour in (1, 9, 17, 99) and now_date.minute in (5, 99) and now_date.second < 15:
        for goat in getSetting(code='GOATS_BANDS'):
            try:
                raidInfo = getPlanedRaidLocation(goat['name'], planRaid = False)
                if raidInfo['rade_location']:
                    report = radeReport(goat, planRaid=False)
                    date_str = time.strftime("%H:%M %d.%m", time.gmtime(( datetime.fromtimestamp(raidInfo["rade_date"]) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp()))
                    send_messages_big(goat['chats']['secret'], text=f'<b>Предварительные</b>\n<b>Результаты рейда {date_str}</b>\n' + report)
                    report = '⚠️ Если ты забыл сбросить форвард захвата, у тебя есть 30 минут с момента прожимания /voevat_suda, либо ты можешь присылать свою награду за рейд аж до 30 минут после рейда!!'
                    send_messages_big(goat['chats']['secret'], text=report)
            except:
                send_message_to_admin(f'⚠️🤬 Сломался Предварительные Отчет по рейду!')

    # Отчет по рейду
    if now_date.hour in (1, 9, 17, 99) and now_date.minute in (30, 99) and now_date.second < 15:
        logger.info('Rade time now!')
        updateUser(None)
        for goat in getSetting(code='GOATS_BANDS'):
            try:
                raidInfo = getPlanedRaidLocation(goat['name'], planRaid = False)
                if raidInfo['rade_location']:
                    report = radeReport(goat, ping=False, planRaid=False)
                    date_str = time.strftime("%H:%M %d.%m", time.gmtime(( datetime.fromtimestamp(raidInfo["rade_date"]) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp())) 
                    send_messages_big(goat['chats']['secret'], text=f'<b>Результаты рейда</b> {date_str}\n' + report)
                    # send_message_to_admin(f'<b>Результаты рейда {date_str}</b>\n' + report)
            except:
                send_message_to_admin(f'⚠️🤬 Сломался Отчет по рейду!')

    # Раздача рейдовых болтов
    if now_date.hour in (1, 9, 17, 99) and now_date.minute in (31 , 99) and now_date.second < 15:
        logger.info('raid bolt info!')
        updateUser(None)
        for goat in getSetting(code='GOATS_BANDS'):
            try:
                # выдаём болты
                setGiftsForRaid(goat)
            except:
                send_message_to_admin(f'⚠️🤬 Сломалась Раздача рейдовых болтов по {goat["name"]}')
    
    # Забывание навыков
    if now_date.hour in (14, 99) and now_date.minute in (28 , 99) and now_date.second < 15:
        logger.info('skill forgetting!')
        updateUser(None)
        for goat in getSetting(code='GOATS_BANDS'):
            
                goat_bands = getGoatBands(goat['name'])
                for user in list(filter(lambda x : x.getBand() in goat_bands and len(x.getInventoryType(['skill'])) > 0, USERS_ARR)):
                    for skill in user.getInventoryType(['skill']):
                        try:            
                            if 'forgetting' in skill:
                                newStorage = skill['storage'] -  skill['storage'] * skill['forgetting']
                                if newStorage > 0:
                                    skill.update({'storage': newStorage})

                                    if skill['flags']['congratulation_max'] == True and newStorage < skill['max']:
                                        skill['flags'].update({'congratulation_max': False})

                                    if skill['flags']['congratulation_min'] == True and newStorage < skill['min']:
                                        skill['flags'].update({'congratulation_min': False})
                                else:
                                    user.removeInventoryThing(skill)
                                    send_messages_big(goat['chats']['info'], text=f'{user.getNameAndGerb()} (@{user.getLogin()}) совсем разучился в умении:\n▫️ {skill["name"]}') 
                        except:
                            send_message_to_admin(f'⚠️🤬 Для бандита {user.getNameAndGerb()} (@{user.getLogin()}) сломалось забывание скила {skill["name"]} по {goat["name"]}')
                    updateUser(user)

    # Отъем болтов
    if now_date.hour in (99, 99) and now_date.minute in (99, 99) and now_date.second < 15:
        u = ['GonzikBenzyavsky', 'Hermia_Nerbne', 'StiffD', 'rocknrolla_777', 'DeadChild', 'WildFire112', 'aohanesian', 'UmnikOff_Vodkin', 'RVM362', 'Java_dentist', 'VTZVTZ', 'MrMrakZ', 'eX3emz', 'chymych', 'striletskyi', 'Lixetini', 'rock_n_rolla01', 'sosopiple']
        antyBoltReport = ''
        counter = 0
        for login in u:
            user = getUserByLogin(login)
            if user:
                
                #acc = '🎫🍼 Билет на гигантскую бутылку'
                bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_5'), None)
                if user.isInventoryThing(bolt):
                    pass
                else:
                    #acc = '🔩🔩🔩🔩 Болт М1488, возложенный на рейд'
                    bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_4'), None)
                    if user.isInventoryThing(bolt):
                        pass
                    else:
                        #acc = '🔩🔩🔩 Болт М404, возложенный на рейд'
                        bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_3'), None)
                        if user.isInventoryThing(bolt):
                            pass
                        else:
                            #acc = '🔩🔩 Болт М228, возложенный на рейд'
                            bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_2'), None)
                            if user.isInventoryThing(bolt):
                                pass
                            else:
                                #acc = '🔩 Болт М69, возложенный на рейд'
                                bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_1'), None)
                                if user.isInventoryThing(bolt):
                                    pass
                                else:
                                    continue
                if user.isInventoryThing(bolt):
                    # send_message_to_admin(f'❎ {user.getNameAndGerb()} @{user.getLogin()}\nЗабрали:\n▫️ {bolt["name"]}!')
                    counter = counter + 1
                    user.removeInventoryThing(bolt)
                    # send_messages_big(goat['chats']['secret'], text=user.getNameAndGerb() + '!\n' + '❎ Ты сдал в общак банды:' + f'\n\n▫️ {bolt["name"]}')    
                    updateUser(user)
                    antyBoltReport = antyBoltReport + f'{counter}. @{user.getLogin()} {user.getNameAndGerb()} {bolt["name"].split(" ")[0]}\n'
        send_message_to_admin(f'🔩 Сдали болты:\n'+antyBoltReport)

    # Проверка на дубликаты бандитов
    # Неправильно работает - не проверяет дубли по Фракции
    if False and now_date.hour in (9,10,11,12,13,14,15,16,17,18,19,20,21,22) and now_date.minute in (0, 3, 10,20,30,40,50) and now_date.second < 15:
        dresult = registered_wariors.aggregate([ 
                                                {   "$group": {
                                                    "_id": "$name", 
                                                    "count": {
                                                        "$sum": 1}}},
                                                {   "$sort" : { "count" : -1 } }
                                                ])
        i = 0
        result = ''
        for d in dresult:
            if d.get("count") > 1:
                i = i + 1
                result = result + f'{i}. {d.get("_id")} {d.get("count")}\n'
                dresult2 = registered_wariors.aggregate([ 
                    {   "$match": {
                                "name": d.get("_id")
                            } 
                    },   
                    {   "$sort" : { "timeUpdate" : 1 } }
                    ])
                z = 1
                for m in dresult2:
                    if z == d.get("count"): break
                    string =  f'    ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(m.get("timeUpdate")))
                    #print(m.get('_id'))
                    registered_wariors.delete_many({'_id': m.get('_id')})
                    z = z + 1
        if i > 0:
            send_message_to_admin(f'👥 Удалены дубликаты бандитов:\n{result}')


def getPidorOfTheDay(goat, now_date):
    user_in_game = []
    goat_bands = getGoatBands(goat['name'])
    for user in list(filter(lambda x : x.getBand() and x.getBand() in goat_bands, USERS_ARR)):
        usersettings = getUserSetting(user.getLogin(), '👨‍❤️‍👨Участник "Пидор дня"')
        if usersettings:
            user_in_game.append(user)

    chat = goat['chats']['info']
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
            if user_login == userWin.getLogin(): continue
            user = getUserByLogin(user_login)
            if user:
                if user.getBand() and user.getBand() in goat_bands:
                    old_pidors.append(user)

        pidor1 = None
        pidor2 = None

        twoPidors = '🤖 Джу и его подруга 👾 Бозя'
        if len(old_pidors)>1:
            pu = random.sample(old_pidors, 1)[0]
            pidor1 = pu.getNameAndGerb()
            old_pidors.remove(pu)
            pidor2 = random.sample(old_pidors, 1)[0].getNameAndGerb()
            twoPidors = f'👬 Два бывалых пидора, {pidor1} и {pidor2},'

        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='REWARDS')['value']) if x['id']=='crown_pidor'), None).copy()
        # acc = '👑 "Пидор дня"'

        lastWinner = None
        for user in list(filter(lambda x : x.getBand() and x.getBand() in goat_bands, USERS_ARR)):
            if user.isInventoryThing(elem):
                user.removeInventoryThing(elem)
                updateUser(user)
                lastWinner = user
                break
        
        send_message_to_admin(f'👨‍❤️‍💋‍👨 Пидор дня!\nВ конкурсе "👨‍❤️‍💋‍👨 Пидор дня" сегодня побеждает:\n▫️ {goat["name"]}\n▫️ {userWin.getNameAndGerb()} (@{userWin.getLogin()})!')

        if lastWinner:
            text = f'🎊🎉🍾 Поздравляю!\nВ конкурсе "👨‍❤️‍💋‍👨 Пидор дня" сегодня побеждает...\n {userWin.getNameAndGerb()} (@{userWin.getLogin()})!\n\n {twoPidors} вырвали из рук {lastWinner.getNameAndGerb()} 👑 золотую корону с гравировкой "Pidor of the day" и передали её главе козла!\n 🎁 Самое время поздравить сегодняшнего победителя!\n\n▫️ {elem["name"]}'
            if lastWinner.getLogin() == userWin.getLogin():
                text = f'🎊🎉🍾 Поздравляю!\nВ конкурсе "👨‍❤️‍💋‍👨 Пидор дня" сегодня побеждает...\n {userWin.getNameAndGerb()} (@{userWin.getLogin()})!\n\n {twoPidors} в шоке! Кому ты отдался, чтобы выигрывать так часто?!! 👑 золотая корона с гравировкой "Pidor of the day" остаётся у тебя !\n 🎁 Самое время поздравить сегодняшнего победителя!\n\n▫️ {elem["name"]}'
        else:
            text = f'🎊🎉🍾 Поздравляю!\nВ конкурсе "👨‍❤️‍💋‍👨 Пидор дня" сегодня побеждает...\n {userWin.getNameAndGerb()} (@{userWin.getLogin()})!\n\n {twoPidors} взяли со склада 👑 золотую корону с гравировкой "Pidor of the day" и передали её главе козла!\n🎁 Самое время поздравить сегодняшнего победителя!\n\n▫️ {elem["name"]}'

        addInventory(userWin, elem)
        updateUser(userWin)
        row = {}
        row.update({'date':now_date.timestamp()})
        row.update({'login':userWin.getLogin()})
        row.update({'description':elem['name']})
        man_of_day.insert_one(row)

        send_messages_big(chat, text=text)
        send_messages_big(chat, text=userWin.getNameAndGerb() + '!\n' + getResponseDialogFlow(userWin.getLogin(), 'new_accessory_add').fulfillment_text + f'\n\n▫️ {elem["name"]}') 
        send_messages_big(chat, text=report_man_of_day(userWin.getLogin())) 

def getPlanedRaidLocation(goatName: str, planRaid = True): 
    tz = config.SERVER_MSK_DIFF
    raid_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
    hour = raid_date.hour

    if not planRaid and raid_date.hour < 1:
        raid_date = raid_date - timedelta(days=1)

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
    
    logger.info(f'==============={goatName}===============')
    raidNone = {}
    raid_date = raid_date.replace(hour=hour, minute=0, second=0, microsecond=0)
    raid_date = raid_date - timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
    raidNone.update({'rade_date': (raid_date).timestamp()})
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
        logger.info(raid)
        if (datetime.fromtimestamp(raid.get('rade_date')) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour) ).hour == hour:
            return raid
    return raidNone

def getRaidTimeText(text, date):
    tz = config.SERVER_MSK_DIFF
    date = (datetime.fromtimestamp(date) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)).timestamp()
    hour = 0
    minute = 0
    second = 0
    result = None
    if len(text)>0:
        if 'ч.' in text:
            hour = int(text.split('ч.')[0].strip())   
            minute = int(text.split(' ')[1].split('мин.')[0].strip()) 
        elif 'мин.' in text:
            minute = int(text.split('мин.')[0].strip())
        elif 'сек.' in text:
            second = int(text.split('сек.')[0].strip())
        result =  datetime.fromtimestamp(date) + timedelta(seconds=second, minutes=minute, hours=hour)
        hour = round((result.hour*60 + result.minute)/60)       
    else:
        d = datetime.fromtimestamp(date) 
        logger.info(f'1: {d} {hour}')
        if d.hour >= 17:
            d = d + timedelta(days=1)
            hour = 1
            logger.info(f'2: {d} {hour}')
        elif d.hour < 1:
            hour = 1
            logger.info(f'3: {d} {hour}')
        elif d.hour >=1 and d.hour < 9:
            hour = 9
            logger.info(f'4: {d} {hour}')
        elif d.hour >=9 and d.hour < 17:
            hour = 17
            logger.info(f'5: {d} {hour}')
        result =  d

    
    result = result.replace(hour=hour, minute=0, second=0, microsecond=0)
    return result.timestamp()

def getRaidTime(planRaid):
    tz = config.SERVER_MSK_DIFF
    raid_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
    hour = raid_date.hour
    if not planRaid and raid_date.hour <= 1:
        raid_date = raid_date - timedelta(days=1)

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
    return raid_date.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp()

def saveUserRaidResult(user, date, location, planed_location=None):
    # if location <= 0:
    #     result = report_raids.delete_one({"login": f"{user.getLogin()}", 'date': date})
    #     return

    row = {}
    row.update({'date': date })
    row.update({'login': user.getLogin()})
    row.update({'band': user.getBand()})
    row.update({'goat': getMyGoatName(user.getLogin())})
    
    if location or location == 0:
        row.update({'user_location': location})
        if location > 0:        
            row.update({'on_raid': True})
        else:
            row.update({'on_raid': False})

    if planed_location or planed_location == 0:
        row.update({'planed_location': planed_location})
        row.update({'notified': False})

    newvalues = { "$set": row }
    result = report_raids.update_one({"login": f"{user.getLogin()}", 'date': date}, newvalues)
    if result.matched_count < 1:
        report_raids.insert_one(row)

def saveRaidResult(goat):
    logger.info(f"saveRaidResult : {goat.get('name')}")
    raid = getPlanedRaidLocation(goat['name'], planRaid=False)
    location = raid.get('rade_location')
    raiddate = raid.get('rade_date')
    logger.info(raid)

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
                if user.getRaidLocation() and user.getRaidLocation() > 0:
                    row.update({'on_raid': True}) 
                    row.update({'user_location': user.getRaidLocation()})    
                    if location and user.getRaidLocation() == location:
                        row.update({'planed_location': True})
                newvalues = { "$set": row }
                result = report_raids.update_one({"login": f"{user.getLogin()}", 'date': raiddate}, newvalues)
                if result.matched_count < 1:
                    report_raids.insert_one(row)

def radeReport(goat, ping=False, planRaid=True):
    updateUser(None)
    
    raidInfo = getPlanedRaidLocation(goat.get('name'), planRaid)
    # send_message_to_admin(f'⚠️ radeReport ⚠️\n{datetime.fromtimestamp(raidInfo["rade_date"])}\n{raidInfo}')
    # logger.info(raidInfo)

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

                user.setRaidLocation(0)
                for uonr in report_raids.find({'login': user.getLogin(), 'date': raidInfo['rade_date']}):
                    if 'user_location' in uonr:
                        user.setRaidLocation(uonr['user_location'])


                if user.getRaidLocation() and user.getRaidLocation()>0:
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
                # 497065022
                ping_on_raid(bands.get("usersoffrade"), goat['chats']['secret'], raidInfo, goat['name'])
    return report

def setGiftsForRaid(goat):
    raidPlan = getPlanedRaidLocation(goatName=goat['name'], planRaid=False)
    # send_message_to_admin(f'⚠️ setGiftsForRaid ⚠️\n{raidPlan}')
    if not raidPlan['rade_location']:
        return

    # raidPlan.update({'rade_date':(datetime(2020, 3, 14, 17, 0)).timestamp() })
    # send_message_to_admin(f'⚠️🔩 Раздача болтов {goat["name"]}!\nРейд {raidPlan["rade_date"]}: {datetime.fromtimestamp(raidPlan["rade_date"])}⚠️')
    
    
    boltReport = ''
    counter = 0
    users_on_raid = [] 

    users_true = []
    users_false = []
    goat_bands = getGoatBands(goat['name'])
    for user in list(filter(lambda x : x.getBand() in goat_bands, USERS_ARR)):
        find = False
        for uonr in report_raids.find({'login': user.getLogin(), 'date': raidPlan['rade_date']}):
            if 'on_raid' in uonr:
                user.setRaidLocation(uonr['user_location'])
                if uonr['on_raid'] == True:
                    find = True
        if find:
            users_true.append(user.getLogin())
        else:
            users_false.append(user.getLogin())

    for raid_user in users_false:
        user = getUserByLogin(raid_user)
        if user:
            counter = counter + 1
            #acc = '🔩 Болт М69, возложенный на рейд'
            bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_1'), None)

            if user.isInventoryThing(bolt):
                #acc = '🔩🔩 Болт М228, возложенный на рейд'
                bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_2'), None)

                if user.isInventoryThing(bolt):
                    #acc = '🔩🔩🔩 Болт М404, возложенный на рейд'
                    bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_3'), None)

                    if user.isInventoryThing(bolt):
                        #acc = '🔩🔩🔩🔩 Болт М1488, возложенный на рейд'
                        bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_4'), None)

                        if user.isInventoryThing(bolt):
                            #acc = '🎫🍼 Билет на гигантскую бутылку'
                            bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_5'), None)

                            if user.isInventoryThing(bolt):
                                boltReport = boltReport + f'{counter}. ⚠️ {user.getLogin()} {user.getNameAndGerb()}\n'
                                #send_message_to_admin(f'⚠️ {user.getNameAndGerb()} {user.getLogin()}\nНа выход за проёбы рейдов!')
                                continue

            # send_message_to_admin(f'⚠️ {user.getNameAndGerb()} @{user.getLogin()}\n▫️ {bolt["name"]}!')
            addInventory(user, bolt)
            #send_messages_big(goat['chats']['secret'], text=user.getNameAndGerb() + '!\n' + getResponseDialogFlow(None, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {bolt["name"]}')    
            users_on_raid.append(
                        {
                            'login': user.getLogin(),
                            'bolt': bolt
                        }
                    )
            updateUser(user)
            boltReport = boltReport + f'{counter}. {"@" if user.isPing() else ""}{user.getLogin()} {user.getNameAndGerb()} {bolt["name"].split(" ")[0]}\n'
    if counter > 0:
        for userWin in random.sample(users_on_raid, 2):
            sec = int(10)
            pending_date = datetime.now() + timedelta(seconds=sec)
            text = f''
            pending_messages.insert_one({ 
                'chat_id': goat['chats']['secret'],
                'reply_message': None,
                'create_date': datetime.now().timestamp(),
                'user_id': userWin['login'],  
                'state': 'WAIT',
                'pending_date': pending_date.timestamp(),
                'dialog_flow_text': f'bolt_congratulation_{userWin["bolt"]["id"]}',
                'dialog_flow_context': {'bolt': userWin['bolt']['name']},
                'text': text})
        boltReport = '<b>Получили болты 🔩</b>\n' + boltReport
    
    users_on_raid = [] 
    antyBoltReport = ''
    counter = 0

    for raid_user in users_true:
        user = getUserByLogin(raid_user)
        # Снимаем больы, если последние два рейда были зачетными
        counter_r = report_raids.find({'login': user.getLogin()}).count()
        N = 2
        if counter_r < N:
                continue
        cursor = report_raids.find({'login': user.getLogin()}).skip(counter_r - N)
        alltrue = True
        for x in cursor:
            if "on_raid" in x and not x["on_raid"]:
                alltrue = False 
        if not alltrue: 
            continue

        if user:
            
            #acc = '🎫🍼 Билет на гигантскую бутылку'
            bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_5'), None)
            if user.isInventoryThing(bolt):
                pass
            else:
                #acc = '🔩🔩🔩🔩 Болт М1488, возложенный на рейд'
                bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_4'), None)
                if user.isInventoryThing(bolt):
                    pass
                else:
                    #acc = '🔩🔩🔩 Болт М404, возложенный на рейд'
                    bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_3'), None)
                    if user.isInventoryThing(bolt):
                        pass
                    else:
                        #acc = '🔩🔩 Болт М228, возложенный на рейд'
                        bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_2'), None)
                        if user.isInventoryThing(bolt):
                            pass
                        else:
                            #acc = '🔩 Болт М69, возложенный на рейд'
                            bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_1'), None)
                            if user.isInventoryThing(bolt):
                                pass
                            else:
                                continue

            if user.isInventoryThing(bolt):
                counter = counter + 1
                # send_message_to_admin(f'❎ {user.getNameAndGerb()} @{user.getLogin()}\nЗабрали:\n▫️ {bolt["name"]}!')
                user.removeInventoryThing(bolt)
                # send_messages_big(goat['chats']['secret'], text=user.getNameAndGerb() + '!\n' + '❎ Ты сдал в общак банды:' + f'\n\n▫️ {bolt["name"]}')    
                antyBoltReport = antyBoltReport + f'{counter}. {user.getNameAndGerb()} {bolt["name"].split(" ")[0]}\n'
            users_on_raid.append(
                    {
                        'login': user.getLogin(),
                        'bolt': bolt
                    }
                )
            updateUser(user)
    if counter > 0:
        for userWin in random.sample(users_on_raid, 2):
            sec = int(20)
            pending_date = datetime.now() + timedelta(seconds=sec)
            text = f''
            pending_messages.insert_one({ 
                'chat_id': goat['chats']['secret'],
                'reply_message': None,
                'create_date': datetime.now().timestamp(),
                'user_id': userWin['login'],  
                'state': 'WAIT',
                'pending_date': pending_date.timestamp(),
                'dialog_flow_text': f'bolt_remove_{userWin["bolt"]["id"]}',
                'dialog_flow_context': {'bolt': userWin['bolt']['name']},
                'text': text})
        antyBoltReport = '<b>Сдали болты ❎</b>\n' + antyBoltReport

    if (not boltReport == '') or (not antyBoltReport == ''):
        send_message_to_admin(text='🔩 Болты:\n' + boltReport + '\n' + antyBoltReport)
        send_messages_big(goat['chats']['secret'], text=boltReport + '\n' + antyBoltReport)

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
        
        if user:
            name = user.getNameAndGerb().strip()
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

        # if isGoatBoss(name):
        #     report_boss = report_boss + f'Еще наш босс не был на некоторых рейдах, потому что был зянят переписью хренейдеров, забивших на общие цели! Это, надеюсь, всем понятно?!\n'
        #     report_boss = '\n'+report_boss
        #     continue
        user = getUserByLogin(name)
        login = name
        if user:
            name = user.getNameAndGerb().strip()

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