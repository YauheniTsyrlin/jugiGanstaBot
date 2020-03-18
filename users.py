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
    if hasattr(newUser, 'wastelandLocation'):
        oldUser.wastelandLocation = newUser.wastelandLocation
    if newUser.dzen:
        oldUser.dzen = newUser.dzen
    if newUser.timeUpdate:
        oldUser.timeUpdate = newUser.timeUpdate

    if hasattr(newUser, 'timeBan'):
        oldUser.timeBan = newUser.timeBan

    if hasattr(newUser, 'ping'):
        if newUser.ping == None:
            pass
        else:
            oldUser.ping = newUser.ping
    if hasattr(newUser, 'chat'):
        if newUser.chat:
            oldUser.chat = newUser.chat

    if hasattr(newUser, 'birthday'):
        if newUser.birthday:
            oldUser.birthday = newUser.birthday

    if hasattr(newUser, 'accessory'):
        if newUser.accessory:
            oldUser.accessory = newUser.accessory
    
    if hasattr(newUser, 'settings'):
        if newUser.settings:
            oldUser.settings = newUser.settings

    if hasattr(newUser, 'maxkm'):
        if newUser.maxkm:
            if oldUser.maxkm == None:
                oldUser.maxkm = newUser.maxkm
            elif oldUser.maxkm < newUser.maxkm: 
                oldUser.maxkm = newUser.maxkm

    if hasattr(newUser, 'rank'):
        if newUser.rank:
            oldUser.rank = newUser.rank

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
    try:
        u.setPing(registered_user['ping'])
    except:
        u.setPing(True)
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
    if (registered_user.get('chat')):    
        u.chat     = registered_user['chat']
    if (registered_user.get('accessory')):    
        u.accessory     = registered_user['accessory']
    if (registered_user.get('settings')):    
        u.settings     = registered_user['settings']
    u.setRaidLocation(registered_user['raidlocation'])
    if (registered_user.get('wastelandLocation')):
        u.setWastelandLocation(registered_user['wastelandLocation'])
    if (registered_user.get('maxkm')):
        u.setMaxkm(registered_user['maxkm'])
    if (registered_user.get('birthday')):
        u.setBirthday(registered_user['birthday'])
    if (registered_user.get('rank')):
        u.setRank(registered_user['rank'])

    return u

