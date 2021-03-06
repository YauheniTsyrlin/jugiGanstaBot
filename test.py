#!/usr/bin/env python
 
from datetime import datetime
from datetime import timedelta
import time
from dateutil.parser import parse
from bson.objectid import ObjectId
import pymongo
import config
import tools
import json
import sys
import random
from functools import reduce

import users 
import wariors
import tools
	
import hashlib

from operator import itemgetter
import itertools

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jugidb"]
registered_users = mydb["users"]
registered_wariors = mydb["wariors"]
battle      = mydb["battle"]
competition = mydb["competition"]
settings    = mydb["settings"]
pending_messages = mydb["pending_messages"]
plan_raids      = mydb["rades"]
report_raids    = mydb["report_raids"]
plan_raids      = mydb["rades"]
dungeons        = mydb["dungeons"]
mob             = mydb["mob"]
pip_history     = mydb["pip_history"]
man_of_day      = mydb["man_of_day"]
shelf           = mydb["shelf"]
workbench       = mydb["workbench"]
farm            = mydb["farm"]
deal            = mydb["deal"]
announcement    = mydb["announcement"]

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

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

def setSetting(code: str, value: str):
    
    """ Сохранение настройки """
    myquery = { "code": code }
    newvalues = { "$set": { "value": json.dumps(value) } }
    u = settings.update_one(myquery, newvalues)

    SETTINGS_ARR.clear() # Зарегистрированные настройки
    for setting in settings.find():
        SETTINGS_ARR.append(setting)
    return True

def getUserByLogin(login: str):
    for user in list(USERS_ARR):
        try:
            if login.lower() == user.getLogin().lower(): return user
        except:
            pass
    return None

def isGoatBoss(login: str):
    for goat in getSetting('GOATS_BANDS'):
        if goat['boss'] == login:
            return True
    return False

def getGoatBands(goatName: str):
    for goat in getSetting('GOATS_BANDS'):
        if goat.get('name') == goatName:
            bands = []
            for band in goat['bands']:
                bands.append(band.get('name'))
            return bands
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

def radeReport(goat):
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

    report = f'🐐<b>{goat_report.get("name")}</b>\n\n'
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
                report = report + f'{counter}. @{u.getLogin()} 📍{u.getRaidLocation()}км\n'
            report = report + f'\n'

        if len(bands.get("usersoffrade")):
            counter = 0
            report = report + f'🐢 <b>Бандиты в проёбе</b>:\n'
            for u in bands.get("usersoffrade"):
                counter = counter + 1
                report = report + f'{counter}. @{u.getLogin()}\n'
            report = report + f'\n'

    return report

def getPlanedRaidLocation(goatName: str, planRaid = True):
    tz = config.SERVER_MSK_DIFF
    raid_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour-23)
    print(raid_date)
    print(planRaid)
    print(raid_date.hour)
    hour = raid_date.hour

    if not planRaid and raid_date.hour < 1:
        raid_date = raid_date - timedelta(days=1)
        print('<1')

    if planRaid and raid_date.hour >= 17:
        raid_date = raid_date + timedelta(days=1)
        print('>17')

    if raid_date.hour >=17 or raid_date.hour <1:
        hour = 1
        if not planRaid:
            print('17-1')
            hour = 17
    if raid_date.hour >=1 and raid_date.hour <9:
        hour = 9
        if not planRaid:
            print('1-9')
            hour = 1
    elif raid_date.hour >=9 and raid_date.hour <17:
        hour = 17
        if not planRaid:
            print('9-17')
            hour = 9


    print(f'hour = {hour}')
    print(raid_date.replace(hour=hour, minute=0, second=0, microsecond=0))
    print(f'==========================')
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
    raid = getPlanedRaidLocation(goat['name'])
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

