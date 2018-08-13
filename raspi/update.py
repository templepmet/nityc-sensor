# coding:utf-8

import psycopg2
from mcp3208 import MCP3208
import urllib2
import time

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

from multiprocessing import Process
import subprocess

while True:
    try:
        f = urllib2.urlopen('https://www.google.co.jp/')
        f.close()
        break
    except urllib2.URLError:
        time.sleep(1)
        continue

adc = MCP3208()

YOUR_CHANNEL_ACCESS_TOKEN = '82eIcjfdECiB+fKT2PDaFrpz/6sOYXGwIvFMqeIuH2MLRojiHWR+t3/CuwPQvU950VvrGi8Wf3QrU7koZDly3rbl1k9Lhp0xFQDSMZof1mtGY78+oulAlKMgKTxgltFSuIN8Rhkoz1C/oimGs38cagdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

dbname = 'dendqdv36g7fdk'
host = 'ec2-54-83-33-213.compute-1.amazonaws.com'
user = 'mtpehusphjyvqw'
password = '4701aeae2673ea67c522eddcf2df2335ba1c9efb2cbeb64660cc0ad6ea3a0fc0'
command = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

conn = psycopg2.connect(command)
cur = conn.cursor()
cur.execute('delete from request')
conn.commit()

process = None
def serial(source, keyword, step):
    conn2 = psycopg2.connect(command)
    cur2 = conn2.cursor()
    num = 1
    while True:
        cds = adc.read(0) * 5 / 4095.0
        uv = adc.read(1) * 5 / 4095.0
        key_t = keyword
        if key_t is None:
            key_t = ''
        key_t += '(' + str(num) + ')'
        num += 1
        cur2.execute('insert into value(cds, uv, keyword) values (%s, %s, %s)', (cds, uv, key_t))
        conn2.commit()

        res = 'CdS:%.2f\nUV:%.2f' % (cds, uv)
        if key_t is not None:
            res = key_t + '\n' + res
        line_bot_api.push_message(source, TextSendMessage(text=res))
        time.sleep(int(step))

try:
    run = False
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
                cds = adc.read(0) * 5 / 4095.0
                uv = adc.read(1) * 5 / 4095.0
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

except KeyboardInterrupt:
    cur.close()
    conn.close()