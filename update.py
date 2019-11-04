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
             {'band': 'Энтропия'},
             {'band': 'Марипоза'}]   
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
             {'band': 'Энтропия'},
             {'band': 'Марипоза'}]
             } } 
u = settings.update_one(myquery, newvalues)


for x in settings.find():
    print(x)

print("#==========================#")              
print("#         USERS            #")    
print("#    update loacation      #")                        
print("#==========================#")

for x in registered_users.find():
    registered_users.update(
        { 'login': x.get('login')},
        { '$unset': { 'loacation': ''} }
    )

for x in registered_users.find():
    registered_users.update(
        { 'login': x.get('login')},
        { '$set': { 'location': None} }
    )

# registered_users.remove()            
# registered_users.insert_one({'accuracy': '120', 'agility': '475', 'armor': '270', 'band': 'Артхаус', 'charisma': '151', 'damage': '1014', 'dzen': 0, 'force': '670', 'fraction': '⚙️Убежище 4', 'health': '675', 'hunger': '13', 'loacation': '👣0км.', 'login': 'GonzikBenzyavsky', 'name': 'Кирилл', 'stamina': '18', 'timeBan': None, 'timeUpdate': 1571635229, 'status': None})
# registered_users.insert_one({'accuracy': '72', 'agility': '401', 'armor': '227', 'band': 'Энтропия', 'charisma': '130', 'damage': '757', 'dzen': 0, 'force': '479', 'fraction': '🔪Головорезы', 'health': '471', 'hunger': '5', 'loacation': '👣11км.', 'login': 'Innok27', 'name': 'Innok27', 'stamina': '29', 'timeBan': None, 'timeUpdate': 1571694768, 'status': None})
# registered_users.insert_one({'accuracy': '65', 'agility': '403', 'armor': '227', 'band': 'Неизвестна /me', 'charisma': '117', 'damage': '817', 'dzen': 0, 'force': '539', 'fraction': '⚙️Убежище 4', 'health': '601', 'hunger': '28', 'loacation': '👣12км.', 'login': 'artiomse', 'name': 'artiomse', 'stamina': '15', 'timeBan': None, 'timeUpdate': 1571246831, 'status': None})
# registered_users.insert_one({'accuracy': '20', 'agility': '233', 'armor': '227', 'band': 'Артхаус', 'charisma': '81', 'damage': '698', 'dzen': 0, 'force': '420', 'fraction': '⚛️Республика', 'health': '480', 'hunger': '15', 'loacation': '👣4км.', 'login': 'olehme', 'name': 'olehme', 'stamina': '19', 'timeBan': None, 'timeUpdate': 1571498193, 'status': None})
# registered_users.insert_one({'accuracy': '9', 'agility': '412', 'armor': '412', 'band': 'Артхаус', 'charisma': '68', 'damage': '1177', 'dzen': 0, 'force': '833', 'fraction': '⚙️Убежище 4', 'health': '860', 'hunger': '42', 'loacation': '👣17км.', 'login': 'Gromnsk', 'name': 'Gromnsk', 'stamina': '15', 'timeBan': None, 'timeUpdate': 1571710462, 'status': None})
# registered_users.insert_one({'accuracy': '22', 'agility': '75 (+20)', 'armor': '111', 'band': 'Энтропия', 'charisma': '111', 'damage': '324', 'dzen': 0, 'force': '175 (+20)', 'fraction': '⚛️Республика', 'health': '165', 'hunger': '2', 'loacation': '👣2км.', 'login': 'AlluZef', 'name': 'AlluZef', 'stamina': '11', 'timeBan': None, 'timeUpdate': 1571691550, 'status': None})
# registered_users.insert_one({'accuracy': '25', 'agility': '245', 'armor': '230', 'band': 'Артхаус', 'charisma': '70', 'damage': '1025', 'dzen': 0, 'force': '750', 'fraction': '💣Мегатонна', 'health': '744', 'hunger': '15', 'loacation': '👣14км.', 'login': 'wildcucumber', 'name': 'wildcucumber', 'stamina': '15', 'timeBan': None, 'timeUpdate': 1570876214})
# registered_users.insert_one({'accuracy': '120', 'agility': '230', 'armor': '227', 'band': 'Артхаус', 'charisma': '150', 'damage': '579', 'dzen': 0, 'force': '301', 'fraction': '💣Мегатонна', 'health': '354', 'hunger': '60', 'loacation': '👣23км.', 'login': 'UnknownUser_One', 'name': 'Титан', 'stamina': '17', 'timeBan': None, 'timeUpdate': 1570988993})
# registered_users.insert_one({'accuracy': '192', 'agility': '303', 'armor': '265', 'band': 'Артхаус', 'charisma': '433', 'damage': '1293', 'dzen': '2', 'force': '921', 'fraction': '⚛️Республика', 'health': '1154', 'hunger': '13', 'loacation': '👣49км.', 'login': 'QurReq', 'name': 'QurReq', 'stamina': '17', 'timeBan': None, 'timeUpdate': 1570992989})
# registered_users.insert_one({'accuracy': '46', 'agility': '352', 'armor': '201', 'band': 'Артхаус', 'charisma': '90', 'damage': '706', 'dzen': 0, 'force': '428', 'fraction': '⚛️Республика', 'health': '427', 'hunger': '78', 'loacation': '👣20км.', 'login': 'Art_Zank', 'name': 'Lidsky', 'stamina': '16', 'timeBan': None, 'timeUpdate': 1570983158, 'status': '🥇1-е место!'})
# registered_users.insert_one({'accuracy': '80', 'agility': '406', 'armor': '270', 'band': 'Артхаус', 'charisma': '207', 'damage': '896', 'dzen': 0, 'force': '552', 'fraction': '💣Мегатонна', 'health': '769', 'hunger': '97', 'loacation': '👣38км.', 'login': 'NiceTry_noCigar', 'name': 'NiceTry_noCigar', 'stamina': '9', 'timeBan': None, 'timeUpdate': 1570983153})
# registered_users.insert_one({'accuracy': '10', 'agility': '36', 'armor': '103', 'band': 'Артхаус', 'charisma': '20', 'damage': '224', 'dzen': 0, 'force': '204', 'fraction': '💣Мегатонна', 'health': '115', 'hunger': '86', 'loacation': '👣34км.', 'login': 'miashas', 'name': 'miashas', 'stamina': '11', 'status': None, 'timeBan': None, 'timeUpdate': 1571496738})
# registered_users.insert_one({'accuracy': '11', 'agility': '11', 'armor': '67 (+30)', 'band': 'Неизвестна /me', 'charisma': '22', 'damage': '157', 'dzen': 0, 'force': '84', 'fraction': '🔪Головорезы', 'health': '43', 'hunger': '23', 'loacation': '👣0км.', 'login': 'Fire_spreading_all_around', 'name': 'Fire_spreading_all_around', 'stamina': '8', 'status': None, 'timeBan': None, 'timeUpdate': 1571503766})
# registered_users.insert_one({'accuracy': '5', 'agility': '173', 'armor': '227', 'band': 'Артхаус', 'charisma': '108', 'damage': '826', 'dzen': 0, 'force': '548', 'fraction': '⚙️Убежище 4', 'health': '600', 'hunger': '60', 'loacation': '👣24км.', 'login': 'drHeterodox', 'name': 'drHeterodox', 'stamina': '19', 'status': None, 'timeBan': None, 'timeUpdate': 1571046410})
# registered_users.insert_one({'accuracy': '50', 'agility': '402', 'armor': '270', 'band': 'Артхаус', 'charisma': '352', 'damage': '1272', 'dzen': 0, 'force': '916', 'fraction': '🔪Головорезы', 'health': '1135', 'hunger': '76', 'loacation': '👣48км.', 'login': 'NorthDragoN', 'name': 'Дмитрий', 'stamina': '15', 'status': None, 'timeBan': None, 'timeUpdate': 1571605560})
# registered_users.insert_one({'band': 'Неизвестна /me', 'dzen': 0, 'login': 'Dostoevskiy_Fedor', 'status': None, 'timeBan': None, 'timeUpdate': 1571373140, 'accuracy': '120', 'agility': '238', 'armor': '227', 'charisma': '150', 'damage': '579', 'force': '301', 'fraction': '💣Мегатонна', 'health': '354', 'hunger': '2', 'loacation': '👣0км.', 'name': 'Титан', 'stamina': '17'})
# registered_users.insert_one({'accuracy': '40', 'agility': '260', 'armor': '227', 'band': 'Артхаус', 'charisma': '175', 'damage': '728', 'dzen': 0, 'force': '450', 'fraction': '🔪Головорезы', 'health': '455', 'hunger': '15', 'loacation': '👣24км.', 'login': 'Ian_reger', 'name': 'Ian_reger', 'stamina': '9', 'status': 'Осталось 55 💔 😢', 'timeBan': None, 'timeUpdate': 1571605344})
# registered_users.insert_one({'accuracy': '5', 'agility': '72', 'armor': '103', 'band': 'Энтропия', 'charisma': '130', 'damage': '210', 'dzen': 0, 'force': '190', 'fraction': '🔪Головорезы', 'health': '150', 'hunger': '57', 'loacation': '👣23км.', 'login': 'trimprim', 'name': 'ALT', 'stamina': '8', 'status': None, 'timeBan': None, 'timeUpdate': 1571834445})
# registered_users.insert_one({'accuracy': '9', 'agility': '36 (+10)', 'armor': '103 (+30)', 'band': 'Неизвестна /me', 'charisma': '25', 'damage': '139', 'dzen': 0, 'force': '101', 'fraction': '⚙️Убежище 4', 'health': '103', 'hunger': '60', 'loacation': '👣30км.', 'login': 'triple6ixx', 'name': 'triple6ixx', 'stamina': '12', 'status': None, 'timeBan': None, 'timeUpdate': 1571858057})
# registered_users.insert_one({'accuracy': '35', 'agility': '14', 'armor': '77 (+30)', 'band': 'Артхаус', 'charisma': '23', 'damage': '217', 'dzen': 0, 'force': '117', 'fraction': '🔪Головорезы', 'health': '87', 'hunger': '55', 'loacation': '👣0км.', 'login': 'Dandel1on', 'name': 'Fire_spreading_all_around', 'stamina': '8', 'status': None, 'timeBan': None, 'timeUpdate': 1571858168})

