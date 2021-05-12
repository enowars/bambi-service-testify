from flask import Flask, render_template, request, make_response, redirect, url_for
import userDBConnecter as db
import session_manager as sm
import appointments_manager as am
import base64
import bleach

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/make_appointment', methods=['POST'])
def make_appointment():
    session_id = request.cookies.get('sessionID')
    prename = request.form.get('prename')
    lastname = request.form.get('lastname')
    date = request.form.get('date')
    time = request.form.get('time')

    if session_id and prename and lastname and date and time:
        appointment = {
            'name': prename + ' ' + lastname,
            'extra_info': 'empty',
            'date': date,
            'time': time
        }
        am.set_appointment(session_id, appointment)
    return redirect(url_for('appointments'))


@app.route('/login', methods=['POST'])
def login():
    request.form.get('username')
    username = request.form.get('username')
    password = request.form.get('password')
    login_type = request.form.get('login')
    email = request.form.get('email')

    if username and password and login_type:
        if login_type == 'signin':
            if db.check_user(username, base64.b64decode(str(password).encode('ascii'))):
                resp = make_response(redirect(url_for('appointments')))
                session_id = sm.create_session(username)
                resp.set_cookie('sessionID', str(session_id))
                resp.set_cookie('username', bleach.clean(username))
                return resp, 302
            else:
                return render_template('index.html', inserts=['login_warning.html']), 401
        elif login_type == 'signup':
            if email:
                if db.create_user(username, base64.b64decode(str(password).encode('ascii')), email):
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
    session_id = request.cookies.get('sessionID')

    if username and session_id:
        if sm.check_session_id(session_id):
            cards = am.get_appointments(session_id)
            return render_template('appointments.html', user=username, cards=cards), 200
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    username = request.cookies.get('username')
    session_id = request.cookies.get('sessionID')
    if username and session_id:
        resp = make_response(redirect(url_for('index')))
        resp.delete_cookie('sessionID')
        resp.delete_cookie('username')
        return resp, 302


@app.route('/restore_username')
def restore_username():
    pass


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True) # TODO: remove debug later
