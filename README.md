# nityc-sensor
get value of sensor and send LINE from linebot

## Description
センサ値を取得、LINEbotを介して送受信する。

## Requirement
### Hardware
*Raspberry Pi (Wi-Fi搭載)
*MCP3208 (A/Dコンバータ)
### Software
*heroku
*PostgreSQL (Herokuの)
*RASPBIAN STRETCH LITE

## Usage
*'get'送信でセンサ値が返信
*'get,キーワード'送信でキーワード付きでセンサ値が返信
*'start,秒数'送信で秒数ごとにセンサ値が返信
*'shutdown'送信でRaspiをシャットダウンさせる

## Installation
raspiディレクトリはRaspiでのみ使用する、それ以外はherokuにデプロイ
main.pyはherokuの環境変数を使用するため設定する必要がある
raspi/update.pyはローカル(Raspi)で環境変数を使用するためこちらも設定
*以下、インターネットで調べること強く推奨*
LINEbotを作成するためのアカウントを作成
MessagingAPIの設定でWebhookURLをherokuのアプリケーションURLに設定
Raspi側はraspi/update.pyを実行
Raspiの起動時に自動実行させたい場合はcrontab @rebootがおすすめ

## Anything Else
エディタはVSCodeがおすすめ
VSCodeのアドオンであるSFTPをインストールすることでRaspiとファイル共有ができる
VSCode上でターミナルを開きRaspiにssh接続することで、ファイルを編集しながら実行が簡単にできる

## License
[MIT](https://github.com/templepmet/nityc-sensor/blob/master/LICENSE)