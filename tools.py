import emoji
from datetime import timedelta
from datetime import datetime

def isOneEmojify(inputString):
    return emoji.emoji_count(inputString) == 1

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

def huificate(uword: str):
    letter = 0
    slogi = []
    range = 0
    slovar = [[u"а", u"я"], [u"я", u"я"], [u"е", "е"], [u"о", u"е"], [u"и", u"и"], [u"ё", u"ё"], [u"ы", u"и"], [u"ю", u"ю"], [u"у", u"ю"]]
    for i in uword:
        if i == u"а" or i== u"е" or i== u"ё" or i== u"и" or i== u"о" or i== u"у" or i== u"э" or i== u"ю" or i==u"ы" or i== u"я":
            slogi.append(uword[range: letter+1])
            range=letter+1
        letter +=1
    slogi.append(uword[range:])

    sloge = [x for x in slogi if x]

    endword = u"ху"
    endbutton = u"е"

    if len(sloge) < 4:
        for l in sloge[0][0:]:
            for m in slovar:
                if l==m[0]:
                    endbutton = m[1]
        endword +=endbutton
        for k in sloge[1:]:
            endword = endword + k

    if len(sloge) >3:
        for l in sloge[1][0:]:
            for m in slovar:
                if l==m[0]:
                    endbutton = m[1]
        endword +=endbutton
        for k in sloge[2:]:
            endword = endword + k
    return endword