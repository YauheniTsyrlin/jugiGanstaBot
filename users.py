import json
import datetime
import time
from datetime import datetime
from datetime import timedelta
import tools

def normalize(string):
    if not string:
        return int(0)
    try:
        return int(string)
    except:
        if '(+' in str(string):
            return int(string.split('(+')[0].strip()) + int(string.split('(+')[1].split(')')[0].strip())
            
def getUser(login, registered_users):
    for registered_user in registered_users.find({"login": f"{login}"}):
        user = importUser(registered_user)
        return user
    return None

def updateUser(newUser, oldUser):
    if oldUser == None:
        return newUser

    if newUser.name:
        oldUser.name = newUser.name
    if newUser.fraction:
        oldUser.fraction = newUser.fraction            
    if newUser.band:
        oldUser.band = newUser.band
    if newUser.health:
        oldUser.health = newUser.health
    if newUser.hunger:
        oldUser.hunger = newUser.hunger
    if newUser.damage:
        oldUser.damage = newUser.damage
    if newUser.armor:
        oldUser.armor = newUser.armor
    if newUser.force:
        oldUser.force = newUser.force
    if newUser.accuracy:
        oldUser.accuracy = newUser.accuracy          
    if newUser.charisma:
        oldUser.charisma = newUser.charisma
    if newUser.agility:
        oldUser.agility = newUser.agility
    if newUser.stamina:
        oldUser.stamina = newUser.stamina
    if hasattr(newUser, 'loсation'):
        if newUser.loсation:
            oldUser.loсation = newUser.loсation
    if hasattr(newUser, 'timeZone'):
        if newUser.timeZone:
            oldUser.timeZone = newUser.timeZone
    if hasattr(newUser, 'raid'):
        oldUser.raid = newUser.raid
    if hasattr(newUser, 'raidlocation'):
        oldUser.raidlocation = newUser.raidlocation
    if newUser.dzen:
        oldUser.dzen = newUser.dzen
    if newUser.timeUpdate:
        oldUser.timeUpdate = newUser.timeUpdate
    if hasattr(newUser, 'ping'):
        oldUser.ping = newUser.ping

    return oldUser

def importUser(registered_user):
        u = User(registered_user['login'], registered_user['timeUpdate'],'')

        u.login          = registered_user['login']
        u.name           = registered_user['name']
        u.fraction       = registered_user['fraction']
        if (registered_user.get('band')):
            u.band       = registered_user['band']
        if (registered_user.get('status')):
            u.status     = registered_user['status']
        u.health         = registered_user['health']
        u.hunger         = registered_user['hunger']
        u.damage         = registered_user['damage']
        u.armor          = registered_user['armor']
        u.force          = registered_user['force']
        u.accuracy       = registered_user['accuracy']
        u.charisma       = registered_user['charisma']
        u.agility        = registered_user['agility']
        u.stamina        = registered_user['stamina']
        
        if (registered_user.get('location')):    
            u.location     = registered_user['location']
        if (registered_user.get('timeZone')):    
            u.timeZone     = registered_user['timeZone']
        if (registered_user.get('dzen')):
            u.dzen        = registered_user['dzen']
        if (registered_user.get('timeBan')):
            u.timeBan        = registered_user['timeBan']
        if (registered_user.get('timeUpdate')):    
            u.timeUpdate     = registered_user['timeUpdate']
        if (registered_user.get('status')):    
            u.status     = registered_user['status']
        if (registered_user.get('raid')):    
            u.raid     = registered_user['raid']

        try:   
            u.ping = registered_user['ping']
        except:
            u.ping = True

        u.setRaidLocation(registered_user['raidlocation'])

        return u

