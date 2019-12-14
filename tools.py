import emoji
from datetime import timedelta
from datetime import datetime

def deEmojify(inputString):
    ''' Delete emoji'''
    return emoji.get_emoji_regexp().sub(r'', inputString)

def getTimeEmoji(time):
    if time > (datetime.now() - timedelta(days=7)).timestamp():
        return '👶'
    elif time > (datetime.now() - timedelta(days=14)).timestamp():
        return '👦'
    elif time > (datetime.now() - timedelta(days=28)).timestamp():
        return '👨'
    elif time > (datetime.now() - timedelta(days=56)).timestamp():
        return '👨‍🦳'
    else:
        return '👴'