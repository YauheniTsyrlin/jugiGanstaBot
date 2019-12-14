import json
import datetime
import time
import tools

def mergeWariors(warior, wariorToUpdate):

    if (warior.damage):
        if wariorToUpdate.damage:
            wariorToUpdate.damage = warior.damage
        else: 
            wariorToUpdate.damage = warior.damage

    if (warior.health): 
        if wariorToUpdate.health:       
            if (wariorToUpdate.health < warior.health):
                wariorToUpdate.health = warior.health
        else: 
            wariorToUpdate.health = warior.health   

    if (warior.bm):
        if wariorToUpdate.bm:
            if (wariorToUpdate.bm < warior.bm):
                wariorToUpdate.bm = warior.bm
        else: 
            wariorToUpdate.bm = warior.bm  

    if (warior.photo):
        wariorToUpdate.photo = warior.photo
    
    if (warior.hithimself):
        if wariorToUpdate.hithimself:
            wariorToUpdate.hithimself       = wariorToUpdate.hithimself + warior.hithimself
        else:
            wariorToUpdate.hithimself       = warior.hithimself
    
    if (warior.missed):
        if wariorToUpdate.missed:
            wariorToUpdate.missed           = wariorToUpdate.missed + warior.missed
        else:
            wariorToUpdate.missed           = warior.missed

    if (warior.kills):
        if wariorToUpdate.kills:
            wariorToUpdate.kills          = wariorToUpdate.kills + warior.kills
        else:
            wariorToUpdate.kills           = warior.kills

    if (warior.enemy_armor):
        wariorToUpdate.enemy_armor = warior.enemy_armor

    if (warior.band):
        wariorToUpdate.band = warior.band

    if (warior.fraction):
        wariorToUpdate.fraction = warior.fraction

    if (warior.goat):
        wariorToUpdate.goat = warior.goat

    return wariorToUpdate

def getWarior(name, wariors):
    for w in wariors.find({"name": f"{tools.deEmojify(name)}"}):
        warior = importWarior(w)
        return warior

def importWarior(warior):
    photo = None
    if (warior.get('photo')) : 
        photo = warior['photo']
        
    war = Warior(warior.get('name'), warior.get('timeUpdate'), '', photo)

    war.name                    = warior.get('name')
    if (warior.get('fraction')):
        war.fraction            = warior.get('fraction')
    if (warior.get('band')):
        war.band                = warior.get('band')
    if (warior.get('goat')):
        war.goat                = warior.get('goat')        
    war.health                  = warior.get('health')
    war.damage                  = warior.get('damage')
    war.bm                      = warior.get('bm')
    if (warior.get('hithimself')):
        war.hithimself          = warior.get('hithimself')
    else:
        war.hithimself          = 0
    
    if (warior.get('hithimself')):
        war.missed              = warior.get('missed')
    else:
        war.missed              = 0
    
    if (warior.get('kills')):
        war.kills               = warior.get('kills')
    else:
        war.kills               = 0

    if (warior.get('photo')):
        war.photo               = warior.get('photo')
    else:
        war.photo = None

    if (warior.get('enemy_armor')):
        war.enemy_armor               = warior.get('enemy_armor')
    else:
        war.enemy_armor = None

    if (warior.get('timeUpdate')):    
        war.timeUpdate          = warior.get('timeUpdate')
    return war

def fromPhotoToWarioirs(date, text, photo):
    result = []
    strings = text.split('\n')
    i = 0
    warior = None
    name_tmp = ''

    for s in strings:
        if i==0:
            name_tmp = strings[i][2:].strip()
            if (' и его ' in strings[i]):
                # ⚛️ ✴ Alfakill и его 🛰Шерлокдрон.\n
                name_tmp = strings[i].split(' и его ')[0].strip()[2:].strip()
        i=i+1
  
    warior = Warior(name_tmp, date, text, photo)
    result.append(warior)
    return result

def getFractionFromString(string: str):
    fraction = None
    if ('⚙️' in string):
        fraction = '⚙️Убежище 4'
    elif ('🔪' in string):
        fraction = '🔪Головорезы'
    elif ('💣' in string):
        fraction = '💣Мегатонна'
    elif ('⚛️' in string):
        fraction = '⚛️Республика'
    elif ('👙' in string):
        fraction = '👙Клуб бикини'  
    return fraction

def fromTopToWariorsBM(forward_date, message, wariors):
    result = []
    strings = message.text.split('\n')
    i = 0
    for s in strings:

        if ('Счет: ' in strings[i] ):
            name = strings[i-1].split('. ')[1].split(' [')[0].strip()
            fraction = getFractionFromString(strings[i-1].split(' [')[1].split(']')[0])
            bm = strings[i].split('Счет: ')[1].strip()

         
            warior = Warior(name, message.forward_date, "", None)
            warior.setBm(bm)
            warior.setFraction(fraction)
            result.append(warior)
        i = i + 1
    return result


