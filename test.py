
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
settings    = mydb["settings"]
competition = mydb["competition"]
USERS = []

def getSetting(code: str):
    """ Получение настройки """
    result = settings.find_one({'code': code})
    if (result):
        return result.get('value') 

def setSetting(code: str, value: str):
    """ Сохранение настройки """
    myquery = { "code": code }
    newvalues = { "$set": { "value": value.toJSON() } }
    settings.update_one(myquery, newvalues)

#myquery = { "code": 'REPORT_KILLERS' }
#newvalues = { "$set": { "value": {'from_date': datetime.datetime(2019, 10, 27).timestamp(), 'to_date': None}} } 
#u = settings.update_one(myquery, newvalues)

setting = getSetting('REPORT_KILLERS')
from_date = setting.get('from_date')
to_date = setting.get('to_date')

#if (not from_date):
from_date = (datetime.datetime(2019, 1, 1) + datetime.timedelta(minutes=180)).timestamp() 

if (not to_date):
    to_date = (datetime.datetime.now() + datetime.timedelta(minutes=180)).timestamp()

print(from_date)
print(to_date)

# registered_users.insert_one({'accuracy': '120', 'agility': '475', 'armor': '270', 'band': 'Артхаус', 'charisma': '151', 'damage': '1014', 'dzen': 0, 'force': '670', 'fraction': '⚙️Убежище 4', 'health': '675', 'hunger': '13', 'loacation': '👣0км.', 'login': 'XyTop_2', 'name': 'Arkа', 'stamina': '18', 'timeBan': None, 'timeUpdate': 1571635229, 'status': None})

for x in battle.find({
                                    "$and" : [
                                        { 
                                            "date": {
                                                '$gte': from_date,
                                                '$lt': to_date
                                                    }       
                                        },
                                        {
                                            "band": 'Артхаус'   
                                        }]
                                }):                                                 
    print(x)

# competition.remove()
# competition.insert_one({'login': 'GonzikBenzyavsky', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Кирилл', 'health': '665', 'damage': '995', 'armor': '227', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['⚔ Нападение', '😎 Провокация', '🛡 Защита'], 'band':'🎩 Городские'})
# competition.insert_one({'login': 'GonzikBenzyavsky1', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Сергей', 'health': '665', 'damage': '1000', 'armor': '150', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['⚔ Нападение', '😎 Провокация', '🛡 Защита'], 'band':'🎩 Городские'})
# competition.insert_one({'login': 'GonzikBenzyavsky2', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Дмитрий', 'health': '665', 'damage': '500', 'armor': '227', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['⚔ Нападение', '😎 Провокация', '🛡 Защита'], 'band':'🎩 Городские'})
# competition.insert_one({'login': 'GonzikBenzyavsky3', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Иван', 'health': '665', 'damage': '700', 'armor': '100', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['⚔ Нападение', '😎 Провокация', '🛡 Защита'], 'band':'🎩 Городские'})
#competition.insert_one({'login': 'GonzikBenzyavsky4', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Петр', 'health': '665', 'damage': '650', 'armor': '200', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['⚔ Нападение', '😎 Провокация', '🛡 Защита'], 'band':'🎩 Городские'})
# competition.insert_one({'login': 'XyTop_2', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Arka', 'health': '665', 'damage': '1100', 'armor': '250', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['🛡 Защита', '⚔ Нападение', '😎 Провокация'], 'band':'🐇 Мертвые кролики'})
# competition.insert_one({'login': 'XyTop_21', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Mark', 'health': '665', 'damage': '200', 'armor': '100', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['😎 Провокация', '🛡 Защита', '⚔ Нападение'], 'band':'🐇 Мертвые кролики'})
# competition.insert_one({'login': 'XyTop_22', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Born', 'health': '665', 'damage': '500', 'armor': '100', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['🛡 Защита', '😎 Провокация', '⚔ Нападение'], 'band':'🐇 Мертвые кролики'})
#competition.insert_one({'login': 'XyTop_23', 'chat': 497065022, 'date': 1571401667.250403, 'state': 'READY', 'name': 'Corn', 'health': '665', 'damage': '900', 'armor': '135', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['🛡 Защита', '⚔ Нападение', '😎 Провокация'], 'band':'🐇 Мертвые кролики'})



# registered_users.remove()  