def statistic(goatName: str): 
    report = f'🐐<b>{goatName}</b>\n\n'
    report = report + f'🧘‍♂️ <b>Рейдеры</b>:\n'

    setting = getSetting('REPORTS','RAIDS')
    from_date = setting.get('from_date')
    to_date = setting.get('to_date')

    #if (not from_date):
    from_date = (datetime(2019, 1, 1)).timestamp() 

    if (not to_date):
        to_date = (datetime.now() + timedelta(minutes=180)).timestamp()

    dresult = report_raids.distinct('date', {"$and" : [
                    { 
                        "date": {
                            '$gte': from_date,
                            '$lt': to_date
                                }       
                    }
                ]})
    for d in dresult:
        print(str(datetime.fromtimestamp(d)))

    for x in report_raids.find({"$and" : [
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
                        "login": "Ilya_Belyaev"
                    }
                ]}):
        print(x["login"]+ " " + str(x["date"]) + str(datetime.fromtimestamp(x["date"])))

    report =  f'👊<b>{len(dresult)}</b> рейдов\n' + report

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
        report = report + f'{count} {name} \n'

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

    report = report + f'\n🤬 <b>Хренейдеры</b>:\n'
    for d in dresult:
        name = d.get("_id")
        count = d.get("count")
        if isGoatBoss(name):
            report_boss = report_boss + f'Еще наш босс не был на некоторых рейдах, потому что был зянят переписью хренейредоров, забивших на общие цели! Это, надеюсь, всем понятно?!\n'
            report_boss = '\n'+report_boss
            continue
        user = getUserByLogin(name)
        
        if user:
            name = user.getName().strip()
        report = report + f'{count} {name} \n'

    report = report + report_boss + f'\n' 
    report = report + '⏰ c ' + time.strftime("%d-%m-%Y", time.gmtime(from_date)) + ' по ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(to_date))

    return report                                 
        

print('\n======== radeReport ==========\n')

# for u in pip_history.find():
#     print(u)
# raid = getPlanedRaidLocation('FǁȺǁggǁØǁAT', False)
# print(raid)
# print(datetime.fromtimestamp(raid["rade_date"]))
# import itertools
# from operator import itemgetter

# inventory_arr = getSetting(code='ACCESSORY_ALL', id='REWARDS')['value'] + getSetting(code='ACCESSORY_ALL', id='THINGS')['value']  + getSetting(code='ACCESSORY_ALL', id='EDIBLE')['value']

def getWariorByName(name: str, fraction: str):
    name = tools.deEmojify(name).strip()
    for warior in list(WARIORS_ARR):
        if name == warior.getName().strip() and (fraction == None or fraction == warior.getFraction()): 
            return warior
    return None

#

def setGiftsForRaid(goat):
    raidPlan = getPlanedRaidLocation(goatName=goat['name'], planRaid=False)
    # raidPlan.update({'rade_date':(datetime(2020, 3, 14, 17, 0)).timestamp() })
    # send_message_to_admin(f'⚠️Рейд {datetime.fromtimestamp(raidPlan["rade_date"])}⚠️')
    print(raidPlan)
    boltReport = ''
    counter = 0
    for raid in report_raids.find(
        {   "date": raidPlan['rade_date'],
            "band": {'$in': getGoatBands(goat['name'])},
            "on_raid": False,
            "planed_location": {'$ne':None}   
        }):
        
        user = getUserByLogin(raid["login"])
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
            user.addInventoryThing(bolt, bolt['quantity'])
            #send_messages_big(goat['chats']['secret'], text=user.getNameAndGerb() + '!\n' + getResponseDialogFlow(None, 'new_accessory_add').fulfillment_text + f'\n\n▫️ {bolt["name"]}')    
            updateUser(user)
            boltReport = boltReport + f'{counter}. {bolt["name"].split(" ")[0]} {"@" if user.isPing() else ""}{user.getLogin()} {user.getNameAndGerb()}\n'
    if counter > 0:
        boltReport = '<b>Получили болты 🔩</b>\n' + boltReport
    
    antyBoltReport = ''
    counter = 0
    for raid in report_raids.find(
            {   "date": raidPlan['rade_date'],
                "band": {'$in': getGoatBands(goat['name'])},
                "on_raid": True,
                "planed_location": {'$ne':None}   
            }):
            user = getUserByLogin(raid["login"])

            # Снимаем больы, если последние два рейда были зачетными
            counter_r = report_raids.find({'login': user.getLogin()}).count()
            N = 2
            if counter_r < N:
                continue
            cursor = report_raids.find({'login': user.getLogin()}).skip(counter_r - N)
            alltrue = True
            for x in cursor:
                if not x["on_raid"]:
                    alltrue = False 
            if not alltrue: 
                continue

            if user:
                counter = counter + 1
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
                    user.removeInventoryThing(bolt)
                    # send_messages_big(goat['chats']['secret'], text=user.getNameAndGerb() + '!\n' + '❎ Ты сдал в общак банды:' + f'\n\n▫️ {bolt["name"]}')    
                    updateUser(user)
                    antyBoltReport = antyBoltReport + f'{counter}. {bolt["name"].split(" ")[0]} {user.getNameAndGerb()}\n'
    if counter > 0:
        antyBoltReport = '<b>Сдали болты ❎</b>\n' + antyBoltReport

    if (not boltReport == '') or (not antyBoltReport == ''):
        print(boltReport + '\n' + antyBoltReport)
        #send_message_to_admin(text=boltReport + '\n' + antyBoltReport)
        #send_messages_big(goat['chats']['secret'], text=boltReport + '\n' + antyBoltReport)

