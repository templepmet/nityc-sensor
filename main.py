# coding:utf-8

from flask import Flask, request, abort
import datetime

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
import os
import psycopg2

dbname = 'dendqdv36g7fdk'
host = 'ec2-54-83-33-213.compute-1.amazonaws.com'
user = 'mtpehusphjyvqw'
password = '4701aeae2673ea67c522eddcf2df2335ba1c9efb2cbeb64660cc0ad6ea3a0fc0'
command = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

app = Flask(__name__)

YOUR_CHANNEL_ACCESS_TOKEN = os.environ["YOUR_CHANNEL_ACCESS_TOKEN"]
YOUR_CHANNEL_SECRET = os.environ["YOUR_CHANNEL_SECRET"]
line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(YOUR_CHANNEL_SECRET)


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    res = 'hoge'

    sourceId = ''
    if isinstance(event.source, SourceUser):
        sourceId = event.source.user_id
    if isinstance(event.source, SourceGroup):
        sourceId = event.source.group_id
    if isinstance(event.source, SourceRoom):
        sourceId = event.source.room_id

    message = event.message.text
    if message == 'get':
        with psycopg2.connect(command) as conn:
            with conn.cursor() as cur:
                cur.execute('select time from update where id = 1')
                (client, ) = cur.fetchone()
                server = datetime.datetime.now()
                if datetime.timedelta(seconds=5) > server - client:
                    cur.execute('insert into request(source) values (%s)', (sourceId))
                    conn.commit()
                else:
                    res = 'RaspberryPiがインターネットに接続されていません'
    elif message == 'id':
        res = sourceId

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=res))

if __name__ == "__main__":
    # app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)