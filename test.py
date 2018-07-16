import psycopg2
import time

dbname = 'dendqdv36g7fdk'
host = 'ec2-54-83-33-213.compute-1.amazonaws.com'
user = 'mtpehusphjyvqw'
password = '4701aeae2673ea67c522eddcf2df2335ba1c9efb2cbeb64660cc0ad6ea3a0fc0'
command = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

conn = psycopg2.connect(command)
cursor = conn.cursor()

cursor.execute('select time from update where id = 1')
(res, ) = cursor.fetchone()
print res

cursor.close()
conn.close()