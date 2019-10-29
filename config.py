POLLING = True
#POLLING = False
TOKEN = '467660905:AAHwK7_rmUdLkJXYyWTGmo7nuPFN2JXzIj8'  # FriendBrotherBot
#TOKEN = '963853904:AAECmtc5yXG9JRIp0-5v1Rl8VCAoskdbjps' # JugiGanstaBot
AI_TOKEN = 'a1cfca26418644cb91966ca22c57df8e'

STIKER_GET_HAND = 'AAQCAAPqBgACfAUHG11GAAGv5PjLJYs5_w0ABAEAB20AA8p4AAIWBA'

ANECDOT_URL = 'http://rzhunemogu.ru/RandJSON.aspx?CType'
WEATHER_URL = 'http://rzhunemogu.ru/RandJSON.aspx?CType'

WEBHOOK_HOST = 'thegangsters.ru'
WEBHOOK_PORT = 8443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = 'thegangsters.ru'  # In some VPS you may need to put here the IP addr

WEBHOOK_SSL_CERT = '/home/godfather/ssl/ssl-bundle.crt'  # Path to the ssl certificate
WEBHOOK_SSL_PRIV = '/home/godfather/ssl/thegangsters.key'  # Path to the ssl private key

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(TOKEN)