import pymongo
import json
import datetime
import time
import users
import tools
import uuid
import random

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

# battle.delete_many({'login':'szpavel'})
# competition.delete_many({'login':'szpavel'})
# dungeons.delete_many({'login':'szpavel'})
# man_of_day.delete_many({'login':'szpavel'})
# pip_history.delete_many({'login':'szpavel'})
# plan_raids.delete_many({'login':'szpavel'})
# report_raids.delete_many({'login':'szpavel'})
# registered_users.delete_many({'login':'szpavel'})
# registered_wariors.delete_many({'name':'szpavel'})

USERS_ARR = [] # Зарегистрированные пользователи
for x in registered_users.find():
    USERS_ARR.append(users.importUser(x))

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
                    print()
                    return arr['name'] 
        elif id:
            for arr in result.get('value'):
                if arr['id'] == id:
                    return arr 
        else:
            return result.get('value')

def setSetting(login: str, code: str, value: str):
    """ Сохранение настройки """
    myquery = { "code": code }
    newvalues = { "$set": { "value": value } }
    u = settings.update_one(myquery, newvalues)


GLOBAL_VARS = {
    'inventory':  getSetting(code='ACCESSORY_ALL', id='PIP_BOY')['value'] + getSetting(code='ACCESSORY_ALL', id='REWARDS')['value'] + getSetting(code='ACCESSORY_ALL', id='THINGS')['value'] + getSetting(code='ACCESSORY_ALL', id='EDIBLE')['value'] + getSetting(code='ACCESSORY_ALL', id='TATU')['value'] + getSetting(code='ACCESSORY_ALL', id='CLOTHES')['value'] + getSetting(code='ACCESSORY_ALL', id='MARKS_OF_EXCELLENCE')['value'] + getSetting(code='ACCESSORY_ALL', id='POSITIONS')['value'] + getSetting(code='ACCESSORY_ALL', id='VIRUSES')['value']  ,
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
    'typeforexcenge': [ 'clothes', 'food', 'decoration', 'things'],
    'typeforcomission': [ 'clothes', 'food', 'decoration', 'things'],
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
                'name': '🛠️🛍️ Магазин',
                'description':'🛍️ Здесь можно посмотреть товара, которые бандиты выставили на продажу.',
                'buttons': []
            },
            {
                'id': 'workbench',
                'name': '🛠️⚙️ Верстак',
                'description':'⚙️ Здесь можно собрать новые вещи или разобрать на 📦 запчасти.',
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
                'id': 'back',
                'name': 'Выйти ❌',
                'description':'🧺 Удачи, до новых встреч!',
                'buttons': []
            }
        ]
    }
}

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

# ==================================================
myquery = {'code': 'OUR_BAND'}
sett = settings.delete_one(myquery)

myquery = {'code': 'BAN_USERS'}
sett = settings.delete_one(myquery)

myquery = {'code': 'BANDS_INLINE_WARIORS'}
sett = settings.delete_one(myquery)

myquery = {'code': 'REPORT_KILLERS'}
sett = settings.delete_one(myquery)

myquery = {'code': 'PROBABILITY_I_DONT_NOW'}
sett = settings.delete_one(myquery)

# ==================================================

result = settings.find_one({'code': 'REPORTS'})
if (not result):
    print('Not Find setting. Insert REPORTS')
    settings.insert_one({
        'code': 'REPORTS', 
        'description': 'Даты для отчетов', 
        'value': ''
    })

result = settings.find_one({'code': 'ADMINISTRATOR'})
if (not result):
    print('Not Find setting. Insert ADMINISTRATOR')
    settings.insert_one({
        'code': 'ADMINISTRATOR', 
        'description': 'Администраторы, имеющие право изменять настройки', 
        'value': ''
             })

result = settings.find_one({'code': 'PROBABILITY'})
if (not result):
    print('Not Find setting. Insert probability')
    settings.insert_one({
        'code': 'PROBABILITY', 
        'description': 'Вероятности', 
        'value': ''   
             })  

result = settings.find_one({'code': 'USER_SETTINGS'})
if (not result):
    print('Not Find setting. Insert USER_SETTINGS')
    settings.insert_one({
        'code': 'USER_SETTINGS', 
        'description': 'Возможные настройки пользователя', 
        'value': ''   
             })  

result = settings.find_one({'code': 'BANDS_ACCESS_WARIORS'})
if (not result):
    print('Not Find setting. Insert BANDS_ACCESS_WARIORS')
    settings.insert_one({
        'code': 'BANDS_ACCESS_WARIORS', 
        'description': 'Банды, имеющие право пользоваться inline сервисом wariors', 
        'value': ''   
             })     

result = settings.find_one({'code': 'GOATS_BANDS'})
if (not result):
    print('Not Find setting. Insert GOATS_BANDS')
    settings.insert_one({
        'code': 'GOATS_BANDS', 
        'description': ' Козлы и их Банды, имеющие право пользоваться Джу', 
        'value': ''   
             })   


result = settings.find_one({'code': 'STICKERS'})
if (not result):
    print('Not Find setting. Insert STICKERS')
    settings.insert_one({
        'code': 'STICKERS', 
        'description': ' Стикеры', 
        'value': ''   
             })  

result = settings.find_one({'code': 'ACCESSORY_ALL'})
if (not result):
    print('Not Find setting. Insert ACCESSORY_ALL')
    settings.insert_one({
        'code': 'ACCESSORY_ALL', 
        'description': ' Аксессуары', 
        'value': ''   
             })  

result = settings.find_one({'code': 'RANK'})
if (not result):
    print('Not Find setting. Insert RANK')
    settings.insert_one({
        'code': 'RANK', 
        'description': ' Ранги и должности', 
        'value': ''   
             })  

result = settings.find_one({'code': 'RAIDLOCATIONS'})
if (not result):
    print('Not Find setting. Insert RAIDLOCATIONS')
    settings.insert_one({
        'code': 'RAIDLOCATIONS', 
        'description': ' Рейдовые локации', 
        'value': ''   
             }) 

result = settings.find_one({'code': 'DUNGEONS'})
if (not result):
    print('Not Find setting. Insert DUNGEONS')
    settings.insert_one({
        'code': 'DUNGEONS', 
        'description': ' Подземелья', 
        'value': ''   
             })   

result = settings.find_one({'code': 'BLACK_LIST'})
if (not result):
    print('Not Find setting. Insert BLACK_LIST')
    settings.insert_one({
        'code': 'BLACK_LIST', 
        'description': ' Бандиты, которые пожизенно забанены', 
        'value': ''   
             })   

result = settings.find_one({'code': 'INVENTORY_CATEGORY'})
if (not result):
    print('Not Find setting. Insert INVENTORY_CATEGORY')
    settings.insert_one({
        'code': 'INVENTORY_CATEGORY', 
        'description': ' Категории для инвентаря', 
        'value': ''   
             })  

print("#==========================#")              
print("#     UPDATE SETTINGS      #")              
print("#==========================#")              


