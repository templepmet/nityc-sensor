from flask import Flask

app = Flask(__name__)

@app.route("/info", methods=['POST'])
def info():
    param_t = float(request.form['temp'])
    param_p = float(request.form['pres'])
    param_h = float(request.form['hum'])
    content = ' temp : {0:3.1f} deg \n hum  : {1:2.1f} % \n pres  : {2:4.1f} hPa '.format(param_t, param_h, param_p)
    return 'POST OK!'

if __name__ == "__main__":
    app.run()