from flask import Flask, render_template, request, make_response, redirect, url_for
import userDBConnecter as db
import session_manager as sm
import base64
import bleach

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
    username = request.form['username']
    password = request.form['password']
    if request.form['login'] == 'signin':
        if db.check_user(username, base64.b64decode(str(password).encode('ascii'))):
            resp = make_response(redirect(url_for('appointments')))
            session_id = sm.create_session(username)
            resp.set_cookie('sessionID', str(session_id))
            resp.set_cookie('username', bleach.clean(username))
            return resp, 302
        else:
            return render_template('index.html', inserts=['login_warning.html']), 401
    elif request.form['login'] == 'signup':
        if db.create_user(username, base64.b64decode(str(password).encode('ascii'))):
            resp = make_response(redirect(url_for('appointments')))
            session_id = sm.create_session(username)
            resp.set_cookie('sessionID', str(session_id))
            resp.set_cookie('username', bleach.clean(username))
            return resp, 302
        else:
            return render_template('index.html', inserts=['login_warning.html']), 401


@app.route('/appointments')
def appointments():
    username = request.cookies.get('username')
    return render_template('appointments.html', user=username), 200


def create_new_cookie():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
