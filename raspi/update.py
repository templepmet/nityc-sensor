# coding:utf-8

import os
import time
import urllib2
import psycopg2
import subprocess
from mcp3208 import MCP3208
from multiprocessing import Process

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
DATABASE_URL = os.environ['DATABASE_URL']
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

def waitInternet():
    while True:
        try:
            f = urllib2.urlopen('https://www.google.co.jp/')
            f.close()
            break
        except urllib2.URLError:
            time.sleep(1)
            continue

def getSensor():
    adc = MCP3208()
    cds = adc.read(0) * 5 / 4095.0
    uv = adc.read(1) * 5 / 4095.0
    return cds, uv

def serial(source, keyword, step):
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            num = 1
            while True:
                key_t = keyword
                if key_t is None:
                    key_t = ''
                key_t += '(' + str(num) + ')'
                cds, uv = getSensor()
                cur.execute('insert into value(cds, uv, keyword) values (%s, %s, %s)', (cds, uv, key_t))
                conn.commit()
                num += 1

                res = key_t + '\nCdS:%.2f\nUV:%.2f' % (cds, uv)
                line_bot_api.push_message(source, TextSendMessage(text=res))
                time.sleep(step)
        
if __name__ == '__main__':
    waitInternet()
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            run = False
            process = None
            while True:
                cur.execute('update update set time = current_timestamp where id = 1')
                conn.commit()
                cur.execute('select * from request')
                row = cur.fetchone()
                if row is not None:
                    id = row[0]
                    source = row[1]
                    keyword = row[2]
                    step = row[3]
                    cur.execute('delete from request where id = %s', (id,))
                    conn.commit()
                    if keyword == 'shutdown':
                        res = '3秒後にシャットダウンします'
                        line_bot_api.push_message(source, TextSendMessage(text=res))
                        time.sleep(3)
                        cmd = 'sudo shutdown -h now'
                        subprocess.call(cmd.split())

                    res = ''
                    if step is None:
                        cds, uv = getSensor()
                        cur.execute('insert into value(cds, uv, keyword) values (%s, %s, %s)', (cds, uv, keyword))
                        conn.commit()

                        res = 'CdS:%.2f\nUV:%.2f' % (cds, uv)
                        if keyword is not None:
                            res = keyword + '\n' + res
                    else:
                        if int(step) > 0:
                            if run:
                                res = '測定中です'
                            else:
                                res = '測定を開始しました'
                                process = Process(target=serial, args=(source, keyword, step))
                                process.start()
                            run = True
                        elif int(step) < 0:
                            if run:
                                res = '測定を停止しました'
                                process.terminate()
                                process.join()
                            else:
                                res = '測定を開始していません'
                            run = False
                    line_bot_api.push_message(source, TextSendMessage(text=res))

                time.sleep(0.5)