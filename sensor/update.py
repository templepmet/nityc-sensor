import psycopg2
import urllib2
import time

while True:
    try:
        f = urllib2.urlopen('https://www.google.co.jp/')
        f.close()
        break
    except urllib2.URLError:
        time.sleep(1)
        continue

# LINE push インターネットに接続されました

dbname = 'dendqdv36g7fdk'
host = 'ec2-54-83-33-213.compute-1.amazonaws.com'
user = 'mtpehusphjyvqw'
password = '4701aeae2673ea67c522eddcf2df2335ba1c9efb2cbeb64660cc0ad6ea3a0fc0'
command = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

conn = psycopg2.connect(command)
cursor = conn.cursor()

try:
    while True:
        cursor.execute('update update set time = current_timestamp where id = 1;')
        conn.commit()
        time.sleep(1)
except KeyboardInterrupt:
    cursor.close()
    conn.close()