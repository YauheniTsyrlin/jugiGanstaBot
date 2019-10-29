import schedule
import time
import random
import pymongo
import config

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["jugidb"]
registered_users = mydb["users"]
registered_wariors = mydb["wariors"]
battle      = mydb["battle"]
competition = mydb["competition"]
settings    = mydb["settings"]

def fight():
    bands = ['🎩 Городские', '🐇 Мертвые кролики']
    
    figthers_rabbit = []
    figthers_urban = []
    fighters = [figthers_rabbit, figthers_urban]
    max_damage = 0
    min_damage = 10000000
    max_armor = 0
    findFighters = False
    for fighter in competition.find({'state': 'FIGHT'}):
        if fighter.get('band') == '🎩 Городские':
            figthers_urban.append(fighter)
        if fighter.get('band') == '🐇 Мертвые кролики':
            figthers_rabbit.append(fighter)
        if max_damage < int(fighter.get('damage')): max_damage = int(fighter.get('damage'))
        if max_armor < int(fighter.get('armor')): max_armor = int(fighter.get('armor'))
        if min_damage > int(fighter.get('damage')): min_damage = int(fighter.get('damage'))
        findFighters = True

    if not findFighters:
        print ('Нет бойцоы, готов к бою!')
        return
    # Какя банда начинает первой

    band1 = random.sample(fighters,  1)[0]
    fighters.remove(band1)
    band2 = random.sample(fighters,  1)[0]

    print(f'Банда {band1[0].get("band")} воспользовалась неожиданностью и напала первой!')
    print(f'Максимальный/Минимальный damage {max_damage}/{min_damage}, максимальныя защита {max_armor}!')
    
    first = band1
    second = band2
    killed = []
    j = 0
    while True:
        j = j + 1
        print('==================')
        if len(first) == 0:
            print(f'{j} Закончился бой')
            print(second)
            break
        
        if len(second) == 0:
            print(f'{j} Закончился бой')
            print(first)
            break

        f1 = random.sample(first,  1)[0]
        f2 = random.sample(second,  1)[0]         

        health1 = float(f1.get('health'))
        health2 = float(f2.get('health'))

        for i in [0, 1, 2]:
            strategy1 = f1.get('strategy')[i]
            strategy2 = f2.get('strategy')[i]

            print(f'{j} {f1.get("name")}({strategy1}) vs {f2.get("name")}({strategy2})')

            damage1 = float(f1.get('damage'))
            damage2 = float(f2.get('damage'))

            armor1 = float(f1.get('armor'))
            armor2 = float(f2.get('armor'))

            if strategy1 == '⚔ Нападение':
                if strategy2 == '⚔ Нападение':
                    damage1 = damage1 * 1
                    damage2 = damage2 * 1
                    #print('⚔⚔')
                if strategy2 == '🛡 Защита':
                    damage1 = damage1 * 1
                    armor2 = armor2 * 4
                    #print('⚔🛡')
                if strategy2 == '😎 Провокация':
                    damage2 = damage2 * 0
                    #print('⚔😎')
            if strategy1 == '🛡 Защита':
                if strategy2 == '⚔ Нападение':
                    armor1 = armor1 * 4
                    damage2 = damage2 * 1
                    #print('🛡😎')
                if strategy2 == '🛡 Защита':
                    armor1 = armor1 * 4
                    armor2 = armor2 * 4
                    #print('🛡🛡')
                if strategy2 == '😎 Провокация':
                    armor2 = armor2 * 0  
                    #print('🛡😎')
            if strategy1 == '😎 Провокация':
                if strategy2 == '⚔ Нападение':
                    damage2 = damage2 * 0
                    #print('😎⚔')
                if strategy2 == '🛡 Защита':
                    armor2 = armor2 * 0
                    #print('😎🛡')
                if strategy2 == '😎 Провокация':
                    armor1 = armor1 * random.random()  
                    armor2 = armor2 * random.random()  
                    damage1 = damage1 * random.random()  
                    damage2 = damage2 * random.random()  
                    #print('😎😎')

            # health1 = health1 -  ( (Урон2-Защита1) / МахУрон) * МинУрон * 0.1)
            # health2 = health2 -  ( (Урон1-Защита2) / МахУрон) * МинУрон * 0.1)
            #
            # '⚔ Нападение', '🛡 Защита', '😎 Провокация'

            print(f'{j} health1  = {health1} -  ( ({damage2}-{armor1}) / {max_damage}) * {min_damage} = {health1}: {(damage2-armor1)/max_damage*min_damage*0.1})')
            print(f'{j} health2  = {health2} -  ( ({damage1}-{armor2}) / {max_damage}) * {min_damage} = {health1}: {(damage1-armor2)/max_damage*min_damage*0.1})')
            
            health1 = health1 - (damage2-armor1)/max_damage*min_damage*0.1
            health2 = health2 - (damage1-armor2)/max_damage*min_damage*0.1

            f1.update({'health': str(int(health1))})
            f2.update({'health': str(int(health2))})

            print(f'{j} {f1.get("name")}({health1}) vs {f2.get("name")}({health2})')
            if int(health1) <= 0:
                print(f'{j} {f1.get("name")} убит!')
                first.remove(f1)
                killed.append(f1)
                break
            if int(health2) <= 0:
                print(f'{j} {f1.get("name")} убит!')
                second.remove(f2)
                killed.append(f2)
                break
    
    for deadman in killed:
        myquery = { 'login': deadman.get('login'), 'state' : 'FIGHT'}
        newvalues = { '$set': { 'state': 'CANCEL', 'health': deadman.get('health') } }
        u = competition.update_one(myquery, newvalues)

    winners = []
    if len(first) == 0:
        winners = second 
    if len(second) == 0:
        winners = first
    
    for winner in winners:  
        myquery = { 'login': winner.get('login'), 'state' : 'FIGHT'}
        newvalues = { '$set': { 'state': 'CANCEL', 'health': winner.get('health') } }
        u = competition.update_one(myquery, newvalues)        

fight()

#schedule.every(20).seconds.do(fight)

# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
# schedule.every().minute.at(":01").do(fight)

# while True:
#     schedule.run_pending()
#     time.sleep(1)