def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None, limit=None, step=None, back_button=None, exit_button=None, forward_button=None ):
    if limit==None: 
        limit=len(buttons)
        step = 0 
    menu = [
                buttons [i:i + n_cols] for i in range(step*limit, (step+1)*limit if (step+1)*limit < len(buttons) else len(buttons), n_cols)
            ]
    
    if back_button:
        if step==0:
            manage_buttons = [exit_button, forward_button]
        elif (step+1)*limit > len(buttons):
            manage_buttons = [back_button, exit_button]
        else:
            manage_buttons = [back_button, exit_button, forward_button]
        menu = menu + [manage_buttons [i:i + n_cols] for i in range(0, len(manage_buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu

buttons = ['1', '1', '1', '2','2','2', '1','2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16']
chat = 'chat_id'
GLOBAL_VARS = {
    'inventory': getSetting(code='ACCESSORY_ALL', id='REWARDS')['value'] + getSetting(code='ACCESSORY_ALL', id='THINGS')['value'] + getSetting(code='ACCESSORY_ALL', id='EDIBLE')['value'] + getSetting(code='ACCESSORY_ALL', id='TATU')['value'] + getSetting(code='ACCESSORY_ALL', id='CLOTHES')['value'] + getSetting(code='ACCESSORY_ALL', id='MARKS_OF_EXCELLENCE')['value'] + getSetting(code='ACCESSORY_ALL', id='POSITIONS')['value'],
    'chat_id':
                {
                    'inventory':getSetting(code='ACCESSORY_ALL', id='VIRUSES')['value']
                },
    'bosses': ['Танкобот','Яо-гай','Супермутант-конг','Квантиум','Коготь смерти'] 
}

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
    print(raid_date.replace(hour=hour, minute=0, second=0, microsecond=0))
    return raid_date.replace(hour=hour, minute=0, second=0, microsecond=0).timestamp()

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
        if d.hour >= 17:
            d = d + timedelta(days=1)
            hour = 1
        elif d.hour < 1:
            hour = 1
        elif d.hour >=1 and d.hour < 9:
            hour = 9
        elif d.hour >=9 and d.hour < 17:
            hour = 17
        result =  d
    
    result = result.replace(hour=hour, minute=0, second=0, microsecond=0)
    return result.timestamp()

def getMyGoatName(login: str):
    user = getUserByLogin(login)
    if not user:
        return None

    for goat in getSetting(code='GOATS_BANDS'):
        for band in goat['bands']:
            if user.getBand() and user.getBand().lower() == band.get('name').lower():
                return goat['name']

    return None 

def getUserSetting(login: str, name: str):
    user = getUserByLogin(login)
    for sett in user.getSettings():
        if sett["name"] == name:
            return sett
    return None

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
            print(f'{user.getLogin()} {goatName} {getMyGoatName(user.getLogin())}')
            if goatName == getMyGoatName(user.getLogin()):
                goat_users.append({'user': user, 'count': d.get("count")})


    # acc = '👑 "Пидор дня"'
    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='REWARDS')['value']) if x['id']=='crown_pidor_of_the_day'), None)

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