myquery = { "code": 'INVENTORY_CATEGORY' }
newvalues = { "$set": 
                { "value": 
                    [
                        {'id':'position', 'name':'🧗 Должность'},
                        {'id':'skill', 'name':'💡 Умения'},
                        {'id':'disease', 'name':'🦠 Болезни'},
                        {'id':'tatu', 'name':'☮️ Татуировки'},
                        {'id':'clothes', 'name':'🧥 Одежда'},
                        {'id':'food', 'name':'🍗 Еда'},
                        {'id':'marks_of_excellence', 'name':'🏵 Награды'},
                        {'id':'decoration', 'name':'🎁 Подарки'},
                        {'id':'things', 'name':'📦 Вещи'},
                        {'id':'bolt', 'name':'🔩 Рейдовые болты'},
                        {'id':'currency', 'name':'💴 Валюта'}
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'RANK' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'id': 'MILITARY',
                            'name': 'MILITARY',
                            'value':
                            [
                                {
                                    'id': '68',
                                    'name': 'титан',
                                    'bm': 68,
                                    'update': 'auto'
                                },
                                {
                                    'id': '99',
                                    'name': '😏зачатие',
                                    'bm': 99,
                                    'update': 'auto'
                                },
                                {
                                    'id': '199',
                                    'name': '🧫признаки жизни',
                                    'bm': 199,
                                    'update': 'auto'
                                },
                                {
                                    'id': '227',
                                    'name': '🦠таджик',
                                    'bm': 227,
                                    'update': 'auto'
                                },
                                {
                                    'id': '278',
                                    'name': '💉у нас не курят',
                                    'bm': 278,
                                    'update': 'auto'
                                },
                                {
                                    'id': '299',
                                    'name': '🦆как вМ',
                                    'bm': 299,
                                    'update': 'auto'
                                },
                                {
                                    'id': '403',
                                    'name': '🚜тракторист',
                                    'bm': 403,
                                    'update': 'auto'
                                },
                                {
                                    'id': '443',
                                    'name': '🧪ошибка природы',
                                    'bm': 443,
                                    'update': 'auto'
                                },
                                {
                                    'id': '504',
                                    'name': '🚐 Гаврилов',
                                    'bm': 504,
                                    'update': 'auto'
                                },
                                {
                                    'id': '599',
                                    'name': '🌊 Поджог',
                                    'bm': 599,
                                    'update': 'auto'
                                },
                                {
                                    'id': '665',
                                    'name': '🔬примечательный',
                                    'bm': 665,
                                    'update': 'auto'
                                },
                                {
                                    'id': '699',
                                    'name': '😈шалун',
                                    'bm': 699,
                                    'update': 'auto'
                                },
                                {
                                    'id': '776',
                                    'name': '💦смарчок',
                                    'bm': 776,
                                    'update': 'auto'
                                },
                                {
                                    'id': '799',
                                    'name': '🥃ВремяПисатьКод',
                                    'bm': 799,
                                    'update': 'auto'
                                },
                                {
                                    'id': '899',
                                    'name': '🍼лактозник',
                                    'bm': 899,
                                    'update': 'auto'
                                },
                                {
                                    'id': '999',
                                    'name': '🍾с почином',
                                    'bm': 999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '1487',
                                    'name': '🐟Косарик',
                                    'bm': 1487,
                                    'update': 'auto'
                                },
                                {
                                    'id': '1499',
                                    'name': '🙋🏿‍♂️Счастье',
                                    'bm': 1499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '1749',
                                    'name': '🔫Пушка-полторушка',
                                    'bm': 1749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '1999',
                                    'name': '🏺Анимэ',
                                    'bm': 1999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '2249',
                                    'name': '⚱️Бабаф',
                                    'bm': 2249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '2499',
                                    'name': '🐕СторожевойЗакладчик',
                                    'bm': 2499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '2749',
                                    'name': '🛠ВАГ',
                                    'bm': 2749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '2999',
                                    'name': '🍢Шашлык',
                                    'bm': 2999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '3249',
                                    'name': '🥔Бульбаш',
                                    'bm': 3249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '3499',
                                    'name': '☕️Бариста',
                                    'bm': 3499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '3749',
                                    'name': '👻Весомый',
                                    'bm': 3749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '3999',
                                    'name': '🙈Масик',
                                    'bm': 3999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '4249',
                                    'name': '🔥Подгоревший',
                                    'bm': 4249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '4499',
                                    'name': '🍌Бананчик',
                                    'bm': 4499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '4749',
                                    'name': '🐻Стальной',
                                    'bm': 4749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '4999',
                                    'name': '📱Звонок',
                                    'bm': 4999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '5249',
                                    'name': '🧔💄It''sATrap',
                                    'bm': 5249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '5499',
                                    'name': '💪🎼РостовПапа',
                                    'bm': 5499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '5749',
                                    'name': '⁉️🌐Знаток',
                                    'bm': 5749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '5999',
                                    'name': '🌀✏️Рисовальщик',
                                    'bm': 5999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '6249',
                                    'name': '🥰🧸Мишка-обнимашка',
                                    'bm': 6249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '6499',
                                    'name': '🤡🃏Жакир',
                                    'bm': 6499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '6665',
                                    'name': '🌿💥Крапивка',
                                    'bm': 6665,
                                    'update': 'auto'
                                },
                                {
                                    'id': '6749',
                                    'name': '🦠🎀ВирусХ',
                                    'bm': 6749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '6968',
                                    'name': '💃👄РадостнаяДонна',
                                    'bm': 6968,
                                    'update': 'auto'
                                },
                                {
                                    'id': '6999',
                                    'name': '🌛🌜DP',
                                    'bm': 6999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '7249',
                                    'name': '🌚💦Насильница',
                                    'bm': 7249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '7499',
                                    'name': '🖥🦝 Енотообразный ИИ',
                                    'bm': 7499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '7749',
                                    'name': '🏎🐲ПламенныйБолид',
                                    'bm': 7749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '7776',
                                    'name': '🤟🥒ОгурчикВишеса',
                                    'bm': 7776,
                                    'update': 'auto'
                                },
                                {
                                    'id': '7999',
                                    'name': '🔯🔭ПутеводнаяЗвезда',
                                    'bm': 7999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '8249',
                                    'name': '🥔💰Белоордер',
                                    'bm': 8249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '8499',
                                    'name': '🏓🌩ГромовойPINGатор',
                                    'bm': 8499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '8749',
                                    'name': '📡🏘 ПоселенскийИТшник',
                                    'bm': 8749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '8999',
                                    'name': '🧬🔮ВысшеесСущество',
                                    'bm': 8999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '9249',
                                    'name': '🔪💀Лютый πц',
                                    'bm': 9249,
                                    'update': 'auto'
                                },
                                {
                                    'id': '9499',
                                    'name': '👽🔦Гиперпространствующий',
                                    'bm': 9499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '9749',
                                    'name': '⚖️⏱БЖУходи',
                                    'bm': 9749,
                                    'update': 'auto'
                                },
                                {
                                    'id': '9999',
                                    'name': '🐮🍀COWEED-19',
                                    'bm': 9999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '12499',
                                    'name': '🔪🔥 Трижды Ярый',
                                    'bm': 12499,
                                    'update': 'auto'
                                },
                                {
                                    'id': '14999',
                                    'name': '⛓🚅 Сидящий',
                                    'bm': 14999,
                                    'update': 'auto'
                                },
                                {
                                    'id': '691487',
                                    'name': '🚷😴СПЯЩИЙвТЗ',
                                    'bm': 691487,
                                    'update': 'auto'
                                },
                                {
                                    'id': '1000000',
                                    'name': '🧞‍♂️🧞‍♀️КАЗАХ',
                                    'bm': 1000000,
                                    'update': 'auto'
                                }
                            ] 
                        }
                        
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)


myquery = { "code": 'ACCESSORY_ALL' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'id': 'POSITIONS',
                            'name': '🧗 Должность',
                            'value':
                            [
                                {
                                    'id': 'pedal_director',
                                    'name': '🚵 Директор педального завода',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'Chinese',
                                    'name': '😷 Китаец',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'operator',
                                    'name': '📽 Оператор',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'friend_of_the_groom',
                                    'name': '👨‍✈️ Друг жениха',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'bridesmaid',
                                    'name': '🦹‍♀️ Подруга невесты',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'toastmaster',
                                    'name': '🪕 Тамада',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'registrar_in_the_office',
                                    'name': '👨‍💼 Регистратор в ЗАГСе',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'paramedic',
                                    'name': '👨‍⚕️ Фельдшер-нарколог',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'doctor',
                                    'name': '👨‍💼 Врач-токсиколог',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'electrician_1',
                                    'name': '🧑‍🏭 Электромонтер',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'electrician_2',
                                    'name': '👨‍🏭 Электромеханик',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'programmer_1',
                                    'name': '👨‍💻 Программист',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'programmer_2',
                                    'name': '🧟‍♂️ Системный администратор',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'robotics_1',
                                    'name': '🤖 Техник',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'robotics_2',
                                    'name': '🦾 Генеральный конструктор',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'fighter_1',
                                    'name': '🥩 боец Клуба UFC',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'fighter_2',
                                    'name': '⚜️ Судья Клуба UFC',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'economist_1',
                                    'name': '🗃️ Товаровед',
                                    'type': 'position',
                                    'cost': 0
                                },
                                {
                                    'id': 'economist_2',
                                    'name': '🗃📈 Главный бухгалтер',
                                    'type': 'position',
                                    'cost': 0
                                }
                            ] 
                        },
                        {
                            'id': 'CLOTHES',
                            'name': '🧥 Одежда',
                            'value':
                            [                               
                                {
                                    'id': 'scientists_robe',
                                    'name': '🔬 Халат учёного',
                                    'cost': 5,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 20,
                                    'weight': 0.3,
                                    'state': [
                                                {'new': 0.8},
                                                {'a little broken': 0.6}, 
                                                {'broken': 0.4}, 
                                                {'tatters': 0.2}
                                            ],
                                    'decay': 0.01,
                                    'position': ['dressed','in inventory', 'in the closet', 'on the ground'],

                                },
                                {
                                    'id': 'straw_hat',
                                    'name': '👒 Соломенная шляпка',
                                    'cost': 10,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 10
                                },
                                {
                                    'id': 'hunter_panties',
                                    'name': '🩲 Трусы охотника на Трогов',
                                    'cost': 10,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 10
                                },
                                {
                                    'id': 'dueling_glove',
                                    'name': '🧤 Дуэльная перчатка',
                                    'cost': 15,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 10
                                },
                                {
                                    'id': 'handkerchief',
                                    'name': '👻 Носовой платок',
                                    'cost': 6,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 10
                                },
                                {
                                    'id': 'leather_bag',
                                    'name': '💰 Кожаный мешок',
                                    'cost': 4,
                                    'type': 'clothes',
                                    'quantity': 10
                                },
                                {
                                    'id': 'condom',
                                    'name': '🥏 Презерватив',
                                    'cost': 1,
                                    'type': 'clothes',
                                    'protection':
                                        [
                                            {
                                                'type':'disease',
                                                'id': 'girlfriend_bouquet',
                                                'value': 0.99
                                            }
                                        ],
                                    'wear': 
                                        {
                                            'one_use': 0.9,
                                            'value': 1
                                        },
                                    'quantity': None
                                },
                                {
                                    'id': 'medical_mask',
                                    'name': '😷 Медицинская маска',
                                    'cost': 1,
                                    'type': 'clothes',
                                    'protection':
                                        [
                                            {
                                                'type':'disease',
                                                'id': 'covid-19',
                                                'value': 0.95
                                            },
                                            {
                                                'type':'disease',
                                                'id': 'mirror_disease',
                                                'value': 0.70
                                            }
                                        ],
                                    'wear': 
                                        {
                                            'one_use': 0.2,
                                            'value': 1
                                        },
                                    'quantity': None
                                },
                                {
                                    'id': 'dads_slippers',
                                    'name': '🥿 Батины тапки',
                                    'cost': 10,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 10
                                },
                                {
                                    'id': 'latex_mask',
                                    'name': '👽 Латексная маска',
                                    'cost': 10,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 10
                                },
                                {
                                    'id': 'linkoln_hat',
                                    'name': '🎩 шляпа Линкольна',
                                    'cost': 50,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 1
                                },
                                {
                                    'id': 'suit_of_the_bride',
                                    'name': '🥋 Платье невесты',
                                    'cost': 200,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 1
                                },
                                {
                                    'id': 'suit_of_the_groom',
                                    'name': '🕺 Костюм жениха',
                                    'cost': 6,
                                    'type': 'clothes',
                                    'wear': 1,
                                    'quantity': 1
                                }
                            ]
                        },
                        {
                            'id': 'RAID_BOLTS',
                            'name': '🔩 Рейдовые болты',
                            'value':
                            [
                                {
                                    'id': 'bolt_1',
                                    'name': '🔩 Болт М69',
                                    'cost': 0,
                                    'type': 'bolt',
                                    'quantity': None
                                },
                                {
                                    'id': 'bolt_2',
                                    'name': '🔩🔩 Болт М228',
                                    'cost': 0,
                                    'type': 'bolt',
                                    'quantity': None
                                },
                                {
                                    'id': 'bolt_3',
                                    'name': '🔩🔩🔩 Болт М404',
                                    'cost': 0,
                                    'type': 'bolt',
                                    'quantity': None
                                },
                                {
                                    'id': 'bolt_4',
                                    'name': '🔩🔩🔩🔩 Болт М1488',
                                    'cost': 0,
                                    'type': 'bolt',
                                    'quantity': None
                                },
                                {
                                    'id': 'bolt_5',
                                    'name': '🎫🍼 Билет на гигантскую бутылку',
                                    'cost': 0,
                                    'type': 'bolt',
                                    'quantity': None
                                }
                            ]
                        },
                        {
                            'id': 'VIRUSES',
                            'name': '🦠 Болезни',
                            'value':
                            [
                                
                                {
                                    'id': 'girlfriend_bouquet',
                                    'name': '🦠 Букет подруги невесты',
                                    'cost': 0,
                                    'type': 'disease',
                                    'quantity': None,
                                    'property':
                                            {
                                                'contagiousness': 0.01,
                                                'halflife': 0.90,
                                                'mortality': 0.01,
                                                'immunity': 0.95,
                                                'treatability': 0.10
                                            }
                                },
                                {
                                    'id': 'covid-19',
                                    'name': '🦇 Коронавирус',
                                    'cost': 0,
                                    'type': 'disease',
                                    'quantity': None,
                                    'property':
                                            {
                                                'contagiousness': 0.05,
                                                'halflife': 0.75,
                                                'mortality': 0.01,
                                                'immunity': 0.95,
                                                'treatability': 0.10
                                            }
                                },
                                {
                                    'id': 'mirror_disease',
                                    'name': '🔬 Зеркальная болезнь',
                                    'cost': 0,
                                    'type': 'disease',
                                    'quantity': None,
                                    'property':
                                            {
                                                'contagiousness': 0.00,
                                                'halflife': 0.5,
                                                'mortality': 0.01,
                                                'immunity': 0.9,
                                                'treatability': 0.10
                                            }
                                }
                            ]
                        },
                        {
                            'id': 'TATU',
                            'name': '☮️ Татуировки',
                            'value':
                            [
                                {
                                    'id': 'happy_together',
                                    'name': '💞 Счастливы вместе',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 1
                                },
                                {
                                    'id': 'corruptionist',
                                    'name': '💰 Коррупционер',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 1
                                }, 
                                {
                                    'id': 'sassicaia',
                                    'name': '🍷 Тату "Sassicaia"',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 1
                                }, 
                                {
                                    'id': 'tatu_arthouse_1',
                                    'name': '♀️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 15
                                },
                                {
                                    'id': 'tatu_arthouse_2',
                                    'name': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 15
                                },
                                {
                                    'id': 'tatu_arthouse_3',
                                    'name': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 15
                                },
                                {
                                    'id': 'tatu_arthouse_4',
                                    'name': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!", с подписью Кеши.',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 15
                                },
                                {
                                    'id': 'tatu_ledonna_1',
                                    'name': '🤍 тату "ЛеДонна"',
                                    'cost': 200,
                                    'type': 'tatu',
                                    'quantity': 1
                                },
                                {
                                    'id': 'tatu_kirill_1',
                                    'name': '🤍 Сердце Кирилла навсегда',
                                    'cost': 200,
                                    'type': 'tatu',
                                    'quantity': 1
                                },
                                {
                                    'id': 'tatu_arthouse_5',
                                    'name': '♂️ Тату "АртхǁȺǁус тебя любит!", с подписью - мы все!',
                                    'cost': 120,
                                    'type': 'tatu',
                                    'quantity': 15
                                },
                                {
                                    'id': 'tatu_runing_man_1',
                                    'name': '🤺 Бегущий по лезвию',
                                    'cost': 100,
                                    'type': 'tatu',
                                    'quantity': 1000
                                }
                            ]
                        },
                        {
                            'id': 'SKILLS',
                            'name': '💡 Умения',
                            'value':
                            [
                                {
                                    'id': 'barman',
                                    'name': '🍾 Бармен',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'moonshiner',
                                    'name': '📖 «Как перегонять спирт»',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'boss',
                                    'name': '📿 четки босса банды',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'boss',
                                    'name': '📿 Чётки босса банды',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'programmer',
                                    'name': '🉐 Программист',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None,
                                    'probability': 1, # Вероятность срабатывания
                                    'value': 1,       # Рамки изменений 
                                    'min': 45,
                                    'max': 50,
                                    'storage': 0,
                                    'forgetting': 0.001, # за 10 дней -1%
                                    'subjects_of_study':
                                    [
                                        'Потенциометр',
                                        'Абсент'
                                    ],
                                    'dialog_old_text': 'default_old_things',
                                    'flags': {
                                        'congratulation_min': False,
                                        'position_min': 'programmer_1',
                                        'present_min': 
                                            {
                                                'id': 'certificate_programmer_1',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            },
                                        'congratulation_max': False,
                                        'position_max': 'programmer_2',
                                        'present_max': 
                                            {
                                                'id': 'certificate_programmer_2',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            }
                                    }
                                },
                                {
                                    'id': 'perfectionist',
                                    'name': '🛑 Круг перфекциониста',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'seducer',
                                    'name': '🗣 Соблазнитель ванаМинго',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'the_running_man',
                                    'name': '🏃 Бегущий человек',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'alien',
                                    'name': '🚼 Чужой',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None
                                },
                                {
                                    'id': 'watchmaker',
                                    'name': '⏰ Часовщик',
                                    'description': 'Умение "⏰ Часовщик" дает больше времени на фарм',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None,
                                    'probability': 1, # Вероятность срабатывания
                                    'value': 1,       # Рамки изменений 
                                    'min': 50,
                                    'max': 200,
                                    'storage': 0,
                                    'forgetting': 0.001, # за 10 дней -1%,
                                    'subjects_of_study':
                                    [
                                        'Кварц 🔹', 'Минизаряд'
                                    ],
                                    'dialog_old_text': 'old_watchmaker',
                                    'flags': {
                                        'congratulation_min': False,
                                        'position_min': 'watchmaker_1',
                                        'present_min': 
                                            {
                                                'id': 'certificate_watchmaker_1',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            },
                                        'congratulation_max': False,
                                        'position_max': 'watchmaker_2',
                                        'present_max': 
                                            {
                                                'id': 'certificate_watchmaker_2',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            }
                                        }
                                },
                                {
                                    'id': 'economist',
                                    'name': '📊 Экономист',
                                    'description': 'Навык дает возможность увеличить стоимость получаемых товаров с вероятностью 30% на 20%...',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None,
                                    'probability': 0.80, # Вероятность срабатывания
                                    'value': 0.33,       # Рамки изменений 33%
                                    'min': 80,
                                    'max': 100,
                                    'storage': 0,       # уровень познания навыка относительно min\max,
                                    'forgetting': 0.001, # за 10 дней -1%
                                    'subjects_of_study':
                                    [
                                        # Учимся на количестве обновленных бандитов из wwtop
                                    ],
                                    'dialog_old_text': 'old_report_wwtop',
                                    'flags': {
                                        'congratulation_min': False,
                                        'position_min': 'economist_1',
                                        'present_min': 
                                            {
                                                'id': 'certificate_economist_1',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            },
                                        'congratulation_max': False,
                                        'position_max': 'economist_2',
                                        'present_max': 
                                            {
                                                'id': 'certificate_economist_2',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            }
                                        }
                                },
                                {
                                    'id': 'fighter',
                                    'name': '🤼‍♂️ Боец',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None,
                                    'probability': 1, # Вероятность срабатывания
                                    'value': 1,       # Рамки изменений 
                                    'min': 100,
                                    'max': 150,
                                    'storage': 0,
                                    'forgetting': 0.001, # за 10 дней -1%,
                                    'subjects_of_study':
                                    [
                                        'FIGHT!'
                                    ],
                                    'dialog_old_text': None,
                                    'flags': {
                                        'congratulation_min': False,
                                        'position_min': 'fighter_1',
                                        'present_min': 
                                            {
                                                'id': 'certificate_fighter_1',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            },
                                        'congratulation_max': False,
                                        'position_max': 'fighter_2',
                                        'present_max': 
                                            {
                                                'id': 'certificate_fighter_2',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            }
                                        }
                                },
                                {
                                    'id': 'robotics',
                                    'name': '🛰 Робототехника',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None,
                                    'probability': 1, # Вероятность срабатывания
                                    'value': 1,       # Рамки изменений 
                                    'min': 12,
                                    'max': 15,
                                    'storage': 0,
                                    'forgetting': 0.001, # за 10 дней -1%,
                                    'subjects_of_study':
                                    [
                                        'Барахло','Малыш','Дефолт','Шерлокдрон','Robot Rock','Рад-дрон','Протекдрон','AWESOM-O'
                                    ],
                                    'dialog_old_text': 'old_robotics',
                                    'flags': {
                                        'congratulation_min': False,
                                        'position_min': 'robotics_1',
                                        'present_min': 
                                            {
                                                'id': 'certificate_robotics_1',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            },
                                        'congratulation_max': False,
                                        'position_max': 'robotics_2',
                                        'present_max': 
                                            {
                                                'id': 'certificate_robotics_2',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            }
                                        }
                                },  
                                {
                                    'id': 'electrician',
                                    'name': '⚡ Электрик',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None,
                                    'probability': 1, # Вероятность срабатывания
                                    'value': 1,       # Рамки изменений 
                                    'min': 160,
                                    'max': 200,
                                    'storage': 0,
                                    'forgetting': 0.001, # за 10 дней -1%,
                                    'subjects_of_study':
                                    [
                                        'Изолента','Провода'
                                    ],
                                    'dialog_old_text': 'old_insulating_tape',
                                    'flags': {
                                        'congratulation_min': False,
                                        'position_min': 'electrician_1',
                                        'present_min': 
                                            {
                                                'id': 'certificate_electric_1',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            },
                                        'congratulation_max': False,
                                        'position_max': 'electrician_2',
                                        'present_max': 
                                            {
                                                'id': 'certificate_electric_2',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            }
                                        }
                                },     
                                {
                                    'id': 'medic',
                                    'name': '💉 Медик',
                                    'cost': 0,
                                    'type': 'skill',
                                    'quantity': None,
                                    'probability': 1, # Вероятность срабатывания
                                    'value': 1,       # Рамки изменений 
                                    'min': 48,
                                    'max': 60,
                                    'storage': 0,
                                    'forgetting': 0.01, # за 1 дней -1%,
                                    'subjects_of_study':
                                    [
                                        'Эфедрин'
                                    ],
                                    'dialog_old_text': 'old_ephedrine',
                                    'flags': {
                                        'congratulation_min': False,
                                        'position_min': 'paramedic',
                                        'present_min': 
                                            {
                                                'id': 'certificate_medic',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            },
                                        'congratulation_max': False,
                                        'position_max': 'doctor',
                                        'present_max': 
                                            {
                                                'id': 'certificate_proctologist',
                                                'type': 'MARKS_OF_EXCELLENCE'
                                            }
                                        }
                                }                                
                            ]
                        },
                        {
                            'id': 'EDIBLE',
                            'name': '🍗 Еда',
                            'value':
                            [
                                {
                                    'id': 'coffee',
                                    'name': '☕ Горячий кофе',
                                    'cost': 10,
                                    'type': 'food',
                                    'quantity': None,
                                    'composition':
                                    [
                                        {
                                            'id': 'milk',
                                            'counter': 1
                                        },
                                        {
                                            'id': 'coffee_grains',
                                            'counter': 1
                                        }
                                    ]
                                },
                                {
                                    'id': 'milk',
                                    'name': '🥛 Молоко',
                                    'cost': 2,
                                    'type': 'food',
                                    'quantity': None,
                                    'subjects_to_find':
                                    [
                                        'Молоко брамина'
                                    ],
                                    'dialog_old_text': 'old_milk'
                                },
                                {
                                    'id': 'coffee_grains',
                                    'name': '🍂 Зёрна кофе',
                                    'cost': 3,
                                    'type': 'food',
                                    'quantity': None,
                                    'subjects_to_find':
                                    [
                                        'Абрик*с'
                                    ],
                                    'dialog_old_text': 'old_grains'
                                },
                                {
                                    'id': 'sugar_seed',
                                    'name': '🦴 Сахарная косточка',
                                    'cost': 2,
                                    'type': 'food',
                                    'quantity': 1
                                },
                                {
                                    'id': 'salt',
                                    'name': '🧂 Соль на рану',
                                    'cost': 1,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'cookies',
                                    'name': '🍪 Довоенное печенье',
                                    'cost': 3,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'head_crombopulus',
                                    'name': '👽 Голова кромбопулуса',
                                    'cost': 7,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'tomato_juice',
                                    'name': '🌡 Томатный сок',
                                    'cost': 2,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'soup_set',
                                    'name': '☠️ Суповой комплект',
                                    'cost': 4,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'truffle',
                                    'name': '💩 Трюфель',
                                    'cost': 10,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'ears',
                                    'name': '👂 Уши из Rivet City',
                                    'cost': 5,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'chocolate_and_whiskey',
                                    'name': '🍫 и 🥃',
                                    'cost': 12,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'banana',
                                    'name': '🍌 Банан преданности',
                                    'cost': 6,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'peach',
                                    'name': '🍑 Персик преданности',
                                    'cost': 5,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'ascorbin',
                                    'name': '🤍 Аскорбинка',
                                    'cost': 8,
                                    'type': 'food',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'snail',
                                    'name': '🐚 Труп улитки',
                                    'cost': 1,
                                    'type': 'food',
                                    'quantity': 1000
                                }
                            ]
                        },
                        {
                            'id': 'MARKS_OF_EXCELLENCE',
                            'name': '🏵 Награды',
                            'value':
                            [
                                
                                {
                                    'id': 'сertificate_of_marriage',
                                    'name': '🧾 Свидетельство о бракосочетании',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'bolt_5_season',
                                    'name': '🔩 Рейдовый болт 5-го сезона',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'fucking_i',
                                    'name': '🖕 Нихуя І степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'fucking_ii',
                                    'name': '🖕🖕 Нихуя ІІ степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'fucking_iii',
                                    'name': '🖕🖕🖕 Нихуя ІІІ степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'fucking_iv',
                                    'name': '🖕🖕🖕🖕 Нихуя IV степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'fucking_v',
                                    'name': '🖕🖕🖕🖕🖕 Нихуя V степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'fucking_full',
                                    'name': '🎖️ Полный кавалер ордена "Нихуя"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'diploma_1',
                                    'name': '📄 Грамота за правильный вопрос!',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'diploma_2',
                                    'name': '📜 Грамота за групповой захват',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'diploma_3',
                                    'name': '💪 За храбрость и мужество!',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_gv',
                                    'name': '💉 Удостоверение "Главврач"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                    
                                },
                                {
                                    'id': 'certificate_economist_1',
                                    'name': '📘 Диплом бакалавра',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_economist_2',
                                    'name': '📕 Диплом экономиста',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_fighter_1',
                                    'name': '💪 Пропуск в Клуб UFC',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_fighter_2',
                                    'name': '🥇 Медаль Чемпиона клуба UFC',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_robotics_1',
                                    'name': '🛰️ Пропуск на космодром «Восточный»"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_robotics_2',
                                    'name': '🦿 Научная работа "Пустошь, Джу и др."',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_programmer_1',
                                    'name': '💾 Корочка "Python для чайников"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_programmer_2',
                                    'name': '💽 Корочка "Инженер-программист"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_electric_1',
                                    'name': '🔌 Корочка "Курс по электробезопасности"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                }
                                ,
                                {
                                    'id': 'certificate_electric_2',
                                    'name': '💡 Корочка "Курс по электроснабжению"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                }
                                ,
                                {
                                    'id': 'certificate_proctologist',
                                    'name': '💉 Корочка "Проктолог"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                }
                                ,
                                {
                                    'id': 'certificate_medic',
                                    'name': '💉 Корочка "Медработник"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                }
                                ,
                                {
                                    'id': 'certificate_mb',
                                    'name': '💉 Удостоверение "Медбрат"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_mm',
                                    'name': '💉 Удостоверение "Медсестричка"',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_donor',
                                    'name': '🩸 Почётный донор',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_donor_i',
                                    'name': '🩸 Значёк "Почетный донор" I-степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_donor_ii',
                                    'name': '🩸 Значёк "Почетный донор" II-степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'certificate_donor_iii',
                                    'name': '🩸 Значёк "Почетный донор" III-степени',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'capture_medal',
                                    'name': '🎖️ Медаль за захват',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'newspaper_article',
                                    'name': '📰 Статья в газете',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'vacation_to_sanatorium',
                                    'name': '📃 Путёвка в санаторий',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'burning_fart',
                                    'name': '🔥 Горящий пердак',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                },
                                {
                                    'id': 'dust_from_woolen',
                                    'name': '🌪 Пыль с Шерстяного',
                                    'cost': 0,
                                    'type': 'marks_of_excellence',
                                    'quantity': None
                                }
                            ]
                        },
                        {
                            'id': 'REWARDS',
                            'name': '🎁 Подарки',
                            'value':
                            [
                                
                                {
                                    'id': 'brides_bouquet',
                                    'name': '💐 Букет невесты',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 1

                                },
                                {
                                    'id': 'memory_wedding',
                                    'name': '📼 Память о свадьбе',
                                    'cost': 2,
                                    'type': 'decoration',
                                    'quantity': 1

                                },
                                {
                                    'id': 'grooms_ring',
                                    'name': '🕳 Кольцо жениха',
                                    'cost': 7,
                                    'type': 'decoration',
                                    'quantity': 1

                                },
                                {
                                    'id': 'brides_ring',
                                    'name': '💍 Кольцо невесты',
                                    'cost': 100,
                                    'type': 'decoration',
                                    'quantity': 1

                                },
                                {
                                    'id': 'stuffed_enclave',
                                    'name': '🚨 Чучело "Анклав"',
                                    'cost': 20,
                                    'type': 'decoration',
                                    'quantity': 1

                                },
                                {
                                    'id': 'rubber_swimmer',
                                    'name': '🐏 Резиновая электроовца',
                                    'cost': 75,
                                    'type': 'decoration',
                                    'quantity': 1

                                },
                                {
                                    'id': 'jugi_model',
                                    'name': '🤖 Моделька "Джу"',
                                    'cost': 100,
                                    'type': 'decoration',
                                    'quantity': 1

                                },
                                {
                                    'id': 'shark',
                                    'name': '🦈 Статуэтка "Акула"',
                                    'cost': 5,
                                    'type': 'decoration',
                                    'quantity': 5

                                },
                                {
                                    'id': 'statuette_complex',
                                    'name': '🤼 Статуэтка из говна и палок',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'statuette_smart_girl',
                                    'name': '💃 Статуэтка "Умница"',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'smart_boy',
                                    'name': '🕺 Статуэтка "Умник, бля"',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'barman_2019',
                                    'name': '🍾 Бармен 2019 года',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'eiffel_tower',
                                    'name': '♟ Эйфелева Башня',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'sticker_pack',
                                    'name': '🎭 Набор стикеров Fallout 2',
                                    'cost': 30,
                                    'type': 'decoration',
                                    'quantity': 3
                                },
                                {
                                    'id': 'rebus_cube',
                                    'name': '🎲 Кубик ребусоведа',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 2
                                },
                                {
                                    'id': 'trident',
                                    'name': '🔱 Трезубец повелителя Пустоши',
                                    'cost': 30,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'saurons_point',
                                    'name': '🏵 Очко Саурона',
                                    'cost': 1,
                                    'type': 'decoration',
                                    'quantity': 10
                                },
                                {
                                    'id': 'urn_baphomet',
                                    'name': '⚱️Бафомет',
                                    'cost': 20,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'urn_faggoat',
                                    'name': '🎷Фаггот',
                                    'cost': 20,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'urn_anime',
                                    'name': '🏺 Анимэ',
                                    'cost': 20,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'two_girls_one_cup',
                                    'name': '🧁 Two girls, one cup',
                                    'cost': 120,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'mythical_friendship',
                                    'name': '✂️ Мифическая дружба',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 5
                                },
                                {
                                    'id': 'deanon',
                                    'name': '🆔 Деанон',
                                    'cost': 5,
                                    'type': 'decoration',
                                    'quantity': 10
                                },
                                {
                                    'id': 'paul',
                                    'name': '🌀 Пауль',
                                    'cost': 100,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'hamlet',
                                    'name': '💀 Гамлет',
                                    'cost': 50,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'yorick',
                                    'name': '💀 Йорик',
                                    'cost': 75,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'statuette_alien_1',
                                    'name': '👾 Ъуъеъкхх',
                                    'cost': 60,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'statuette_alien_2',
                                    'name': '👾 тпфптлтвфт ъуъ сука',
                                    'cost': 60,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'multipass_arthouse',
                                    'name': '💳 Мультипас бандита АртхǁȺǁус',
                                    'cost': 15,
                                    'type': 'decoration',
                                    'quantity': 15
                                },
                                {
                                    'id': '100_bucks',
                                    'name': '💵 Кровавые 100 баксов',
                                    'cost': 100,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': '200_bucks',
                                    'name': '💵 Кровные 200 баксов',
                                    'cost': 200,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'name_ring',
                                    'name': '🔅 Именной перстень "5-ый сезон"',
                                    'cost': 0,
                                    'type': 'decoration',
                                    'quantity': 75
                                },
                                {
                                    'id': 'something',
                                    'name': '🧫 Нечто',
                                    'cost': 50,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'punching_bag',
                                    'name': '🦙 Груша для битья',
                                    'cost': 50,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'pickman_painting',
                                    'name': '🎨 Картина Пикмана "F-395"',
                                    'cost': 100,
                                    'type': 'decoration',
                                    'quantity': 1
                                },
                                {
                                    'id': 'death_flag',
                                    'name': '🏴 Флаг смерти',
                                    'cost': 7,
                                    'type': 'decoration',
                                    'quantity': 10
                                },
                                {
                                    'id': 'armenian_rosary',
                                    'name': '📿 Армяне на стиле',
                                    'cost': 1,
                                    'type': 'decoration',
                                    'quantity': 4
                                },
                                {
                                    'id': 'sasai_kudasai',
                                    'name': '🔪 Сасайкудасай',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 5
                                },
                                {
                                    'id': 'pip_boy_toy',
                                    'name': '📟 игрушечный Пип-бой',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 5
                                },
                                {
                                    'id': 'pip_boy_model',
                                    'name': '📟 моделька Пип-боя',
                                    'cost': 10,
                                    'type': 'decoration',
                                    'quantity': 5
                                },
                                {
                                    'id': 'crown_pidor',
                                    'name': '👑 "Пидор дня"',
                                    'cost': 100,
                                    'type': 'decoration',
                                    'quantity': None
                                }
                            ] 
                        },
                        {
                            'id': 'THINGS',
                            'name': '📦 Вещи',
                            'value':
                            [
                                
                                {
                                    'id': 'redeemed_raid_ticket',
                                    'name': '🎫 Талон на рейд',
                                    'cost': 20,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'scalp_of_zak',
                                    'name': '🤯 Скальп зека',
                                    'cost': 50,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'scalp_of_banditos',
                                    'name': '🤯 Скальп бандита',
                                    'cost': 50,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'scalp_of_deus_ex_machina',
                                    'name': '🤯 Скальп Deus Ex Machina',
                                    'cost': 50,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'scalp_of_goose_point',
                                    'name': '🍩 Очко гуся',
                                    'cost': 50,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'bouquet_of_flowers',
                                    'name': '💐 Букет цветов',
                                    'cost': 12,
                                    'type': 'things',
                                    'quantity': 1000
                                },
                                {
                                    'id': 'nettle_list',
                                    'name': '🌿 Лечебная трава',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'wafelnitsa',
                                    'name': '🖨 Wafelница',
                                    'cost': 75,
                                    'type': 'things',
                                    'quantity': 10
                                },
                                {
                                    'id': 'sticks',
                                    'name': '🥢 Близкая дружба',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': 10
                                },
                                {
                                    'id': 'nipple_clamp',
                                    'name': '🗜 Зажим на соски',
                                    'cost': 10,
                                    'type': 'things',
                                    'quantity': 10
                                },
                                {
                                    'id': 'butt_plug',
                                    'name': '🕹️ Анальная пробка',
                                    'cost': 10,
                                    'type': 'things',
                                    'quantity': 10
                                },
                                {
                                    'id': 'magnifier',
                                    'name': '🔍 Лупа',
                                    'cost': 15,
                                    'type': 'things',
                                    'quantity': 2
                                },
                                {
                                    'id': 'disabled_carriage',
                                    'name': '♿️ Зато не пешком',
                                    'cost': 60,
                                    'type': 'things',
                                    'quantity': 2
                                },
                                {
                                    'id': 'speakers',
                                    'name': '🎶 Долбит нормально',
                                    'cost': 20,
                                    'type': 'things',
                                    'quantity': 30
                                },
                                {
                                    'id': 'flower_pervonach',
                                    'name': '🌷 Цветок "Первонах"',
                                    'cost': 3,
                                    'type': 'things',
                                    'quantity': 50
                                },
                                {
                                    'id': 'teddy_bear',
                                    'name': '🧸 Мишка-обнимашка',
                                    'cost': 10,
                                    'type': 'things',
                                    'quantity': 2
                                },
                                {
                                    'id': 'baby_tooth',
                                    'name': '🦷 Молочный зуб Рашки',
                                    'cost': 99,
                                    'type': 'things',
                                    'quantity': 1
                                },
                                {
                                    'id': 'key_to_halo',
                                    'name': '🔑 от квартиры в Ореоле',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': 75
                                },
                                {
                                    'id': 'brick',
                                    'name': '🧱 Кирпич на голову',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': 75
                                },
                                {
                                    'id': 'fork',
                                    'name': '🍴 Вилка в глаз',
                                    'cost': 2,
                                    'type': 'things',
                                    'quantity': 75
                                },
                                {
                                    'id': 'iron',
                                    'name': '🥌 Утюг',
                                    'cost': 7,
                                    'type': 'things',
                                    'quantity': 7
                                },
                                {
                                    'id': 'radar_detector',
                                    'name': '💿 Козырёк в авто',
                                    'cost': 15,
                                    'type': 'things',
                                    'quantity': 7
                                },
                                {
                                    'id': 'radar_detector_ii',
                                    'name': '📀 Блатной козырёк в авто',
                                    'cost': 20,
                                    'type': 'things',
                                    'quantity': 7
                                },
                                {
                                    'id': 'gps',
                                    'name': '🔊 GPS',
                                    'cost': 70,
                                    'type': 'things',
                                    'quantity': 5
                                },
                                {
                                    'id': 'horseshoe',
                                    'name': '🧲 Подкова',
                                    'cost': 25,
                                    'type': 'things',
                                    'quantity': 4
                                },
                                {
                                    'id': 'raid_plan',
                                    'name': '🧻 План рейда',
                                    'cost': 0,
                                    'type': 'things',
                                    'quantity': 1
                                },
                                {
                                    'id': 'comb',
                                    'name': '🚿 Расчёска от лох',
                                    'cost': 2,
                                    'type': 'things',
                                    'quantity': 15
                                },
                                {
                                    'id': 'pot',
                                    'name': '🏆 Горшок',
                                    'cost': 2,
                                    'type': 'things',
                                    'quantity': 20
                                },
                                {
                                    'id': '85',
                                    'name': '🚬 Арома стик',
                                    'cost': 3,
                                    'type': 'things',
                                    'quantity': 20
                                },
                                {
                                    'id': 'sword_of_the_jedi',
                                    'name': '🗡️ Меч джедая',
                                    'cost': 130,
                                    'type': 'things',
                                    'quantity': 20
                                },
                                {
                                    'id': 'photo_8_bandits',
                                    'name': '🎞️Фото 8-ми',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'sign_from_the_door',
                                    'name': '☢️Табличка на дверь',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'test_tube',
                                    'name': '🍼 Пробирка',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'trolley_bus_ticket',
                                    'name': '🎫 Билет на троллебус',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'pip_boy_2000',
                                    'name': '📟 Пип-бой 2000',
                                    'cost': 1000,
                                    'type': 'things',
                                    'quantity': 1000,
                                    'composition':
                                    [
                                        {
                                            'id': 'pip_broken_part',
                                            'counter': 1
                                        },
                                        {
                                            'id': 'pip_antenna',
                                            'counter': 1
                                        },
                                        {
                                            'id': 'pip_battery',
                                            'counter': 1
                                        },
                                        {
                                            'id': 'pip_spare_part',
                                            'counter': 2
                                        },
                                        {
                                            'id': 'pip_bolt',
                                            'counter': 3
                                        }
                                    ]
                                    
                                },
                                {
                                    'id': 'cast_iron',
                                    'name': '⛓️ Что-то чугунное',
                                    'cost': 30,
                                    'type': 'things',
                                    'quantity': None,
                                    'subjects_to_find':
                                    [
                                        'Что-то чугунное'
                                    ],
                                    'dialog_old_text': 'old_cast_iron'
                                },
                                {
                                    'id': 'pip_repair_kit',
                                    'name': '🛠️ Ремкомплект',
                                    'cost': 300,
                                    'type': 'things',
                                    'quantity': None,
                                    'composition':
                                    [
                                        {
                                            'id': 'cast_iron',
                                            'counter': 10
                                        }
                                    ],
                                    'wear': 
                                        {
                                            'one_use': 0.1,
                                            'value': 1
                                        }
                                },
                                {
                                    'id': 'bag_of_crypto_1000',
                                    'name': '🔘 Сертификат на 1000 Crypto',
                                    'cost': 1000,
                                    'type': 'things',
                                    'quantity': None,
                                    'composition':
                                    [
                                        {
                                            'id': 'bag_of_crypto_100',
                                            'counter': 10
                                        }
                                    ]
                                },
                                {
                                    'id': 'bag_of_crypto_100',
                                    'name': '🔘 Флэшка с 100 Crypto',
                                    'cost': 100,
                                    'type': 'things',
                                    'quantity': None,
                                    'composition':
                                    [
                                        {
                                            'id': 'crypto',
                                            'counter': 100
                                        }
                                    ]
                                },
                                {
                                    'id': 'collapsar',
                                    'name': '🔲 Collapsar',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None,
                                },
                                {
                                    'id': 'metal_detector',
                                    'name': '🧑‍🦯 Металлоискатель',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None,
                                    'skill':
                                        {   
                                            'storage': {
                                                'id':'watchmaker',
                                                'probability': 1,
                                                'value': 1000                                            
                                            }
                                        },
                                    'wear': 
                                        {
                                            'one_use': 0.01,
                                            'value': 1
                                        }
                                },
                                {
                                    'id': 'playstation5',
                                    'name': '🎮 PlayStation 5',
                                    'cost': 300,
                                    'type': 'things',
                                    'quantity': None,
                                    'skill':
                                        {   
                                            'training': {
                                                'id':'economist',
                                                'probability': 0.66,
                                                'value': -1,
                                                'dialog_text': 'playstation5_no_training' 
                                            }                                                                                     
                                        },
                                    'wear': 
                                        {
                                            'one_use': 0.01,
                                            'value': 1
                                        }
                                },
                                {
                                    'id': 'subscription_salon',
                                    'name': '💅 Абонемент в салон красоты',
                                    'cost': 150,
                                    'type': 'things',
                                    'quantity': None,
                                    'skill':
                                        {   
                                            'training': {
                                                'id':'economist',
                                                'probability': 0.66,
                                                'value': -1,
                                                'dialog_text': 'subscription_salon_no_training' 
                                            }                                                                                     
                                        },
                                    'wear': 
                                        {
                                            'one_use': 0.01,
                                            'value': 1
                                        }
                                }
                                
                            ]
                        },
                        {
                            'id': 'CURRENCY',
                            'name': '💴 Валюта',
                            'value':
                            [
                                {
                                    'id': 'crypto',
                                    'name': '🔘 Crypto',
                                    'cost': 1,
                                    'type': 'currency',
                                    'quantity': None,
                                }
                            ]
                        },
                        {
                            'id': 'PIP_BOY',
                            'name': '📟 Пип-бой',
                            'value':
                            [
                                {
                                    'id': 'pip_antenna',
                                    'name': '📟 антена от Пип-боя',
                                    'cost': 20,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'pip_battery',
                                    'name': '📟 аккумулятор от Пип-боя',
                                    'cost': 20,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'pip_packaging',
                                    'name': '📟 упаковка от Пип-боя',
                                    'cost': 1,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'pip_spare_part',
                                    'name': '📟 запчасть от Пип-боя',
                                    'cost': 25,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'pip_broken_part',
                                    'name': '📟 сломанный Пип-бой',
                                    'cost': 50,
                                    'type': 'things',
                                    'quantity': None
                                },
                                {
                                    'id': 'pip_bolt',
                                    'name': '📟 болт от Пип-боя',
                                    'cost': 20,
                                    'type': 'things',
                                    'quantity': None
                                }
                            ] 
                        }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'STICKERS' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'name': 'NEW_YEAR',
                            'value': 
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADZQEAAiUDUg9wLtRNP5HEShYE'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAADAgADZAEAAiUDUg9eJr3T5SlzNRYE'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAADAgADYwEAAiUDUg8xb6Oi5xhKIRYE'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAADAgADYgEAAiUDUg-BPZaIyNkJcRYE'
                                },
                                {
                                    'name': '5',
                                    'value': 'CAADAgADYQEAAiUDUg_cspuyDXpmOhYE'
                                },

                                {
                                    'name': '6',
                                    'value': 'CAADAgADXwEAAiUDUg8Vng-FXAEjcRYE'
                                },
                                {
                                    'name': '7',
                                    'value': 'CAADAgADYAEAAiUDUg8_nsFTwZHrYxYE'
                                },
                                {
                                    'name': '8',
                                    'value': 'CAADAgADXgEAAiUDUg_LK-sPC_cJwBYE'
                                },
                                {
                                    'name': '9',
                                    'value': 'CAADAgADXQEAAiUDUg95Y2aMiIFtVxYE'
                                },
                                {
                                    'name': '10',
                                    'value': 'CAADAgADWwEAAiUDUg-MMerpYQqc5RYE'
                                },

                                {
                                    'name': '11',
                                    'value': 'CAADAgADWgEAAiUDUg95rJid1HvscBYE'
                                },
                                {
                                    'name': '12',
                                    'value': 'CAADAgADWQEAAiUDUg_OxLS7v_c4HRYE'
                                },
                                {
                                    'name': '13',
                                    'value': 'CAADAgADWQEAAiUDUg_OxLS7v_c4HRYE'
                                },
                                {
                                    'name': '14',
                                    'value': 'CAADAgADWAEAAiUDUg_kwTI7r9mCvBYE'
                                },
                                {
                                    'name': '15',
                                    'value': 'CAADAgADVwEAAiUDUg-uJRhLA-w2JBYE'
                                },
                                {
                                    'name': '16',
                                    'value': 'CAADAgADUgEAAiUDUg8m7BF7uCsezhYE'
                                },
                                {
                                    'name': '17',
                                    'value': 'CAADAgADUwEAAiUDUg_elJYAAaQFd3UWBA'
                                },
                                {
                                    'name': '18',
                                    'value': 'CAADAgADVAEAAiUDUg8ggQAB7ZuCZzsWBA'
                                },
                                {
                                    'name': '19',
                                    'value': 'CAADAgADVQEAAiUDUg8De_0X8Gk8SBYE'
                                },
                                {
                                    'name': '20',
                                    'value': 'CAADAgADVgEAAiUDUg8epYq-rDccuxYE'
                                },
                                {
                                    'name': '21',
                                    'value': 'CAADAgADUQEAAiUDUg8k4gRFGJ52WBYE'
                                },
                                {
                                    'name': '22',
                                    'value': 'CAADAgADUAEAAiUDUg-ySAOTHhuI3RYE'
                                },
                                {
                                    'name': '23',
                                    'value': 'CAADAgADTwEAAiUDUg-IvO3zAz1k8RYE'
                                },
                                {
                                    'name': '24',
                                    'value': 'CAADAgADTgEAAiUDUg8Hwc4KQsJGXRYE'
                                },
                                {
                                    'name': '25',
                                    'value': 'CAADAgADTQEAAiUDUg_LuVlnrID-hxYE'
                                }                                
                            ]
                        },
                        {
                            'name': 'LOVE_DAY',
                            'value': 
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADVwMAAoe3Gh5fN2JO7jWn2RYE'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAADAgADWAMAAoe3Gh6pitv5db4FkRYE'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAADAgADWQMAAoe3Gh5uz6P8gKqkNRYE'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAADAgADWgMAAoe3Gh4eUR-h9SYeWxYE'
                                },
                                {
                                    'name': '5',
                                    'value': 'CAADAgADXAMAAoe3Gh4M8BxFfEUdqRYE'
                                },

                                {
                                    'name': '6',
                                    'value': 'CAADAgADXQMAAoe3Gh6twGryPCR3tRYE'
                                },
                                {
                                    'name': '7',
                                    'value': 'CAADAgADXgMAAoe3Gh5xCQI6xpkGXRYE'
                                },
                                {
                                    'name': '8',
                                    'value': 'CAADAQADyQADTNZnMNX19QPGYpuvFgQ'
                                },
                                {
                                    'name': '9',
                                    'value': 'CAADAQADyAADTNZnMK1RYUeWCxm_FgQ'
                                },
                                {
                                    'name': '10',
                                    'value': 'CAADAQADxwADTNZnMKFlT04S1hqcFgQ'
                                },

                                {
                                    'name': '11',
                                    'value': 'CAADAQADxgADTNZnMMFLbnRzfsOOFgQ'
                                },
                                {
                                    'name': '12',
                                    'value': 'CAADAQADxAADTNZnMElO0Tuc_g0fFgQ'
                                },
                                {
                                    'name': '13',
                                    'value': 'CAADAQADwwADTNZnMHa8oJvHTFqIFgQ'
                                },
                                {
                                    'name': '14',
                                    'value': 'CAADAQADwgADTNZnMNPfeHSSUMpxFgQ'
                                },
                                {
                                    'name': '15',
                                    'value': 'CAADAQADwQADTNZnMAxj6hRLhbl1FgQ'
                                },
                                {
                                    'name': '16',
                                    'value': 'CAADAQADwAADTNZnMLlDhK-nyCo1FgQ'
                                },
                                {
                                    'name': '17',
                                    'value': 'CAADAQADvwADTNZnMBTVM9xEDpvcFgQ'
                                }                         
                            ]
                        },
                        {
                            'name': '8_MARCH',
                            'value': 
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAK_Bl5j-llphvp78XdkwKfNL6VJv_4OAAK4HAAC6VUFGKbJ480GLs9TGAQ'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAACAgIAAxkBAAK_CF5j-ltUdC_DpmgYjPyz9K9kqrZaAAK5HAAC6VUFGDFazo8YxHcXGAQ'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAACAgIAAxkBAAK_Cl5j-l52rW4yx-FQvpO_d5bb_hKHAAK6HAAC6VUFGJr-i_4xlf4nGAQ'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAACAgIAAxkBAAK_DF5j-l_rLbvni7xhRHyzE7Uck8BqAAK7HAAC6VUFGLkHvyNI1f9LGAQ'
                                },
                                {
                                    'name': '5',
                                    'value': 'CAACAgIAAxkBAAK_Dl5j-myHvzV9PLqLG3Pv7orcqKA2AAK9HAAC6VUFGK6-vfbLuy34GAQ'
                                },

                                {
                                    'name': '6',
                                    'value': 'CAACAgIAAxkBAAK_EF5j-nCXgn4YWFNwDJvGcZqPFw1fAAK-HAAC6VUFGDeF17MNNZwNGAQ'
                                },
                                {
                                    'name': '7',
                                    'value': 'CAACAgIAAxkBAAK_El5j-nbBlvPk4SioM-siH_vvvV88AAK_HAAC6VUFGOvhMml9MfUGGAQ'
                                },
                                {
                                    'name': '8',
                                    'value': 'CAACAgIAAxkBAAK_FF5j-njZuoFrKAwqQ8FXd-H0ELdHAALAHAAC6VUFGBpkt-QvdKUWGAQ'
                                },
                                {
                                    'name': '9',
                                    'value': 'CAACAgIAAxkBAAK_Fl5j-otv_i9P_LDdwVLgZ8fjx8R5AALGHAAC6VUFGHC55PHXL4S7GAQ'
                                },
                                {
                                    'name': '10',
                                    'value': 'CAACAgIAAxkBAAK_GF5j-pVZj6vORQWNXyDWIKS7R1yXAALPHAAC6VUFGJCHEuEL02LtGAQ'
                                },

                                {
                                    'name': '11',
                                    'value': 'CAACAgIAAxkBAAK_Gl5j-pg0MECfBHcYsFVzRd4qmB0lAALOHAAC6VUFGA2COUl53RxnGAQ'
                                },
                                {
                                    'name': '12',
                                    'value': 'CAACAgIAAxkBAAK_HF5j-ps01cFbpj8lOQhhsF7PS4cYAALMHAAC6VUFGBl49GcrtAk9GAQ'
                                },
                                {
                                    'name': '13',
                                    'value': 'CAACAgIAAxkBAAK_Hl5j-qpj7sf5tzZCIdYp3tVXRHLDAALfHAAC6VUFGJZhBpkC7iVEGAQ'
                                },
                                {
                                    'name': '14',
                                    'value': 'CAACAgIAAxkBAAK_IF5j-rHti_Vj1glxYoAa8kohOMWtAALjHAAC6VUFGCaLHp4cyNcJGAQ'
                                },
                                {
                                    'name': '15',
                                    'value': 'CAACAgIAAxkBAAK_Il5j-rfdtwsrsW-0_wpDbgf-lT4CAALiHAAC6VUFGAhFqc6xKC3ZGAQ'
                                },
                                {
                                    'name': '16',
                                    'value': 'CAACAgIAAxkBAAK_JF5j-r9Al4J0yY7JOXxJna5a6Ws0AALhHAAC6VUFGEJUO9uqdGiTGAQ'
                                },
                                {
                                    'name': '17',
                                    'value': 'CAACAgIAAxkBAAK_Jl5j-sm_s2KcCqg-TELKxi5pgAqvAALgHAAC6VUFGAxlJoqvGXwWGAQ'
                                },
                                {
                                    'name': '18',
                                    'value': 'CAACAgIAAxkBAAK_KF5j-tHzJH_NM1m-LORZD98-Dh-KAALnHAAC6VUFGHBPoTA-sCZ7GAQ'
                                }                          
                            ]
                        },
                        {
                            'name': 'BOT_VOICE',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADKAAD29t-AAHTqBFpbSvY8xYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_LOVE',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADLgAD29t-AAHj7r1tLLx9rxYE'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAADAgADJgAD29t-AAF-dqsVA8i9LRYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_FUCKOFF',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADLQAD29t-AAFZ6winaM23ehYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_LIKE',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADKwAD29t-AAG92hgvlAcIAxYE'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAADAgADKgAD29t-AAFacpWXMyDGihYE'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAADAgADLAAD29t-AAEZWj4hb9ADpRYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_DEAD',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADKQAD29t-AAFgFIcFdTXiDhYE'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAACAgIAAxkBAAJ-uF4wjlwuQ6ort2ZkdYlSovXbkNNZAAIhAAPyBCAW9ZOxMuI8IPMYBA'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_LOOK',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADJwAD29t-AAFc8IBFtdp6yxYE'
                                }
                            ] 
                        },
                        {
                            'name': 'NEW_MEMBER_IMG',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'AgADAgADrawxG6IbCEkSxD_UTVbIseyDwQ8ABAEAAwIAA3kAAzw0AwABFgQ'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_NEW_MEMBER',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgAD3gADHqvRF44ChJs0J0IAARYE'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAADAgADRQADmFw8HIiMxKGRHpSlFgQ'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAADAgADxT8AAuCjggd50ofpjPyNAAEWBA'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAADAgADAQADkp8eEQpfUwLsF-b2FgQ'
                                },
                                {
                                    'name': '5',
                                    'value': 'CAADAgADpwMAAs-71A6n4GtRdkxtohYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_FINGER_TYK',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADHwAD8gQgFh9xxAnDN9D6FgQ'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAACAgIAAxkBAAJ-jF4wa3_QsJkHiyfbdYwB-LjkKcNOAAIgAAPyBCAWr8697eDb43AYBA'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_DA_PINDA',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADDgYAAj6IGgu5HWcwB3TQVhYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_NO_PINDA',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADDwYAAj6IGguD0q7ZODC79RYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_A_PINDA',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAJ7g14t6foXyqRJtOR-XMK5h6yNKGqkAAJQAAPyBCAWeiu5xwoM98oYBA'
                                }
                            ] 
                        },
                        {
                            'name': 'CENSORSHIP',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADfA4AAmOLRgzxiNhOjVmDPBYE'
                                },
                                {
                                    'name': '2',
                                    'value': 'AgADAgADy60xG8QNIEmLFUZxY320f8pdyw4ABAEAAwIAA3kAA5MOAQABFgQ'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAADAgADsgAD-6tWB5W7vi6ux7SnFgQ'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAADAgADBgADCMJfFtQS7GCowxIKFgQ'
                                },
                                {
                                    'name': '5',
                                    'value': 'CAADAgAD4QIAAmX_kgpWiaS39GiDWxYE'
                                },
                                {
                                    'name': '6',
                                    'value': 'AgADAgADzq0xG8QNIEnthvJx7PnW9UWnwg8ABAEAAwIAA3gAA4tOAwABFgQ'
                                },
                                {
                                    'name': '7',
                                    'value': 'AgADAgADz60xG8QNIEltT1biwObh8ZdRyw4ABAEAAwIAA3kAA0UNAQABFgQ'
                                },
                                {
                                    'name': '8',
                                    'value': 'AgADAgAD0K0xG8QNIElRY5tmpYRk5D9pwQ8ABAEAAwIAA3kAAwZTAwABFgQ'
                                },
                                {
                                    'name': '9',
                                    'value': 'AgADAgAD0a0xG8QNIEkR-yip89sUUr5lXA8ABAEAAwIAA3gAA5xaBAABFgQ'
                                },
                                {
                                    'name': '10',
                                    'value': 'AgADAgAD0q0xG8QNIEn9XHNBn3JmP_B5wQ8ABAEAAwIAA3gAA6pLAwABFgQ'
                                },
                                {
                                    'name': '11',
                                    'value': 'CAADAgADhgADhUEyEMHpvvkmUG5QFgQ'
                                },
                                {
                                    'name': '12',
                                    'value': 'CAADAgADcAADNIWFDAm2gLIQsJ0OFgQ'
                                },
                                {
                                    'name': '13',
                                    'value': 'CAADAgADBAMAAoR7MhzxetN6F8OrlBYE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_SALUTE',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAADAgADtgADTptkAqpNYvdldSrYFgQ'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAADAgADKwAD8gQgFjLRhiYsCHQTFgQ'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAADBQADlAMAAukKyAPXbNncxSnLkRYE'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAACAgIAAxkBAAKcc15DFTQFZ-ztPuwb7WUYiAPM_OtmAAK2AANOm2QCqk1i92V1KtgYBA'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_MORNING',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAKEy142fCMG7X0MjErMnCW_L9kYIla8AALCPwAC4KOCB6u6lHvLpulbGAQ'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAACAgQAAxkBAAKE0V42gLJ0vnjsbZsQNv_YuY24P09pAAI8AQACa65eCWU2xUL2sOUQGAQ'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_NIGHT',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAKEzV42f8A_r2sQsKzfjgVDXpzzZ0yLAAJPAgACWuOKF5k-9glf2ST7GAQ'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAACAgIAAxkBAAKEz142gCsRn2f3r-e-fB-AlGW21dS2AALDPwAC4KOCB5UoxIzuehFgGAQ'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_GO_FLEX',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAKVC148VaR7rrZrEPG4lozAc4bKcKChAAJkAAOFQTIQGugJwpZxbJ0YBA'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_FLEX',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAKVD148VhBELpdpWH-hL47yQwyrQi0ZAAJUAAOFQTIQ2ZWEJZvDUmoYBA'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAACAgIAAxkBAAKVEV48VhFWneZt-_ikDC0FbIN-N5v6AAJVAAOFQTIQS8S4HV367O8YBA'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAACAgIAAxkBAAKVE148Vk0kqnscDqURTEmK8jK-GA6TAAIPAAN1UIETwg1RZjDIXX8YBA'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAACAgIAAxkBAAKVFV48VlYtoKDAi0gUr8i4U047O9S4AAIOAAN1UIET_sdrEVjKnl0YBA'
                                },
                                {
                                    'name': '5',
                                    'value': 'CAACAgIAAxkBAAKVF148VnpTtwyJlIHyGk0H3JPiM9t_AAIQAAN1UIETE8FnCIyfw_sYBA'
                                },
                                {
                                    'name': '6',
                                    'value': 'CAACAgIAAxkBAAKVGV48VoW6wk9967s0AAGEsdZR8eo9zAACCAADdVCBEz9--bhiHsOGGAQ'
                                },
                                {
                                    'name': '7',
                                    'value': 'CAACAgIAAxkBAAKVG148VzCiNRRB5yyt4AwrrvsSVIgqAAIHAAN1UIET-UUCe-oKIroYBA'
                                },
                                {
                                    'name': '8',
                                    'value': 'CAACAgIAAxkBAAKVHV48VzhEbnSmzb5YAlYf4YbGN4L-AAILAAN1UIET3l2gshmuaO0YBA'
                                },
                                {
                                    'name': '9',
                                    'value': 'CAACAgIAAxkBAAKVH148V1nqnEaeRUXwQrL9UljQCZZBAAI4dgEAAWOLRgwsE7xUfVt_5hgE'
                                },
                                {
                                    'name': '10',
                                    'value': 'CAACAgIAAxkBAAKVIV48V2awGJxVPZHIB_UWdNiKka7dAAI7dgEAAWOLRgxZxmSeLOoRXBgE'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_END_FLEX',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAKVDV48VezE11O-GkbhFbU0t0K8O5o3AAJjAAOFQTIQveRUbGOqm4UYBA'
                                }
                            ] 
                        },
                        {
                            'name': 'GOTORAID',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAECXj5ercl5kyy8XAzzKH2dfZpjNSuokwACGAADkaI7BudYKDBs40YmGQQ'
                                },
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAECXkRercmoA48Y-oDA6h4Gj3uBiOTC1wACIgAD8gQgFhbcd1mXrcBaGQQ'
                                }
                            ] 
                        },
                        {
                            'name': 'DOOR',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'AgACAgIAAxkBAALmrl5v0aD7Y9IU_YszBYvuj4M8VYLUAAKkqzEbgWg4S28P5Y5J_n1Oktq6DwAEAQADAgADeAADsjMGAAEYBA'
                                }
                            ] 
                        },
                        {
                            'name': 'BOT_CRY',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': 'CAACAgIAAxkBAAKVMV48dN0Ymx-YHrGwIi4GuJnRRVbWAAI6AANlbZgfExN7LTUarJAYBA'
                                },
                                {
                                    'name': '2',
                                    'value': 'CAACAgIAAxkBAAKVN148ed0hN5FOyvmYPDmozwGb-wABoAACBAADrQLSHUWyEm4hVhw3GAQ'
                                },
                                {
                                    'name': '3',
                                    'value': 'CAACAgIAAxkBAAKVOF48ed3-C_3Mec1JTV7d5GTB6mY6AAJiAANlbZgfP47FZbJNJQQYBA'
                                },
                                {
                                    'name': '4',
                                    'value': 'CAACAgIAAxkBAAKVOV48ed1lrZXiZXMffEVmg37Xe-hvAAI8AANlbZgf0BmLu68jxS8YBA'
                                },
                                {
                                    'name': '5',
                                    'value': 'CAACAgIAAxkBAAKVOl48ed1lX3iy-04Wc5xyOZ5j_BphAAIgAAOYXDwc1NuZ1qm4LXYYBA'
                                },
                                {
                                    'name': '6',
                                    'value': 'CAACAgIAAxkBAAKVPl48ed1gDBghgY0egpqLJSDA4si5AAIMAAP6o7QP-r_rl5vsbUkYBA'
                                },
                                {
                                    'name': '7',
                                    'value': 'CAACAgIAAxkBAAKVPV48ed0tsgABThh9liFAxymbNnLHawACDgAD8gQgFlDy6fGIe-u2GAQ'
                                },
                                {
                                    'name': '8',
                                    'value': 'CAACAgIAAxkBAAKVO148ed19WlzDhSfCU0RjCdd97GqSAAJsAAM0hYUMN36StWevo6AYBA'
                                },
                                {
                                    'name': '9',
                                    'value': 'CAACAgIAAxkBAAKVPF48ed2Vwpw51C3vrhOhhCOo6oBYAAJwAAM0hYUMCbaAshCwnQ4YBA'
                                }
                            ] 
                        }

                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'RAIDLOCATIONS' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'id': '0',
                            'name': 'Не пинговать 🔕',
                            'liga': 'Детская лига'
                        },
                        {
                            'id': '5',
                            'name': 'Старая фабрика 📍5км',
                            'liga': 'Детская лига'
                        },
                        {
                            'id': '9',
                            'name': 'Завод "Ядер-Кола" 📍9км',
                            'liga': 'Детская лига'
                        },
                        {
                            'id': '12',
                            'name': 'Тюрьма 📍12км',
                            'liga': 'Детская лига'
                        },
                        {
                            'id': '16',
                            'name': 'Склады 📍16км',
                            'liga': 'Вторая лига'
                        },
                        {
                            'id': '20',
                            'name': 'Датацентр 📍20км',
                            'liga': 'Савант-лига'
                        },
                        {
                            'id': '24',
                            'name': 'Госпиталь 🚷 📍24км',
                            'liga': 'Детская лига'
                        },
                        {
                            'id': '28',
                            'name': 'Завод "Электрон" 🚷 📍28км',
                            'liga': 'Вторая лига'
                        },
                        {
                            'id': '32',
                            'name': 'Офисное здание 🚷 📍32км',
                            'liga': 'Детская лига'
                        },
                        {
                            'id': '38',
                            'name': 'Иридиевые шахты 🚷 📍38км',
                            'liga': 'Савант-лига'
                        },
                        {
                            'id': '46',
                            'name': 'Склад металла 📍46км',
                            'liga': 'Вторая лига'
                        },
                        {
                            'id': '53',
                            'name': 'Радиостанция 🚷📍53км',
                            'liga': 'Вторая лига'
                        },
                        {
                            'id': '54',
                            'name': 'Водохранилище 📍54км',
                            'liga': 'Савант-лига'
                        },
                        {
                            'id': '57',
                            'name': 'Реактор 🚷📍57км',
                            'liga': 'Савант-лига'
                        },
                        {
                            'id': '63',
                            'name': 'Институт 🚷📍63км',
                            'liga': 'Савант-лига'
                        }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'DUNGEONS' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'name': '⛏️Старая шахта',
                            'value': '11'
                        },{
                            'name': '🚷🚽Сточная труба',
                            'value': '23'
                        },{
                            'name': '⚙️Открытое убежище',
                            'value': '29'
                        },{
                            'name': '🚷🦇Бэт-пещера',
                            'value': '34'
                        },{
                            'name': '🦆Перевал Уткина',
                            'value': '39'
                        },{
                            'name': '⛰️Высокий Хротгар',
                            'value': '45'
                        },{
                            'name': '🛑Руины Гексагона',
                            'value': '50'
                        },{
                            'name': '🚷🔬Научный комплекс',
                            'value': '56'
                        },{
                            'name': '⛩️Храм Испытаний',
                            'value': '69'
                        },{
                            'name': '🗨️Черная меза',
                            'value': '74'
                        }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'BLACK_LIST' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'name': '*******ve1es88',
                            'value': 'За попытку скрытно бросить старый пип Джу.'
                        }
                        
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'PROBABILITY' }
newvalues = { "$set": { "value": 
                    [
                        {
                            # Вероятность Я тебя не знаю
                            'name': 'I_DONT_KNOW_YOU',
                            'value': 0.5
                        },
                        {
                            # Вероятность Быть или не быть
                            'name': 'TO_BE_OR_NOT',
                            'value': 0.5
                        },
                        {
                            # Range Бан тебе!
                            'name': 'FUNY_BAN',
                            'value': 600
                        },
                        {
                            # Вероятность Эмоции
                            'name': 'EMOTIONS',
                            'value': 0.10
                        },
                        {
                            # Вероятность Да, сэр!
                            'name': 'YES_STICKER',
                            'value': 0.10
                        },
                        {
                            # Вероятность Нет!
                            'name': 'NO_STICKER',
                            'value': 0.10
                        },
                        {
                            # Вероятность Тык!
                            'name': 'FINGER_TYK',
                            'value': 1.00
                        },
                        {
                            # Вероятность Ты победил!
                            'name': 'YOU_WIN',
                            'value': 0.50
                        },
                        {
                            # Вероятность Ты проиграл
                            'name': 'YOU_LOSER',
                            'value': 0.50
                        },
                        {
                            # Вероятность
                            'name': 'SALUTE_STICKER',
                            'value': 0.50
                        },
                        {
                            # Вероятность
                            'name': 'MORNING_STICKER',
                            'value': 0.30
                        },
                        {
                            # Вероятность
                            'name': 'DOOR_STICKER',
                            'value': 1.00
                        },
                        {
                            # Вероятность
                            'name': 'NIGHT_STICKER',
                            'value': 0.30
                        },
                        {
                            # Вероятность
                            'name': 'A_STICKER',
                            'value': 0.00
                        },
                        {
                            # Вероятность
                            'name': 'YOU_PRIVATE_CHAT',
                            'value': 0.5
                        },
                        {
                            # Range
                            'name': 'JUGI_BAD_BOT_BAN',
                            'value': 1488
                        },
                        {
                            # Range
                            'name': 'PANDING_WAIT_START_1',
                            'value': 5
                        },
                        {
                            # Range
                            'name': 'PANDING_WAIT_END_1',
                            'value': 10
                        },
                        {
                            # Range
                            'name': 'PANDING_WAIT_START_2',
                            'value': 15
                        },
                        {
                            # Range
                            'name': 'PANDING_WAIT_END_2',
                            'value': 20
                        },
                        {
                            # Range
                            'name': 'JUGI_FLEX',
                            'value': 500
                        },
                        {
                            # Вероятность заражения
                            'name': 'KORONOVIRUS',
                            'value': 0.1
                        },
                        {
                            # скорость полураспада
                            'name': 'KORONOVIRUS_HALFLIFE',
                            'value': 0.5
                        },
                        {
                            # Вероятность защита от медицинской маски
                            'name': 'MASK_DEFENCE',
                            'value': 0.9
                        },
                        {
                            # Вероятность лечения доктора
                            'name': 'DOCTOR_CURED',
                            'value': 0.3
                        },
                        {
                            # Вероятность лечения доктора
                            'name': 'DOCTOR_MAIN_CURED',
                            'value': 0.6
                        }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'USER_SETTINGS' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'id': 'pidor_of_the_day',
                            'name': '👨‍❤️‍👨Участник "Пидор дня"',
                            'value': False
                        },
                        {
                            'id': 'my_gerb',
                            'name': '🃏Мой герб',
                            'value': ""
                        },
                        {
                            'id': 'partizan',
                            'name': '🧠Играю в "П"артизана',
                            'value': False
                        }
                        # ,
                        # {
                        #     'name': '⌚Часовой пояс',
                        #     'value': ""
                        # },
                        # {
                        #     'name': '🗓️День рождения',
                        #     'value': ""
                        # },
                        # {
                        #     'name': '🔔Пинги',
                        #     'value': ""
                        # }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'REPORTS' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'name': 'KILLERS',
                            'value': {
                                'from_date': datetime.datetime(2020, 1, 31, 6, 0, 0).timestamp(), 
                                'to_date': None
                            }
                        },
                        {
                            'name': 'RAIDS',
                            'value': {
                                'from_date': datetime.datetime(2020, 3, 11, 6, 0, 0).timestamp(), 
                                'to_date': None
                            }
                        }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'ADMINISTRATOR' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'login': 'GonzikBenzyavsky',
                            'chat' : 497065022
                        },
                        {
                            'login': 'WestMoscow',
                            'chat' : 0 #214221494
                        }
                    ]
                }
            } 
             
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'BANDS_ACCESS_WARIORS' }
newvalues = { "$set": { "value": 
            [
                {'band': 'АртхǁȺǁус'},
                {'band': 'без банды'},
                {'band': 'Crewname'},
                {'band': 'ЭнтрǁØǁпия'},
                # {'band': 'ЩекØтилы БанȺнов'},
                {'band': 'ǁGØodfeelȺssǁ'},
                {'band': 'New Vegas'},
                {'band': 'Тамплиеры'}
                
            ]
        } 
    } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'GOATS_BANDS' }