class User(object):
    def __init__(self, login, date, text):
        i = 0
        self.login = login
        self.timeUpdate = date
        self.status = None
        self.dzen = 0
        self.band = None
        self.location = None
        self.timeZone = None
        self.timeBan  = None
        self.raid = None
        self.raidlocation = None
        self.wastelandLocation = None
        self.ping = None
        self.chat = None
        self.accessory = None
        self.settings = None
        self.maxkm = None
        self.birthday = None
        self.rank = None

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
            elif ('📍' in strings[i]):
                self.wastelandLocation = int(strings[i].split('👣')[1].split('км.')[0])
                self.setMaxkm(self.wastelandLocation)
                
            if ('🏵' in strings[i]):
                if '/me' in text:
                    self.setDzen(int(strings[i].count('🏵')))
                else:
                    dzen_tmp = strings[i][1:].split(' ')[0].strip()
                    if dzen_tmp == '':
                        self.setDzen(0)
                    elif (int(dzen_tmp) >=2):
                        self.setDzen(int(dzen_tmp)-1)

            i=i+1

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
        if self.rank:
            string = string + f'├🥋Звание: {self.getRankName()}\n'
     
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
        if self.birthday:
            string = string + f'├🥳День рождения: {time.strftime("%d %b", time.gmtime(self.birthday))}\n'
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
        elif self.getMaxkm():
            string = string + f'├👣Был замечен на {self.getMaxkm()}км\n'
        if self.raidlocation:
            tmpkm = f'{self.raidlocation}'
            if self.raidlocation == 1:
                tmpkm = f'?'
            string = string + f'├👊На рейде на {tmpkm}км\n'

        string = string + f'└🏋️‍♂️Вес на рейде: {self.getRaidWeight()}\n'
        string = string + f'\n'
        
        string = string + self.getSettingsReport() + '\n'


        string = string + f'🛒Аксессуары:\n'
        if self.accessory and len(self.accessory) > 0:
            for acc in self.accessory:
                string = string + f'▫️ {acc}\n'
            string = string + f'\n'
        else:
            string = string + f'▫️ У тебя ничего нет\n\n'

        string = string + f'⏰{tools.getTimeEmoji(self.timeUpdate)} ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(self.getTimeByUserTimeZone(self.timeUpdate))) +'\n'
        if self.timeBan:
            if self.timeBan > datetime.now().timestamp():
                string = string + '☠️Забанен до ' + time.strftime("%d-%m-%Y %H:%M:%S", time.gmtime(self.getTimeByUserTimeZone(self.timeBan))) +'\n'  
        return string

    def getLogin(self):
        return self.login

    def setName(self, name):
        self.name = tools.deEmojify(name)
    def getName(self):
        return self.name

    def getNameAndGerb(self):
        gerb = self.getSettingValue(name="🃏Мой герб")
        if gerb == None: gerb = ''
        return gerb+self.name

    def setFraction(self, fraction):
        self.fraction = fraction
    def getFraction(self):
        return self.fraction

    def setBand(self, band):
        self.band = band
        
    def getBand(self):
        return self.band

    def setHealth(self, health):
        self.health = int(health)
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

    def setWastelandLocation(self, wastelandLocation):
        self.wastelandLocation = wastelandLocation  
    def getWastelandLocation(self):
        return self.wastelandLocation

    def setMaxkm(self, maxkm):
        if self.maxkm == None:
            self.maxkm = maxkm
        elif maxkm > self.maxkm:
            self.maxkm = maxkm   
    def getMaxkm(self):
        if self.maxkm == None: 
            return 0
        return self.maxkm

    def setStatus(self, status):
        self.status = status  
    def getStatus(self):
        return self.status
        
    def setPing(self, ping):
        self.ping = ping
    def isPing(self):
        return self.ping

    def setChat(self, chat):
        self.chat = chat  
    def getChat(self):
        return self.chat

    def setBirthday(self, birthday):
        self.birthday = birthday  
    def getBirthday(self):
        return self.birthday

    def setRank(self, rank):
        self.rank = rank  
    def getRank(self):
        return self.rank
    def getRankName(self):
        return self.rank['value']

    def setAccessory(self, accessory):
        self.accessory = accessory  
    def getAccessory(self):
        if self.accessory == None:
            self.accessory = []
        return self.accessory

    def getAccessoryReport(self):
        accessory = ''
        if self.accessory and len(self.accessory)>0:
            for acc in self.accessory:
                accessory = accessory + f'▫️ {acc}\n'
        if not accessory == '':
            return accessory
        else:
            return 'Ничего нет'
    def isAccessoryItem(self, accessoryItem: str):
        if self.accessory == None:
            self.accessory = []

        find = False
        for acc in self.accessory:
            if acc == accessoryItem:
                find = True
                break
        return find
    def addAccessory(self, accessoryItem: str):
        if self.accessory == None:
            self.accessory = []
        find = False
        for acc in self.accessory:
            if acc == accessoryItem:
                find = True
                break
        if not find:
            self.accessory.append(accessoryItem)
    def removeAccessory(self, accessoryItem: str):
        if self.accessory == None:
            self.accessory = []
            
        if self.isAccessoryItem(accessoryItem):
            self.accessory.remove(accessoryItem)

    def setSettings(self, settings):
        self.settings = settings  
    def getSettings(self):
        if self.settings == None:
            self.settings = []
        return self.settings
    def getSettingsReport(self):
        result = ''
        if self.settings and len(self.settings)>0:
            for setting in self.settings:
                value = setting["value"]
                if value == True:
                    value = 'Да'
                elif value == False:
                    value = 'Нет'

                result = result + f'▫️ {setting["name"]}: {value}\n'
        if not result == '':
            return f'📋Личные настройки (/usset):\n'+result
        else:
            
            return f'📋Личные настройки (/usset):\n▫️ Ничего нет' + '\n'
    def addSettings(self, settingItem: str):
        if self.settings == None:
            self.settings = []
        find = False
        for setting in self.settings:
            if setting["name"] == settingItem["name"]:
                setting.update({'value': settingItem["value"]})
                find = True
        if not find:
            self.settings.append(settingItem)
    def getSettingValue(self, name=None, id=None):
        if self.settings == None:
            self.settings = []
        for setting in self.settings:
            try:
                if id:
                    if setting["id"] == id:
                        return setting["value"]
                elif name:
                    if setting["name"] == name:
                        return setting["value"]
            except: pass
        return None
    def removeSettings(self, settingItem: str):
        if self.settings == None:
            self.settings = []
        
        sett = None
        for setting in self.settings:
            if setting["name"] == settingItem:
                sett = setting
                break

        if not (sett == None):
            self.settings.remove(sett)
# ------------------------------------------
    def setTimeBan(self, timeBan):
        self.timeBan = timeBan  
    def getTimeBan(self):
        return self.timeBan

    def setTimeUpdate(self, timeUpdate):
        self.timeUpdate = timeUpdate  
    def getTimeUpdate(self):
        return self.timeUpdate