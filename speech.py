import uuid
import requests

from config import YANDEX_SPEECH_TOKEN
from config import YANDEX_CLOUD_CATALOG

import subprocess
import tempfile
import os

CHUNK_SIZE = 1024 ** 2

def speech_to_text(filename=None, bytes=None, request_id=uuid.uuid4().hex, topic='notes', lang='ru-RU',
                   key=YANDEX_SPEECH_TOKEN):
    # Если передан файл
    if filename:
        with open(filename, 'br') as file:
            bytes = file.read()
    if not bytes:
        raise Exception('Neither file name nor bytes provided.')

    # Считывание блока байтов
    chunks = read_chunks(CHUNK_SIZE, bytes)

  
    # connection.putheader('Transfer-Encoding', 'chunked')
    # connection.putheader('Content-Type', 'audio/x-pcm;bit=16;rate=16000')
    # connection.endheaders()

    # # Отправка байтов блоками
    # for chunk in chunks:
    #     connection.send(('%s\r\n' % hex(len(chunk))[2:]).encode())
    #     connection.send(chunk)
    #     connection.send('\r\n'.encode())

    # connection.send('0\r\n\r\n'.encode())
    # response = connection.getresponse()
    # print(bytes)
    #headers={'Authorization': f'Bearer {YANDEX_SPEECH_TOKEN}', 'Transfer-Encoding': 'chunked', 'Content-Type': 'audio/x-pcm;bit=16;rate=16000'}
    
    headers={'Authorization': f'Bearer {YANDEX_SPEECH_TOKEN}', 'Content-Type': 'audio/x-pcm;bit=16;rate=16000'}
    url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?lang={lang}&folderId={YANDEX_CLOUD_CATALOG}'
    response = requests.post(url, data=bytes, headers=headers)

    if response.status_code == 200:
        return response.json()['result']
    else:
        raise SpeechException('Unknown error.\nCode: %s\n\n%s' % (response.status_code, response.raise_for_status()))

# Создание своего исключения
class SpeechException(Exception):
    pass

def read_chunks(chunk_size, bytes):
    while True:
        chunk = bytes[:chunk_size]
        bytes = bytes[chunk_size:]

        yield chunk

        if not bytes:
            break