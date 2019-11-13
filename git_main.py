import logging
import ssl
import sys
import apiai, json
import requests
import telebot
from aiohttp import web
import config
from subprocess import call

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


def main_loop():
    app = web.Application()
    async def commit(request):
        logger.info('getCommit from webHook gitHub')
        if request.match_info.get('token') == config.TOKEN:
            request_body_dict = await request.json()
            logger.info('clone to /foo repository : ' + request_body_dict['repository']['full_name'])
            call('git clone https://github.com/gonzikbenzyavsky/jugiGanstaBot.git /home/godfather/foo', shell=True)
            logger.info('moving *.py to jugiGanstaBot')
            call('mv /home/godfather/foo/*.py /home/godfather/jugiGanstaBot', shell=True)
            logger.info('remove /foo')
            call('rm -rf /home/godfather/foo', shell=True)
            logger.info('restar bot')
            call('sudo systemctl restart bot', shell=True)
            logger.info('OK')
            return web.Response()
        else:
            return web.Response(status=403)

    app.router.add_route('*', '/{token}/commit', commit, name='commit')
    
    # Build ssl context
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.load_cert_chain(config.WEBHOOK_SSL_CERT, config.WEBHOOK_SSL_PRIV)
    # Start aiohttp server
    web.run_app(
        app,
        host=config.WEBHOOK_LISTEN,
        port=8444,
        ssl_context=context,
    )

if __name__ == '__main__': 
    try:
        main_loop()
        
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)