print("#==========================#")              
print("#         WARIORS          #")              
print("#==========================#")
# registered_wariors.remove()     
# registered_wariors.insert_one({'band': 'Артхаус', 'bm': 0, 'damage': 577, 'fraction': '💣Мегатонна', 'goat': None, 'health': 1221, 'hithimself': 3, 'kills': 10, 'missed': 2, 'name': 'Arkа', 'photo': 'AgADAgAD_KsxG3hzOUm1iMPIlgksuH_Ktw8ABAEAAwIAA20AAwtcBQABFgQ', 'timeUpdate': 1570955113, 'enemy_armor': None})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 0, 'fraction': '🔪Головорезы', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Чехов', 'photo': None, 'timeUpdate': 1570955113})
# registered_wariors.insert_one({'band': 'New Vegas', 'bm': 0, 'damage': 316, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': 260, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'BananaCompote ŇṼ', 'photo': None, 'timeUpdate': 1570025519, 'enemy_armor': '227'})
# registered_wariors.insert_one({'band': 'сорок два', 'bm': 0, 'damage': 0, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'IlMai⁴²', 'photo': None, 'timeUpdate': 1570960088})
# registered_wariors.insert_one({'band': 'Iamlaserpewpew', 'bm': 0, 'damage': 450, 'fraction': '🔪Головорезы', 'goat': 'Iamlaserpewpew', 'health': 932, 'hithimself': 0, 'kills': 3, 'missed': 0, 'name': 'Ирина', 'photo': 'AgADAgADZ6sxG5RtcUmzSwzFwWN91sDguQ8ABAEAAwIAA20AA69CBAABFgQ', 'timeUpdate': 1570960370, 'enemy_armor': '260'})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 515, 'fraction': '⚛️Республика', 'goat': None, 'health': 531, 'hithimself': 0, 'kills': 2, 'missed': 0, 'name': 'Дядя Duck ŇṼ', 'photo': None, 'timeUpdate': 1570966124, 'enemy_armor': None})
# registered_wariors.insert_one({'band': 'New Vegas East', 'bm': 0, 'damage': 348, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': 195, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Дядя Divnaia ŇṼ', 'photo': 'AgADAgADBKsxG3JReUldKBfmDOtsyuN3XA8ABAEAAwIAA20AAzZYAAIWBA', 'timeUpdate': 1570968590, 'enemy_armor': None})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': 0, 'damage': 0, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Andjey', 'photo': 'AgADAgAD-6sxGydKGEla6ssSTVair-Lxug8ABAEAAwIAA20AA9m9AwABFgQ', 'timeUpdate': 1570968951, 'enemy_armor': None})
# registered_wariors.insert_one({'band': 'Memento Mori', 'bm': 0, 'damage': 0, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'KamchaCat', 'photo': None, 'timeUpdate': 1570969740})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': 0, 'damage': 0, 'fraction': '💣Мегатонна', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'ashapasintes', 'photo': None, 'timeUpdate': 1570970394})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': 0, 'damage': 0, 'fraction': '💣Мегатонна', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': '3ihiko Нации', 'photo': None, 'timeUpdate': 1570972283})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': 0, 'damage': 0, 'fraction': '💣Мегатонна', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'aul', 'photo': None, 'timeUpdate': 1570972728})
# registered_wariors.insert_one({'band': 'Гей Клуб', 'bm': 0, 'damage': 0, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Riders_on_the_storm', 'photo': None, 'timeUpdate': 1570973969})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 184, 'fraction': '⚛️Республика', 'goat': None, 'health': 336, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Лоликонщик Ночи', 'photo': None, 'timeUpdate': 1570974987})
# registered_wariors.insert_one({'band': 'Артхаус', 'bm': 0, 'damage': 279, 'fraction': '⚛️Республика', 'goat': None, 'health': 568, 'hithimself': 1, 'kills': 4, 'missed': 1, 'name': 'olehme', 'photo': 'AgADAgADEqwxG1DTWUkikzVIGKeRWiLItw8ABAEAAwIAA20AA4Z7BQABFgQ', 'timeUpdate': 1570974987, 'enemy_armor': None})
# registered_wariors.insert_one({'band': 'Волчий отряд', 'bm': 0, 'damage': 0, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Nikita', 'photo': None, 'timeUpdate': 1570977733})
# registered_wariors.insert_one({'band': 'Энтропия', 'bm': 0, 'damage': 0, 'fraction': '🔪Головорезы', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'nnok27', 'photo': None, 'timeUpdate': 1570977817})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 83, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 295, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Starvy', 'photo': None, 'timeUpdate': 1570982269})
# registered_wariors.insert_one({'band': 'Артхаус', 'bm': 0, 'damage': 249, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 494, 'hithimself': 0, 'kills': 13, 'missed': 0, 'name': 'Lidsky', 'photo': 'AgADAgAD_qsxG4lqcEkdQ9ZtIlKZ7FRoXA8ABAEAAwIAA20AA4RUAAIWBA', 'timeUpdate': 1570982269})
# registered_wariors.insert_one({'band': 'Артхаус', 'bm': 0, 'damage': 277, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 816, 'hithimself': 0, 'kills': 11, 'missed': 0, 'name': 'Кирилл', 'photo': 'AgADAgADeqwxG8GOaUmdwL5FlimbgwzHtw8ABAEAAwIAA20AAxqTBQABFgQ', 'timeUpdate': 1570983387})
# registered_wariors.insert_one({'band': 'Потомки Oгня', 'bm': 0, 'damage': 0, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': 'Академия Ханов', 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'братакробат', 'photo': 'AgADAgADFqwxG9SsQEkV4YoyJu6fPSHutw8ABAEAAwIAA20AA9RgBQABFgQ', 'timeUpdate': 1570980002})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 403, 'enemy_armor': '342', 'fraction': '🔪Головорезы', 'goat': None, 'health': 776, 'hithimself': 1, 'kills': 2, 'missed': 1, 'name': 'I7cux37', 'photo': None, 'timeUpdate': 1570778395})
# registered_wariors.insert_one({'band': 'Pro100KAPIBARY', 'bm': 0, 'damage': 122, 'enemy_armor': '227', 'fraction': '⚙️Убежище 4', 'goat': 'Pro100KAPIBARY', 'health': 344, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Sovertkov', 'photo': 'AgADAgADXasxG6EfMUnKw1Sd6yYCxNLUug8ABAEAAwIAA20AAyHuAwABFgQ', 'timeUpdate': 1570650410})
# registered_wariors.insert_one({'band': 'Гей Клуб', 'bm': 0, 'damage': 211, 'enemy_armor': '167', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 494, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Dipper', 'photo': 'AgADAgADwasxG6bIKUniFG3u_AHmwkruug8ABAEAAwIAA20AAzO9AwABFgQ', 'timeUpdate': 1570132209})
# registered_wariors.insert_one({'band': 'сорок два', 'bm': 0, 'damage': 0, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': '_MrFoxy_', 'photo': 'AgADAgADcqwxG7McGEnDSqnJbg9SOK8BuA8ABAEAAwIAA20AAw0xBQABFgQ', 'timeUpdate': 1570988263})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 309, 'enemy_armor': '227', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 284, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': '🛡_MrFoxy_🛡', 'photo': None, 'timeUpdate': 1570988286})
# registered_wariors.insert_one({'band': 'Демоны', 'bm': 0, 'damage': 570, 'enemy_armor': '227', 'fraction': '🔪Головорезы', 'goat': 'Бафомет', 'health': 837, 'hithimself': 0, 'kills': 2, 'missed': 0, 'name': 'AKBИЛЛА', 'photo': 'AgADAgADl6sxG-E-IUkZuKJlG104YK_dug8ABAEAAwIAA20AA9W8AwABFgQ', 'timeUpdate': 1570991475})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': 0, 'damage': 0, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Сунь Хуй Вчай ☕️', 'photo': 'AgADAgADFa0xG9X0GUnjJ7upbODhwQ7stw8ABAEAAwIAA20AA3MtBQABFgQ', 'timeUpdate': 1570992735})
# registered_wariors.insert_one({'band': '108 какахи', 'bm': 0, 'damage': 0, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Snake_Dragon', 'photo': 'AgADAgADJK4xGzUvGEmUj_N-NgH6a-_uug8ABAEAAwIAA20AA227AwABFgQ', 'timeUpdate': 1570992668})
# registered_wariors.insert_one({'band': 'сорoк два', 'bm': 0, 'damage': 0, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': '影Kawaii Waifu', 'photo': 'AgADAgADIKwxG-VHcUnR6_HZWc7HQZvttw8ABAEAAwIAA20AA2-jBQABFgQ', 'timeUpdate': 1570996364})
# registered_wariors.insert_one({'band': 'без банды', 'bm': 0, 'damage': 482, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': 747, 'hithimself': 0, 'kills': 4, 'missed': 0, 'name': 'WestMoscow', 'photo': 'AgADAgADxq8xG9-PUUk9tQ7sDkw2q6v8tw8ABAEAAwIAA20AA316BQABFgQ', 'timeUpdate': 1570996633})
# registered_wariors.insert_one({'band': 'Детсад браззерс', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': 'Iamlaserpewpew', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'bramat', 'photo': 'AgADAgADXawxG467QUlYTgSqgHussm_yug8ABAEAAwIAA20AAynnAwABFgQ', 'timeUpdate': 1570996755})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 382, 'enemy_armor': '260', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 876, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Alexandra Lady Keda R12👠', 'photo': None, 'timeUpdate': 1570998088})
# registered_wariors.insert_one({'band': 'сорoк два', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Alexandra Lady Keda R12', 'photo': 'AgADAgADDKwxG3fDIUkGN8Yb4gKc7nnuug8ABAEAAwIAA20AA7m0AwABFgQ', 'timeUpdate': 1570998064})
# registered_wariors.insert_one({'band': 'crewname', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Алексей', 'photo': 'AgADAgADHasxG_UIIEm9tYGbf3mFV2sAAbgPAAQBAAMCAANtAANPKAUAARYE', 'timeUpdate': 1570998559})
# registered_wariors.insert_one({'band': 'Iamlaserpewpew', 'bm': None, 'damage': 492, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': 'Iamlaserpewpew', 'health': 925, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'God_eater_90', 'photo': 'AgADAgADiKwxG9-PQUnqmT4mqmfih43huQ8ABAEAAwIAA20AA34DBAABFgQ', 'timeUpdate': 1570999186})
# registered_wariors.insert_one({'band': 'Москвичи', 'bm': None, 'damage': 40, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 185, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'matthew_grygan', 'photo': 'AgADAgADX6sxG1W8SEnCyZAUDt8w-krqug8ABAEAAwIAA20AA8XvAwABFgQ', 'timeUpdate': 1571003574})
# registered_wariors.insert_one({'band': 'МАЙОНЕЗИК', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'БУТЕРБРОДИК', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'SHEPARD BX', 'photo': 'AgADAgADI6wxGzFqQEkGZ-crUec2pRjsug8ABAEAAwIAA20AA3DyAwABFgQ', 'timeUpdate': 1571004122})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': 417, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 828, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Iulian', 'photo': 'AgADAgAD6qsxG9ElcUmH5Q-VUknO7nnpug8ABAEAAwIAA20AA94hBAABFgQ', 'timeUpdate': 1571005743})
# registered_wariors.insert_one({'band': 'Pro100KAPIBARY', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Pro100KAPIBARY', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Ali', 'photo': 'AgADAgADlasxG_rVGElnA9EFoivPhMziug8ABAEAAwIAA20AA262AwABFgQ', 'timeUpdate': 1571007540})
# registered_wariors.insert_one({'band': 'Iamlaserpewpew', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Iamlaserpewpew', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Reigan', 'photo': 'AgADAgADYawxG2HCIEmnGy5ZoeH_GXDxug8ABAEAAwIAA20AAxK1AwABFgQ', 'timeUpdate': 1571029627})
# registered_wariors.insert_one({'band': 'Артхаус', 'bm': None, 'damage': 252, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 422, 'hithimself': 0, 'kills': 5, 'missed': 0, 'name': 'Титан', 'photo': 'AgADAgADS64xG4ouOEnAw0ebPFvPpvTYtw8ABAEAAwIAA20AA05aBQABFgQ', 'timeUpdate': 1571030201})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 636, 'enemy_armor': '260', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 793, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Lena_volchonok_15', 'photo': None, 'timeUpdate': 1571034487})
# registered_wariors.insert_one({'band': 'Орден Пустоши', 'bm': 0, 'damage': 808, 'enemy_armor': '260', 'fraction': '⚛️Республика', 'goat': 'Каганат ВХ', 'health': 1456, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Georgy', 'photo': 'AgADAgADo6sxG3voIUlklg1IhaMNZormug8ABAEAAwIAA20AA_q8AwABFgQ', 'timeUpdate': 1571037069})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 210, 'enemy_armor': '201', 'fraction': '💣Мегатонна', 'goat': None, 'health': 322, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'HaringtonVl', 'photo': None, 'timeUpdate': 1571037397})
# registered_wariors.insert_one({'band': 'Archam', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'N0nst0p', 'photo': 'AgADAgADJ6sxG5XAIUnuqJz1Rt3LoErmug8ABAEAAwIAA20AA2rBAwABFgQ', 'timeUpdate': 1571037921})
# registered_wariors.insert_one({'band': 'W34W', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Nastya_Jdanova', 'photo': 'AgADAgAD1awxGw9IUUkeZcop6YkOxV3huQ8ABAEAAwIAA20AAykWBAABFgQ', 'timeUpdate': 1571039601})
# registered_wariors.insert_one({'band': 'New Vegas East', 'bm': 0, 'damage': 542, 'enemy_armor': '227', 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': 1231, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Дядя Серёжа ŇṼ', 'photo': 'AgADAgADw6sxGwTHcUnnHn2RbvHCRqF2XA8ABAEAAwIAA20AAxtVAAIWBA', 'timeUpdate': 1571039590})
# registered_wariors.insert_one({'band': 'BNN', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'OrangeKaktus', 'photo': 'AgADAgADrKsxG-drIUneYl7KARTchtfhuQ8ABAEAAwIAA20AAz3NAwABFgQ', 'timeUpdate': 1571041740})
# registered_wariors.insert_one({'band': 'Артхаус', 'bm': None, 'damage': 136, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 150, 'hithimself': 0, 'kills': 2, 'missed': 0, 'name': 'miashas', 'photo': 'AgADAgADvKsxGydKIEkZfYL9fQIOdXXwug8ABAEAAwIAA20AA9q5AwABFgQ', 'timeUpdate': 1571042239})
# registered_wariors.insert_one({'band': 'Выпившие Ханы', 'bm': None, 'damage': 314, 'enemy_armor': '201', 'fraction': '⚛️Республика', 'goat': 'Академия Ханов', 'health': 548, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Stalker26', 'photo': 'AgADAgAD1a0xG33yIEn5gxsYHrulHxTbug8ABAEAAwIAA20AA4W9AwABFgQ', 'timeUpdate': 1571042335})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 343, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 328, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Mikhail_MGO', 'photo': None, 'timeUpdate': 1570752904})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 272, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 710, 'hithimself': 1, 'kills': 0, 'missed': 0, 'name': 'drHeterodox', 'photo': None, 'timeUpdate': 1570752904})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 939, 'enemy_armor': '77', 'fraction': '🔪Головорезы', 'goat': None, 'health': 2269, 'hithimself': 0, 'kills': 3, 'missed': 0, 'name': 'Лютый', 'photo': None, 'timeUpdate': 1571047097})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 335, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 722, 'hithimself': 1, 'kills': 2, 'missed': 1, 'name': 'artiomse', 'photo': None, 'timeUpdate': 1571047097})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 659, 'enemy_armor': '227', 'fraction': '⚛️Республика', 'goat': None, 'health': 928, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Дядя Миша ŇṼ', 'photo': None, 'timeUpdate': 1571048309})
# registered_wariors.insert_one({'band': 'КОЛБАСКА', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'БУТЕРБРОДИК', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Релейщик Нации', 'photo': 'AgADAgADqK0xGzfeIUko44Ptkj0We-oBuA8ABAEAAwIAA20AAz85BQABFgQ', 'timeUpdate': 1571050136})
# registered_wariors.insert_one({'band': 'Артхаус', 'bm': None, 'damage': 415, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 1032, 'hithimself': 1, 'kills': 7, 'missed': 1, 'name': 'Gromnsk', 'photo': 'AgADAgAD_asxG6ebcEmoOVy8aEBlicfYug8ABAEAAwIAA20AA-hBBAABFgQ', 'timeUpdate': 1571039351, 'heakth': 784})
# registered_wariors.insert_one({'band': 'New Vegas North', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Дядя Тёти ŇṼ', 'photo': 'AgADAgAD6KsxG9RXIUmiQu3cuc4gywjdug8ABAEAAwIAA20AAyzBAwABFgQ', 'timeUpdate': 1571051692})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 494, 'enemy_armor': '265', 'fraction': '🔪Головорезы', 'goat': None, 'health': 760, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Brainyak', 'photo': None, 'timeUpdate': 1571051789})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 435, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 854, 'hithimself': 0, 'kills': 2, 'missed': 0, 'name': 'QurReq', 'photo': None, 'timeUpdate': 1571051789})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 465, 'enemy_armor': '270', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 826, 'hithimself': 0, 'kills': 0, 'missed': 2, 'name': 'ИЛЬИЧ', 'photo': None, 'timeUpdate': 1571039958})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 374, 'enemy_armor': '227', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 712, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': '🏎 big_zmei', 'photo': None, 'timeUpdate': 1570794891})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 259, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 357, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Ian_reger', 'photo': None, 'timeUpdate': 1571054496})
# registered_wariors.insert_one({'band': 'без банды', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'WORSA_crew', 'photo': 'AgADAgADZasxG_7IIEm9BbX9xx95GMjmtw8ABAEAAwIAA20AA645BQABFgQ', 'timeUpdate': 1571056002})
# registered_wariors.insert_one({'band': 'hookahplace', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Ruslan_mojo', 'photo': 'AgADAgADnqsxGzo3IEnyHPjdserfm1z4tw8ABAEAAwIAA20AA2kwBQABFgQ', 'timeUpdate': 1571056256})
# registered_wariors.insert_one({'band': 'Великие Ханы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Каганат ВХ', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'N1kAdm1n', 'photo': 'AgADAgAD4qsxG9nzKElFYMUuynEcR-XjuQ8ABAEAAwIAA20AAz_RAwABFgQ', 'timeUpdate': 1571056490})
# registered_wariors.insert_one({'band': 'Москвичи', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Z0HI9GR', 'photo': 'AgADAgADSa0xG6H6KUlV7IdyiXO_Z9nVuQ8ABAEAAwIAA20AA7_dAwABFgQ', 'timeUpdate': 1571054003})
# registered_wariors.insert_one({'band': 'Northern Bears', 'bm': None, 'damage': 113, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'SWAT', 'health': 662, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Dadrok', 'photo': 'AgADAgADQawxGx5DQUkLRlhfOx5mEIfVtw8ABAEAAwIAA20AA25YBQABFgQ', 'timeUpdate': 1571060217})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Филипп', 'photo': 'AgADAgADLawxGydKIEl0Fav2_2tYlZLrtw8ABAEAAwIAA20AAyk5BQABFgQ', 'timeUpdate': 1571067433})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'mkllr', 'photo': 'AgADAgADvKsxG-tgKEk0Oa-XwjG2pdHhuQ8ABAEAAwIAA20AAwvjAwABFgQ', 'timeUpdate': 1571067808})
# registered_wariors.insert_one({'band': 'Выпившие Ханы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Академия Ханов', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Boris the Anial', 'photo': 'AgADAgAD2qsxG0S6KElX3Soi1Dt2x5ztug8ABAEAAwIAA20AA9_DAwABFgQ', 'timeUpdate': 1571071555})
# registered_wariors.insert_one({'band': 'Sons of Владик', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Korwel', 'photo': 'AgADAgAD4qoxGxtrKUlcdz3HAAGyyZKb8LcPAAQBAAMCAANtAAOBQAUAARYE', 'timeUpdate': 1571071545})
# registered_wariors.insert_one({'band': 'crewname', 'bm': None, 'damage': 414, 'enemy_armor': '227', 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Asaelko', 'photo': 'AgADAgADhKwxG5viIElnhuHF1LnR1eMBuA8ABAEAAwIAA20AAyc9BQABFgQ', 'timeUpdate': 1571072922, 'heakth': 665})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Anton', 'photo': 'AgADAgADiawxG5viIEm82U3KPoGxS57eug8ABAEAAwIAA20AA67FAwABFgQ', 'timeUpdate': 1571075784})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 193, 'enemy_armor': '201', 'fraction': '⚛️Республика', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Шипастый Ананас', 'photo': None, 'timeUpdate': 1567360032, 'heakth': 169})
# registered_wariors.insert_one({'band': 'Umbrella Corp', 'bm': 0, 'damage': 630, 'enemy_armor': '260', 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': 1138, 'hithimself': 0, 'kills': 5, 'missed': 0, 'name': 'myakishh', 'photo': 'AgADAgAErDEb8REhSQFBpBRGTA9kQe26DwAEAQADAgADbQADBcUDAAEWBA', 'timeUpdate': 1571082838})
# registered_wariors.insert_one({'band': 'Выпившие Ханы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Академия Ханов', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'БАД ᴮᵡ', 'photo': 'AgADAgADjq0xGwOoIUnHdC3JYINbOVbZtw8ABAEAAwIAA20AA0U-BQABFgQ', 'timeUpdate': 1571087397})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 0, 'enemy_armor': '201', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 0, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'GENTIC', 'photo': None, 'timeUpdate': 1571118861})
# registered_wariors.insert_one({'band': 'Вялые питоны', 'bm': 0, 'damage': 386, 'enemy_armor': '227', 'fraction': '🔪Головорезы', 'goat': 'Pro100KAPIBARY', 'health': 570, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'rotoyo', 'photo': 'AgADAgADz6wxG4mjOUmUUx6TWs2WkGLutw8ABAEAAwIAA20AA-JeBQABFgQ', 'timeUpdate': 1571131931})
# registered_wariors.insert_one({'band': 'сорок два', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'boshenika', 'photo': 'AgADAgADN6sxG9tYMEl9MjubXkSovWr1tw8ABAEAAwIAA20AAx9IBQABFgQ', 'timeUpdate': 1571132121})
# registered_wariors.insert_one({'band': 'Волчий отряд', 'bm': None, 'damage': None, 'enemy_armor': '227', 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': 200, 'hithimself': 0, 'kills': 0, 'missed': 1, 'name': 'Арес', 'photo': 'AgADAgAD76sxG9BWMUktJKccpriTqpTytw8ABAEAAwIAA20AA-pJBQABFgQ', 'timeUpdate': 1571132116})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 191, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 924, 'hithimself': 1, 'kills': 5, 'missed': 0, 'name': 'NiceTry_noCigar', 'photo': None, 'timeUpdate': 1571132948})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 663, 'enemy_armor': '270', 'fraction': '🔪Головорезы', 'goat': None, 'health': 1175, 'hithimself': 0, 'kills': 2, 'missed': 0, 'name': 'АдмиралГенерал', 'photo': None, 'timeUpdate': 1571132948})
# registered_wariors.insert_one({'band': 'без банды', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'WildFire112', 'photo': 'AgADAgADo6sxG3VJKUlBvvPjXQhkIyHWtw8ABAEAAwIAA20AAxpPBQABFgQ', 'timeUpdate': 1571134354})
# registered_wariors.insert_one({'band': 'Топ Дево4ки', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'SWAT', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Sorandd', 'photo': 'AgADAgAD9KsxG2GnMEnXwxAMqZSjV_jLuQ8ABAEAAwIAA20AA3vjAwABFgQ', 'timeUpdate': 1571134375})
# registered_wariors.insert_one({'band': 'crewname', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Scorpells', 'photo': 'AgADAgADDawxG1g5KEkkDbk220ABQInLuQ8ABAEAAwIAA20AAxLiAwABFgQ', 'timeUpdate': 1571134743})
# registered_wariors.insert_one({'band': 'Ларец Gang', 'bm': None, 'damage': 418, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'БУТЕРБРОДИК', 'health': 401, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Shinigami', 'photo': 'AgADAgADj60xG61MKEl74XVV1Bc8fkrhtw8ABAEAAwIAA20AA2RJBQABFgQ', 'timeUpdate': 1571134817})
# registered_wariors.insert_one({'band': 'New Vegas North', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Toli4RUS ŇṼ', 'photo': 'AgADAgADR6sxG4ggQUm7-Ll4EBW_xdXMtw8ABAEAAwIAA20AA55hBQABFgQ', 'timeUpdate': 1571135186})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 108, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 169, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'AlluZef', 'photo': None, 'timeUpdate': 1571135400})
# registered_wariors.insert_one({'band': 'Kykyryza', 'bm': None, 'damage': 328, 'enemy_armor': '167', 'fraction': '🔪Головорезы', 'goat': None, 'health': 529, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Vasstin', 'photo': 'AgADAgAD96sxG4SSMUnMqDpyK-m3LI_dtw8ABAEAAwIAA20AA-BBBQABFgQ', 'timeUpdate': 1571136422})
# registered_wariors.insert_one({'band': '1 Ударный Корпус', 'bm': None, 'damage': 452, 'enemy_armor': '227', 'fraction': '⚛️Республика', 'goat': 'Академия Ханов', 'health': 568, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Смертник', 'photo': 'AgADAgAD86sxGzn_MEmgFfOHLUAfYG7kug8ABAEAAwIAA20AA3PXAwABFgQ', 'timeUpdate': 1571136629})
# registered_wariors.insert_one({'band': 'Вялые питоны', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Pro100KAPIBARY', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Аяно', 'photo': 'AgADAgADDq0xG1dIKUlJ1X6o4pyrogwCuA8ABAEAAwIAA20AA15DBQABFgQ', 'timeUpdate': 1571140595})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 420, 'enemy_armor': '227', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 416, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Radzhiv', 'photo': None, 'timeUpdate': 1571142070})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 277, 'enemy_armor': '167', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 393, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'M242434', 'photo': None, 'timeUpdate': 1571146686})
# registered_wariors.insert_one({'band': 'Ленинцы', 'bm': None, 'damage': 482, 'enemy_armor': '260', 'fraction': '💣Мегатонна', 'goat': 'Iamlaserpewpew', 'health': 596, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Denis', 'photo': 'AgADAgADA60xG78RMUkUPSs7Q4IIC3Tvtw8ABAEAAwIAA20AA4pJBQABFgQ', 'timeUpdate': 1571150324})
# registered_wariors.insert_one({'band': 'New Vegas North', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Kopрoзия', 'photo': 'AgADAgAD2KwxG1dIMUmBphAl14pflyHNtw8ABAEAAwIAA20AA1lLBQABFgQ', 'timeUpdate': 1571158515})
# registered_wariors.insert_one({'band': 'МАЙОНЕЗИК', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'БУТЕРБРОДИК', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'EBASOS DESTROYER', 'photo': 'AgADAgADv6sxG5qdWUlEY9zlm3SGo_Xhug8ABAEAAwIAA20AAw4OBAABFgQ', 'timeUpdate': 1571159878})
# registered_wariors.insert_one({'band': 'Звёздочки', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'VI_TALIK', 'photo': 'AgADAgAD46wxG6H6MUmynChI9IXAQ7p4XA8ABAEAAwIAA20AA08BAAIWBA', 'timeUpdate': 1571161056})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Вова', 'photo': 'AgADAgAD-KwxG6H6MUlArw7HfB0-xmLwug8ABAEAAwIAA20AA97XAwABFgQ', 'timeUpdate': 1571163270})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'ホЛисоедツ', 'photo': 'AgADAgAD5KwxG0ZtMUnR9CqYE3bZgcTMtw8ABAEAAwIAA20AA11VBQABFgQ', 'timeUpdate': 1571163877})
# registered_wariors.insert_one({'band': '42 Nuclear', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'deder_ua', 'photo': 'AgADAgADjKsxG2PpMEnOoGzhmz2QBtrSuQ8ABAEAAwIAA20AA9PqAwABFgQ', 'timeUpdate': 1571164485})
# registered_wariors.insert_one({'band': 'Memento Mori', 'bm': 0, 'damage': 240, 'enemy_armor': '270', 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 115, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'PainAndHatred', 'photo': 'AgADAgADHqwxGxDoWUn5uRrZal2fzSn4tw8ABAEAAwIAA20AAzF6BQABFgQ', 'timeUpdate': 1571166475})
# registered_wariors.insert_one({'band': 'New Vegas North', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'GeneralGinger ŇṼ', 'photo': 'AgADAgAD06sxG6ebcEn-R3y-uv6Vy_Dqtw8ABAEAAwIAA20AA-ybBQABFgQ', 'timeUpdate': 1571178307})
# registered_wariors.insert_one({'band': 'сорoк два', 'bm': None, 'damage': 624, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': 589, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Airdispatcher', 'photo': 'AgADAgADC60xG3-mOUmVbv7_JJI9MXzbug8ABAEAAwIAA20AA0jiAwABFgQ', 'timeUpdate': 1571205925})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 664, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 1194, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'sshilin', 'photo': None, 'timeUpdate': 1571174429})
# registered_wariors.insert_one({'band': 'Туннельные змеи', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Pro100KAPIBARY', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Laughing_Bright', 'photo': 'AgADAgADzqwxG1CWMUmo3r0BnMR7FTjSuQ8ABAEAAwIAA20AAyHwAwABFgQ', 'timeUpdate': 1571212089})
# registered_wariors.insert_one({'band': 'Ларец Gang', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'БУТЕРБРОДИК', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Время пить чай', 'photo': 'AgADAgADz6sxG4tBOEno4SU6yPrFRGLvtw8ABAEAAwIAA20AA-tZBQABFgQ', 'timeUpdate': 1571212246})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 702, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 960, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': '𝕹𝖎𝖌𝖍𝖙 𝖇𝖊𝖆𝖘𝖙', 'photo': None, 'timeUpdate': 1571216376})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 465, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 959, 'hithimself': 0, 'kills': 3, 'missed': 0, 'name': 'Retif77', 'photo': None, 'timeUpdate': 1571222056})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 586, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 1062, 'hithimself': 0, 'kills': 4, 'missed': 0, 'name': 'Kolder112', 'photo': None, 'timeUpdate': 1571226791})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 435, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 899, 'hithimself': 0, 'kills': 2, 'missed': 0, 'name': 'Дмитрий', 'photo': None, 'timeUpdate': 1571238043})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 755, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 883, 'hithimself': 1, 'kills': 1, 'missed': 0, 'name': 'LikeSmile', 'photo': None, 'timeUpdate': 1571238043})
# registered_wariors.insert_one({'band': 'Ленивки', 'bm': None, 'damage': 280, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 495, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Молчун', 'photo': 'AgADAgADQawxG4QnOEl1MbdnOUOVMQllXA8ABAEAAwIAA20AA4UNAAIWBA', 'timeUpdate': 1571240759})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 426, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 442, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Красивое Имя', 'photo': None, 'timeUpdate': 1571241226})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 224, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 506, 'hithimself': 0, 'kills': 1, 'missed': 1, 'name': 'XxXJAGAXxX', 'photo': None, 'timeUpdate': 1571242571})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 882, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 1920, 'hithimself': 0, 'kills': 3, 'missed': 0, 'name': '🌚 PoT3akpou ŇṼ', 'photo': None, 'timeUpdate': 1571242344})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 871, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 842, 'hithimself': 0, 'kills': 3, 'missed': 0, 'name': 'ХопХейЛалаей ŇṼ', 'photo': None, 'timeUpdate': 1571245154})
# registered_wariors.insert_one({'band': 'Волчий отряд', 'bm': None, 'damage': 253, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': 663, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Пивло', 'photo': 'AgADAgADwqwxG4mjOUmoLNGA-UTBE0Xwug8ABAEAAwIAA20AA5PsAwABFgQ', 'timeUpdate': 1571246086})
# registered_wariors.insert_one({'band': 'ПОМИДОРКА', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'БУТЕРБРОДИК', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'player1993', 'photo': 'AgADAgADa6wxGyg_OEk0-9-GydFKzxHQug8ABAEAAwIAA20AA5j2AwABFgQ', 'timeUpdate': 1571248157})
# registered_wariors.insert_one({'band': '42 Кромбопулуса', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Viking', 'photo': 'AgADAgADBawxGyXnOUmOsFHMUKnLjEHnug8ABAEAAwIAA20AA1XeAwABFgQ', 'timeUpdate': 1571249401})
# registered_wariors.insert_one({'band': 'Жнецы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Бафомет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Mei_Ling_Zhou', 'photo': 'AgADAgAD36sxG-_iOUnnx_wddxHQBJzZuQ8ABAEAAwIAA20AA_bzAwABFgQ', 'timeUpdate': 1571249992})
# registered_wariors.insert_one({'band': 'Марипоза', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Каганат ВХ', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'trueflawy', 'photo': 'AgADAgADgKsxG899cUmrh5FDSeV0zO5lXA8ABAEAAwIAA20AA39VAAIWBA', 'timeUpdate': 1571252607})
# registered_wariors.insert_one({'band': 'BisNovaNatus', 'bm': None, 'damage': 695, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': 1059, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Blackprincer', 'photo': 'AgADAgADWawxG1CWOUkRKWEMhfJkbszbuQ8ABAEAAwIAA20AA834AwABFgQ', 'timeUpdate': 1571259533})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 765, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 1189, 'hithimself': 0, 'kills': 3, 'missed': 0, 'name': 'ησλყღթak', 'photo': None, 'timeUpdate': 1571282978})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 548, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 1032, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'oxwordmc', 'photo': None, 'timeUpdate': 1571291853})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 339, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 679, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'mFrolov', 'photo': None, 'timeUpdate': 1571294392})
# registered_wariors.insert_one({'band': 'Panamera', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'big_zmei', 'photo': 'AgADAgADkasxGynmSUmScAr0RKiBUfn9tw8ABAEAAwIAA20AA4VjBQABFgQ', 'timeUpdate': 1571297463})
# registered_wariors.insert_one({'band': 'сорок два', 'bm': None, 'damage': 317, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Сорок два', 'health': 458, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'lisfi', 'photo': 'AgADAgADpqsxG-NJaElI52ky1n86Rirgug8ABAEAAwIAA20AA-4kBAABFgQ', 'timeUpdate': 1571297796})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 762, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 1131, 'hithimself': 3, 'kills': 3, 'missed': 0, 'name': 'Тайпан Жестокая', 'photo': None, 'timeUpdate': 1571302865})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 808, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 1545, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Shkvarkoman', 'photo': None, 'timeUpdate': 1571303211})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 924, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 316, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': '\U0001f92cEBASOS DESTROYER', 'photo': None, 'timeUpdate': 1571304248})
# registered_wariors.insert_one({'band': 'BisNovaNatus', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Дикий Ежик', 'photo': 'AgADAgADg6sxG2xYSEnGX2OpF7sIGETstw8ABAEAAwIAA20AA4toBQABFgQ', 'timeUpdate': 1571308363})
# registered_wariors.insert_one({'band': 'Old School', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'ホ Lorenser ツ', 'photo': 'AgADAgADL6wxGzibSUk9dV55-kPN2srKtw8ABAEAAwIAA20AA7NjBQABFgQ', 'timeUpdate': 1571313565})
# registered_wariors.insert_one({'band': 'Динисторы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Nevi"Dimka\'\'', 'photo': 'AgADAgAErDEbbFhISTUPtIlblLngr9G5DwAEAQADAgADbQADdgoEAAEWBA', 'timeUpdate': 1571331789})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'HanTru', 'photo': 'AgADAgADcqsxG1W8SEnWp_rm-P3k1Pfrtw8ABAEAAwIAA20AAxFrBQABFgQ', 'timeUpdate': 1571345197})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 504, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 593, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Ghost👻', 'photo': None, 'timeUpdate': 1571345851})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Степ Нации', 'photo': 'AgADAgADaasxG3aHUUnF5ha8lPaARgjZug8ABAEAAwIAA20AAxMMBAABFgQ', 'timeUpdate': 1571385002})
# registered_wariors.insert_one({'band': 'Ковен', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'Бафомет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Mironische1', 'photo': 'AgADAgADJK0xG467SUmQph-Hiozdh8pfXA8ABAEAAwIAA20AA5ghAAIWBA', 'timeUpdate': 1571384988})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Dmitriy', 'photo': 'AgADAgADZqwxG_l5SUkD46dl0VYlx6B0XA8ABAEAAwIAA20AA6kgAAIWBA', 'timeUpdate': 1571384983})
# registered_wariors.insert_one({'band': 'Демоны', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'Бафомет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Sshiki', 'photo': 'AgADAgADh6sxG0ExSUmYTAE0E1z8-uvZuQ8ABAEAAwIAA20AA8AMBAABFgQ', 'timeUpdate': 1571384975})
# registered_wariors.insert_one({'band': 'Демоны', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'Бафомет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Hououin Kyouma', 'photo': 'AgADAgADbKsxG3aHUUnWu33R4V1nyc0AAbgPAAQBAAMCAANtAAOGawUAARYE', 'timeUpdate': 1571387332})
# registered_wariors.insert_one({'band': 'КОЛБАСКА', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'БУТЕРБРОДИК', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Дeнчик', 'photo': 'AgADAgAD46wxG64AAVBJ_SY7-mx5KlwE6roPAAQBAAMCAANtAAPg-gMAARYE', 'timeUpdate': 1571394177})
# registered_wariors.insert_one({'band': 'Еретики', 'bm': None, 'damage': 469, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': 'Бафомет', 'health': 686, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Электрофорез', 'photo': 'AgADAgAD5KwxG64AAVBJMs15WzkKTG6F97cPAAQBAAMCAANtAAO3aQUAARYE', 'timeUpdate': 1571394195})
# registered_wariors.insert_one({'band': 'Panamera', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Владимир', 'photo': 'AgADAgADLasxG-u0UUkpvuYnUq9qDePlug8ABAEAAwIAA20AA-ADBAABFgQ', 'timeUpdate': 1571396898})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 154, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 547, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Твоя Паранойя', 'photo': None, 'timeUpdate': 1571398301})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 103, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 343, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Pavel Gus ŇṼ', 'photo': None, 'timeUpdate': 1571399473})
# registered_wariors.insert_one({'band': 'Волчий отряд', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'New Vegas', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Tanelda', 'photo': 'AgADAgADvKwxG2xYUEnT4B1wJ7bg0DHwug8ABAEAAwIAA20AA5v_AwABFgQ', 'timeUpdate': 1571405244})
# registered_wariors.insert_one({'band': 'Потомки Oгня', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': 'Академия Ханов', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Nyaaka', 'photo': 'AgADAgADna8xG9-PUUn1j7Y10OvGtr7guQ8ABAEAAwIAA20AAykVBAABFgQ', 'timeUpdate': 1571406884})
# registered_wariors.insert_one({'band': 'Жнецы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'Бафомет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Шусрик', 'photo': 'AgADAgADe6wxGwPJSUmRZQiaaDthSTTtug8ABAEAAwIAA20AA1QCBAABFgQ', 'timeUpdate': 1571411969})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 893, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 610, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Тρąп Нãцūū', 'photo': None, 'timeUpdate': 1571414180})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 586, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 1317, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Esperansa', 'photo': None, 'timeUpdate': 1571417234})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 561, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 655, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Жаксон', 'photo': None, 'timeUpdate': 1571417981})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 218, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 238, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Press F to PR', 'photo': None, 'timeUpdate': 1571418506})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 832, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 1318, 'hithimself': 0, 'kills': 1, 'missed': 1, 'name': 'dannerinho', 'photo': None, 'timeUpdate': 1571418768})
# registered_wariors.insert_one({'band': 'Туннельные змеи', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Pro100KAPIBARY', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'BoogieMan75', 'photo': 'AgADAgADNK4xG3bJUEkSiO8rUQzd1Oj7tw8ABAEAAwIAA20AAzd1BQABFgQ', 'timeUpdate': 1571419266})
# registered_wariors.insert_one({'band': 'Жнецы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'Бафомет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Авиатор Нации', 'photo': 'AgADAgADy6wxG-u1UUm7aA2X95-ei8ZwXA8ABAEAAwIAA20AA6MpAAIWBA', 'timeUpdate': 1571419332})
# registered_wariors.insert_one({'band': 'Ларец Gang', 'bm': None, 'damage': 336, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'БУТЕРБРОДИК', 'health': 25, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Bogdan', 'photo': 'AgADAgADBK0xG4HCUUlUEoFdTQIhySvtug8ABAEAAwIAA20AAycCBAABFgQ', 'timeUpdate': 1571423856})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 375, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 657, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Rushka', 'photo': None, 'timeUpdate': 1571421705})
# registered_wariors.insert_one({'band': 'Pro100KAPIBARY', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Pro100KAPIBARY', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': '4r3nchbr3ad', 'photo': 'AgADAgAD26sxG4SUUUmqKzhEF34AAY3U1rkPAAQBAAMCAANtAAN9FQQAARYE', 'timeUpdate': 1571431740})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 498, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 915, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'AНОНИMНЫЙ AЛKAШ', 'photo': None, 'timeUpdate': 1571469914})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'WisJG', 'photo': 'AgADAgADyKsxG-44WUk7rJv-UW0VjAbNtw8ABAEAAwIAA20AA4J3BQABFgQ', 'timeUpdate': 1571481132})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 0, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 213, 'hithimself': 2, 'kills': 0, 'missed': 0, 'name': '𝐁𝐥𝐚𝐜𝐤𝐒𝐏𝐞𝐞𝐃', 'photo': None, 'timeUpdate': 1571488165})
# registered_wariors.insert_one({'band': 'Вялые питоны', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Pro100KAPIBARY', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': '@BlackSPeeD_L', 'photo': 'AgADAgADc6wxGyZzWEmFx-4-C8ChW6Llug8ABAEAAwIAA20AA-ESBAABFgQ', 'timeUpdate': 1571488108})
# registered_wariors.insert_one({'band': 'Энтропия', 'bm': None, 'damage': 277, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 553, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Innok27', 'photo': 'AgADAgAD-qsxG-VFWElujyjJqpR9WoPSuQ8ABAEAAwIAA20AA3cUBAABFgQ', 'timeUpdate': 1571490868})
# registered_wariors.insert_one({'band': 'β Ti3Au Виверны', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': 'β Ti3Au Виверны', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Marlboro', 'photo': 'AgADAgAD-6sxG5lEUEkCiYvlwZ8-IcwAAbgPAAQBAAMCAANtAAMceAUAARYE', 'timeUpdate': 1571493235})
# registered_wariors.insert_one({'band': 'Umbrella Corp', 'bm': None, 'damage': 413, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': 894, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'lopastik', 'photo': 'AgADAgAD56sxG6lUWUleTuojLLebT8VjXA8ABAEAAwIAA20AAxY1AAIWBA', 'timeUpdate': 1571494734})
# registered_wariors.insert_one({'band': 'Демоны', 'bm': 0, 'damage': 992, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Бафомет', 'health': 1049, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Ivan', 'photo': 'AgADAgADGq0xG3bFWEmp4yy4eoJk9Tt-XA8ABAEAAwIAA20AA881AAIWBA', 'timeUpdate': 1571499541})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 755, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 74, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': '𝖘𝖆𝖘𝖙𝖊𝖗 𝖓𝖛', 'photo': None, 'timeUpdate': 1571501795})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 592, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 919, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Ogre ВХ', 'photo': None, 'timeUpdate': 1571512176})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 229, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 369, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'өлім әкелетін', 'photo': None, 'timeUpdate': 1571517488})
# registered_wariors.insert_one({'band': 'Москвичи', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Hellshit666', 'photo': 'AgADAgADrqwxGwHRWUn7srpVNep4Irzqtw8ABAEAAwIAA20AA1KDBQABFgQ', 'timeUpdate': 1571553883})
# registered_wariors.insert_one({'band': 'New Vegas East', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': 'New Vegas', 'health': None, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'D1SKR1 ŇṼ', 'photo': 'AgADAgAD5KsxGw9IYUm70jvOawczxebUug8ABAEAAwIAA20AA04lBAABFgQ', 'timeUpdate': 1571558864})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 161, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 355, 'hithimself': 0, 'kills': 2, 'missed': 0, 'name': 'Golodniy', 'photo': None, 'timeUpdate': 1571568146})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 631, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 1388, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Дядя gakatas ŇṼ', 'photo': None, 'timeUpdate': 1571591785})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 122, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 151, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'iojigg', 'photo': None, 'timeUpdate': 1571594502})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Недокинь', 'photo': 'AgADAgAD_qsxG_5faUn49t70mpZQm-nrug8ABAEAAwIAA20AAzMcBAABFgQ', 'timeUpdate': 1571608800})
# registered_wariors.insert_one({'band': 'crewname', 'bm': 0, 'damage': 132, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': 117, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'forest', 'photo': 'AgADAgADsqwxG2D2cEnb1P5luZbddITItw8ABAEAAwIAA20AA1OdBQABFgQ', 'timeUpdate': 1571567352})
# registered_wariors.insert_one({'band': 'Old School', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'KierkegaardCreed', 'photo': 'AgADAgADvqwxG-HLYEmuqGTxd3WTeWN1XA8ABAEAAwIAA20AAwxIAAIWBA', 'timeUpdate': 1571636849})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 429, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': 793, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'B0oka', 'photo': None, 'timeUpdate': 1571638996})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 214, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 111, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Оценочка', 'photo': None, 'timeUpdate': 1571653572})
# registered_wariors.insert_one({'band': 'Великие Ханы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Каганат ВХ', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'ПьяныйРомантик', 'photo': 'AgADAgADLK4xGzA7aEndtIaVsqunCoL6tw8ABAEAAwIAA20AA4qYBQABFgQ', 'timeUpdate': 1571670404})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 72, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 260, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'srachello', 'photo': None, 'timeUpdate': 1571671614})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Ερετικ Ηαμιι', 'photo': 'AgADAgADpqsxGwTHcUmyPWnnlhDjF6D8tw8ABAEAAwIAA20AAyGjBQABFgQ', 'timeUpdate': 1571677964})
# registered_wariors.insert_one({'band': 'Марипоза', 'bm': None, 'damage': 828, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Каганат ВХ', 'health': 818, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Tipun', 'photo': 'AgADAgADKKwxGwMgcUnG1y6HO2rXlcTntw8ABAEAAwIAA20AA7GfBQABFgQ', 'timeUpdate': 1571679883})
# registered_wariors.insert_one({'band': 'Жнецы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'Бафомет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': '@Alex_Fenya', 'photo': 'AgADAgADq6sxGwTHcUl_GvAp49mX92d-XA8ABAEAAwIAA20AA6FUAAIWBA', 'timeUpdate': 1571681882})
# registered_wariors.insert_one({'band': 'сорок два', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Машенька', 'photo': 'AgADAgADP6wxGwZhaEmXXGvHRz6m1FfQuQ8ABAEAAwIAA20AA7pDBAABFgQ', 'timeUpdate': 1571682056})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 1062, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': None, 'health': 2400, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Rizasto BX', 'photo': None, 'timeUpdate': 1571683214})
# registered_wariors.insert_one({'band': 'Восставшие Ханы', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚛️Республика', 'goat': 'Каганат ВХ', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Troynik BX', 'photo': 'AgADAgADG6wxG9ElcUmd5rUjAAF8Dh6dzbkPAAQBAAMCAANtAAOnQwQAARYE', 'timeUpdate': 1571687040})
# registered_wariors.insert_one({'band': 'Panamera', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': 'Ангирский Совет', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Greifeld', 'photo': 'AgADAgADxKsxGwTHcUlTzK0X9XaM1RLmug8ABAEAAwIAA20AAxgoBAABFgQ', 'timeUpdate': 1571687487})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'ALT', 'photo': 'AgADAgADpq0xG4AJcUkvMo0_dJuSNPJ5XA8ABAEAAwIAA20AA_pXAAIWBA', 'timeUpdate': 1571694593})
# registered_wariors.insert_one({'band': 'без банды', 'bm': None, 'damage': None, 'enemy_armor': None, 'fraction': '💣Мегатонна', 'goat': 'faggoat', 'health': None, 'hithimself': None, 'kills': None, 'missed': None, 'name': 'Настя', 'photo': 'AgADAgADpqwxG29jcUlGj_WP46P5bnTLtw8ABAEAAwIAA20AAw2eBQABFgQ', 'timeUpdate': 1571696519})
# registered_wariors.insert_one({'band': 'NO_BAND', 'bm': None, 'damage': 31, 'enemy_armor': None, 'fraction': '⚙️Убежище 4', 'goat': None, 'health': 120, 'hithimself': 0, 'kills': 0, 'missed': 0, 'name': 'Gewells', 'photo': 'AgADAgAD_6wxG7grcUmAPR7CPy3i9Vd6XA8ABAEAAwIAA20AAw9WAAIWBA', 'timeUpdate': 1571698389})
# registered_wariors.insert_one({'band': None, 'bm': 0, 'damage': 448, 'enemy_armor': None, 'fraction': '🔪Головорезы', 'goat': None, 'health': 392, 'hithimself': 0, 'kills': 1, 'missed': 0, 'name': 'Paul', 'photo': None, 'timeUpdate': 1571731227})