def getPidorOfTheDay(goat, now_date):
    user_in_game = []
    goat_bands = getGoatBands(goat)

    print(goat_bands)

    for user in list(filter(lambda x : x.getBand() and x.getBand() in goat_bands, USERS_ARR)):
        usersettings = getUserSetting(user.getLogin(), '👨‍❤️‍👨Участник "Пидор дня"')
        if usersettings:
            user_in_game.append(user)

    # chat = goat['chats']['info']
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

        print(goat_bands)
        old_pidors = []
        for d in dresult:
            user_login = d.get("_id")
            print(f'{user_login}' )
            if user_login == userWin.getLogin(): 
                print(f'!!!! pass' )
                continue
            user = getUserByLogin(user_login)
            if user:
                
                if user.getBand() and user.getBand() in goat_bands:
                    print(f'FIND! {user.getLogin()}')
                    old_pidors.append(user)
        print(len(old_pidors))
        pidor1 = None
        pidor2 = None
        twoPidors = '🤖 Джу и его подруга 👾 Бозя'
        if len(old_pidors)>1:
            pu = random.sample(old_pidors, 1)[0]
            pidor1 = pu.getNameAndGerb()
            old_pidors.remove(pu)
            pidor2 = random.sample(old_pidors, 1)[0].getNameAndGerb()
            twoPidors = f'👬 Два бывалых пидора, {pidor1} и {pidor2},'

        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='REWARDS')['value']) if x['id']=='crown_pidor_of_the_day'), None)
        # acc = '👑 "Пидор дня"'

        lastWinner = None
        for user in list(filter(lambda x : x.getBand() and x.getBand() in goat_bands, USERS_ARR)):
            if user.isInventoryThing(elem):
                user.removeInventoryThing(elem)
                updateUser(user)
                lastWinner = user
                break
        
        if lastWinner:
            text = f'Поздравляю!\nВ конкурсе "Пидор дня" сегодня побеждает...\n{userWin.getNameAndGerb()} (@{userWin.getLogin()})!\n\n{twoPidors} вырвали из рук {lastWinner.getNameAndGerb()} золотую корону с гравировкой "Pidor of the day" и передали её главе козла!\n Самое время поздравить сегодняшнего победителя!\n\n▫️ {elem["name"]}'
            if lastWinner.getLogin() == userWin.getLogin():
                text = f'🎊🎉🍾 Поздравляю!\nВ конкурсе "👨‍❤️‍💋‍👨 Пидор дня" сегодня побеждает...\n{userWin.getNameAndGerb()} (@{userWin.getLogin()})!\n\n {twoPidors} в шоке! Кому ты отдался, чтобы выигрывать так часто?!! 👑 золотая корона с гравировкой "Pidor of the day" остаётся у тебя !\n🎁 Самое время поздравить сегодняшнего победителя!\n\n▫️ {elem["name"]}'
        else:
            text = f'🎊🎉🍾 Поздравляю!\nВ конкурсе "👨‍❤️‍💋‍👨 Пидор дня" сегодня побеждает...\n{userWin.getNameAndGerb()} (@{userWin.getLogin()})!\n\n{twoPidors} достали со склада 👑 золотую корону с гравировкой "Pidor of the day" и передали её главе козла!\n🎁 Самое время поздравить сегодняшнего победителя!\n\n▫️ {elem["name"]}'

        # addInventory(userWin, elem)
        # updateUser(userWin)
        row = {}
        row.update({'date':now_date.timestamp()})
        row.update({'login':userWin.getLogin()})
        row.update({'description':elem['name']})
        man_of_day.insert_one(row)

        return f'⚠️🤬 Pidor of the day!\n\n {text}'


# print(report_man_of_day('GonzikBenzyavsky'))
# tz = config.SERVER_MSK_DIFF
# now_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
# print(getPidorOfTheDay('New Vegas', now_date))

# tt = ['7ч. 27мин.', '3ч. 0мин.', '1 мин.', '10 сек.', '1ч. 15мин.']
# ttt = [ '1ч. 15мин.']
# for t in ttt:

# print(f"{int('0')}")

# import uuid
# print(uuid.uuid4())

# dateT = 1587911050
# date = getRaidTimeText('', dateT)
# print(f'{datetime.fromtimestamp(dateT)} {datetime.fromtimestamp(date)}')

# for i in range(0,24):
#     dateT = datetime.now().replace(hour=i, minute=0, second=0, microsecond=0).timestamp()
#     date = getRaidTimeText('', dateT)
#     print(f'{i} {datetime.fromtimestamp(dateT)} {datetime.fromtimestamp(date)}')

#tz = config.SERVER_MSK_DIFF
#ticket = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']=='redeemed_raid_ticket'), None)             
#date_stamp = getRaidTimeText("1ч. 15мин.", 1586177073)
#date_str = time.strftime("%d.%m %H:%M", time.gmtime( (datetime.fromtimestamp(date_stamp) + timedelta(hours=tz.hour)).timestamp()))

# searchfor = ['опустошил бокал бурбона.', 'жадно ест сухари.']
# searchstr = 'опустошил бокал бурбона. жадно'
# if len([ele for ele in searchfor if(ele in searchstr)])>0:
#     print('res')


# print(getWariorByName('КириλλǁȺǁ','⚙️Убежище 4').getBm())

# send_messages_big(message.chat.id, text=getResponseDialogFlow(message.from_user.username, 'shot_message_zbs').fulfillment_text + 
#     f'\nВ специальном паркомате на рейдовой точке ты взял талончик на рейд:\n▫️ 🎫 Талон на рейд {date_str}')


#getRaidTime(False)
#print(viruses_in)

#GLOBAL_VARS[chat]['inventory'].append([x for x in viruses_in])

#print('==========================================')
#print(GLOBAL_VARS[chat]['inventory'])

# print(build_menu(buttons, 3, limit=6, step=1, back_button='back', forward_button='forward', exit_button='exit'))

# position = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='POSITIONS')['value']) if x['id']=='electrician_1'), None)
# print(position)                
#user = getUserByLogin('GonzikBenzyavsky')


