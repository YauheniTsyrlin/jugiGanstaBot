import pymongo
import json
import datetime

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["jugidb"]
registered_users = mydb["users"]
try_counters = mydb["try_counter"]
registered_wariors = mydb["wariors"]
battle = mydb["battle"]
settings = mydb["settings"]
report_raids    = mydb["report_raids"]

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
        'value': 
            [{'login': 'GonzikBenzyavsky'},
             {'login': 'Innok27'}]   
             })

result = settings.find_one({'code': 'PROBABILITY'})
if (not result):
    print('Not Find setting. Insert probability')
    settings.insert_one({
        'code': 'PROBABILITY', 
        'description': 'Вероятности', 
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

myquery = { "code": 'ACCESSORY' }
newvalues = { "$set": { "value": 
                    [
                        {
                            'name': 'PIP_BOY',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': '📟 Пип-бой 2000'
                                },
                                {
                                    'name': '2',
                                    'value': '📟 антена от Пип-боя'
                                },
                                {
                                    'name': '3',
                                    'value': '📟 аккумулятор от Пип-боя'
                                },
                                {
                                    'name': '4',
                                    'value': '📟 игрушечный Пип-бой'
                                },
                                {
                                    'name': '5',
                                    'value': '📟 упаковка от Пип-боя'
                                },
                                {
                                    'name': '6',
                                    'value': '📟 запчасть от Пип-боя'
                                },
                                {
                                    'name': '7',
                                    'value': '📟 моделька Пип-боя'
                                },
                                {
                                    'name': '8',
                                    'value': '📟 сломанный Пип-бой'
                                },
                                {
                                    'name': '9',
                                    'value': '📟 болт от Пип-боя'
                                }
                            ] 
                        },
                        {
                            'name': 'REWARDS',
                            'value':
                            [
                                {
                                    'name': '1',
                                    'value': '🔬 Халат учёного'
                                },
                                {
                                    'name': '2',
                                    'value': '🎩 Шляпа Линкольна'
                                },
                                {
                                    'name': '3',
                                    'value': '👒 Соломенная шляпка'
                                },
                                {
                                    'name': '4',
                                    'value': '🩲 Трусы охотника на Трогов'
                                },
                                {
                                    'name': '5',
                                    'value': '🐚 Труп улитки'
                                },
                                {
                                    'name': '6',
                                    'value': '🦈 Статуэтка "Акула"'
                                },
                                {
                                    'name': '7',
                                    'value': '🦇 Медалька с мышью'
                                },
                                {
                                    'name': '8',
                                    'value': '🍾 Бармен 2019 года'
                                },
                                {
                                    'name': '9',
                                    'value': '🎭 Набор стикеров Fallout 2'
                                },
                                {
                                    'name': '10',
                                    'value': '🔪 Сасайкудасай'
                                },
                                {
                                    'name': '11',
                                    'value': '🧂 Соль на рану'
                                },
                                {
                                    'name': '12',
                                    'value': '🥋 Чёрный пояс по PvP'
                                },
                                {
                                    'name': '13',
                                    'value': '🍴 Вилка в глаз'
                                },
                                {
                                    'name': '14',
                                    'value': '🎲 Кубик ребусоведа'
                                },
                                {
                                    'name': '15',
                                    'value': '🍪 Довоенное печенье'
                                },
                                {
                                    'name': '16',
                                    'value': '🏴 Флаг смерти'
                                },
                                {
                                    'name': '17',
                                    'value': '👽 Голова кромбопулуса'
                                },
                                {
                                    'name': '18',
                                    'value': '📖 «Как перегонять спирт»'
                                },
                                {
                                    'name': '19',
                                    'value': '🗡️ Меч джедая'
                                },
                                {
                                    'name': '20',
                                    'value': '🦷 Молочный зуб Рашки'
                                },
                                {
                                    'name': '21',
                                    'value': '📿 Чётки босса банды'
                                },
                                {
                                    'name': '22',
                                    'value': '🔑 От квартиры в Ореоле'
                                },
                                {
                                    'name': '23',
                                    'value': '🏵️ Грамота за 1-ый Дзен'
                                },
                                {
                                    'name': '24',
                                    'value': '🏵️ Грамота за 2-ый Дзен'
                                },
                                {
                                    'name': '25',
                                    'value': '🏵️ Грамота за 3-ый Дзен'
                                },
                                {
                                    'name': '26',
                                    'value': '🏵️ Грамота за 4-ый Дзен'
                                },
                                {
                                    'name': '27',
                                    'value': '🏵️ Грамота за 5-ый Дзен'
                                },
                                {
                                    'name': '28',
                                    'value': '🧤 Дуэльная перчатка'
                                },
                                {
                                    'name': '29',
                                    'value': '🔩 Болт М69, возложенный на рейд'
                                },
                                {
                                    'name': '30',
                                    'value': '🔩🔩 Болт М228, возложенный на рейд'
                                },
                                {
                                    'name': '31',
                                    'value': '🔩🔩🔩 Болт М404, возложенный на рейд'
                                },
                                {
                                    'name': '32',
                                    'value': '🔩🔩🔩🔩 Болт М1488, возложенный на рейд'
                                },
                                {
                                    'name': '33',
                                    'value': '🎫🍼 Билет на гигантскую бутылку'
                                },
                                {
                                    'name': '34',
                                    'value': '🧱 Кирпич на голову'
                                },
                                {
                                    'name': '35',
                                    'value': '🎞️Фото 8-ми бандитов на фоне Научного комплекса'
                                },
                                {
                                    'name': '36',
                                    'value': '☢️Табличка с двери Научного комплекса с 8-ю подписями бойцов АртхǁȺǁус'
                                },
                                {
                                    'name': '37',
                                    'value': '📜 Грамота от вМ за групповой захват Научного комплекса'
                                },
                                {
                                    'name': '38',
                                    'value': '🍼 Пробирка из Научного комплекса с надписью - здэс был Артоха̶уз'
                                },
                                {
                                    'name': '39',
                                    'value': '🤼 Статуэтка из говна и палок - "Групповой захват Научного комплекса"'
                                },
                                {
                                    'name': '40',
                                    'value': '🎫 Билет на троллебус на групповую поездку до Научного комплекса'
                                },
                                {
                                    'name': '41',
                                    'value': '🎖️ Медаль за захват 7-ми данже подряд 1-ой степени'
                                },
                                {
                                    'name': '42',
                                    'value': '📰 Статья в газете о легендарном походе за семью данжами'
                                },
                                {
                                    'name': '43',
                                    'value': '📃 Путёвка в санаторий "SPA Пустошь" за захват 7-ми данжей'
                                },
                                {
                                    'name': '44',
                                    'value': '🔱 Трезубец повелителя Пустоши'
                                },
                                {
                                    'name': '45',
                                    'value': '🛠️ Ремкомплект для Пип-боя'
                                },
                                {
                                    'name': '46',
                                    'value': '🥢 Близкая дружба'
                                },
                                {
                                    'name': '47',
                                    'value': '🌪 Пыль с Шерстяного'
                                },
                                {
                                    'name': '48',
                                    'value': '🗜 Зажим на соски'
                                },
                                {
                                    'name': '49',
                                    'value': '💿 Козырёк в авто'
                                },
                                {
                                    'name': '50',
                                    'value': '📀 Блатной козырёк в авто'
                                },
                                {
                                    'name': '51',
                                    'value': '🕹️ Анальная пробка'
                                },
                                {
                                    'name': '52',
                                    'value': '🥌 Утюг'
                                },
                                {
                                    'name': '53',
                                    'value': '🏵 Очко Саурона'
                                },
                                {
                                    'name': '54',
                                    'value': '🎷Фаггот'
                                },

                                {
                                    'name': '55',
                                    'value': '💸 Лёгкие на подъём'
                                },
                                {
                                    'name': '56',
                                    'value': '⚱️Бафомет'
                                },
                                {
                                    'name': '57',
                                    'value': '🏺 Анимэ'
                                },
                                {
                                    'name': '58',
                                    'value': '🧁 Two girls, one cup'
                                },
                                {
                                    'name': '59',
                                    'value': '🔍 Лупа'
                                },
                                {
                                    'name': '60',
                                    'value': '🔎 Щёка'
                                },
                                {
                                    'name': '61',
                                    'value': '✂️ Мифическая дружба'
                                },
                                {
                                    'name': '62',
                                    'value': '🆔 Деанон'
                                },
                                {
                                    'name': '63',
                                    'value': '🉐💮 Язык программирования'
                                },
                                {
                                    'name': '64',
                                    'value': '🛑 Круг перфекциониста'
                                },
                                {
                                    'name': '65',
                                    'value': '🌀 Пауль'
                                },
                                {
                                    'name': '66',
                                    'value': '♿️ Зато не пешком'
                                },
                                {
                                    'name': '67',
                                    'value': '🚼 Чужой'
                                },
                                {
                                    'name': '68',
                                    'value': '🎶 Долбит нормально'
                                },
                                {
                                    'name': '69',
                                    'value': '🔊 GPS'
                                },
                                {
                                    'name': '70',
                                    'value': '🧲 Подкова'
                                },
                                {
                                    'name': '71',
                                    'value': '📿 Армяне на стиле'
                                },
                                {
                                    'name': '72',
                                    'value': '⚗️ На 95% безопаснее'
                                },
                                {
                                    'name': '73',
                                    'value': '🔬 Зеркальная болезнь'
                                },
                                {
                                    'name': '74',
                                    'value': '🕳 Бывшая'
                                },
                                {
                                    'name': '75',
                                    'value': '🍯 Бывшая [2]'
                                },
                                {
                                    'name': '76',
                                    'value': '🧻 План рейда'
                                },
                                {
                                    'name': '77',
                                    'value': '🚿 Расчёска от лох'
                                },
                                {
                                    'name': '78',
                                    'value': '🌡 Томатный сок'
                                },
                                {
                                    'name': '79',
                                    'value': '♟ Эйфелева Башня'
                                },
                                {
                                    'name': '80',
                                    'value': '🚵 Директор педального завода'
                                },
                                {
                                    'name': '81',
                                    'value': '🏆 Горшок'
                                },
                                {
                                    'name': '82',
                                    'value': '🤯 Расчёт РМ'
                                },
                                {
                                    'name': '83',
                                    'value': '😷 Китаец'
                                },
                                {
                                    'name': '84',
                                    'value': '👻 Носовой платок'
                                },
                                {
                                    'name': '85',
                                    'value': '🚬 Арома стик'
                                },
                                {
                                    'name': '86',
                                    'value': '🧑‍🦽 Цены на бензин'
                                },
                                {
                                    'name': '87',
                                    'value': '🧑‍🦯 Металлоискатель'
                                },
                                {
                                    'name': '88',
                                    'value': '🥱 Ем руку'
                                },
                                {
                                    'name': '89',
                                    'value': '🤮 Полёт на Марс'
                                },
                                {
                                    'name': '90',
                                    'value': '🤒 Пью томатный сок'
                                },
                                {
                                    'name': '91',
                                    'value': '💀 Гамлет'
                                },
                                {
                                    'name': '92',
                                    'value': '💀 Йорик'
                                },
                                {
                                    'name': '93',
                                    'value': '☠️ Суповой комплект'
                                },
                                {
                                    'name': '94',
                                    'value': '👽 Латексная маска'
                                },
                                {
                                    'name': '95',
                                    'value': '👾 Ъуъеъкхх'
                                },
                                {
                                    'name': '96',
                                    'value': '👾 тпфптлтвфт ъуъ сука'
                                },
                                {
                                    'name': '97',
                                    'value': '💩 Трюфель'
                                },
                                {
                                    'name': '98',
                                    'value': '🥿 Батины тапки'
                                },
                                {
                                    'name': '99',
                                    'value': '🖕 Нихуя І степени'
                                },
                                {
                                    'name': '100',
                                    'value': '🖕🖕 Нихуя ІІ степени'
                                },
                                {
                                    'name': '101',
                                    'value': '🖕🖕🖕 Нихуя ІІІ степени'
                                },
                                {
                                    'name': '102',
                                    'value': '🖕🖕🖕🖕 Нихуя IV степени'
                                },
                                {
                                    'name': '103',
                                    'value': '🖕🖕🖕🖕🖕 Нихуя V степени'
                                },
                                {
                                    'name': '104',
                                    'value': '🎖️ Полный кавалер ордена "Нихуя"'
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
                            'name': '⚙️Открытое Убежище',
                            'value': '29'
                        },{
                            'name': '🚷🦇Бэт-пешера',
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
                            'name': '🚷⛩️Храм испытаний',
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
                            'value': 180
                        },
                        {
                            # Вероятность
                            'name': 'EMOTIONS',
                            'value': 0.10
                        },
                        {
                            # Вероятность
                            'name': 'YES_STICKER',
                            'value': 1.00
                        },
                        {
                            # Вероятность
                            'name': 'NO_STICKER',
                            'value': 1.00
                        },
                        {
                            # Вероятность
                            'name': 'A_STICKER',
                            'value': 1.00
                        },
                        {
                            # Вероятность
                            'name': 'YOU_PRIVATE_CHAT',
                            'value': 0.5
                        },
                        {
                            # Range
                            'name': 'JUGI_BAD_BOT_BAN',
                            'value': 600
                        }

                        
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
                                'from_date': datetime.datetime(2020, 1, 23, 0, 0, 0).timestamp(), 
                                'to_date': None
                            }
                        },
                        {
                            'name': 'RAIDS',
                            'value': {
                                'from_date': datetime.datetime(2020, 1, 23, 0, 0, 0).timestamp(), 
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
                }
            ]
        } } 
             
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
                                            'boss': 'GonzikBenzyavsky'
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


x = report_raids.delete_many({'date':1580162400.0});

print("#==========================#")              
print("#         USERS            #")    
print("#==========================#")

# for x in registered_users.find():
#     registered_users.update(
#         { 'login': x.get('login')},
#         { '$set': { 'raidlocation': None} }
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
# for x in battle.find():
#     print(x)