newvalues = { "$set": 
                { "value": 
                    [
                        { 
                            'name': 'FǁȺǁggǁØǁAT',
                            'liga': 'Детская лига',
                            'boss': [
                                        'WestMoscow',
                                        'GonzikBenzyavsky'
                                    ],
                            'poweruser': 
                                    [
                                        'WestMoscow',
                                        'Viktoriya_Sizko',
                                        'EastMinsk',
                                        'nik_stopka',
                                        'GonzikBenzyavsky',
                                        'VirtusX',
                                        'HaringtonVl'
                                    ],
                            'bands': 
                                    [
                                        {
                                            'name': 'без банды',
                                            'boss': 'WestMoscow'
                                        },
                                        {
                                            'name': 'ЭнтрǁØǁпия',
                                            'boss': 'Viktoriya_Sizko'
                                        },
                                        {
                                            'name': 'АртхǁȺǁус',
                                            'boss': 'Innok27'
                                        },
                                        {
                                            'name': 'ǁGØodfeelȺssǁ',
                                            'boss': 'nik_stopka'
                                        },
                                        {
                                            'name': 'crewname',
                                            'boss': 'EastMinsk'
                                        }
                                    ],
                            'chats_test': 
                                    {
                                        'secret' : -1001297175242,
                                        'info' : -351796836
                                    },
                            'chats': 
                                    {
                                        'secret' : -1001326436156,
                                        'info' : -1001296823890
                                    }

                        },
                        { 
                            'name': 'New Vegas',
                            'liga': 'Вторая лига',
                            'boss': [
                                        'SSG76reg'
                                    ],
                            'poweruser': 
                                    [
                                        'SSG76reg'
                                    ],        
                            'bands': 
                                    [
                                        {
                                            'name': 'New Vegas',
                                            'boss': 'SSG76reg'
                                        }
                                    ],
                            'chats': 
                                    {
                                        'secret' : -0,
                                        'info' : -0
                                    }
                        },
                        { 
                            'name': 'Бафомет',
                            'liga': 'Савант-лига',
                            'boss': [
                                        'kMitty',
                                        'AutismusMaximus',
                                    ],
                            'poweruser': 
                                    [
                                        'kMitty',
                                        'AutismusMaximus',
                                    ],  
                            'bands': 
                                    [
                                        {
                                            'name': 'Тамплиеры',
                                            'boss': 'kMitty'
                                        }
                                    ],
                            'chats': 
                                    {
                                        'secret' : -491611374,
                                        'info' : -491611374
                                    }
                        }
                        
                    ]   
                } 
            } 