# medic = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='medic'), None) 
# for user in sorted(list(filter(lambda x : x.getInventoryThingCount(medic) > 0, USERS_ARR)), key = lambda i: i.getInventoryThing(medic)['storage'], reverse=True):
#     print(user.getLogin() + "|"+ str(user.getInventoryThing(medic)['storage']))


# report_raids.delete_many({'date': 1588716000})
# counter = report_raids.find({'login': user.getLogin()}).count()

# cursor = report_raids.find({'login': user.getLogin()}).skip(counter - 2)
# alltrue = True
# for x in cursor:
#     if not x["on_raid"]:
#         alltrue = False 
#     print(f'{datetime.fromtimestamp(x["date"])} {x["on_raid"]}')
# print(alltrue)

# filtered_arr = list(filter(lambda x : x['type'] == 'decoration', user.getInventory())) 
# sorted_arr = sorted(filtered_arr, key=itemgetter('id'))
# print(sorted_arr)
# for i in sorted_arr:
#     print(i)

# print('============================================')
# report = ''
# for key, group in itertools.groupby(sorted_arr, key=lambda x: x['id']):
#         # print (key)
#         gr = list(group)
#         report = f'▫️ {gr[0]["name"]} {str(len(gr)) if len(gr)>1 else str(len(gr))}\n'
#         print(report)  

# for goat in getSetting(code='GOATS_BANDS'):
#     getPlanedRaidLocation(goat['name'], planRaid = False)

def getInventoryReport(user, types):
        full_report = ''
        for type in types:
            report = ''
            cost = 0
            filtered_arr = list(filter(lambda x : x['type'] == type['id'], user.getInventory())) 
            sorted_arr = sorted(filtered_arr, key=itemgetter('id'))

            for key, gr in itertools.groupby(sorted_arr, key=lambda x:x['id']):
                group = list(gr)

                print('==================')
                print(list(group)[-1])


                percent = 0
                if list(group)[-1]["type"] == 'skill':
                    try:
                        storage = list(group)[-1]['storage']
                        if storage > 0:
                            percent = int(storage*100/list(group)[-1]['max'])
                    except: pass

                elif list(group)[-1]["type"] in ('clothes', 'things'):
                    try:
                        wear = list(group)[-1]['wear']['value']
                        if wear > 0:
                            percent = int(wear*100/1)
                    except: pass

                elem_cost = 0
                for elem in list(group):
                    if 'cost' in elem:
                        elem_cost = elem_cost + elem["cost"]
                        cost = cost + elem["cost"]


                report = report + f'▫️ {list(group)[-1]["name"]} {"<b>" + str(percent)+"%</b>" if percent>0 else ""}{"("+str(len(list(group)))+")" if len(list(group))>1 else ""} {" 🔘"+str(elem_cost) if elem_cost > 0 else ""}\n'

            if not report == '':
                report = type['name'] + (f' (🔘 {cost}):\n' if cost>0 else ':\n') + report + '\n'
            full_report = full_report + report
        return full_report

# user = getUserByLogin('GonzikBenzyavsky')
# inventory_category = [
#                         {'id':'things', 'name':'📦 Вещи'}
#                     ]
# print(getInventoryReport(user, inventory_category))

# print(f"{report_raids.count_documents({'band': {'$in': getGoatBands('FǁȺǁggǁØǁAT')}, 'date': 1589032800, 'planed_location': {'&gt': 0} })}")
# print(f"{report_raids.count_documents({'band': {'$in': getGoatBands('FǁȺǁggǁØǁAT')}, 'date': 1589032800, 'planed_location': {'$gt': 0} })}")

stats2 = []
# result = max(stats, key=lambda x: x['cost'])
# result = list(filter(lambda x: True, stats))
# 
stats = [{'cost': 1000, 'name': 2}, {'cost': 5000, 'name': 3}, {'cost': 200, 'name': 4}]

result = sum([d['cost'] for d in stats])
print(result)



# import pandas as pd
# df =  pd.DataFrame(list(deal.find()))
# df['date'] = [datetime.fromtimestamp(x).strftime("%d/%m") for x in df.date]
# del df['_id']
# del df['seller']
# del df['buyer']
# del df['inventory_id']
# del df['inventory']

# # print(df.date.values)

# import matplotlib.pyplot as plt

# Независимая (x) и зависимая (y) переменные
# x = [1, 2, 3, 4, 5]
# x2 = [5, 4, 3, 3, 1]
# y = x

# # Построение графика
# plt.title("Линейная зависимость y = x") # заголовок
# plt.xlabel("x") # ось абсцисс
# plt.ylabel("y") # ось ординат
# plt.grid()      # включение отображение , 
# plt.plot(x, y, "r--", x, x2, "r--")  # построение графика



