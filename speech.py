import uuid
import requests

from config import YANDEX_SPEECH_KEY
from config import YANDEX_CLOUD_CATALOG

import subprocess
import tempfile
import os

CHUNK_SIZE = 1024 ** 2

def speech_to_text(filename=None, bytes=None, request_id=uuid.uuid4().hex, topic='notes', lang='ru-RU',
                   key=YANDEX_SPEECH_KEY):
    # Если передан файл
    if filename:
        with open(filename, 'br') as file:
            bytes = file.read()
    if not bytes:
        raise Exception('Neither file name nor bytes provided.')
    
    headers={
        'Authorization': f'Api-Key {YANDEX_SPEECH_KEY}',
        'Transfer-encoding':'chunked',
        'Content-Type': 'audio/x-pcm;bit=16;rate=16000'
        }

    url = f'https://stt.api.cloud.yandex.net/speech/v1/stt:recognize?lang={lang}&folderId={YANDEX_CLOUD_CATALOG}'
    response = requests.post(url, data=read_chunks(CHUNK_SIZE, bytes), headers=headers)

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