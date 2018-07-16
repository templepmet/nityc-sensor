import psycopg2
import time
import datetime

dbname = 'dendqdv36g7fdk'
host = 'ec2-54-83-33-213.compute-1.amazonaws.com'
user = 'mtpehusphjyvqw'
password = '4701aeae2673ea67c522eddcf2df2335ba1c9efb2cbeb64660cc0ad6ea3a0fc0'
command = 'dbname=%s host=%s user=%s password=%s' % (dbname, host, user, password)

conn = psycopg2.connect(command)
cursor = conn.cursor()

print datetime.datetime.now()

time1 = '2018-07-16 13:15:53.443845'

cursor.execute('select time from update where id = 1')
(time2, ) = cursor.fetchone()
print time1
print time2

new_time1 = datetime.datetime.strptime(time1, '%Y-%m-%d %H:%M:%S.%f')
comp = datetime.timedelta(seconds=2)

res = new_time1.strftime('%Y-%m-%d %H:%M:%S.%f') + '\n' + time2.strftime('%Y-%m-%d %H:%M:%S.%f')
print res

print new_time1 - time2

if comp > new_time1 - time2:
    print 1
else:
    print 0

cursor.close()
conn.close()