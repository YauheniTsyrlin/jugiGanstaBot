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

import users 
import wariors
import tools

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

SETTINGS_ARR = [] # Зарегистрированные настройки
for setting in settings.find():
    SETTINGS_ARR.append(setting)

def getSetting(code: str):
    """ Получение настройки """
    result = settings.find_one({'code': code})
    if (result):
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


print('\n======== radeReport ==========\n')

print(
        tools.getTimeEmoji((datetime.now() - timedelta(days=0)).timestamp())
    )

print(
        tools.getTimeEmoji((datetime.now() - timedelta(days=9)).timestamp())
    )
print(
        tools.getTimeEmoji((datetime.now() - timedelta(days=20)).timestamp())
    )
print(
        tools.getTimeEmoji((datetime.now() - timedelta(days=40)).timestamp())
    )
print(
        tools.getTimeEmoji((datetime.now() - timedelta(days=70)).timestamp())
    )
# for goat in getSetting('GOATS_BANDS'):
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