print("#==========================#")              
print("#         BATTLE           #")              
print("#==========================#")
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571236203.272932, 'winnerWarior': 'Kolder112', 'loseWarior': 'NiceTry_noCigar'})
# battle.insert_one({'login': 'NorthDragoN', 'date': 1571238354.116366, 'winnerWarior': 'LikeSmile', 'loseWarior': 'Дмитрий'})
# battle.insert_one({'login': 'Art_Zank', 'date': 1571239503.401004, 'winnerWarior': 'Lidsky', 'loseWarior': 'Dadrok'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571241267.46355, 'winnerWarior': 'Красивое Имя', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571242662.391866, 'winnerWarior': 'XxXJAGAXxX', 'loseWarior': 'Титан'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571246231.338308, 'winnerWarior': 'ХопХейЛалаей ŇṼ', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571246262.89254, 'winnerWarior': '🌚 PoT3akpou ŇṼ', 'loseWarior': 'Arkа'})
# battle.insert_one({'login': 'artiomse', 'date': 1571246683.717642, 'winnerWarior': 'artiomse', 'loseWarior': 'Пивло'})
# battle.insert_one({'login': 'artiomse', 'date': 1571250567.189881, 'winnerWarior': 'rotoyo', 'loseWarior': 'artiomse'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571283241.35779, 'winnerWarior': 'ησλყღթak', 'loseWarior': 'Gromnsk'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571291866.702269, 'winnerWarior': 'oxwordmc', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571294426.641811, 'winnerWarior': 'Кирилл', 'loseWarior': 'mFrolov'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571297845.994525, 'winnerWarior': 'Кирилл', 'loseWarior': 'lisfi'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571301628.897026, 'winnerWarior': 'Кирилл', 'loseWarior': 'Dadrok'})
# battle.insert_one({'login': 'NorthDragoN', 'date': 1571302888.80073, 'winnerWarior': 'Дмитрий', 'loseWarior': 'Тайпан Жестокая'})
# battle.insert_one({'login': 'QurReq', 'date': 1571303310.326101, 'winnerWarior': 'Shkvarkoman', 'loseWarior': 'QurReq'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571304323.605605, 'winnerWarior': '\U0001f92cEBASOS DESTROYER', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571305750.875265, 'winnerWarior': 'myakishh', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571311790.399244, 'winnerWarior': 'Лютый', 'loseWarior': 'Arkа'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571321195.575356, 'winnerWarior': 'Arkа', 'loseWarior': 'God_eater_90'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571337202.757966, 'winnerWarior': 'WestMoscow', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571345863.393463, 'winnerWarior': 'Ghost👻', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'olehme', 'date': 1571388507.11234, 'winnerWarior': 'I7cux37', 'loseWarior': 'olehme'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571388859.321401, 'winnerWarior': 'WestMoscow', 'loseWarior': 'Gromnsk'})
# battle.insert_one({'login': 'Art_Zank', 'date': 1571390866.234456, 'winnerWarior': 'Lidsky', 'loseWarior': 'lisfi'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571394417.017029, 'winnerWarior': 'Arkа', 'loseWarior': 'Электрофорез'})
# battle.insert_one({'login': 'artiomse', 'date': 1571394705.584076, 'winnerWarior': 'Iulian', 'loseWarior': 'artiomse'})
# battle.insert_one({'login': 'NiceTry_noCigar', 'date': 1571398323.176977, 'winnerWarior': 'NiceTry_noCigar', 'loseWarior': 'Твоя Паранойя'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571398998.637975, 'winnerWarior': 'Gromnsk', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'NiceTry_noCigar', 'date': 1571399486.483291, 'winnerWarior': 'NiceTry_noCigar', 'loseWarior': 'Pavel Gus ŇṼ'})
# battle.insert_one({'login': 'NiceTry_noCigar', 'date': 1571399982.24335, 'winnerWarior': 'АдмиралГенерал', 'loseWarior': 'NiceTry_noCigar'})
# battle.insert_one({'login': 'Art_Zank', 'date': 1571408101.293235, 'winnerWarior': 'WestMoscow', 'loseWarior': 'Lidsky'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571414216.847867, 'winnerWarior': 'Тρąп Нãцūū', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'olehme', 'date': 1571415952.182019, 'winnerWarior': 'Radzhiv', 'loseWarior': 'olehme'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571417279.809443, 'winnerWarior': 'Esperansa', 'loseWarior': 'Gromnsk'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571418002.558206, 'winnerWarior': 'Жаксон', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571418526.410768, 'winnerWarior': 'Press F to PR', 'loseWarior': 'Титан'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571418795.449643, 'winnerWarior': 'dannerinho', 'loseWarior': 'Arkа'})
# battle.insert_one({'login': 'NorthDragoN', 'date': 1571423949.451073, 'winnerWarior': 'Дмитрий', 'loseWarior': 'Bogdan'})
# battle.insert_one({'login': 'artiomse', 'date': 1571429065.083805, 'winnerWarior': 'Rushka', 'loseWarior': 'artiomse'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571466476.560115, 'winnerWarior': 'Ирина', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'artiomse', 'date': 1571471336.57303, 'winnerWarior': 'AНОНИMНЫЙ AЛKAШ', 'loseWarior': 'artiomse'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571488029.938795, 'winnerWarior': 'Титан', 'loseWarior': 'PainAndHatred'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571488177.778314, 'winnerWarior': 'Титан', 'loseWarior': '𝐁𝐥𝐚𝐜𝐤𝐒𝐏𝐞𝐞𝐃'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571494934.09816, 'winnerWarior': 'Arkа', 'loseWarior': 'lopastik'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571561981.966616, 'winnerWarior': 'Ivan', 'loseWarior': 'Arkа'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571561997.515785, 'winnerWarior': 'Retif77', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571561998.394179, 'winnerWarior': 'Gromnsk', 'loseWarior': '𝖘𝖆𝖘𝖙𝖊𝖗 𝖓𝖛'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571562042.280725, 'winnerWarior': 'Дядя Duck ŇṼ', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571562042.550285, 'winnerWarior': 'Gromnsk', 'loseWarior': 'Молчун'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571562042.799884, 'winnerWarior': 'Arkа', 'loseWarior': 'Ogre ВХ'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571562043.785888, 'winnerWarior': 'өлім әкелетін', 'loseWarior': 'Титан'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571562045.388504, 'winnerWarior': 'ησλყღթak', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571588872.364745, 'winnerWarior': 'Тайпан Жестокая', 'loseWarior': 'Gromnsk'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571588873.879147, 'winnerWarior': 'Gromnsk', 'loseWarior': 'Молчун'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571591160.46994, 'winnerWarior': 'Golodniy', 'loseWarior': 'Титан'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571592507.680193, 'winnerWarior': 'Gromnsk', 'loseWarior': 'Молчун'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571592508.79029, 'winnerWarior': 'Тайпан Жестокая', 'loseWarior': 'Gromnsk'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571600637.923915, 'winnerWarior': 'Тайпан Жестокая', 'loseWarior': 'Gromnsk'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571600637.932114, 'winnerWarior': 'Gromnsk', 'loseWarior': 'Молчун'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571600639.423207, 'winnerWarior': 'Golodniy', 'loseWarior': 'Титан'})
# battle.insert_one({'login': 'QurReq', 'date': 1571601873.626607, 'winnerWarior': 'QurReq', 'loseWarior': 'Дядя Duck ŇṼ'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571601877.233854, 'winnerWarior': 'Дядя gakatas ŇṼ', 'loseWarior': 'Arkа'})
# battle.insert_one({'login': 'AlluZef', 'date': 1571601881.293685, 'winnerWarior': 'iojigg', 'loseWarior': 'AlluZef'})
# battle.insert_one({'login': 'miashas', 'date': 1571602303.540317, 'winnerWarior': 'miashas', 'loseWarior': 'matthew_grygan'})
# battle.insert_one({'login': 'miashas', 'date': 1571634704.01879, 'winnerWarior': 'miashas', 'loseWarior': 'forest'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571639136.213481, 'winnerWarior': 'lisfi', 'loseWarior': 'Титан'})
# battle.insert_one({'login': 'B0oka', 'date': 1571640015.735503, 'winnerWarior': 'ησλყღթak', 'loseWarior': 'B0oka'})
# battle.insert_one({'login': 'Innok27', 'date': 1571653581.09087, 'winnerWarior': 'Innok27', 'loseWarior': 'Оценочка'})
# battle.insert_one({'login': 'B0oka', 'date': 1571653667.439713, 'winnerWarior': 'B0oka', 'loseWarior': 'Dadrok'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571661326.260294, 'winnerWarior': 'Титан', 'loseWarior': 'Sovertkov'})
# battle.insert_one({'login': 'Dostoevskiy_Fedor', 'date': 1571671683.393446, 'winnerWarior': 'Титан', 'loseWarior': 'srachello'})
# battle.insert_one({'login': 'Gromnsk', 'date': 1571677933.728699, 'winnerWarior': 'myakishh', 'loseWarior': 'Gromnsk'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571680703.990718, 'winnerWarior': 'Tipun', 'loseWarior': 'Arkа'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571680978.56388, 'winnerWarior': 'Retif77', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571683234.022072, 'winnerWarior': 'Rizasto BX', 'loseWarior': 'Arkа'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571687125.750976, 'winnerWarior': 'Kolder112', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'AlluZef', 'date': 1571698461.801531, 'winnerWarior': 'AlluZef', 'loseWarior': 'Gewells'})
# battle.insert_one({'login': 'XyTop_2', 'date': 1571719661.248371, 'winnerWarior': 'Arkа', 'loseWarior': 'Дядя Divnaia ŇṼ'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571725716.759968, 'winnerWarior': 'WestMoscow', 'loseWarior': 'Кирилл'})
# battle.insert_one({'login': 'artiomse', 'date': 1571726924.54427, 'winnerWarior': 'Shinigami', 'loseWarior': 'artiomse'})
# battle.insert_one({'login': 'artiomse', 'date': 1571731243.09857, 'winnerWarior': 'Paul', 'loseWarior': 'artiomse'})
# battle.insert_one({'login': 'GonzikBenzyavsky', 'date': 1571732619.3757, 'winnerWarior': 'Blackprincer', 'loseWarior': 'Кирилл'})