u = settings.update_one(myquery, newvalues)

print("#==========================#")              
print("#         RAIDS            #")    
print("#==========================#")
print("#==========================#")              
print("#         USERS            #")    
print("#==========================#")
print("#==========================#")              
print("#         WARIORS          #")              
print("#==========================#")
print("#==========================#")              
print("#         BATTLE           #")              
print("#==========================#")


if 1==2: # обновляем composition 
    updateUser(None)
    listInv = GLOBAL_VARS['inventory']
    # for z in listInv:
    #     print(z)
    for user in list(filter(lambda x : len(x.getInventory()) > 0, USERS_ARR)):
        print(f'Update {user.getLogin()}')
        for inv in user.getInventory():
            elem = next((x for i, x in enumerate(listInv) if x['id']==inv['id']), None)
            
            if elem == None:
                continue
            elem = elem.copy()
            if 'composition' in elem:
                print(f'    {inv}')
                composition_arr = []
                for com in elem['composition']:
                    composit = next((x for i, x in enumerate(listInv) if x['id']==com['id']), None).copy()
                    if composit == None:
                        continue
                    for i in range(0, com["counter"]):
                        composit.update(({'uid': f'{uuid.uuid4()}'}))
                        composition_arr.append(composit)
                        print(f'         {composit["name"]}')
                if len(composition_arr)>0:
                    inv.update({'composition': composition_arr})    
        updateUser(user)     

