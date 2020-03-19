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

import users 
import wariors
import tools
	
import hashlib

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

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

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
    raid_date = datetime.now() - timedelta(minutes=34, hours=2) + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
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
raid = getPlanedRaidLocation('FǁȺǁggǁØǁAT', False)
print(raid)
print(datetime.fromtimestamp(raid["rade_date"]))
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