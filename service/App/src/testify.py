from flask import Flask, render_template, request
import userDBConnecter as db
import base64

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/make_appointment', methods=['POST'])
def make_appointment():
    print(request.form['prename'])
    print(request.form['lastname'])
    print(request.form['date'])
    return 'ok', 200


@app.route('/login', methods=['POST'])
def login():
    if request.form['login'] == 'signin':
        if db.check_user(request.form['username'], base64.b64decode(str(request.form['password']).encode('ascii'))):
            return render_template('appointments.html', user=request.form['username']), 200
        else:
            return render_template('index.html', inserts=['login_warning.html']), 401
    elif request.form['login'] == 'signup':
        if db.create_user(request.form['username'], base64.b64decode(str(request.form['password']).encode('ascii'))):
            return render_template('appointments.html', user=request.form['username']), 200
        else:
            return render_template('index.html', inserts=['login_warning.html']), 401


@app.route('/appointments')
def appointments():
    # TODO: check cookie
    return render_template('appointments.html', user=request.form['username']), 200


def create_new_cookie():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
