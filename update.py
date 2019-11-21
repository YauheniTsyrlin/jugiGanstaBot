import pymongo
import json
import datetime
import main


myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["jugidb"]
registered_users = mydb["users"]
try_counters = mydb["try_counter"]
registered_wariors = mydb["wariors"]
battle = mydb["battle"]
settings = mydb["settings"]

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


result = settings.find_one({'code': 'REPORT_KILLERS'})
if (not result):
    print('Not Find setting. Insert REPORT_KILLERS')
    settings.insert_one({
        'code': 'REPORT_KILLERS', 
        'description': 'Дата начала отчета, Дата завершения отчета', 
        'value': {
            'from_date': None, 
            'to_date': None}})

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

result = settings.find_one({'code': 'PROBABILITY_I_DONT_NOW'})
if (not result):
    print('Not Find setting. Insert probability')
    settings.insert_one({
        'code': 'PROBABILITY_I_DONT_NOW', 
        'description': 'Вероятность того, бот спросит, кто ты такой', 
        'value': 0.3   
             })

result = settings.find_one({'code': 'OUR_BAND'})
if (not result):
    print('Not Find setting. Insert OUR_BAND')
    settings.insert_one({
        'code': 'OUR_BAND', 
        'description': 'Банды, имеющие право пользоваться Джу', 
        'value': 
            [{'band': 'Артхаус'},
             {'band': 'Энтропия'}]   
             })             

result = settings.find_one({'code': 'BANDS_INLINE_WARIORS'})
if (not result):
    print('Not Find setting. Insert BANDS_INLINE_WARIORS')
    settings.insert_one({
        'code': 'BANDS_INLINE_WARIORS', 
        'description': 'Банды, имеющие право пользоваться inline сервисом wariors', 
        'value': 
            [{'band': 'Артхаус'},
             {'band': 'Энтропия'},
             {'band': 'без банды'},
             {'band': 'Crewname'},
             {'band': 'FgoatUpd'}]   
             })     


print("#==========================#")              
print("#         SETTINGS         #")              
print("#==========================#")              

myquery = { "code": 'REPORT_KILLERS' }
newvalues = { "$set": { "value": {'from_date': datetime.datetime(2019, 10, 27).timestamp(), 'to_date': None}} } 
u = settings.update_one(myquery, newvalues)


myquery = { "code": 'OUR_BAND' }
newvalues = { "$set": { "value": 
            [{'band': 'Артхаус'},
             {'band': 'Энтропия'}]
             } } 
u = settings.update_one(myquery, newvalues)

myquery = { "code": 'BANDS_INLINE_WARIORS' }
newvalues = { "$set": { "value": 
            [{'band': 'Артхаус'},
             {'band': 'Энтропия'},
             {'band': 'без банды'},
             {'band': 'Crewname'},
             {'band': 'FgoatUpd'}]
             } } 
u = settings.update_one(myquery, newvalues)

for x in settings.find():
    print(x)

print("#==========================#")              
print("#         USERS            #")    
print("#    update loacation      #")                        
print("#==========================#")

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