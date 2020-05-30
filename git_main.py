import logging
import ssl
import sys
import time
import json
import requests
import telebot
from aiohttp import web
import config
from subprocess import call, check_output
import threading
from multiprocessing import Process

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

# Проверяем утилизацию памяти и делаем рестарт сервера, если > 85%
def job():
    try:
        result = check_output("grep MemAvailable /proc/meminfo", shell=True)
        available_mem = int(result.split(b'MemAvailable:')[1].split(b' kB')[0].strip())
        # logger.info(f'Mem Available: {available_mem}')

        result = check_output("grep MemTotal /proc/meminfo", shell=True)
        total_mem = int(result.split(b'MemTotal:')[1].split(b' kB')[0].strip())
        # logger.info(f'Mem total: {total_mem}')

        logger.info(f'Mem used: {int(available_mem/total_mem*100)}%')

        if int(available_mem/total_mem*100) <= 15: # Если свободной памяти осталось меньше 15%,
            logger.info(f'============= Вызываем рестарт сервера =============')
            call('sudo shutdown -r now', shell=True)
    except:
        logger.error(f'error CheckMem')

# 30 secund
def job_loop():
    while True:
        job()
        time.sleep(60)

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
            logger.info('update jugidb')
            call('/home/godfather/jugiGanstaBot/updexec.sh', shell=True)
            logger.info('restar bot Jugi')
            call('sudo systemctl restart bot', shell=True)
            logger.info('OK bot')

            # logger.info('restar bot Bozya')
            # call('sudo systemctl restart bozya', shell=True)
            # logger.info('OK Bozya')
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
        host=config.WEBHOOK_HOST,
        port=8444,
        ssl_context=context,
    )

if __name__ == '__main__': 
    try:

        proccessJob = Process(target=job_loop, args=())
        proccessJob.start() # Start new thread 

        main_loop()
        
    except KeyboardInterrupt:
        print('\nExiting by user request.\n')
        sys.exit(0)