if 1==2: # Обновляем атрибуты навыков
    updateUser(None)
    
    for user in list(filter(lambda x : len(x.getInventoryType(['skill'])) > 0, USERS_ARR)):
        for skill in user.getInventoryType(['skill']):
            elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']==skill['id']), None) 
            if 'forgetting' in elem:
                skill.update({'forgetting': elem['forgetting']})
                print(f'    {skill["name"]}')
        updateUser(user)
        print(f'Update {user.getLogin()}')

if 1==2:
    # Запускать один раз! Иначе затрет
    old_login = 'Mefabest'
    new_login = 'Y0ur_sugar'

    # Убиваем пользователя с новым логином
    myquery = {'login': new_login}
    registered_users.delete_one(myquery)

    # Находим старого и меняем ему логин на новый
    registered_users.update_one(
        { 'login': old_login},
        { '$set': 
            { 'login': new_login } 
        }
    )
    print(f'Бандиту {old_login} заменена логин на {new_login}')

viruses = ['girlfriend_bouquet', 'covid-19', 'mirror_disease']
if 1==2:
    for virus in viruses:
        updateUser(None)
        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='VIRUSES')['value']) if x['id']==virus), None) 

        for user in list(filter(lambda x : x.getInventoryThingCount(elem) > 0, USERS_ARR)):
            vir = user.getInventoryThing(elem)
            
            print(f'before {user.getLogin()} {vir}')
            user.removeInventoryThing(vir)
            user.addInventoryThing(elem)
            updateUser(user)
            print(f'after {user.getLogin()} {user.getInventoryThing(elem)}')
            print(f'=======================================================')

