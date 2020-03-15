import pymongo
import json
import datetime
import time
import users

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["jugidb"]
registered_users = mydb["users"]
try_counters = mydb["try_counter"]
registered_wariors = mydb["wariors"]
battle = mydb["battle"]
settings = mydb["settings"]
report_raids    = mydb["report_raids"]
plan_raids      = mydb["rades"]
pending_messages = mydb["pending_messages"]
mob             = mydb["mob"]

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

result = settings.find_one({'code': 'ACCESSORY'})
if (not result):
    print('Not Find setting. Insert ACCESSORY')
    settings.insert_one({
        'code': 'ACCESSORY', 
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


print("#==========================#")              
print("#     UPDATE SETTINGS      #")              
print("#==========================#")              

myquery = { "code": 'RANK' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'name': 'MILITARY',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': '🧪Воин из пробирки',
                                    'bm': 50,
                                    'update': 'auto'
                                },
                                {
                                    'name': '2',
                                    'value': '🧫Опытный образец',
                                    'bm': 100,
                                    'update': 'auto'
                                },
                                {
                                    'name': '3',
                                    'value': '🦠Ошибка природы',
                                    'bm': 150,
                                    'update': 'auto'
                                },
                                {
                                    'name': '4',
                                    'value': '🦐Планктон 150-300',
                                    'bm': 300,
                                    'update': 'auto'
                                },
                                {
                                    'name': '5',
                                    'value': '🍤Облучённый планктон',
                                    'bm': 600,
                                    'update': 'auto'
                                },
                                {
                                    'name': '6',
                                    'value': '🐛Совсем зелёный',
                                    'bm': 1000,
                                    'update': 'auto'
                                },
                                {
                                    'name': '7',
                                    'value': '🐣Как у птенчика',
                                    'bm': 1400,
                                    'update': 'auto'
                                },
                                {
                                    'name': '8',
                                    'value': '🍬Барбариска',
                                    'bm': 1800,
                                    'update': 'auto'
                                },
                                {
                                    'name': '9',
                                    'value': '🎩Опытный выживший',
                                    'bm': 2200,
                                    'update': 'auto'
                                },
                                {
                                    'name': '10',
                                    'value': '🤺Воин Пустоши',
                                    'bm': 2600,
                                    'update': 'auto'
                                },
                                {
                                    'name': '11',
                                    'value': '🌪Радиоактивный ураган',
                                    'bm': 3000,
                                    'update': 'auto'
                                },
                                {
                                    'name': '12',
                                    'value': '👨🏿‍🚀«Стармэн»',
                                    'bm': 3400,
                                    'update': 'auto'
                                },
                                {
                                    'name': '13',
                                    'value': '👑Иван-из-Мегатонны',
                                    'bm': 3800,
                                    'update': 'auto'
                                },
                                {
                                    'name': '14',
                                    'value': '🦋Чудотворец',
                                    'bm': 4200,
                                    'update': 'auto'
                                },
                                {
                                    'name': '15',
                                    'value': '🌵Быстрый Гонзалес',
                                    'bm': 4600,
                                    'update': 'auto'
                                },
                                {
                                    'name': '16',
                                    'value': '⭐️Легендарный герой',
                                    'bm': 5000,
                                    'update': 'auto'
                                },
                                {
                                    'name': '17',
                                    'value': '🍅Вождь Помидоров',
                                    'bm': 5400,
                                    'update': 'auto'
                                },
                                {
                                    'name': '18',
                                    'value': '🧨Любитель шахт',
                                    'bm': 5800,
                                    'update': 'auto'
                                },
                                {
                                    'name': '19',
                                    'value': '🌰Крепкий орешек',
                                    'bm': 6200,
                                    'update': 'auto'
                                },
                                {
                                    'name': '20',
                                    'value': 'Тёртый калач',
                                    'bm': 6600,
                                    'update': 'auto'
                                },
                                {
                                    'name': '21',
                                    'value': '🧂Соль земли',
                                    'bm': 7000,
                                    'update': 'auto'
                                },
                                {
                                    'name': '22',
                                    'value': '👽Тварь',
                                    'bm': 7200,
                                    'update': 'auto'
                                },
                                {
                                    'name': '23',
                                    'value': '🧬Высшее существо',
                                    'bm': 8000,
                                    'update': 'auto'
                                }
                            ] 
                        },
                        {
                            'name': 'MEDICS',
                            'value':
                            [
                                
                                {
                                    'id': '1',
                                    'name': '💉 Медсестра',
                                    'cost': 1
                                    
                                },
                                {
                                    'id': '2',
                                    'name': '💉 Медбрат',
                                    'cost': 1
                                },
                                {
                                    'id': '3',
                                    'name': '💊 Главврач',
                                    'cost': 1
                                }
                            ] 
                        },
                        {
                            'name': 'POSITIONS',
                            'value':
                            [
                                {
                                    'id': '1',
                                    'name': '🚵 Директор педального завода',
                                    'cost': 1
                                },
                                {
                                    'id': '2',
                                    'name': '😷 Китаец',
                                    'cost': 1
                                }
                            ] 
                        }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)