def fromFightToWarioirs(forward_date, message, USERS_ARR: list, battle):
    
    def getUserByLogin(login: str):
        for user in list(USERS_ARR):
            if login == user.getLogin(): return user
        return None

    strings = message.text.split('\n')
    i = 0
    result = []
    fillResult = False
    winnerName = ''
    loserName = ''
    for s in strings:
        if (strings[i].startswith('VS.')):
            w1 = Warior(strings[i-1].split(' из ')[0].strip(), forward_date, message.text, None)
            w2 = Warior(strings[i+1].split(' из ')[0].strip(), forward_date, message.text, None)
            result.append(w1)
            result.append(w2)
            fillResult = True
        if fillResult and (result[0].name in strings[i] and result[1].name in strings[i]):
            if (strings[i].startswith(result[0].name)):
                result[0].kills = result[0].kills + 1
                winnerName = result[0].name
                loserName = result[1].name
            else:
                result[1].kills = result[1].kills + 1
                winnerName = result[1].name
                loserName = result[0].name
        i=i+1


    for user in list(USERS_ARR):
        # TODO Проверить еще на банду
        if (user.getLogin() == message.forward_from.username and user.getName() == result[0].getName()):
            result[1].setEnemy_armor(user.getArmor())
            
            break
        if (user.getLogin() == message.forward_from.username and user.getName() == result[1].getName()):
            result[0].setEnemy_armor(user.getArmor())
            break

    # for user in list(USERS_ARR):
    #     if (user.getLogin() == message.from_user.username and user.getName() == winnerName):

    isReplay = False
    for x in battle.find({'winnerWarior': winnerName, 'loseWarior': loserName, 'date': forward_date } ):
        isReplay = True
        return None

    user = getUserByLogin(message.from_user.username)
    band = None
    if user:
        band = user.getBand()
        
    if not isReplay:
        battle.insert_one({
            'login': message.from_user.username, 
            'date': forward_date, 
            'winnerWarior': winnerName, 
            'loseWarior': loserName,
            'band': band})

    return result