class User(object):
    def __init__(self, login, date, text):
        i = 0
        self.login = login
        self.timeUpdate = date
        self.timeBan = None
        self.status = None
        self.dzen = 0
        self.band = None
        self.location = None
        self.timeZone = None
        self.timeBan  = None
        self.raid = None
        self.raidlocation = None
        self.ping = True

        strings = text.split('\n')
        isEquipequipment = False
        for s in strings:
            if ('Экипировка' in strings[i]):
                isEquipequipment = True

            if ('Банда' in strings[i]):
                self.setBand(strings[i].split(':')[1].strip())
            if ('Здоровье' in strings[i]):
                self.setHealth(strings[i].split(':')[1].split('/')[1])
                if ('Банда' in strings[i-1]):
                    self.setName(strings[i-2].split(',')[0])
                    self.setFraction(strings[i-2].split(',')[1].strip())
                else:
                    self.setName(strings[i-1].split(',')[0])
                    self.setFraction(strings[i-1].split(',')[1].strip())

            if ('Голод' in strings[i]):
                self.setHunger(int(strings[i].split(':')[1].split('%')[0].strip()))
            if ('Урон' in strings[i]):
                self.setDamage(int(strings[i].split(':')[1].split(' ')[1].strip()))

            if (not isEquipequipment) and ('Броня' in strings[i]):
                #'armor': '145 (+30)'
                self.setArmor(int(strings[i].split(':')[2].split('(+')[0].strip()))
                if '(+' in strings[i]:
                    self.setArmor(int(self.getArmor()) + int(strings[i].split(':')[2].split('(+')[1].split(')')[0].strip()))

            if ('Сила' in strings[i]):
                self.setForce(int(strings[i].split(':')[1].split('🎯')[0].split('(+')[0].strip()))
                if '(+' in strings[i].split('Меткость')[0]:
                    self.setForce(int(self.getForce()) + int(strings[i].split(':')[1].split('🎯')[0].split('(+')[1].split(')')[0].strip()))

            if ('Меткость' in strings[i]):
                self.setAccuracy(int(strings[i].split(':')[2].split('(+')[0].strip()))
                if '(+' in strings[i].split('Меткость')[1]:
                    self.setAccuracy(int(self.getAccuracy()) + int(strings[i].split(':')[2].split('(+')[1].split(')')[0].strip()))

            # 9 - |🗣Харизма: 80 ��🏽🏽‍♂️Ловкость: 318(+30)|
            if ('Харизма' in strings[i]):
                self.setCharisma(int(strings[i].split(': ')[1].split(' ')[0].split('(+')[0].strip()))
                if '(+' in strings[i].split('Ловкость')[0]:
                    self.setCharisma(int(self.getCharisma()) + int(strings[i].split(': ')[1].split('(+')[1].split(')')[0].strip()))

            if ('Ловкость' in strings[i]):
                self.setAgility(int(strings[i].split(':')[2].split('(+')[0].strip()))
                if '(+' in strings[i].split('Ловкость')[1]:
                    self.setAgility(int(self.getAgility()) + int(strings[i].split(':')[2].split('(+')[1].split(')')[0].strip()))

            # 11 - |�🔋Выносливость: 8/16 /ref|
            if ('Выносливость' in strings[i]):
                self.setStamina(int(strings[i].split(':')[1].split('/')[1].strip()))
            if ('📍' in strings[i] and '👊' in strings[i]):
                self.raidlocation = int(strings[i].split('👣')[1].split('км.')[0])
                self.raid = strings[i].split('📍')[1].split('👊')[0].strip()
            if ('🏵' in strings[i]):
                if '/me' in text:
                    self.setDzen(int(strings[i].count('🏵')))
                else:
                    dzen_tmp = strings[i][1:2].strip()
                    if dzen_tmp == '':
                        self.setDzen(0)
                    elif (int(dzen_tmp) >=2):
                        self.setDzen(int(dzen_tmp)-1)

            i=i+1
        #print(self.toJSON())

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
    
    def getTimeByUserTimeZone(self, date: datetime.timestamp):
        dt = datetime.fromtimestamp(date)
        if self.getTimeZone():
            tz = datetime.strptime(self.getTimeZone(),"%H:%M:%S")
            dt = dt + timedelta(seconds=tz.second, minutes=tz.minute, hours=tz.hour)
        return dt.timestamp()

    def getBm(self):
        stat = normalize(self.force) + normalize(self.accuracy) + normalize(self.health) + normalize(self.charisma) + normalize(self.agility)
        return int(stat)

    def getRaidWeight(self):
        dzen = int(self.dzen)
        return int(self.getBm() + self.getBm() * dzen * 0.25)

    def getProfile(self):
        string = ''
        string = string + f'┌{self.name}\n'  
        string = string + f'├🏷 {self.login}\n'
        string = string + f'├{self.fraction}\n'
        
        if self.band:
            string = string + f'├🤟Банда: {self.band}\n'
        
        if self.location:
            timeZone = '+00:00'
            if self.timeZone:
                tz = datetime.strptime(self.timeZone,"%H:%M:%S")
                timeZone = f'+{str(tz.hour).zfill(2)}:{str(tz.minute).zfill(2)}'
            string = string + f'├📍{self.location}|⏰{timeZone}\n'
        else:
            string = string + f'├📍Скажи Джу: Я живу в ...\n'

        if self.ping == True:
            string = string + f'├🔔Пингуйте меня семеро!\n'
        else:
            string = string + f'├🔕Нихт!\n'
            
        if self.status:
            string = string + f'└😏Статус: {self.status}\n'
        else:
            string = string + f'└😏Статус: Пустынник\n'  


        string = string + f'\n'  
        string = string + f'┌📯Боевая мощь: '+ str(self.getBm()) +'\n'  
        string = string + f'├⚔{self.damage}|🛡{self.armor}|🏵{self.dzen}|\n'  
        string = string + f'├💪{self.force}|🔫{self.accuracy}|❤{self.health}|\n'
        string = string + f'├🗣{self.charisma}|🤸🏽‍{self.agility}|🔋{self.stamina}|\n'
        if self.raid:
            string = string + f'├👊{self.raid}\n'
        string = string + f'└🏋️‍♂️Вес на рейде: {self.getRaidWeight()}\n'
        string = string + f'\n'

        string = string + f'⏰{tools.getTimeEmoji(self.timeUpdate)} ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(self.getTimeByUserTimeZone(self.timeUpdate))) +'\n'
        if self.timeBan:
            if self.timeBan > datetime.datetime.now().timestamp():
                string = string + '☠️Забанен до ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(self.getTimeByUserTimeZone(self.timeBan))) +'\n'  
        return string

    def getLogin(self):
        return self.login

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

    def setHealth(self, health):
        self.health = health
    def getHealth(self):
        return self.health

    def setHunger(self, hunger):
        self.hunger = hunger
    def getHunger(self):
        return self.hunger

    def setDamage(self, damage):
        self.damage = damage
    def getDamage(self):
        return self.damage

    def setArmor(self, armor):
        self.armor = armor    
    def getArmor(self):
        return self.armor

    def setForce(self, force):
        self.force = force  
    def getForce(self):
        return self.force

    def setAccuracy(self, accuracy):
        self.accuracy = accuracy  
    def getAccuracy(self):
        return self.accuracy

    def setCharisma(self, charisma):
        self.charisma = charisma  
    def getCharisma(self):
        return self.charisma
        
    def setAgility(self, agility):
        self.agility = agility  
    def getAgility(self):
        return self.agility

    def setStamina(self, stamina):
        self.stamina = stamina  
    def getStamina(self):
        return self.stamina

    def setLocation(self, location):
        self.location = location  
    def getLocation(self):
        try:
            return self.location
        except:
            return None

    def setTimeZone(self, timeZone):
        self.timeZone = timeZone  
    def getTimeZone(self):
        try:
            return self.timeZone
        except:
            return None

    def setDzen(self, dzen):
        self.dzen = dzen  
    def getDzen(self):
        return self.dzen

    def setRaid(self, raid):
        self.raid = raid  
    def getRaid(self):
        return self.raid

    def setRaidLocation(self, raidlocation):
        self.raidlocation = raidlocation  
    def getRaidLocation(self):
        return self.raidlocation

    def setStatus(self, status):
        self.status = status  
    def getStatus(self):
        return self.status
        
    def setPing(self, ping):
        self.ping = ping  
    def isPing(self):
        return self.ping

# ------------------------------------------
    def setTimeBan(self, timeBan):
        self.timeBan = timeBan  
    def getTimeBan(self):
        return self.timeBan

    def setTimeUpdate(self, timeUpdate):
        self.timeUpdate = timeUpdate  
    def getTimeUpdate(self):
        return self.timeUpdate