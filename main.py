# coding:utf-8

# linebotプログラム
# 公式サンプルを参考に記述<https://github.com/line/line-bot-sdk-python>
# ブロックにコメントを書いていない箇所はサンプル通り

# psycopg2:PostgreSQLに接続するモジュール
# flask:webアプリケーションフレームワーク
# linebot:LINE MessagingAPI
import os
import datetime
import psycopg2
from flask import Flask, request, abort

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

# os.environでherokuに設定した環境変数を取得
CHANNEL_ACCESS_TOKEN = os.environ['CHANNEL_ACCESS_TOKEN']
CHANNEL_SECRET = os.environ['CHANNEL_SECRET']
DATABASE_URL = os.environ['DATABASE_URL']

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

# linebotの設定で"[herokuのURL]/callback"にアクセスするように設定
@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 送信元のid（これがわかれば送り返せる一意なもの）を取得
    if isinstance(event.source, SourceUser):
        source = event.source.user_id
    if isinstance(event.source, SourceGroup):
        source = event.source.group_id
    if isinstance(event.source, SourceRoom):
        source = event.source.room_id

    message = event.message.text
    res = ''
    if message == 'id': # 'id'と送信したら
        res = source # 送信元idを返信する
    else:
        # 以下２行はデータベースに接続する定型文
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                cur.execute('select time from update where id = 1')
                (client, ) = cur.fetchone() # raspiの最終起動時間を取得
                server = datetime.datetime.now() # 現在時間を取得
                # 現在時間との差でraspiが起動しているか判定
                connected = False
                if datetime.timedelta(seconds=10) > server - client:
                    connected = True

                flag = False
                keyword = None
                ele = message.split(',') # 送信メッセージはカンマ指定→カンマで分割
                if ele[0] == 'get':
                    flag = True
                    if connected:
                        if len(ele) > 1: # キーワード付き
                            keyword = ele[1]
                        # requestテーブルにリクエストを追加
                        cur.execute('insert into request(source,keyword) values (%s,%s)', (source, keyword))
                        conn.commit()
                elif ele[0] == 'start':
                    flag = True
                    if connected:
                        step = None
                        if len(ele) > 1: # 測定間隔
                            step = ele[1]
                        if len(ele) > 2: # キーワード
                            keyword = ele[2]
                        if step.isdigit() and step > 0: # 測定間隔が自然数ならば
                            cur.execute('insert into request(source,keyword,step) values (%s,%s,%s)', (source, keyword, step))
                elif ele[0] == 'stop':
                    flag = True
                    if connected:
                        # stepを負にしてリクエストすることで測定を停止する
                        cur.execute('insert into request(source,step) values (%s,%s)', (source, '-1'))
                elif ele[0] == 'shutdown':
                    flag = True
                    if connected:
                        # keywordを'shutdown'にしてリクエストすることでシャットダウンする
                        cur.execute('insert into request(source,keyword) values (%s,%s)', (source, 'shutdown'))

                if flag and connected == False:
                    res = 'RaspberryPiがインターネットに接続されていません'

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=res)) # 返信

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)