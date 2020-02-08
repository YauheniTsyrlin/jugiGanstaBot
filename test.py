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

from main import isAdmin

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

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

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

def getPlanedRaidLocation(goatName: str):
    tz = config.SERVER_MSK_DIFF
    raid_date = datetime.now() + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
    hour = raid_date.hour

    if raid_date.hour >= 17:
        raid_date = raid_date + timedelta(days=1)


    if raid_date.hour >=1 and raid_date.hour <9:
        hour = 9
    elif raid_date.hour >=9 and raid_date.hour <17:
        hour = 17
    if raid_date.hour >=17 or raid_date.hour <1:
        hour = 1

    raidNone = {}
    raidNone.update({'rade_date': (raid_date.replace(hour=hour, minute=0, second=0, microsecond=0)).timestamp()})
    raidNone.update({'rade_location': None})

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

# dresult = dungeons.aggregate([ 
#     {   "$match": {
#                 "band": "АртхǁȺǁус"
#             } 
#     },
#     {   "$group": {
#         "_id": "$date", 
#         "count": {
#             "$sum": 1}}},
        
#     {   "$sort" : { "count" : -1 } }
#     ])
    
# for d in dresult:
#     print(d)
#     date = d.get("_id") 
#     print(f'{d.get("count")} - {datetime.fromtimestamp(date)}')  

b = 'True'
if b == True:
    print(f'{1}')

sys.exit(0)

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