# plt.show()
# c = random.randint(1, 3)
# print(f'random = {c}')
# for i in range(0, c):
#     print(f'{i}')

def getPlotСourse(cursor, username: str):
    #Make a query to the specific DB and Collection
    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))
    #df['date'] = [datetime.fromtimestamp(x).strftime("%d/%m") for x in df.date]
    
    # # Delete the _id ...
    if True:
        del df['_id']
        del df['seller']
        del df['buyer']
        del df['inventory_id']
        del df['inventory']
        del df['inventory_name']
    print(df)
    columns_name = {
            'cost'     :'Цена'
            }

    columns_color = {
            'cost'     :'tab:green'
            }

    # Define the upper limit, lower limit, interval of Y axis and colors

    # Draw Plot and Annotate
    fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi= 80)  

    y_MAX = []
    y_MIN = []
    columns = df.columns[1:]  
    for i, column in enumerate(columns):    
        print(df.date.values)
        print(df[column].values)
        
        plt.plot(df.date.values, df[column].values) 
        #plt.scatter(df.date.values, df[column].values, edgecolors=columns_color[column], c=columns_color[column], s=40)
        #y_MAX.append(int(df[column].max().max()))
        #y_MIN.append(int(df[column].min().min()))
        #ax.plot(df.date.values, df[column].values, label = f'{df[column].max()} {columns_name[column]}', color=columns_color[column])

    y_interval = 50
    
    # [datetime.fromtimestamp(x).strftime("%d/%m") for x in df.date]
    
    # Draw Tick lines  
    # for y in range(0, max(y_LL), y_interval):    
    #     plt.hlines(y, xmin=0, xmax=10, colors='black', alpha=0.3, linestyles="--", lw=0.5)


    # Decorations    
    # plt.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom=True, left=False, right=False, labelleft=True)        

    # # Lighten borders
    # plt.gca().spines["top"].set_alpha(.3)
    # plt.gca().spines["bottom"].set_alpha(.3)
    # plt.gca().spines["right"].set_alpha(.3)
    # plt.gca().spines["left"].set_alpha(.3)
    # plt.title(f'Сделки', fontsize=22)

    # N = 14
    # plt.yticks(range( 0, max(y_MAX) + y_interval, y_interval), [str(y) for y in range( 0, max(y_MAX) + y_interval  , y_interval)], fontsize=12)    
    # plt.xticks(range(0, N), df.date.values, horizontalalignment='left', fontsize=12)    
    # plt.ylim( int( min(y_MIN) - y_interval ), int( max(y_MAX) + y_interval) )    
    # plt.xlim(0, N) 
    # ax.legend()

    # # Shrink current axis's height by 10% on the bottom
    # box = ax.get_position()
    # ax.set_position([box.x0, box.y0 + box.height * 0.1,
    #                 box.width, box.height * 0.9])

    # # ax.set_xticklabels(df.date.values,
    # #                fontsize = 15,    #  Размер шрифта
    # #                color = 'b',    #  Цвет текста
    # #                rotation = 90,    #  Поворот текста
    # #                verticalalignment =  'center')    #  Вертикальное выравнивание



    # # Put a legend below current axis
    # ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
    #         fancybox=True, shadow=True, ncol=5, prop={'size': 12})
    # ax.grid()
    # fig.savefig(config.PATH_IMAGE + f'graf_{username}.png', dpi=fig.dpi)
    plt.show()


cursor = deal.find({'inventory_id': 'scalp_of_banditos'})
getPlotСourse(cursor, '12345')
sys.exit(0)

# import pandas as pd
# import matplotlib as mpl
# import matplotlib.pyplot as plt


# pip_history     = mydb["pip_history"]

# #Make a query to the specific DB and Collection
# cursor = pip_history.find({'login': 'GonzikBenzyavsky'})



# # Expand the cursor and construct the DataFrame
# df =  pd.DataFrame(list(cursor))
# df['date'] = [datetime.fromtimestamp(x).strftime("%d/%m") for x in df.date]

# # # Delete the _id
# if True:
#     del df['_id']
#     del df['login']
#     del df['damage']
#     del df['armor']
#     del df['dzen']
#     del df['stamina']

# columns_name = {
#         'force'     :'Сила',
#         'accuracy'  :'Меткость',
#         'health'    :'Здоровье',
#         'agility'   :'Ловкость',
#         'charisma'  :'Харизма'
#         }

# columns_color = {
#         'force'     :'gold',
#         'accuracy'  :'tab:green',
#         'health'    :'tab:red',
#         'agility'   :'darkgrey',
#         'charisma'  :'mediumblue'
#         }