clothes = ['medical_mask']
if 1==2:
    for clothes_name in clothes:
        updateUser(None)
        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='CLOTHES')['value']) if x['id']==clothes_name), None) 

        for user in list(filter(lambda x : x.getInventoryThingCount(elem) > 0, USERS_ARR)):
            clo = user.getInventoryThing(elem)
            
            print(f'before {user.getLogin()} {clo}')
            try:
                elem['wear'].update({'value': clo['wear']['value']})
            except:
                pass

            user.removeInventoryThing(clo)
            user.addInventoryThing(elem)
            updateUser(user)
            print(f'after {user.getLogin()} {user.getInventoryThing(elem)}')
            print(f'=======================================================')

# 'electrician', 'medic', 'robotics','programmer', 'watchmaker', 'economist', 'fighter', 
skill_names = ['electrician', 'medic', 'robotics','programmer', 'watchmaker', 'economist', 'fighter']
if 1==2:
    for skill_name in skill_names:
        updateUser(None)
        elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']==skill_name), None) 

        for user in list(filter(lambda x : x.getInventoryThingCount(elem) > 0, USERS_ARR)):
            skill = user.getInventoryThing(elem)
            
            print(f'before {user.getLogin()} {skill}')
            elem.update({'storage': skill['storage']})
            elem.update({'flags': skill['flags']})

            user.removeInventoryThing(skill)
            user.addInventoryThing(elem)
            updateUser(user)
            print(f'after {user.getLogin()} {user.getInventoryThing(elem)}')
            print(f'=======================================================')


