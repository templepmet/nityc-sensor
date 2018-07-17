# coding:utf-8

import psycopg2
# from mcp3208 import MCP3208
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

while True:
    try:
        f = urllib2.urlopen('https://www.google.co.jp/')
        f.close()
        break
    except urllib2.URLError:
        time.sleep(1)
        continue

YOUR_CHANNEL_ACCESS_TOKEN = '82eIcjfdECiB+fKT2PDaFrpz/6sOYXGwIvFMqeIuH2MLRojiHWR+t3/CuwPQvU950VvrGi8Wf3QrU7koZDly3rbl1k9Lhp0xFQDSMZof1mtGY78+oulAlKMgKTxgltFSuIN8Rhkoz1C/oimGs38cagdB04t89/1O/w1cDnyilFU='
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)

dbname = 'dendqdv36g7fdk'
host = 'ec2-54-83-33-213.compute-1.amazonaws.com'
user = 'mtpehusphjyvqw'
password = '4701aeae2673ea67c522eddcf2df2335ba1c9efb2cbeb64660cc0ad6ea3a0fc0'
command = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

conn = psycopg2.connect(command)
cur = conn.cursor()

# adc = MCP3208()

cur.execute('select * from update')
ele = cur.fetchone()
print ele

cur.close()
conn.close()