# # Define the upper limit, lower limit, interval of Y axis and colors

# # Draw Plot and Annotate
# fig, ax = plt.subplots(1,1,figsize=(10, 10), dpi= 80)  

# y_MAX = []
# y_MIN = []
# columns = df.columns[1:]  
# for i, column in enumerate(columns):    
#     plt.plot(df.date.values, df[column].values, lw=1.5, color=columns_color[column]) 
#     # plt.text(df.shape[0]+1, df[column].values[-1], f'{column} {df[column].max()}')
#     plt.scatter(df.date.values, df[column].values, edgecolors=columns_color[column], c=columns_color[column], s=40)
#     y_MAX.append(int(df[column].max().max()))
#     y_MIN.append(int(df[column].min().min()))
#     ax.plot(df.date.values, df[column].values, label = f'{df[column].max()} {columns_name[column]}', color=columns_color[column])

# y_interval = 100


# # Draw Tick lines  
# # for y in range(0, max(y_LL), y_interval):    
# #     plt.hlines(y, xmin=0, xmax=10, colors='black', alpha=0.3, linestyles="--", lw=0.5)


# # Decorations    
# plt.tick_params(axis="both", which="both", bottom=False, top=False, labelbottom=True, left=False, right=False, labelleft=True)        

# # Lighten borders
# plt.gca().spines["top"].set_alpha(.3)
# plt.gca().spines["bottom"].set_alpha(.3)
# plt.gca().spines["right"].set_alpha(.3)
# plt.gca().spines["left"].set_alpha(.3)
# plt.title('Прогресс Пип-боев', fontsize=22)

# plt.yticks(range( 0, max(y_MAX) + y_interval, y_interval), [str(y) for y in range( 0, max(y_MAX) + y_interval  , y_interval)], fontsize=12)    
# plt.xticks(range(0, 10), df.date.values, horizontalalignment='left', fontsize=12)    
# plt.ylim( int( min(y_MIN) - y_interval ), int( max(y_MAX) + y_interval) )    
# plt.xlim(0, 10) 
# ax.legend()

# # Shrink current axis's height by 10% on the bottom
# box = ax.get_position()
# ax.set_position([box.x0, box.y0 + box.height * 0.1,
#                  box.width, box.height * 0.9])

# # Put a legend below current axis
# ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
#           fancybox=True, shadow=True, ncol=5, prop={'size': 12})
# ax.grid()

# fig.savefig('temp.png', dpi=fig.dpi)
# plt.show()


# dresult = registered_wariors.aggregate([ 
#     {   "$group": {
#         "_id": "$name", 
#         "count": {
#             "$sum": 1}}},
        
#     {   "$sort" : { "count" : -1 } }
#     ])

# i = 1
# for d in dresult:
#     if d.get("count") > 1:
#         print(f'{i}. {d.get("_id")} {d.get("count")}')
        
#         dresult2 = registered_wariors.aggregate([ 
#             {   "$match": {
#                         "name": d.get("_id")
#                     } 
#             },   
#             {   "$sort" : { "timeUpdate" : 1 } }
#             ])
        
#         z = 1
#         for m in dresult2:
#             if z == d.get("count"): break

#             string =  f'    ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(m.get("timeUpdate")))
#             print(m.get('_id'))
#             registered_wariors.delete_many({'_id': m.get('_id')})
#             z = z + 1
#     i = i + 1


# for ts in (1579191477, 1579191477):
# #     print(f"{datetime.fromtimestamp(ts)}")

# report = ''
# jsonfind = json.loads('{"chat":{"$not":{"$exists": "true"}}}')
# for req in mydb["users"].find(jsonfind
#                             ):
#                                 value = req[f'login']
#                                 report = report + f'{value}\n'

# print(report)


# #report_raids.remove()
for goat in getSetting('GOATS_BANDS'):
    #saveRaidResult(goat)
    print(statistic(goat['name']))

# for goat in getSetting('GOATS_BANDS'): 1576447200
#     report = radeReport(goat)
#     # print(report)

# for b in getGoatBands('АdaptationǁȺǁ'):
#     print(b)
# for x in registered_users.find({'band':{'$in':getGoatBands('АdaptationǁȺǁ')}}):
#     print(x['name'])

# for goat in getSetting('GOATS_BANDS'):
#     registered_users.update_many(
#         {'band':{'$in':getGoatBands(goat.get('name'))}},
#         { '$set': { 'raidlocation': None} }
#     )

sys.exit(0)

print('\n======== setSetting ==========\n')

for registered_user in registered_users.find():
    print(registered_user)