# competition.insert_one({'login': 'GonzikBenzyavsky', 'chat': 497065022, 'date': 1571771071.300144, 'state': 'READY', 'name': 'Кирилл', 'health': '665', 'damage': '995', 'armor': '227', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['🛡 Защита', '😎 Провокация', '⚔ Нападение'], 'band': '🐇 Мертвые кролики'})
# competition.insert_one({'login': 'XyTop_2', 'chat': 497065022, 'date': 1571771071.300144, 'state': 'READY', 'name': 'Монстр', 'health': '665', 'damage': '995', 'armor': '227', 'accuracy': '120', 'agility': '452', 'charisma': '151', 'bm': 2383, 'strategy': ['⚔ Нападение', '😎 Провокация', '🛡 Защита'], 'band': '🎩 Городские'})
# for x in competition.find():                                                 
#     print(x)

# dresult = battle.aggregate([
#                             {   "$match": {
#                                     "$and" : [
#                                         {
#                                             "band": "Артхаус"  
#                                         }]
#                                 }
#                             }, 
#                             {   "$group": {
#                                 "_id": "$winnerWarior", 
#                                 "count": {
#                                     "$sum": 1}}},
                                
#                             {   "$sort" : { "count" : -1 } }
#                             ])
# for x in dresult:
#     print(x)

    
# competition.delete_many({'login':'GonzikBenzyavsky3'})
# isReplay = False
# for x in competition.find({'login': 'GonzikBenzyavsky', 'chat': '12345678',   'state': { '$ne': '/^WAIT.*/' } }):                                                 
#     isReplay = True
#     break

# if not isReplay:
#     competition.insert_one({'login': 'GonzikBenzyavsky', 
#                             'chat': '12345678',
#                             'date': datetime.datetime.now().timestamp(), 
#                             'state': 'WAIT',
#                             'strategy': None})
 

# for x in competition.find():
#        print(x)
                            
# 
#     
#settings.delete_many({})
# for x in settings.find():
#        print(x)

# report = ''
# report = report + '🏆ТОП УБИЙЦ \n'
# report = report + '\n'
# setting = getSetting('REPORT_KILLERS')

# from_date = setting.get('from_date')
# to_date = setting.get('to_date')

# if (not from_date):
#     from_date = datetime.datetime(2019, 1, 1).timestamp() 
# else:
#     from_date = datetime.datetime.strptime(from_date, '%d/%m/%y').timestamp()

# if (not to_date):
#     to_date = datetime.datetime.now().timestamp()
# else:
#     to_date = datetime.datetime.strptime(to_date, '%d/%m/%y').timestamp()

# dresult = battle.aggregate([
#     {   "$match": { "date": {
#                 '$gte': from_date,
#                 '$lt': to_date
#             }
#         } 
#     }, 
#     {   "$group": {
#         "_id": "$winnerWarior", 
#         "count": {
#             "$sum": 1}}},
        
#     {   "$sort" : { "count" : -1 } }
#     ])

# findInWinner = False
# i = 0
# for d in dresult:
#     i = i + 1
#     if i == 1:
#         emoji = '🥇 '
#     elif i == 2:
#         emoji = '🥈 '    
#     elif i == 3:
#         emoji = '🥉 '
#     else:
#         emoji = ''
#     user_name = d.get("_id")
#     if user_name == 'Кирилл':
#         user_name = f'*{user_name}*'
#         findInWinner = True

#     report = report + f'{i}. {emoji}{user_name}: {d.get("count")}\n' 
#     if i == 10: break

# if (i == 0): 
#     report = report + f'Мир! Пис! ✌️🌷🐣\n'
# else:
#     if (not findInWinner): report = report + f'👹 Тебя нет среди нормальных пацанов!\n'
    
# report = report + f'\n' 
# report = report + f'⚰️ТОП НЕУДАЧНИКОВ' 
# dresult = battle.aggregate([
#     {   "$match": { "date": {
#                 '$gte': from_date,
#                 '$lt': to_date
#             }
#         } 
#     }, 
#     {   "$group": {
#         "_id": "$loseWarior", 
#         "count": {
#             "$sum": 1}}},
        
#     {   "$sort" : { "count" : -1 } }
#     ])

# findInLoser = False
# i = 0
# for d in dresult:
#     i = i + 1
#     if i == 1:
#         emoji = '👻 '
#     elif i == 2:
#         emoji = '💀️ '    
#     elif i == 3:
#         emoji = '☠️ '
#     else:
#         emoji = ''
#     user_name = d.get("_id")
#     if user_name == 'Кирилл':
#         user_name = f'*{user_name}*'
#         findInLoser = True

