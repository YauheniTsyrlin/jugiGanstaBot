import emoji

def deEmojify(inputString):
    ''' Delete emoji'''
    return emoji.get_emoji_regexp().sub(r'', inputString.decode('utf8'))