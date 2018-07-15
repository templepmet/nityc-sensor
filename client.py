import urllib 
def post_message(t, p, h):
    print('post')
    data = {}
    data["temp"] = t
    data["pres"] = p
    data["hum"]  = h
    # server_addr = 'https://nityc-sensor.herokuapp.com/info'
    server_addr = 'http://localhost:5000'
    try:
        data = urllib.urlencode(data).encode("utf-8")
        res = urllib.urlopen(server_addr, data=data)
        res = res.read().decode("utf-8")
        print 999
        print(res)
    except:
        print 10000
        print('error')

post_message(10, 20, 30)