thing_names = ['crown_pidor_of_the_day']
if 1==2:
    updateUser(None)
    for thing_name in thing_names:
        # elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='THINGS')['value']) if x['id']==thing_name), None) 
        elem = {'id': thing_name, 'type': 'decoration'}

        for user in list(filter(lambda x : x.getInventoryThingCount(elem) > 0, USERS_ARR)):
            things = user.getInventoryThings(elem)
            
            for inv in things:
                # Заменяем цену у всех вещей этого типа
                # if 'cost' in inv:
                #    inv.update({'cost': elem['cost']})
                # Заменяем id
                inv.update({'id': 'crown_pidor'})


            updateUser(user)
            print(f'Обновили {thing_name}')

# if 1==2:
    # if now_date.hour in (99, 19) and now_date.minute in (99, 58) and now_date.second < 15:
        
    #     # u = ('Hermia_Nerbne', 'DaisyBellTrot', 'dan4yk', 'pif_paf_zero', 'misscalderona', 'VirtusX', 'A_Baikonur',
    #     # 'aohanesian', 'asaelko', 'szvika', 'WildFire112', 'Balbes_36', 'puhnastiyus', 'MrMrakZ', 'GonzikBenzyavsky',
    #     # 'Innok27', 'artiomse', 'wildcucumber', 'trimprim', 'triple6ixx', 'XyTop_2', 'DeadChild', 'Gromnsk', 'Serjanioo',
    #     # 'darthmall', 'PelMen479', 'Mefabest', 'barondumdeedum', 'EastMinsk', 'GolodniyEnot', 'WORSA_crew NaRdiST', 'Tanelda','eX3emz')
    #     # u = ('GonzikBenzyavsky', 'Innok27', 'artiomse' ,'wildcucumber','Art_Zank','NorthDragoN','triple6ixx','XyTop_2','DeadChild','Gromnsk','Serjanioo','darthmall','PelMen479', 'Mefabest')
    #     u = []
    #     for user in list(filter(lambda x : 1 > 0, USERS_ARR)):
    #         u.append(user.getLogin())
    #     antyBoltReport = ''
    #     counter = 0
    #     for login in u:
    #         user = getUserByLogin(login)
    #         if user:
    #             counter = counter + 1
    #             #acc = '🎫🍼 Билет на гигантскую бутылку'
    #             bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_5'), None)
    #             if user.isInventoryThing(bolt):
    #                 pass
    #             else:
    #                 #acc = '🔩🔩🔩🔩 Болт М1488, возложенный на рейд'
    #                 bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_4'), None)
    #                 if user.isInventoryThing(bolt):
    #                     pass
    #                 else:
    #                     #acc = '🔩🔩🔩 Болт М404, возложенный на рейд'
    #                     bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_3'), None)
    #                     if user.isInventoryThing(bolt):
    #                         pass
    #                     else:
    #                         #acc = '🔩🔩 Болт М228, возложенный на рейд'
    #                         bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_2'), None)
    #                         if user.isInventoryThing(bolt):
    #                             pass
    #                         else:
    #                             #acc = '🔩 Болт М69, возложенный на рейд'
    #                             bolt = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='RAID_BOLTS')['value']) if x['id']=='bolt_1'), None)
    #                             if user.isInventoryThing(bolt):
    #                                 pass
    #                             else:
    #                                 continue

    #             if user.isInventoryThing(bolt):
    #                 # send_message_to_admin(f'❎ {user.getNameAndGerb()} @{user.getLogin()}\nЗабрали:\n▫️ {bolt["name"]}!')
    #                 user.removeInventoryThing(bolt)
    #                 # send_messages_big(goat['chats']['secret'], text=user.getNameAndGerb() + '!\n' + '❎ Ты сдал в общак банды:' + f'\n\n▫️ {bolt["name"]}')    
    #                 updateUser(user)
    #                 antyBoltReport = antyBoltReport + f'{counter}. @{user.getLogin()} {user.getNameAndGerb()} {bolt["name"].split(" ")[0]}\n'
    #     send_message_to_admin(antyBoltReport)

