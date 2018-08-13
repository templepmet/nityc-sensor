# coding:utf-8

from flask import Flask, request, abort
import os
import datetime
import psycopg2

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
)

CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
DATABASE_URL = os.environ['DATABASE_URL']
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    if isinstance(event.source, SourceUser):
        source = event.source.user_id
    if isinstance(event.source, SourceGroup):
        source = event.source.group_id
    if isinstance(event.source, SourceRoom):
        source = event.source.room_id

    message = event.message.text
    res = ''
    if message == 'id':
        res = source
    else:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute('select time from update where id = 1')
                (client, ) = cur.fetchone()
                server = datetime.datetime.now()
                ele = message.split(',')
                if datetime.timedelta(seconds=10) > server - client:
                    keyword = None
                    if ele[0] == 'get':
                        if len(ele) > 1:
                            keyword = ele[1]
                        cur.execute('insert into request(source, keyword) values (%s, %s)', (source, keyword))
                        conn.commit()
                    elif ele[0] == 'start':
                        step = None
                        if len(ele) > 1:
                            step = ele[1]
                        if len(ele) > 2:
                            keyword = ele[2]
                        if step.isdigit() and step != '0':
                            cur.execute('insert into request(source, keyword, step) values (%s, %s, %s)', (source, keyword, step))
                    elif ele[0] == 'stop':
                        cur.execute('insert into request(source, step) values (%s, %s)', (source, '-1'))
                    elif ele[0] == 'shutdown':
                        cur.execute('insert into request(source, keyword) values (%s, %s)', (source, 'shutdown'))
                else:
                    if ele[0] in ['get', 'start', 'stop', 'shutdown']:
                        res = 'RaspberryPiがインターネットに接続されていません'

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)