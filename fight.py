

# Handle '/fight'
@bot.message_handler(commands=['fight'])
def send_welcome(message):
    privateChat = ('private' in message.chat.type)
    if not privateChat:
        return

    list_buttons = []
    isReady = True
    for cuser in competition.find({'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):
        if cuser.get('state') == 'WAIT':
            #list_buttons.append('💰 Ставка')
            list_buttons.append('🤼 В ринг')
            bot.send_message(message.chat.id, text='Ты сам еще не готов к бою!', reply_markup=getButtonsMenu(list_buttons) )
            return

    counter_rabbit = 0
    counter_urban = 0
    for cuser in competition.find({'state': 'READY'}):
        if (cuser.get('band') == '🎩 Городские'):
            counter_urban = counter_urban + 1
        if (cuser.get('band') == '🐇 Мертвые кролики'):
            counter_rabbit = counter_rabbit + 1

    if counter_urban >= 1 and counter_rabbit >= 1:
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
        
        myquery = {'state': 'READY'}
        newvalues = { '$set': { 'state': 'FIGHT' } }
        u = competition.update_many(myquery, newvalues)

        bot.send_message(message.chat.id, text='Бой скоро начнется!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
        bot.send_message(message.chat.id, text='Недостаточно бойцов в одной из банд!', reply_markup=getButtonsMenu(list_buttons) )

# '✅ Готово'
@bot.message_handler(func=lambda message: message.text and '✅ Готово' in message.text and message.chat.type == 'private', content_types=['text'])
def ok_message(message: Message):

    list_buttons = []
 
    isReady = True
    for cuser in competition.find({
                                    'login': message.from_user.username, 
                                    'state': 'WAIT'
                                    }):
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
        isReady = False

    if isReady:
        bot.send_message(message.chat.id, text='Ты готов к бою!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        myquery = {'login': message.from_user.username, 
                     'state': 'WAIT'}
        newvalues = { '$set': { 'state': 'READY' } }
        u = competition.update_one(myquery, newvalues)
        bot.send_message(message.chat.id, text='Готово...', reply_markup=getButtonsMenu(list_buttons) )

# 🎲'⚔ Нападение' '🛡 Защита' '😎 Провокация'
@bot.message_handler(func=lambda message: message.text and message.text in ('⚔ Нападение', '🛡 Защита', '😎 Провокация')  and message.chat.type == 'private', content_types=['text'])
def chose_strategy_message(message: Message):

    etalone = []
    etalone.append('⚔ Нападение')
    etalone.append('🛡 Защита')
    etalone.append('😎 Провокация')

    real = []

    list_buttons = []
 
    isReplay = False
    isReady = False
    isBand = False
    isStrategy = False
    lenStr = 0
    for cuser in competition.find({'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):
        isReplay = True
        if cuser.get('state') == 'READY':
            isReady = True
        
        if cuser.get('band'):
            isBand = True

        if cuser.get('strategy'):
            isStrategy = True
            lenStr = len(cuser.get('strategy'))
            real = cuser.get('strategy')

    if lenStr >= 3:
        if not isBand:
            list_buttons.append('⚖️ Банда')
            bot.send_message(message.chat.id, text='Выбери банду!', reply_markup=getButtonsMenu(list_buttons) )
        else:
            if isReady:
                #list_buttons.append('💰 Ставка')
                list_buttons.append('🤼 В ринг')
                bot.send_message(message.chat.id, text='Готово!', reply_markup=getButtonsMenu(list_buttons) )
            else:
                list_buttons.append('✅ Готово')
                bot.send_message(message.chat.id, text='Жми готово!', reply_markup=getButtonsMenu(list_buttons) )
    elif  lenStr == 0:
        for x in etalone:
            if x == message.text:
                pass
            else:
                list_buttons.append(x)
        real.append(message.text)
        
        myquery = {'login': message.from_user.username, 
                                    '$or': [
                                                {'state': 'WAIT'},
                                                {'state': 'READY'}]    
                                    }
        newvalues = { '$set': { 'strategy': real } }
        u = competition.update_one(myquery, newvalues)
        bot.send_message(message.chat.id, text='Дальше...', reply_markup=getButtonsMenu(list_buttons) )
    else: # 1 - 2
        real.append(message.text)
        myquery = {'login': message.from_user.username, 
                                    '$or': [
                                                {'state': 'WAIT'},
                                                {'state': 'READY'}]    
                                    }

        newvalues = { '$set': { 'strategy':  real} }
        u = competition.update_one(myquery, newvalues)

        for x in etalone:
            find = False
            for z in real:
                if z == x:
                    find = True;
                    break;
            if not find: list_buttons.append(x)
        if len(list_buttons) == 0:
            if not isBand:
                list_buttons.append('⚖️ Банда')
                bot.send_message(message.chat.id, text='Выбери банду!', reply_markup=getButtonsMenu(list_buttons) )
            else:
                if isReady:
                    #list_buttons.append('💰 Ставка')
                    list_buttons.append('🤼 В ринг')
                    bot.send_message(message.chat.id, text='Готово!', reply_markup=getButtonsMenu(list_buttons) ) 
                else:
                    list_buttons.append('✅ Готово')
                    bot.send_message(message.chat.id, text='Жми готово!', reply_markup=getButtonsMenu(list_buttons) )      
        else:
            bot.send_message(message.chat.id, text='Дальше... Еще...', reply_markup=getButtonsMenu(list_buttons) )        

# 🎲 Стратегия
@bot.message_handler(func=lambda message: message.text and '🎲 Стратегия' in message.text and message.chat.type == 'private', content_types=['text'])
def strategy_message(message: Message):
        
    list_buttons = []
 
    isReplay = False
    isReady = False
    for cuser in competition.find({'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):                                                
        isReplay = True
        if cuser.get('state') == 'READY':
            isReady = True

    if isReady:
        #list_buttons.append('💰 Ставка')
        list_buttons.append('🤼 В ринг')
    
        bot.send_message(message.chat.id, text='Ты готов к битве!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        list_buttons.append('⚔ Нападение')
        list_buttons.append('🛡 Защита')
        list_buttons.append('😎 Провокация')
        bot.send_message(message.chat.id, text='Выбирай', reply_markup=getButtonsMenu(list_buttons) )

# 🎩 Городские or 🐇 Мертвые кролики
@bot.message_handler(func=lambda message: message.text and message.text and message.text in ('🎩 Городские', '🐇 Мертвые кролики') and message.chat.type == 'private', content_types=['text'])
def my_band_message(message: Message):

    list_buttons = []
 
    isReplay = False
    isStrategy = False
    isReady = False
    for cuser in competition.find({'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):                                                
        isReplay = True
        if cuser.get('strategy'):
            isStrategy = True
        if cuser.get('state') == 'READY':
            isReady = True

    myquery = {'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }

    newvalues = { '$set': { 'band': message.text } }
    u = competition.update_one(myquery, newvalues)

    if not isStrategy:
        list_buttons.append('🎲 Стратегия')
        bot.send_message(message.chat.id, text='Определись со своими действиями в бою!', reply_markup=getButtonsMenu(list_buttons) )
    else:
        if isReady:
            #list_buttons.append('💰 Ставка')
            list_buttons.append('🤼 В ринг')
        
            bot.send_message(message.chat.id, text='Ты готов к битве!', reply_markup=getButtonsMenu(list_buttons) )
        else:
            list_buttons.append('✅ Готово')
            bot.send_message(message.chat.id, text='Жми готов!', reply_markup=getButtonsMenu(list_buttons) )

# ⚖️ Банда
@bot.message_handler(func=lambda message: message.text and '⚖️ Банда' in message.text  and message.chat.type == 'private', content_types=['text'])
def band_message(message: Message):

    list_buttons = []
 
    isReplay = False
    isBand = False
    for cuser in competition.find({'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'}]    
                                }):                                                
        isReplay = True
        if cuser.get('band'):
            isBand = True
        break

    if not isReplay:
        list_buttons.append('⚔️ Записаться на бой')
        bot.send_message(message.chat.id, text='Ты не записан!', reply_markup=getButtonsMenu(list_buttons) )

    else:
        if not isBand:
            list_buttons.append('🎩 Городские')
            list_buttons.append('🐇 Мертвые кролики')
        if not cuser.get('strategy'):
            list_buttons.append('🎲 Стратегия')
            
        bot.send_message(message.chat.id, text='Выбирай!', reply_markup=getButtonsMenu(list_buttons) )

# '⚔️ Записаться на бой'
@bot.message_handler(func=lambda message: message.text and '⚔️ Записаться на бой' in message.text and message.chat.type == 'private', content_types=['text'])
def register_message(message: Message):
    
    list_buttons = []
    if not isRegisteredUserLogin(message.from_user.username):
        list_buttons.append('⚔️ Записаться на бой')
        list_buttons.append('🤼 В ринг')
        bot.send_message(message.chat.id, text='Я тебя не знаю! Брось мне свои пип-бой или иди нафиг!', reply_markup=getButtonsMenu(list_buttons))
        return

    isReplay = False
    for cuser in competition.find({'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'},
                                            {'state': 'FIGHT'}]   
                                }):                                                 
        if cuser.get('state') == 'READY':
            list_buttons.append('⚔️ Записаться на бой')
            list_buttons.append('🤼 В ринг')
            bot.send_message(message.chat.id, text='Бой еще не закончен!', reply_markup=getButtonsMenu(list_buttons) )
            return
        isReplay = True
        

    if not isReplay:
        u = getUserByLogin(message.from_user.username)
        competition.insert_one({'login': message.from_user.username, 
                                'chat': message.chat.id,
                                'date': datetime.now().timestamp(), 
                                'state': 'WAIT',
                                'name': u.getName(),
                                'health': u.getHealth(),
                                'damage': u.getDamage(),
                                'armor': u.getArmor(),
                                'accuracy': u.getAccuracy(),
                                'agility': u.getAgility(),
                                'charisma': u.getCharisma(),
                                'bm': u.getBm(),                                
                                'strategy': None,
                                'band': None,
                                'killedBy': None})

        list_buttons.append('⚖️ Банда')
        list_buttons.append('🎲 Стратегия')
        bot.send_message(message.chat.id, text=getResponseDialogFlow('sign_up_for_a_fight'), reply_markup=getButtonsMenu(list_buttons) )
    else:
        if not cuser.get('band'):
            list_buttons.append('⚖️ Банда')
        if not cuser.get('strategy'):
            list_buttons.append('🎲 Стратегия')

        bot.send_message(message.chat.id, text=getResponseDialogFlow('sign_up_replay'), reply_markup=getButtonsMenu(list_buttons) )

# Handle 🤼 В ринг
@bot.message_handler(func=lambda message: message.text and '🤼 В ринг' in message.text and message.chat.type == 'private', content_types=['text'])
def ring_message(message: Message):

    list_buttons = []

    isReplay = False
    isStrategy = False
    isReady = False
    isBand = False
    for cuser in competition.find({'login': message.from_user.username, 
                                '$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'},
                                            {'state': 'FIGHT'}]   
                                }):                                                 
        isReplay = True
        if cuser.get('state') == 'READY':
            isReady = True

        if cuser.get('strategy'):
            isStrategy = True

        if cuser.get('band'):
            isBand = True

        if isStrategy and isBand and len(cuser.get('strategy')) >= 3 and cuser.get('state') == 'WAIT':
            list_buttons.append('✅ Готово')     

        if cuser.get('state') == 'WAIT':
            if not cuser.get('band'):
                list_buttons.append('⚖️ Банда')
            if not cuser.get('strategy') or len(cuser.get('strategy')) <3:
                list_buttons.append('🎲 Стратегия')
            break
            

    usersOnCompetition = '🤼 В ринге:\n\n'
    i = 0
    for cuser in competition.find({'$or': [
                                            {'state': 'WAIT'},
                                            {'state': 'READY'},
                                            {'state': 'FIGHT'}]
                                        }):
        i = i + 1
        band = cuser.get("band")
        state = cuser.get('state')
        if state == 'WAIT':
            state = '⏳'
        elif state == 'READY':
            state = '✅'
        elif state == 'FIGHT':
            state = '⚔'
        if not band:
            band = '❔'

        usersOnCompetition = usersOnCompetition + f'{i}.{state} {band[0:1]} {cuser.get("name")} 📯{cuser.get("bm")}\n'

    if i == 0:
        usersOnCompetition = 'Никого нет в ринге! Запишись первым!\n'
        list_buttons.append('⚔️ Записаться на бой')
    else:
        if (not isReplay):
            list_buttons.append('⚔️ Записаться на бой')
        list_buttons.append('🤼 В ринг')
        usersOnCompetition = usersOnCompetition + '\nНачать бой /fight\n' 
    
    usersOnCompetition = usersOnCompetition + '\n' 
    usersOnCompetition = usersOnCompetition + '⏰ ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(datetime.now().timestamp())) +'\n'

    bot.send_message(message.chat.id, text=usersOnCompetition, reply_markup=getButtonsMenu(list_buttons) ) 


def fight():
    #logger.info('Calculate fight')

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
        if max_damage < int(str(fighter.get('damage')).split(' ')[0]): max_damage = int(str(fighter.get('damage')).split(' ')[0])
        if max_armor < int(str(fighter.get('armor')).split(' ')[0]): max_armor = int(str(fighter.get('armor')).split(' ')[0])
        if min_damage > int(str(fighter.get('damage')).split(' ')[0]): min_damage = int(str(fighter.get('damage')).split(' ')[0])
        findFighters = True

    if not findFighters:
        return

    # Какя банда начинает первой

    band1 = random.sample(fighters,  1)[0]
    fighters.remove(band1)
    band2 = random.sample(fighters,  1)[0]
 
    first = band1
    second = band2

    bot.send_message(fighter.get('chat'), text=f'Банда <b>{band1[0].get("band")}</b> воспользовалась неожиданностью и напала первой!', parse_mode='HTML')

    killed = []
    j = 0
    
    while True:
        j = j + 1
        doExit = False
        if len(first) == 0 or len(second) == 0:
            break

        f1 = random.sample(first,  1)[0]
        f2 = random.sample(second,  1)[0]         

        health1 = float(f1.get('health').split(' ')[0])
        health2 = float(f2.get('health').split(' ')[0])

        doBreak = False
        vs_log = '<b>⚔ ХОД БИТВЫ:</b>\n\n'
        vs_log = f'❤{f1.get("health")} <b>{f1.get("band")[0:1]} {f1.get("name")}</b>\nvs\n❤{f2.get("health")} <b>{f2.get("band")[0:1]} {f2.get("name")}</b>\n\n'
        damage = 0

        for i in range(0, 3):
            strategy1 = f1.get('strategy')[i]
            strategy2 = f2.get('strategy')[i]

            damage1 = float(str(f1.get('damage')).split(' ')[0])
            damage2 = float(str(f2.get('damage')).split(' ')[0])

            armor1 = float(str(f1.get('armor')).split(' ')[0])
            armor2 = float(str(f2.get('armor')).split(' ')[0])
            fight_str = ''


            # ⚔ 1024 vs ⚔ 800
            # 🛡 276  vs 🛡 300
            # ❤ 650  vs ❤ 500

            #1 - 1024

            #1 - 800


            if strategy1 == '⚔ Нападение':
                if strategy2 == '⚔ Нападение':
                    damage1 = damage1 * 1
                    damage2 = damage2 * 1
                    fight_str = '⚔⚔'
                if strategy2 == '🛡 Защита':
                    damage1 = damage1 * 1
                    armor2 = armor2 * 4
                    fight_str = '⚔🛡'
                if strategy2 == '😎 Провокация':
                    damage2 = damage2 * 0
                    fight_str = '⚔😎'
            if strategy1 == '🛡 Защита':
                if strategy2 == '⚔ Нападение':
                    armor1 = armor1 * 4
                    damage2 = damage2 * 1
                    fight_str = '🛡⚔'
                if strategy2 == '🛡 Защита':
                    armor1 = armor1 * 4
                    armor2 = armor2 * 4
                    fight_str = '🛡🛡'
                if strategy2 == '😎 Провокация':
                    armor2 = armor2 * 0  
                    fight_str = '🛡😎'
            if strategy1 == '😎 Провокация':
                if strategy2 == '⚔ Нападение':
                    damage2 = damage2 * 0
                    fight_str = '😎⚔'
                if strategy2 == '🛡 Защита':
                    armor2 = armor2 * 0
                    fight_str = '😎🛡'
                if strategy2 == '😎 Провокация':
                    armor1 = armor1 * random.random()  
                    armor2 = armor2 * random.random()  
                    damage1 = damage1 * random.random()  
                    damage2 = damage2 * random.random()  
                    fight_str = '😎😎'

            # health1 = health1 -  ( (Урон2-Защита1) / МахУрон) * МинУрон * 0.1)
            # health2 = health2 -  ( (Урон1-Защита2) / МахУрон) * МинУрон * 0.1)
            #
            # '⚔ Нападение', '🛡 Защита', '😎 Провокация'

            # print(f'{j} health1  = {health1} -  ( ({damage2}-{armor1}) / {max_damage}) * {min_damage} = {health1}: {(damage2-armor1)/max_damage*min_damage*0.1})')
            # print(f'{j} health2  = {health2} -  ( ({damage1}-{armor2}) / {max_damage}) * {min_damage} = {health1}: {(damage1-armor2)/max_damage*min_damage*0.1})')
            dmg1 = (damage2-armor1)/max_damage*min_damage*0.35
            dmg2 = (damage1-armor2)/max_damage*min_damage*0.35
            
            if int(dmg1) > int(dmg2):
                damage = dmg1-dmg2
                health2 = health2 - damage
                f2.update({'health': str(int(health2))})
                vs_log = vs_log + f'{fight_str} ❤{f2.get("health")} 💥{str(int(damage))} <b>{f1.get("band")[0:1]} {f1.get("name")}</b> {getResponseDialogFlow("you_win")}\n'
                if int(f2.get("health")) <= 0:
                    killed.append(f2)
                    second.remove(f2)
                    f2.update({'killedBy': f'{f1.get("band")[0:1]} {f1.get("name")}'})
                    break
            elif int(dmg1) == int(dmg2): 
                damage = 0
                vs_log = vs_log + f'{fight_str} {getResponseDialogFlow("draw_competition")}\n'
            else:
                damage = dmg2-dmg1
                health1 = health1 - damage
                f1.update({'health': str(int(health1))})
                vs_log = vs_log + f'{fight_str} ❤{f1.get("health")} 💥{str(int(damage))} <b>{f2.get("band")[0:1]} {f2.get("name")}</b> {getResponseDialogFlow("you_win")}\n'
                if int(f1.get("health")) <= 0:
                    killed.append(f1)
                    first.remove(f1)
                    f1.update({'killedBy': f'{f2.get("band")[0:1]} {f2.get("name")}'})
                    break

        if int(f1.get('health')) <= 0:
                vs_log = vs_log + f'\n'
                vs_log = vs_log + f'☠️ {f1.get("health")} <b>{f1.get("band")[0:1]} {f1.get("name")}</b> {getResponseDialogFlow("you_deadman")}\n'
        elif int(f2.get('health')) <= 0:
                vs_log = vs_log + f'\n'
                vs_log = vs_log + f'☠️ {f2.get("health")} <b>{f2.get("band")[0:1]} {f2.get("name")}</b> {getResponseDialogFlow("you_deadman")}\n'
        else:
                vs_log = vs_log + f'\n'
                vs_log = vs_log + f'{getResponseDialogFlow("draw_competition")}\n'

        send_messages_big(chat_id = f1.get('chat'), text=vs_log)
        send_messages_big(chat_id = f2.get('chat'), text=vs_log)
        time.sleep(5)

    fight_log = '<b>ИТОГИ БОЯ:</b>\n\n'
 
    winners = []
    if len(first) == 0:
        winners = second 
    if len(second) == 0:
        winners = first
    
    if (len(winners)>0):
        fight_log = fight_log + f'Победила банда <b>{winners[0].get("band")}</b>\n'
        m = 0
        for winFigther in winners:
            m = m + 1
            fight_log = fight_log + f'{m}. ❤{winFigther.get("health")} <b>{winFigther.get("band")[0:1]} {winFigther.get("name")}</b> \n'
    else:
        fight_log = fight_log + f'ВСЕ УМЕРЛИ!\n'

    fight_log = fight_log + f'\n'
    z = 0
    for deadman in killed:
        z = z+1
        fight_log = fight_log + f'{z}. ☠️{deadman.get("health")} <b>{deadman.get("band")[0:1]} {deadman.get("name")}</b> убит бойцом <b>{deadman.get("killedBy")}</b>\n'

    fight_log = fight_log + f'\n'
    fight_log = fight_log + '⏰ ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(datetime.now().timestamp())) +'\n'

    for fighter in competition.find({'state': 'FIGHT'}):
        send_messages_big(chat_id = fighter.get('chat'), text=fight_log)

    z = 0
    for deadman in killed:
        z = z+1
        myquery = { 'login': deadman.get('login'), 'state' : 'FIGHT'}
        newvalues = { '$set': { 'state': 'CANCEL', 'health': deadman.get('health'), 'killedBy': deadman.get('killedBy') } }
        u = competition.update_one(myquery, newvalues)

    for winner in winners:  
        myquery = { 'login': winner.get('login'), 'state' : 'FIGHT'}
        newvalues = { '$set': { 'state': 'CANCEL', 'health': winner.get('health') } }
        u = competition.update_one(myquery, newvalues)   


def fight_job():
    while True:
        fight()
        time.sleep(20)