# myquery = { "code": 'ACCESSORY' }
# newvalues = { "$set": { "value": 
#                     [
#                         {
#                             'name': 'CLOTHES',
#                             'value':
#                             [                               
#                                 {
#                                     'id': 'scientists_robe',
#                                     'name': '🔬 Халат учёного',
#                                     'cost': 5,
#                                     'type': 'clothes',
#                                     'quantity': 20,
#                                     'weight': 0.3,
#                                     'state': [
#                                                 {'new': 0.8},
#                                                 {'a little broken': 0.6}, 
#                                                 {'broken': 0.4}, 
#                                                 {'tatters': 0.2}
#                                             ],
#                                     'decay': 0.01,
#                                     'position': ['dressed','in inventory', 'in the closet', 'on the ground'],

#                                 },
#                                 {
#                                     'id': 'straw_hat',
#                                     'name': '👒 Соломенная шляпка',
#                                     'cost': 10,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'hunter_panties',
#                                     'name': '🩲 Трусы охотника на Трогов',
#                                     'cost': 10,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'dueling_glove',
#                                     'name': '🧤 Дуэльная перчатка',
#                                     'cost': 15,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'handkerchief',
#                                     'name': '👻 Носовой платок',
#                                     'cost': 6,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'leather_bag',
#                                     'name': '💰 Кожаный мешок',
#                                     'cost': 4,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'medical_mask',
#                                     'name': '😷 Медицинская маска',
#                                     'cost': 8,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'dads_slippers',
#                                     'name': '🥿 Батины тапки',
#                                     'cost': 10,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'latex_mask',
#                                     'name': '👽 Латексная маска',
#                                     'cost': 10,
#                                     'type': 'clothes',
#                                     'quantity': 10
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'RAID_BOLTS',
#                             'value':
#                             [
#                                 {
#                                     'id': 'bolt_1',
#                                     'name': '🔩 Болт М69, возложенный на рейд',
#                                     'cost': 0,
#                                     'type': 'bolt',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'bolt_2',
#                                     'name': '🔩🔩 Болт М228, возложенный на рейд',
#                                     'cost': 0,
#                                     'type': 'bolt',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'bolt_3',
#                                     'name': '🔩🔩🔩 Болт М404, возложенный на рейд',
#                                     'cost': 0,
#                                     'type': 'bolt',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'bolt_4',
#                                     'name': '🔩🔩🔩🔩 Болт М1488, возложенный на рейд',
#                                     'cost': 0,
#                                     'type': 'bolt',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'bolt_5',
#                                     'name': '🎫🍼 Билет на гигантскую бутылку',
#                                     'cost': 0,
#                                     'type': 'bolt',
#                                     'quantity': 1000
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'VIRUSES',
#                             'value':
#                             [
#                                 {
#                                     'id': 'COVID-19',
#                                     'name': '🦇 Коронавирус',
#                                     'cost': 0,
#                                     'type': 'disease',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'mirror_disease',
#                                     'name': '🔬 Зеркальная болезнь',
#                                     'cost': 0,
#                                     'type': 'disease',
#                                     'quantity': 1000
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'TATU',
#                             'value':
#                             [
#                                 {
#                                     'id': 'tatu_arthouse_1',
#                                     'name': '♀️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
#                                     'cost': 100,
#                                     'type': 'tatu',
#                                     'quantity': 15
#                                 },
#                                 {
#                                     'id': 'tatu_arthouse_2',
#                                     'name': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
#                                     'cost': 100,
#                                     'type': 'tatu',
#                                     'quantity': 15
#                                 },
#                                 {
#                                     'id': 'tatu_arthouse_3',
#                                     'name': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
#                                     'cost': 100,
#                                     'type': 'tatu',
#                                     'quantity': 15
#                                 },
#                                 {
#                                     'id': 'tatu_arthouse_4',
#                                     'name': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!", с подписью Кеши.',
#                                     'cost': 100,
#                                     'type': 'tatu',
#                                     'quantity': 15
#                                 },
#                                 {
#                                     'id': 'tatu_ledonna_1',
#                                     'name': '🤍 тату "ЛеДонна"',
#                                     'cost': 200,
#                                     'type': 'tatu',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'tatu_kirill_1',
#                                     'name': '🤍 Сердце Кирилла навсегда',
#                                     'cost': 200,
#                                     'type': 'tatu',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'tatu_arthouse_5',
#                                     'name': '♂️ Тату "АртхǁȺǁус тебя любит!", с подписью - мы все!',
#                                     'cost': 120,
#                                     'type': 'tatu',
#                                     'quantity': 15
#                                 },
#                                 {
#                                     'id': 'tatu_runing_man_1',
#                                     'name': '🤺 Бегущий по лезвию',
#                                     'cost': 100,
#                                     'type': 'tatu',
#                                     'quantity': 1000
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'SKILLS',
#                             'value':
#                             [
#                                 {
#                                     'id': 'barman',
#                                     'name': '🍾 Бармен',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'moonshiner',
#                                     'name': '📖 «Как перегонять спирт»',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'fighter',
#                                     'name': '🥋 Чёрный пояс по PvP',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'boss',
#                                     'name': '📿 Чётки босса банды',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'programmer',
#                                     'name': '🉐💮 Язык программирования',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'perfectionist',
#                                     'name': '🛑 Круг перфекциониста',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'seducer',
#                                     'name': '🗣 Соблазнитель ванаМинго',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'the_running_man',
#                                     'name': '🏃 Бегущий человек',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'alien',
#                                     'name': '🚼 Чужой',
#                                     'cost': 0,
#                                     'type': 'skill',
#                                     'quantity': 1000
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'EDIBLE',
#                             'value':
#                             [
#                                 {
#                                     'id': 'salt',
#                                     'name': '🧂 Соль на рану',
#                                     'cost': 1,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'cookies',
#                                     'name': '🍪 Довоенное печенье',
#                                     'cost': 3,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'head_crombopulus',
#                                     'name': '👽 Голова кромбопулуса',
#                                     'cost': 7,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'tomato_juice',
#                                     'name': '🌡 Томатный сок',
#                                     'cost': 2,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'soup_set',
#                                     'name': '☠️ Суповой комплект',
#                                     'cost': 4,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'truffle',
#                                     'name': '💩 Трюфель',
#                                     'cost': 10,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'ears',
#                                     'name': '👂 Уши из Rivet City',
#                                     'cost': 5,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'chocolate_and_whiskey',
#                                     'name': '🍫 и 🥃',
#                                     'cost': 12,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'banana',
#                                     'name': '🍌 Банан преданности',
#                                     'cost': 6,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'peach',
#                                     'name': '🍑 Персик преданности',
#                                     'cost': 5,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'ascorbin',
#                                     'name': '🤍 Аскорбинка',
#                                     'cost': 8,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 },
#                                 {
#                                     'id': 'snail',
#                                     'name': '🐚 Труп улитки',
#                                     'cost': 1,
#                                     'type': 'food',
#                                     'quantity': 1000
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'MARKS_OF_EXCELLENCE',
#                             'value':
#                             [
#                                 {
#                                     'id': 'fucking_i',
#                                     'name': '🖕 Нихуя І степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'fucking_ii',
#                                     'name': '🖕🖕 Нихуя ІІ степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'fucking_iii',
#                                     'name': '🖕🖕🖕 Нихуя ІІІ степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'fucking_iv',
#                                     'name': '🖕🖕🖕🖕 Нихуя IV степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'fucking_v',
#                                     'name': '🖕🖕🖕🖕🖕 Нихуя V степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'fucking_full',
#                                     'name': '🎖️ Полный кавалер ордена "Нихуя"',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'diploma_1',
#                                     'name': '📄 Грамота за правильный вопрос!',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'diploma_2',
#                                     'name': '📜 Грамота от вМ за групповой захват Научного комплекса',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'diploma_3',
#                                     'name': '💪 За храбрость и мужество',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'certificate_gv',
#                                     'name': '💉 Удостоверение "Главврач"',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
                                    
