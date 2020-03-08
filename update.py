import pymongo
import json
import datetime
import time

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

def getSetting(code: str):
    """ Получение настройки """
    result = settings.find_one({'code': code})
    if (result):
        return result.get('value') 

def setSetting(login: str, code: str, value: str):
    """ Сохранение настройки """
    myquery = { "code": code }
    newvalues = { "$set": { "value": value } }
    u = settings.update_one(myquery, newvalues)

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
                                    'value': '🧪Воин из пбробирки',
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
                                    'bm': 1000000,
                                    'update': 'auto'
                                }
                            ] 
                        },
                        {
                            'name': 'MEDICS',
                            'value':
                            [
                                
                                {
                                    'name': '1',
                                    'value': '💉 Медсестра',
                                    'cost': 1
                                    
                                },
                                {
                                    'name': '2',
                                    'value': '💉 Медбрат',
                                    'cost': 1
                                },
                                {
                                    'name': '3',
                                    'value': '💊 Главврач',
                                    'cost': 1
                                }
                            ] 
                        }
                    ]
                } 
            } 
u = settings.update_one(myquery, newvalues)


myquery = { "code": 'ACCESSORY' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'name': 'PIP_BOY',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': '📟 Пип-бой 2000',
                                    'cost': 1
                                },
                                {
                                    'name': '2',
                                    'value': '📟 антена от Пип-боя',
                                    'cost': 1
                                },
                                {
                                    'name': '3',
                                    'value': '📟 аккумулятор от Пип-боя',
                                    'cost': 1
                                },
                                {
                                    'name': '4',
                                    'value': '📟 игрушечный Пип-бой',
                                    'cost': 1
                                },
                                {
                                    'name': '5',
                                    'value': '📟 упаковка от Пип-боя',
                                    'cost': 1
                                },
                                {
                                    'name': '6',
                                    'value': '📟 запчасть от Пип-боя',
                                    'cost': 1
                                },
                                {
                                    'name': '7',
                                    'value': '📟 моделька Пип-боя',
                                    'cost': 1
                                },
                                {
                                    'name': '8',
                                    'value': '📟 сломанный Пип-бой',
                                    'cost': 1
                                },
                                {
                                    'name': '9',
                                    'value': '📟 болт от Пип-боя',
                                    'cost': 1
                                }
                            ] 
                        },
                        {
                            'name': 'REWARDS',
                            'value':
                            [
                                
                                {
                                    'name': '1',
                                    'value': '🔬 Халат учёного',
                                    'cost': 1
                                    
                                },
                                {
                                    'name': '2',
                                    'value': '🎩 Шляпа Линкольна',
                                    'cost': 1
                                },
                                {
                                    'name': '3',
                                    'value': '👒 Соломенная шляпка',
                                    'cost': 1
                                },
                                {
                                    'name': '4',
                                    'value': '🩲 Трусы охотника на Трогов',
                                    'cost': 1
                                },
                                {
                                    'name': '5',
                                    'value': '🐚 Труп улитки',
                                    'cost': 1
                                },
                                {
                                    'name': '6',
                                    'value': '🦈 Статуэтка "Акула"',
                                    'cost': 1
                                },
                                {
                                    'name': '7',
                                    'value': '🦇 Коронавирус',
                                    'cost': 1
                                },
                                {
                                    'name': '8',
                                    'value': '🍾 Бармен 2019 года',
                                    'cost': 1
                                },
                                {
                                    'name': '9',
                                    'value': '🎭 Набор стикеров Fallout 2',
                                    'cost': 1
                                },
                                {
                                    'name': '10',
                                    'value': '🔪 Сасайкудасай',
                                    'cost': 1
                                },
                                {
                                    'name': '11',
                                    'value': '🧂 Соль на рану',
                                    'cost': 1
                                },
                                {
                                    'name': '12',
                                    'value': '🥋 Чёрный пояс по PvP',
                                    'cost': 1
                                },
                                {
                                    'name': '13',
                                    'value': '🍴 Вилка в глаз',
                                    'cost': 1
                                },
                                {
                                    'name': '14',
                                    'value': '🎲 Кубик ребусоведа',
                                    'cost': 1
                                },
                                {
                                    'name': '15',
                                    'value': '🍪 Довоенное печенье',
                                    'cost': 1
                                },
                                {
                                    'name': '16',
                                    'value': '🏴 Флаг смерти',
                                    'cost': 1
                                },
                                {
                                    'name': '17',
                                    'value': '👽 Голова кромбопулуса',
                                    'cost': 1
                                },
                                {
                                    'name': '18',
                                    'value': '📖 «Как перегонять спирт»',
                                    'cost': 1
                                },
                                {
                                    'name': '19',
                                    'value': '🗡️ Меч джедая',
                                    'cost': 1
                                },
                                {
                                    'name': '20',
                                    'value': '🦷 Молочный зуб Рашки',
                                    'cost': 1
                                },
                                {
                                    'name': '21',
                                    'value': '📿 Чётки босса банды',
                                    'cost': 1
                                },
                                {
                                    'name': '22',
                                    'value': '🔑 От квартиры в Ореоле',
                                    'cost': 1
                                },
                                {
                                    'name': '23',
                                    'value': '🏵️ Грамота за 1-й Дзен',
                                    'cost': 1
                                },
                                {
                                    'name': '24',
                                    'value': '🏵️ Грамота за 2-й Дзен',
                                    'cost': 1
                                },
                                {
                                    'name': '25',
                                    'value': '🏵️ Грамота за 3-й Дзен',
                                    'cost': 1
                                },
                                {
                                    'name': '26',
                                    'value': '🏵️ Грамота за 4-й Дзен',
                                    'cost': 1
                                },
                                {
                                    'name': '27',
                                    'value': '🏵️ Грамота за 5-й Дзен',
                                    'cost': 1
                                },
                                {
                                    'name': '28',
                                    'value': '🧤 Дуэльная перчатка',
                                    'cost': 1
                                },
                                {
                                    'name': '29',
                                    'value': '🔩 Болт М69, возложенный на рейд',
                                    'cost': 1
                                },
                                {
                                    'name': '30',
                                    'value': '🔩🔩 Болт М228, возложенный на рейд',
                                    'cost': 1
                                },
                                {
                                    'name': '31',
                                    'value': '🔩🔩🔩 Болт М404, возложенный на рейд',
                                    'cost': 1
                                },
                                {
                                    'name': '32',
                                    'value': '🔩🔩🔩🔩 Болт М1488, возложенный на рейд',
                                    'cost': 1
                                },
                                {
                                    'name': '33',
                                    'value': '🎫🍼 Билет на гигантскую бутылку',
                                    'cost': 1
                                },
                                {
                                    'name': '34',
                                    'value': '🧱 Кирпич на голову',
                                    'cost': 1
                                },
                                {
                                    'name': '35',
                                    'value': '🎞️Фото 8-ми бандитов на фоне Научного комплекса',
                                    'cost': 1
                                },
                                {
                                    'name': '36',
                                    'value': '☢️Табличка с двери Научного комплекса с 8-ю подписями бойцов АртхǁȺǁус',
                                    'cost': 1
                                },
                                {
                                    'name': '37',
                                    'value': '📜 Грамота от вМ за групповой захват Научного комплекса',
                                    'cost': 1
                                },
                                {
                                    'name': '38',
                                    'value': '🍼 Пробирка из Научного комплекса с надписью - здэс был Артоха̶уз',
                                    'cost': 1
                                },
                                {
                                    'name': '39',
                                    'value': '🤼 Статуэтка из говна и палок - "Групповой захват Научного комплекса"',
                                    'cost': 1
                                },
                                {
                                    'name': '40',
                                    'value': '🎫 Билет на троллебус на групповую поездку до Научного комплекса',
                                    'cost': 1
                                },
                                {
                                    'name': '41',
                                    'value': '🎖️ Медаль за захват 7-ми данже подряд 1-ой степени',
                                    'cost': 1
                                },
                                {
                                    'name': '42',
                                    'value': '📰 Статья в газете о легендарном походе за семью данжами',
                                    'cost': 1
                                },
                                {
                                    'name': '43',
                                    'value': '📃 Путёвка в санаторий "SPA Пустошь" за захват 7-ми данжей',
                                    'cost': 1
                                },
                                {
                                    'name': '44',
                                    'value': '🔱 Трезубец повелителя Пустоши',
                                    'cost': 1
                                },
                                {
                                    'name': '45',
                                    'value': '🛠️ Ремкомплект для Пип-боя',
                                    'cost': 1
                                },
                                {
                                    'name': '46',
                                    'value': '🥢 Близкая дружба',
                                    'cost': 1
                                },
                                {
                                    'name': '47',
                                    'value': '🌪 Пыль с Шерстяного',
                                    'cost': 1
                                },
                                {
                                    'name': '48',
                                    'value': '🗜 Зажим на соски',
                                    'cost': 1
                                },
                                {
                                    'name': '49',
                                    'value': '💿 Козырёк в авто',
                                    'cost': 1
                                },
                                {
                                    'name': '50',
                                    'value': '📀 Блатной козырёк в авто',
                                    'cost': 1
                                },
                                {
                                    'name': '51',
                                    'value': '🕹️ Анальная пробка',
                                    'cost': 1
                                },
                                {
                                    'name': '52',
                                    'value': '🥌 Утюг',
                                    'cost': 1
                                },
                                {
                                    'name': '53',
                                    'value': '🏵 Очко Саурона',
                                    'cost': 1
                                },
                                {
                                    'name': '54',
                                    'value': '🎷Фаггот',
                                    'cost': 1
                                },

                                {
                                    'name': '55',
                                    'value': '💸 Лёгкие на подъём',
                                    'cost': 1
                                },
                                {
                                    'name': '56',
                                    'value': '⚱️Бафомет',
                                    'cost': 1
                                },
                                {
                                    'name': '57',
                                    'value': '🏺 Анимэ',
                                    'cost': 1
                                },
                                {
                                    'name': '58',
                                    'value': '🧁 Two girls, one cup',
                                    'cost': 1
                                },
                                {
                                    'name': '59',
                                    'value': '🔍 Лупа',
                                    'cost': 1
                                },
                                {
                                    'name': '60',
                                    'value': '🔎 Щёка',
                                    'cost': 1
                                },
                                {
                                    'name': '61',
                                    'value': '✂️ Мифическая дружба',
                                    'cost': 1
                                },
                                {
                                    'name': '62',
                                    'value': '🆔 Деанон',
                                    'cost': 1
                                },
                                {
                                    'name': '63',
                                    'value': '🉐💮 Язык программирования',
                                    'cost': 1
                                },
                                {
                                    'name': '64',
                                    'value': '🛑 Круг перфекциониста',
                                    'cost': 1
                                },
                                {
                                    'name': '65',
                                    'value': '🌀 Пауль',
                                    'cost': 1
                                },
                                {
                                    'name': '66',
                                    'value': '♿️ Зато не пешком',
                                    'cost': 1
                                },
                                {
                                    'name': '67',
                                    'value': '🚼 Чужой',
                                    'cost': 1
                                },
                                {
                                    'name': '68',
                                    'value': '🎶 Долбит нормально',
                                    'cost': 1
                                },
                                {
                                    'name': '69',
                                    'value': '🔊 GPS',
                                    'cost': 1
                                },
                                {
                                    'name': '70',
                                    'value': '🧲 Подкова',
                                    'cost': 1
                                },
                                {
                                    'name': '71',
                                    'value': '📿 Армяне на стиле',
                                    'cost': 1
                                },
                                {
                                    'name': '72',
                                    'value': '⚗️ На 95% безопаснее',
                                    'cost': 1
                                },
                                {
                                    'name': '73',
                                    'value': '🔬 Зеркальная болезнь',
                                    'cost': 1
                                },
                                {
                                    'name': '74',
                                    'value': '🕳 Бывшая',
                                    'cost': 1
                                },
                                {
                                    'name': '75',
                                    'value': '🍯 Бывшая [2]',
                                    'cost': 1
                                },
                                {
                                    'name': '76',
                                    'value': '🧻 План рейда',
                                    'cost': 1
                                },
                                {
                                    'name': '77',
                                    'value': '🚿 Расчёска от лох',
                                    'cost': 1
                                },
                                {
                                    'name': '78',
                                    'value': '🌡 Томатный сок',
                                    'cost': 1
                                },
                                {
                                    'name': '79',
                                    'value': '♟ Эйфелева Башня',
                                    'cost': 1
                                },
                                {
                                    'name': '80',
                                    'value': '🚵 Директор педального завода',
                                    'cost': 1
                                },
                                {
                                    'name': '81',
                                    'value': '🏆 Горшок',
                                    'cost': 1
                                },
                                {
                                    'name': '82',
                                    'value': '🤯 Расчёт РМ',
                                    'cost': 1
                                },
                                {
                                    'name': '83',
                                    'value': '😷 Китаец',
                                    'cost': 1
                                },
                                {
                                    'name': '84',
                                    'value': '👻 Носовой платок',
                                    'cost': 1
                                },
                                {
                                    'name': '85',
                                    'value': '🚬 Арома стик',
                                    'cost': 1
                                },
                                {
                                    'name': '86',
                                    'value': '🧑‍🦽 Цены на бензин',
                                    'cost': 1
                                },
                                {
                                    'name': '87',
                                    'value': '🧑‍🦯 Металлоискатель',
                                    'cost': 1
                                },
                                {
                                    'name': '88',
                                    'value': '🥱 Ем руку',
                                    'cost': 1
                                },
                                {
                                    'name': '89',
                                    'value': '🤮 Полёт на Марс',
                                    'cost': 1
                                },
                                {
                                    'name': '90',
                                    'value': '🤒 Пью томатный сок',
                                    'cost': 1
                                },
                                {
                                    'name': '91',
                                    'value': '💀 Гамлет',
                                    'cost': 1
                                },
                                {
                                    'name': '92',
                                    'value': '💀 Йорик',
                                    'cost': 1
                                },
                                {
                                    'name': '93',
                                    'value': '☠️ Суповой комплект',
                                    'cost': 1
                                },
                                {
                                    'name': '94',
                                    'value': '👽 Латексная маска',
                                    'cost': 1
                                },
                                {
                                    'name': '95',
                                    'value': '👾 Ъуъеъкхх',
                                    'cost': 1
                                },
                                {
                                    'name': '96',
                                    'value': '👾 тпфптлтвфт ъуъ сука',
                                    'cost': 1
                                },
                                {
                                    'name': '97',
                                    'value': '💩 Трюфель',
                                    'cost': 1
                                },
                                {
                                    'name': '98',
                                    'value': '🥿 Батины тапки',
                                    'cost': 1
                                },
                                {
                                    'name': '99',
                                    'value': '🖕 Нихуя І степени',
                                    'cost': 1
                                },
                                {
                                    'name': '100',
                                    'value': '🖕🖕 Нихуя ІІ степени',
                                    'cost': 1
                                },
                                {
                                    'name': '101',
                                    'value': '🖕🖕🖕 Нихуя ІІІ степени',
                                    'cost': 1
                                },
                                {
                                    'name': '102',
                                    'value': '🖕🖕🖕🖕 Нихуя IV степени',
                                    'cost': 1
                                },
                                {
                                    'name': '103',
                                    'value': '🖕🖕🖕🖕🖕 Нихуя V степени',
                                    'cost': 1
                                },
                                {
                                    'name': '104',
                                    'value': '🎖️ Полный кавалер ордена "Нихуя"',
                                    'cost': 1
                                },
                                {
                                    'name': '105',
                                    'value': '🎨 Картина Пикмана "F-395"',
                                    'cost': 1
                                },
                                {
                                    'name': '106',
                                    'value': '👂 Уши из Rivet City',
                                    'cost': 1
                                },
                                {
                                    'name': '107',
                                    'value': '💵 Кровавые 100 баксов',
                                    'cost': 1
                                },
                                {
                                    'name': '108',
                                    'value': '💵 Кровные 200 баксов',
                                    'cost': 1
                                },
                                {
                                    'name': '109',
                                    'value': '💰 Сколько смог унести',
                                    'cost': 1
                                },
                                {
                                    'name': '110',
                                    'value': '🩸 Почётный донор',
                                    'cost': 1
                                },
                                {
                                    'name': '111',
                                    'value': '💰 Кожаный мешок',
                                    'cost': 1
                                },
                                {
                                    'name': '112',
                                    'value': '♀️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
                                    'cost': 1
                                },
                                {
                                    'name': '113',
                                    'value': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
                                    'cost': 1
                                },
                                {
                                    'name': '114',
                                    'value': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!"',
                                    'cost': 1
                                },
                                {
                                    'name': '115',
                                    'value': '♂️ Тату "Не забуду Кешу и АртхǁȺǁус!", с подписью Кеши.',
                                    'cost': 1
                                },
                                {
                                    'name': '116',
                                    'value': '💳 Мультипас бандита АртхǁȺǁус',
                                    'cost': 1
                                },
                                {
                                    'name': '117',
                                    'value': '♂️ Тату "АртхǁȺǁус тебя любит!", с подписью - мы все!',
                                    'cost': 1
                                },
                                {
                                    'name': '118',
                                    'value': '🍫 и 🥃',
                                    'cost': 1
                                },
                                {
                                    'name': '119',
                                    'value': '📄 Грамота за правильный вопрос!',
                                    'cost': 1
                                },
                                {
                                    'name': '120',
                                    'value': '🧸 Мишка-обнимашка',
                                    'cost': 1
                                },
                                {
                                    'name': '121',
                                    'value': '💪 За храбрость и мужество',
                                    'cost': 1
                                },
                                {
                                    'name': '122',
                                    'value': '🍌 Банан преданности',
                                    'cost': 1
                                },
                                {
                                    'name': '123',
                                    'value': '🍑 Персик преданности',
                                    'cost': 1
                                },
                                {
                                    'name': '124',
                                    'value': '🔅 Именной перстень "5-ый сезон"',
                                    'cost': 1
                                },
                                {
                                    'name': '125',
                                    'value': '💉 Удостоверение "Медбрат"',
                                    'cost': 1
                                },
                                {
                                    'name': '126',
                                    'value': '💉 Удостоверение "Медсестричка"',
                                    'cost': 1
                                },
                                {
                                    'name': '127',
                                    'value': '🩸 Значёк "Почетный донор" I-степени',
                                    'cost': 1
                                },
                                {
                                    'name': '128',
                                    'value': '🩸 Значёк "Почетный донор" II-степени',
                                    'cost': 1
                                },
                                {
                                    'name': '129',
                                    'value': '🩸 Значёк "Почетный донор" III-степени',
                                    'cost': 1
                                },
                                {
                                    'name': '130',
                                    'value': '🔥 Горящий пердак',
                                    'cost': 1
                                },
                                {
                                    'name': '131',
                                    'value': '🏃 Бегущий человек',
                                    'cost': 1
                                },
                                {
                                    'name': '132',
                                    'value': '🤺 Бегущий по лезвию',
                                    'cost': 1
                                },
                                {
                                    'name': '133',
                                    'value': '🤍 Аскорбинка',
                                    'cost': 1
                                },
                                {
                                    'name': '134',
                                    'value': '😷 Медицинская маска',
                                    'cost': 1
                                },
                                {
                                    'name': '135',
                                    'value': '💉 Удостоверение "Главврач"',
                                    'cost': 1
                                },
                                {
                                    'name': '136',
                                    'value': '💃 Статуэтка "Умница"',
                                    'cost': 1
                                },
                                {
                                    'name': '137',
                                    'value': '🕺 Статуэтка "Умник, бля"',
                                    'cost': 1
                                },
                                {
                                    'name': '138',
                                    'value': '🌷 Цветок "Первонах"',
                                    'cost': 1
                                },
                                {
                                    'name': '139',
                                    'value': '🗣 Соблазнитель ванаМинго',
                                    'cost': 1
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
                            'name': '👨‍❤️‍👨Участник "Пидор дня"',
                            'value': False
                        }
                        ,
                        {
                            'name': '🃏Мой герб',
                            'value': ""
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
                                'from_date': datetime.datetime(2020, 1, 31, 6, 0, 0).timestamp(), 
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
                {'band': 'FgoatUpd'},
                {'band': 'ЭнтрǁØǁпия'}
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
                                            'name': 'crewname',
                                            'boss': 'EastMinsk'
                                        },
                                        {
                                            'name': 'FgoatUpd',
                                            'boss': 'nik_stopka'
                                        },
                                        {
                                            'name': 'ЭнтрǁØǁпия',
                                            'boss': 'Viktoriya_Sizko'
                                        },
                                        {
                                            'name': 'АртхǁȺǁус',
                                            'boss': 'Innok27'
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

# x = plan_raids.delete_many({'rade_date':1580162400.0})
# print(x.deleted_count)

print("#==========================#")              
print("#         USERS            #")    
print("#==========================#")

# for x in registered_users.find({'rank': None}):
#     registered_users.update(
#         { 'login': x.get('login')},
#         { '$set': { 'rank': 
#                             {
#                                 'name': '1',
#                                 'value': '🧪Воин из пбробирки',
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

print("#==========================#")              
print("#         WARIORS          #")              
print("#==========================#")

print("#==========================#")              
print("#         BATTLE           #")              
print("#==========================#")
# pip_history     = mydb["pip_history"]
# 
#  mob.remove()


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






