# coding:utf-8

# raspi側のプログラム
# linebotのプログラムを先に見ることを推奨します（コメントの都合）

# subprocess:shutdown実行用
# mcp3208:ADコンバータMCP3208用パッケージ（外部プログラム）
# Process:並列処理ライブラリ
import os
import time
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

# データベースに接続できるまで待機する
def waitDatabase():
    while True:
        try:
            with psycopg2.connect(DATABASE_URL) as conn:
                with conn.cursor() as cur:
                    pass
            break
        except psycopg2.OperationalError:
            time.sleep(1)
            continue

# センサ値を取得する
def getSensor():
    adc = MCP3208()
    cds = adc.read(0) * 5 / 4095.0
    uv = adc.read(1) * 5 / 4095.0
    return cds, uv

# 一定間隔に連続でセンサ値を取得する
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
                # 測定間隔ごとに送る
                line_bot_api.push_message(source, TextSendMessage(text=res))
                time.sleep(step)
        
if __name__ == '__main__':
    waitDatabase()
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            run = False # 連続測定中かどうか
            process = None
            while True:
                # 起動時間を更新
                cur.execute('update update set time = current_timestamp where id = 1')
                conn.commit()
                # リクエストをひとつずつ取得
                cur.execute('select * from request')
                row = cur.fetchone()
                if row is not None:
                    id = row[0]
                    source = row[1]
                    keyword = row[2]
                    step = row[3]
                    # 取得したリクエストを削除
                    cur.execute('delete from request where id = %s', (id,))
                    conn.commit()
                    if keyword == 'shutdown':
                        res = '3秒後にシャットダウンします'
                        line_bot_api.push_message(source, TextSendMessage(text=res))
                        time.sleep(3)
                        # 'shutdown'コマンドを実行
                        cmd = 'sudo shutdown -h now'
                        subprocess.call(cmd.split())

                    res = ''
                    if step is None:
                        cds, uv = getSensor()
                        # 測定値を保存（テーブルに記録）
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
                                # メインループと並列して連続測定を行う
                                process = Process(target=serial, args=(source, keyword, step))
                                process.start()
                            run = True
                        elif int(step) < 0:
                            if run:
                                res = '測定を停止しました'
                                # 連続測定を終了
                                process.terminate()
                                process.join()
                            else:
                                res = '測定を開始していません'
                            run = False
                    line_bot_api.push_message(source, TextSendMessage(text=res)) # メッセージの送信（返信ではない）

                time.sleep(0.5)