#                                 },
#                                 {
#                                     'id': 'certificate_mb',
#                                     'name': '💉 Удостоверение "Медбрат"',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'certificate_mm',
#                                     'name': '💉 Удостоверение "Медсестричка"',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'certificate_honorary_donor',
#                                     'name': '🩸 Почётный донор',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'certificate_honorary_donor_i',
#                                     'name': '🩸 Значёк "Почетный донор" I-степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'certificate_honorary_donor_ii',
#                                     'name': '🩸 Значёк "Почетный донор" II-степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'certificate_honorary_donor_iii',
#                                     'name': '🩸 Значёк "Почетный донор" III-степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'photo_8_bandits_in_scientific_complex',
#                                     'name': '🎞️Фото 8-ми бандитов на фоне Научного комплекса',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'sign_from_the_door_of_the_scientific_complex',
#                                     'name': '☢️Табличка с двери Научного комплекса с 8-ю подписями бойцов АртхǁȺǁус',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'test_tube_from_the_scientific_complex',
#                                     'name': '🍼 Пробирка из Научного комплекса с надписью - здэс был Артоха̶уз',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'trolley_bus_ticket_scientific_complex',
#                                     'name': '🎫 Билет на троллебус на групповую поездку до Научного комплекса',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'capture_medal_scientific_complex',
#                                     'name': '🎖️ Медаль за захват 7-ми данже подряд 1-ой степени',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'newspaper_article_scientific_complex',
#                                     'name': '📰 Статья в газете о легендарном походе за семью данжами',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'vacation_to_sanatorium',
#                                     'name': '📃 Путёвка в санаторий "SPA Пустошь" за захват 7-ми данжей',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'burning_fart',
#                                     'name': '🔥 Горящий пердак',
#                                     'cost': 1,
#                                     'type': 'marks_of_excellence',
#                                     'quantity': 30
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'REWARDS',
#                             'value':
#                             [
#                                 {
#                                     'id': 'statuette_shark',
#                                     'name': '🦈 Статуэтка "Акула"',
#                                     'cost': 5,
#                                     'type': 'decoration',
#                                     'quantity': 5