class Warior(object):
    """docstring"""

    def __init__(self, name, date, text, photo):
        strings = text.split('\n')
 
        self.name = tools.deEmojify(name)
        self.band = None
        self.goat = None
        self.fraction = None
        self.bm = None
        self.damage = None
        self.health = None
        self.hithimself = None
        self.missed = None
        self.kills = None
        self.timeUpdate = date
        self.photo = photo
        self.enemy_armor = None

        i = 0
        if ('FIGHT!' in text):
            self.bm = 0
            self.damage = 0
            self.health = 0
            self.hithimself = 0
            self.missed = 0
            self.kills = 0
            for s in strings:
                if (strings[i].startswith('VS.')):
                    if (strings[i-1].startswith(name)):
                        self.setFraction(strings[i-1].split('из')[1].strip())
                    elif (strings[i+1].startswith(name)):
                        self.setFraction(strings[i+1].split('из')[1].strip())
                if (strings[i].startswith('❤️') and name in strings[i]):
                    # '❤️1130 BACDAFUCUP ŇṼ наступил на мизинец (💥529)'
                    health_tmp = int(strings[i].split(name)[0].split('❤️')[1].strip())
                    if (health_tmp > self.getHealth()):
                        self.setHealth(health_tmp)

                    if ('💥' in strings[i]):
                        damage_tmp = int(strings[i].split(name)[1].split('💥')[1].split(')')[0])
                        if (damage_tmp > self.getDamage()):
                            self.setDamage(damage_tmp)

                    if ('💔' in strings[i]):
                        self.hithimself = self.hithimself + 1    
                    if ('💫' in strings[i]):
                        self.missed = self.missed + 1
                i=i+1
        if (photo):
            for s in strings:
                if ('🤘(без банды)' in strings[i]):
                    self.setBand(None)
                elif ('🤘' in strings[i]):
                    self.setBand(strings[i].split('🤘')[1].strip())
                if ('🐐' in strings[i]):
                    self.setGoat(strings[i].split('🤘')[0][1:].strip())
                if (i==0):
                    if (strings[i].startswith('⚙️')):
                        self.setFraction('⚙️Убежище 4')
                    elif (strings[i].startswith('🔪')):
                        self.setFraction('🔪Головорезы')
                    elif (strings[i].startswith('💣')):
                        self.setFraction('💣Мегатонна')
                    elif (strings[i].startswith('⚛️')):
                        self.setFraction('⚛️Республика')
                    elif (strings[i].startswith('👙')):
                        self.setFraction('👙Клуб бикини')
                i=i+1

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def getFractionSmall(self):
        if (self.fraction.startswith('⚙️')):
            return '⚙️'
        elif (self.fraction.startswith('🔪')):
            return '🔪'
        elif (self.fraction.startswith('💣')):
            return '💣'
        elif (self.fraction.startswith('⚛️')):
            return '⚛️'
        elif (self.fraction.startswith('👙')):
            return '👙'

    def getProfileInline(self):
        string = '┌'

        if self.goat:
            string = string + f'🐐{self.goat}'

        band = ''
        if (not self.band) or (self.band == 'NO_BAND'):
            band = ''
        else:
            band = self.band
        
        if string == '┌':
            string = string + f'🤘{band}'
        else:
            string = string + f'|🤘{band}'
        

        second_string = '└'

        if self.health:
            second_string = second_string + f'❤{self.health}'

        if self.bm:
            if not self.bm == 0:
                second_string = second_string + f'📯{self.bm}' 

        if self.enemy_armor:
            if self.damage:
                second_string = second_string + f'💥{self.damage} при 🛡{self.enemy_armor}'
            else:
                pass
        else:
            if self.damage:
                second_string = second_string + f'💥{self.damage}' 
        if second_string == '└':
            second_string = '└...'
        return string + '\n' + second_string

    def getProfileSmall(self):
        first_string = f'┌{tools.getTimeEmoji(self.timeUpdate)}{self.getFractionSmall()} {self.name}'
        
        string = '├'
        if self.goat:
            string = string + f'🐐{self.goat}'
        band = ''
        if (not self.band) or (self.band == 'NO_BAND'):
            band = None
        else:
            band = self.band
        
        if (band):
            if string == '├':
                string = string + f'🤘{band}'
            else:
                string = string + f'\n├🤘{band}'
        
        if string == '├':
            string = ''
        else:
            string = string + '\n'

        second_string = '└'

        if self.health:
            second_string = second_string + f'❤{self.health}'

        if self.bm:
            if not self.bm == 0:
                second_string = second_string + f'📯{self.bm}' 

        if self.enemy_armor:
            if self.damage:
                second_string = second_string + f'💥{self.damage} при 🛡{self.enemy_armor}'
            else:
                pass
        else:
            if self.damage:
                second_string = second_string + f'💥{self.damage}' 
        
        if second_string == '└':
            second_string = '└...'
        else:
            second_string = second_string + '\n'

        return first_string + '\n' + string + second_string

    def getProfile(self):
        string = ''
        string = string + f'┌{self.name}\n'  
        if self.fraction:
            string = string + f'├{self.fraction}\n'        
        if self.band:
            if (self.band == None):
                string = string + f'├🤘 Банда: (без банды)\n'
            else:
                string = string + f'├🤘 Банда: {self.band}\n' 
        if self.goat:
            string = string + f'├🐐 Козел: {self.goat}\n'
        if self.kills:          
            string = string + f'└☠️ Убийств: {self.kills}\n'
        else:
            string = string + f'└☠️ Убийств: 0\n'

        string = string + f'\n'  
        bm_str = 'Неизвестна'
        if self.bm:
            if not self.bm == 0:
                bm_str = self.bm
        string = string + f'┌📯 Боевая мощь: '+ bm_str +'\n'  
        
        if self.enemy_armor:
            if self.damage:
                string = string + f'├💥{self.damage} при 🛡 {self.enemy_armor}\n'
            else:
                pass
        else:
            if self.damage:
                string = string + f'├💥{self.damage}\n'  
        
        if self.health:
            string = string + f'├❤{self.health}\n'
        else: 
            pass

        if self.missed:
            string = string + f'├💫{self.missed} раз\n'
        else: 
            pass
        if self.hithimself:
            string = string + f'└💔{self.hithimself} раз\n'
        else: 
            string = string + f'└...\n'

        string = string + '\n'

        string = string + f'⏰{tools.getTimeEmoji(self.timeUpdate)} ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(self.timeUpdate)) +'\n'
        return string

    def setName(self, name):
        self.name = tools.deEmojify(name)
    def getName(self):
        return self.name

    def setFraction(self, fraction):
        self.fraction = fraction
    def getFraction(self):
        return self.fraction

    def setBand(self, band):
        self.band = band
    def getBand(self):
        return self.band
    
    def setGoat(self, goat):
        self.goat = goat
    def getGoat(self):
        return self.goat

    def setHealth(self, health):
        self.health = health

    def getHealth(self):
        return self.health

    def setDamage(self, damage):
        self.damage = damage
    def getDamage(self):
        return self.damage

    def setBm(self, bm):
        self.bm = bm
    def getBm(self):
        return self.bm

    def setHithimself(self, hithimself):
        self.hithimself = hithimself
    def getHithimself(self):
        return self.hithimself

    def setMissed(self, missed):
        self.missed = missed
    def getMissed(self):
        return self.missed

    def setKills(self, kills):
        self.kills = kills
    def getKills(self):
        return self.kills

    def setEnemy_armor(self, enemy_armor):
        self.enemy_armor = enemy_armor
    def getEnemy_armor(self):
        return self.enemy_armor

    def getPhoto(self):
        return self.photo

    def setTimeUpdate(self, timeUpdate):
        self.timeUpdate = timeUpdate  
    def getTimeUpdate(self):
        return self.timeUpdate