sys.exit(0)

print('\n======== rade report ==========\n')
goats = []
for goat in getSetting('GOATS_BANDS'):
    goat_report = {}
    goat_report.update({'name': goat.get('name')})
    goat_report.update({'chat': goat.get('chat')})
    goat_report.update({'bands': []})

    for band in goat.get('bands'):
        band_arr = {}
        band_arr.update({'name': band})
        band_arr.update({'weight_all': 0})
        band_arr.update({'weight_on_rade': 0})
        band_arr.update({'counter_all': 0})
        band_arr.update({'counter_on_rade': 0})

        for user in list(USERS_ARR):
            # Обрабатываем по козлам
            if user.getBand() == band:
                band_arr.update({'weight_all': band_arr.get('weight_all') + user.getRaidWeight()})
                band_arr.update({'counter_all': band_arr.get('counter_all') + 1}) 
                if user.getRaidLocation():
                    band_arr.update({'weight_on_rade': band_arr.get('weight_on_rade') + user.getRaidWeight()})
                    band_arr.update({'counter_on_rade': band_arr.get('counter_on_rade') + 1}) 
        goat_report.get('bands').append(band_arr)
    goats.append(goat_report)

for goat in goats:
    report = f'🐐{goat.get("name")}\n\n'
    for bands in goat.get('bands'):
        report = report + f'🤟{bands.get("name")}\n'
        if bands.get("weight_all") > 0:
            report = report + f'👤{bands.get("counter_on_rade")}/{bands.get("counter_all")} 🏋️‍♂️{str(int(bands.get("weight_on_rade")/bands.get("weight_all")*100))}%\n'
        else:
            report = report + f'👤{bands.get("counter_on_rade")}/{bands.get("counter_all")} 🏋️‍♂️0%\n'
        report = report + f'\n'
    print(report)    

for x in registered_users.find():
    registered_users.update(
        { 'login': x.get('login')},
        { '$set': { 'raidlocation': None} }
    )
    
print(goats)

print('\n======== geocoders ==========\n')

from yandex_geocoder import Client
import timezonefinder, pytz

Client.PARAMS = {"format": "json", "apikey": config.YANDEX_GEOCODING_API_KEY}
location = Client.coordinates('Одеса')
tf = timezonefinder.TimezoneFinder()
timezone_str = tf.certain_timezone_at(lat=float(location[1]), lng=float(location[0]))

print(timezone_str)
if timezone_str is None:
    print ("Could not determine the time zone")
else:
    # Display the current time in that time zone
    timezone = pytz.timezone(timezone_str)
    
    dt = datetime.utcnow()
    print(timezone.utcoffset(dt))
    print ("The time in {} {}", timezone_str, dt + timezone.utcoffset(dt))

    t = datetime.strptime('3:00:00',"%H:%M:%S")
    print(t)
    dts = dt + timedelta(days=t.day, seconds=t.second, microseconds=t.microsecond,
                milliseconds=0, minutes=t.minute, hours=t.hour, weeks=0)
    print(str(dts))
# print('\n======== TEST users ==========\n')
# for registered_user in registered_users.find():
#      print(registered_user)

print('\n======== TEST pending message ==========\n')
#pending_messages.remove()
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
    print('-=============================================-')
    print(time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(datetime.now().timestamp())))
    print(time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(pending_message.get('pending_date'))))
    print('-=============================================-')


print('\n======== TEST parse(datetime_str) ==========\n')
datetime_str = '2019-11-03T03:00:00+03:00'
dt = parse(datetime_str)
print(str(dt.hour).zfill(2)+':'+str(dt.minute).zfill(2))

print('\n======== Ordering users by bm ==========\n')

def getBm(user):
    stat = int(str(user.get('damage')).split('(+')[0].strip()) + int(str(user.get('accuracy')).split('(+')[0].strip()) + int(str(user.get('health')).split('(+')[0].strip()) + int(str(user.get('charisma')).split('(+')[0].strip()) + int(str(user.get('agility')).split('(+')[0].strip())
    return int(stat)

def getRaidWeight(user):
    dzen = int(user.get('dzen'))
    return int(getBm(user) + getBm(user) * dzen * 0.25)

users = []
for registered_user in registered_users.find():
    registered_user.update({'weight': getRaidWeight(registered_user)})
    users.append(registered_user)
print('-------------------------------------------------------------------')
for registered_user in sorted(users, key = lambda i: i['weight'], reverse=True):
    print(registered_user['weight'])

print('\n======== GOATS_BANDS users by bm ==========\n')

for goat in getSetting('GOATS_BANDS'):
    print(goat['name'])
    for band in goat['bands']:
        print(band)