#     report = report + f'{i}. {emoji}{user_name}: {d.get("count")}\n' 
#     if i == 10: break

# if (i == 0): 
#     report = report + f'Мы бессмертны ✌️👻💀☠️\n'
# else:
#     if (findInWinner): report = report + f'🧸 Ты, лузер!\n'
# report = report + f'\n' 
# report = report + '⏰ c ' + time.strftime("%d-%m-%Y", time.gmtime(from_date)) + ' по ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(to_date))

# print(report)

# battle.insert_one({'login': 'monzik', 'date': datetime.now().timestamp(), 'winnerWarior': 'Win1', 'loseWarior': 'lose'})
# battle.insert_one({'login': 'konzik', 'date': datetime.now().timestamp(), 'winnerWarior': 'Win1', 'loseWarior': 'lose'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': datetime.now().timestamp(), 'winnerWarior': 'Кирилл', 'loseWarior': 'lose1'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': datetime.now().timestamp(), 'winnerWarior': 'lose1', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': datetime.now().timestamp(), 'winnerWarior': 'Кирилл', 'loseWarior': 'lose1'})
# battle.insert_one({'login': 'konzik', 'date': datetime.now().timestamp(), 'winnerWarior': 'lose', 'loseWarior': 'Win1'})
# battle.insert_one({'login': 'tonzik', 'date': datetime.now().timestamp(), 'winnerWarior': 'lose', 'loseWarior': 'Win1'})

# for x in registered_wariors.find():
#        print(x)

# print("==================================================")

# for x in registered_wariors.find({'name':{'$regex':'ири', '$options':'i'}}):
#    print(x.get('name'))

# myquery = {}
# newvalues = { "$set": { "photo": None } }
# x = registered_wariors.update_many(myquery, newvalues)

# text = u'📟Пип-бой 3000 v2.2b1\nНачалось игровое событие\n\"Легкие на подъем\"\nArkа, 💣Мегатонна\n🤟Банда: Артхаус\n❤️Здоровье: 1103/969\n☠️Голод: 100% /myfood\n⚔️Урон: 1272 🛡Броня: 260\n\n💪Сила: 928 🎯Меткость: 63\n🗣Харизма: 54 🤸🏽‍♂️Ловкость: 526\n\n🔋Выносливость: 18/21 /ref\n📍Школа, 👣45км. \n\nЭкипировка:\nДвуствольное ружье \n🛠Мультизащита🔆 +168🛡 🔧99%\n🛠Костяной шлем +92🛡 🔧77%\n🧠Брейналайзер +344⚔️ 🔧100%\n📥Модуль регенерации\n\nРесурсы:\n🕳Крышки: 18874 \n📦Материалы: 24519\n💈Пупсы: 2 /thanks\n🏆Рейтинг /wwtop\n\nРепутация:\nНейтральный\n🏵2 ▓▓░░░░░░░░\nID256292161\n\nРейд в 17:00 16.9:\nСтарая фабрика\n 🕳+1792 📦+2688 📦+0'
# text = '⚛️ ✴ Alfakill и его 🛰Шерлокдрон.\n🤘(без банды)\n⚔️ /p_I2CL'
# text = '⚙️ Laughing_Bright\n🐐Pro100KAPIBARY 🤘Туннельные змеи\n⚔️ /p_UOMB'

# i = 0
# strings = text.split('\n')
# isEquipequipment = False
# for s in strings:
#    print(strings[i].split(' ')[0])
#    if (strings[i].startswith('⚛️')) : print('Ура!')
#    if (strings[i].startswith('⚙️')) : print('Ура!2')
   
#    i = i + 1

# i = 0
# strings = text.split('\n')
# isEquipequipment = False
# for s in strings:
#     if ('🏵' in strings[i]):
#         dzen_tmp = strings[i][1:2].strip()
#         if dzen_tmp == '':
#             print('Dzen = 0')
#         elif (int(dzen_tmp) >=2):
#             print(str(int(dzen_tmp)-1))
        
#     # print(str(i)+' - |'+s+'|')
#     i=i+1

    
# for target_list in USERS:
#     print(target_list.get('login'))
# for registered_user in registered_users.find({"login": f"XyTop_2"}):
#     print(registered_user)

# registered_users.remove()
# registered_wariors.remove()
# try_counters.remove()