if 1==2: # Изменение уровня обучения навыку
    userupd = {}
    userupd.update({'GonzikBenzyavsky': 90})
    elem = next((x for i, x in enumerate(getSetting(code='ACCESSORY_ALL', id='SKILLS')['value']) if x['id']=='economist'), None) 

    for key in userupd.keys():
        user = getUserByLogin(key)
    
        skill = user.getInventoryThing(elem)
        if skill == None:
            skill = elem
        print(skill)
        elem.update({'storage': userupd[key] })
        user.addInventoryThing(elem, replace=True)
        print(skill)
        updateUser(user)

# x = plan_raids.delete_many({'rade_date':1580162400.0})
# print(x.deleted_count)

# registered_users.update_many( {'band': 'Deus Ex Machina'},
#     { '$set': { 'band': 'Δeus Σx Machina'} }
# )
    
# for x in registered_users.find({'rank': None}):
#     registered_users.update(
#         { 'login': x.get('login')},
#         { '$set': { 'rank': 
#                             {
#                                 'name': '1',
#                                 'value': '🧪Воин из пробирки',
#                                 'bm': 50,
#                                 'update': 'auto'
#                             }
#                     } 
#         }
#     )

# for x in registered_users.find():
#     registered_users.update(
#         { 'login': x.get('login')},
#         { '$unset': { 'loacation': ''} }
#     )

# for x in registered_users.find():
#     registered_users.update(
#         { 'login': x.get('login')},
#         { '$set': { 'location': None} }
#     )


# pip_history     = mydb["pip_history"]
# 
#  mob.remove()

#boss.remove()
# mob_class = ''
# for x in mob.find({'mob_class': mob_class}):
#     print(x)

# mob.delete_many({'mob_class': mob_class})

# for x in mob.find({'mob_class': mob_class}):
#     print(x)
#
# ======================================== #
#          Удаление дубликатов             #
# ======================================== #
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
#             #registered_wariors.delete_many({'_id': m.get('_id')})
#             z = z + 1
#     i = i + 1
# ======================================== #