#                                 },
#                                 {
#                                     'id': 'statuette_complex',
#                                     'name': '🤼 Статуэтка из говна и палок - "Групповой захват Научного комплекса"',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'statuette_smart_girl',
#                                     'name': '💃 Статуэтка "Умница"',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'statuette_smart_boy',
#                                     'name': '🕺 Статуэтка "Умник, бля"',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'statuette_barman_2019',
#                                     'name': '🍾 Бармен 2019 года',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'statuette_the_eiffel_tower',
#                                     'name': '♟ Эйфелева Башня',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'sticker_pack',
#                                     'name': '🎭 Набор стикеров Fallout 2',
#                                     'cost': 30,
#                                     'type': 'decoration',
#                                     'quantity': 3
#                                 },
#                                 {
#                                     'id': 'rebus_cube',
#                                     'name': '🎲 Кубик ребусоведа',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 2
#                                 },
#                                 {
#                                     'id': 'trident',
#                                     'name': '🔱 Трезубец повелителя Пустоши',
#                                     'cost': 30,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'dust_from_woolen',
#                                     'name': '🌪 Пыль с Шерстяного',
#                                     'cost': 50,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'saurons_point',
#                                     'name': '🏵 Очко Саурона',
#                                     'cost': 1,
#                                     'type': 'decoration',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'urn_baphomet',
#                                     'name': '⚱️Бафомет',
#                                     'cost': 20,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'urn_faggoat',
#                                     'name': '🎷Фаггот',
#                                     'cost': 20,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'urn_anime',
#                                     'name': '🏺 Анимэ',
#                                     'cost': 20,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'two_girls_one_cup',
#                                     'name': '🧁 Two girls, one cup',
#                                     'cost': 120,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'mythical_friendship',
#                                     'name': '✂️ Мифическая дружба',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'id': 'deanon',
#                                     'name': '🆔 Деанон',
#                                     'cost': 5,
#                                     'type': 'decoration',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'paul',
#                                     'name': '🌀 Пауль',
#                                     'cost': 100,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'hamlet',
#                                     'name': '💀 Гамлет',
#                                     'cost': 50,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'yorick',
#                                     'name': '💀 Йорик',
#                                     'cost': 75,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'statuette_alien_1',
#                                     'name': '👾 Ъуъеъкхх',
#                                     'cost': 60,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'statuette_alien_2',
#                                     'name': '👾 тпфптлтвфт ъуъ сука',
#                                     'cost': 60,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'multipass_arthouse',
#                                     'name': '💳 Мультипас бандита АртхǁȺǁус',
#                                     'cost': 15,
#                                     'type': 'decoration',
#                                     'quantity': 15
#                                 },
#                                 {
#                                     'id': '100_bucks',
#                                     'name': '💵 Кровавые 100 баксов',
#                                     'cost': 100,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': '200_bucks',
#                                     'name': '💵 Кровные 200 баксов',
#                                     'cost': 200,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'name_ring',
#                                     'name': '🔅 Именной перстень "5-ый сезон"',
#                                     'cost': 0,
#                                     'type': 'decoration',
#                                     'quantity': 75
#                                 },
#                                 {
#                                     'id': 'something',
#                                     'name': '🧫 Нечто',
#                                     'cost': 50,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'pickman_painting',
#                                     'name': '🎨 Картина Пикмана "F-395"',
#                                     'cost': 100,
#                                     'type': 'decoration',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'death_flag',
#                                     'name': '🏴 Флаг смерти',
#                                     'cost': 7,
#                                     'type': 'decoration',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'armenian_rosary',
#                                     'name': '📿 Армяне на стиле',
#                                     'cost': 1,
#                                     'type': 'decoration',
#                                     'quantity': 4
#                                 },
#                                 {
#                                     'id': 'sasai_kudasai',
#                                     'name': '🔪 Сасайкудасай',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'name': '4',
#                                     'value': '📟 игрушечный Пип-бой',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'name': '7',
#                                     'value': '📟 моделька Пип-боя',
#                                     'cost': 10,
#                                     'type': 'decoration',
#                                     'quantity': 5
#                                 }                                
#                             ] 
#                         },
#                         {
#                             'name': 'THINGS',
#                             'value':
#                             [
#                                 {
#                                     'id': 'sticks',
#                                     'name': '🥢 Близкая дружба',
#                                     'cost': 1,
#                                     'type': 'things',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'nipple_clamp',
#                                     'name': '🗜 Зажим на соски',
#                                     'cost': 10,
#                                     'type': 'things',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'butt_plug',
#                                     'name': '🕹️ Анальная пробка',
#                                     'cost': 10,
#                                     'type': 'things',
#                                     'quantity': 10
#                                 },
#                                 {
#                                     'id': 'magnifier',
#                                     'name': '🔍 Лупа',
#                                     'cost': 15,
#                                     'type': 'things',
#                                     'quantity': 2
#                                 },
#                                 {
#                                     'id': 'disabled_carriage',
#                                     'name': '♿️ Зато не пешком',
#                                     'cost': 60,
#                                     'type': 'things',
#                                     'quantity': 2
#                                 },
#                                 {
#                                     'id': 'speakers',
#                                     'name': '🎶 Долбит нормально',
#                                     'cost': 20,
#                                     'type': 'things',
#                                     'quantity': 30
#                                 },
#                                 {
#                                     'id': 'flower_pervonach',
#                                     'name': '🌷 Цветок "Первонах"',
#                                     'cost': 3,
#                                     'type': 'things',
#                                     'quantity': 50
#                                 },
#                                 {
#                                     'id': 'teddy_bear',
#                                     'name': '🧸 Мишка-обнимашка',
#                                     'cost': 10,
#                                     'type': 'things',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'baby_tooth',
#                                     'name': '🦷 Молочный зуб Рашки',
#                                     'cost': 99,
#                                     'type': 'things',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'key_to_the_apartment_in_halo',
#                                     'name': '🔑 От квартиры в Ореоле',
#                                     'cost': 1,
#                                     'type': 'things',
#                                     'quantity': 75
#                                 },
#                                 {
#                                     'id': 'brick',
#                                     'name': '🧱 Кирпич на голову',
#                                     'cost': 1,
#                                     'type': 'things',
#                                     'quantity': 75
#                                 },
#                                 {
#                                     'id': 'fork',
#                                     'name': '🍴 Вилка в глаз',
#                                     'cost': 2,
#                                     'type': 'things',
#                                     'quantity': 75
#                                 },
#                                 {
#                                     'id': 'iron',
#                                     'name': '🥌 Утюг',
#                                     'cost': 7,
#                                     'type': 'things',
#                                     'quantity': 7
#                                 },
#                                 {
#                                     'id': 'radar_detector',
#                                     'name': '💿 Козырёк в авто',
#                                     'cost': 15,
#                                     'type': 'things',
#                                     'quantity': 7
#                                 },
#                                 {
#                                     'id': 'radar_detector_ii',
#                                     'name': '📀 Блатной козырёк в авто',
#                                     'cost': 20,
#                                     'type': 'things',
#                                     'quantity': 7
#                                 },
#                                 {
#                                     'id': 'gps',
#                                     'name': '🔊 GPS',
#                                     'cost': 70,
#                                     'type': 'things',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'id': 'horseshoe',
#                                     'name': '🧲 Подкова',
#                                     'cost': 25,
#                                     'type': 'things',
#                                     'quantity': 4
#                                 },
#                                 {
#                                     'id': 'raid_plan',
#                                     'name': '🧻 План рейда',
#                                     'cost': 0,
#                                     'type': 'things',
#                                     'quantity': 1
#                                 },
#                                 {
#                                     'id': 'comb',
#                                     'name': '🚿 Расчёска от лох',
#                                     'cost': 2,
#                                     'type': 'things',
#                                     'quantity': 15
#                                 },
#                                 {
#                                     'id': 'pot',
#                                     'name': '🏆 Горшок',
#                                     'cost': 2,
#                                     'type': 'things',
#                                     'quantity': 20
#                                 },
#                                 {
#                                     'id': '85',
#                                     'name': '🚬 Арома стик',
#                                     'cost': 3,
#                                     'type': 'things',
#                                     'quantity': 20
#                                 },
#                                 {
#                                     'id': 'sword_of_the_jedi',
#                                     'name': '🗡️ Меч джедая',
#                                     'cost': 130,
#                                     'type': 'things',
#                                     'quantity': 20
#                                 },
#                                 {
#                                     'id': 'metal_detector',
#                                     'name': '🧑‍🦯 Металлоискатель',
#                                     'cost': 100,
#                                     'type': 'things',
#                                     'quantity': 20
#                                 },
#                                 {
#                                     'name': 'pip_boy_2000',
#                                     'value': '📟 Пип-бой 2000',
#                                     'cost': 1000,
#                                     'type': 'things',
#                                     'quantity': 1000,
#                                     'composition':
#                                     {
#                                         [
#                                             {
#                                                 'id': 'pip_broken_part',
#                                                 'count': 1
#                                             },
#                                             {
#                                                 'id': 'pip_antenna',
#                                                 'count': 1
#                                             },
#                                             {
#                                                 'id': 'pip_battery',
#                                                 'count': 1
#                                             },
#                                             {
#                                                 'id': 'pip_spare_part',
#                                                 'count': 2
#                                             },
#                                             {
#                                                 'id': 'pip_bolt',
#                                                 'count': 3
#                                             },
#                                             {
#                                                 'id': 'pip_repair_kit',
#                                                 'count': 1
#                                             }
#                                         ]
#                                     }
#                                 },
#                                 {
#                                     'id': 'pip_repair_kit',
#                                     'name': '🛠️ Ремкомплект для Пип-боя',
#                                     'cost': 100,
#                                     'type': 'things',
#                                     'quantity': 2,
#                                 }
#                             ]
#                         },
#                         {
#                             'name': 'PIP_BOY',
#                             'value':
#                             [
#                                 {
#                                     'id': 'pip_antenna',
#                                     'name': '📟 антена от Пип-боя',
#                                     'cost': 20,
#                                     'type': 'things',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'id': 'pip_battery',
#                                     'name': '📟 аккумулятор от Пип-боя',
#                                     'cost': 20,
#                                     'type': 'things',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'id': 'pip_packaging',
#                                     'name': '📟 упаковка от Пип-боя',
#                                     'cost': 1,
#                                     'type': 'things',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'id': 'pip_spare_part',
#                                     'name': '📟 запчасть от Пип-боя',
#                                     'cost': 25,
#                                     'type': 'things',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'id': 'pip_broken_part',
#                                     'name': '📟 сломанный Пип-бой',
#                                     'cost': 50,
#                                     'type': 'things',
#                                     'quantity': 5
#                                 },
#                                 {
#                                     'id': 'pip_bolt',
#                                     'name': '📟 болт от Пип-боя',
#                                     'cost': 20,
#                                     'type': 'things',
#                                     'quantity': 30
#                                 }
#                             ] 
#                         }
#                     ]
#                 } 
#             } 
# u = settings.update_one(myquery, newvalues)

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
                            'value': '55'
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
                            # Вероятность
                            'name': 'I_DONT_KNOW_YOU',
                            'value': 0.5
                        },
                        {
                            # Вероятность
                            'name': 'TO_BE_OR_NOT',
                            'value': 0.5
                        },
                        {
                            # Range
                            'name': 'FUNY_BAN',
                            'value': 600
                        },
                        {
                            # Вероятность
                            'name': 'EMOTIONS',
                            'value': 0.10
                        },
                        {
                            # Вероятность
                            'name': 'YES_STICKER',
                            'value': 0.00
                        },
                        {
                            # Вероятность
                            'name': 'NO_STICKER',
                            'value': 0.00
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
                            'value': 5
                        },
                        {
                            # Range
                            'name': 'PANDING_WAIT_END_2',
                            'value': 10
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
                            'chat' : 0
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
                {'band': 'ЩекØтилы БанȺнов'}
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
                            'boss': [
                                        'WestMoscow',
                                        'Innok27',
                                        'Viktoriya_Sizko',
                                        'EastMinsk',
                                        'nik_stopka',
                                        'GonzikBenzyavsky'
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
                                            'name': 'ЩекØтилы БанȺнов',
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
                                        'info' : -1001377870371
                                    }

                        }
                    ]   
                } 
            } 
u = settings.update_one(myquery, newvalues)

for x in settings.find():
    print(x)

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

updateUser(None)
for user in USERS_ARR:
    pass



# x = plan_raids.delete_many({'rade_date':1580162400.0})
# print(x.deleted_count)

# mob.update_many(
#     { '$set': { 'dark_zone': False} }
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
#             registered_wariors.delete_many({'_id': m.get('_id')})
#             z = z + 1
#     i = i + 1
# ======================================== #






