from flask import Flask, render_template, request, make_response, redirect, url_for, send_file
import userDBConnecter as db
import session_manager as sm
import appointments_manager as am
import forgotUsername as fu
import base64
import bleach
import online_users as ou

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
    extra = request.form.get('extra')
    doctor = request.form.get('doctor')
    file = request.files.get('id_image')

    appointment_id = None

    if session_id and prename and lastname and date and time and doctor:
        appointment = {
            'name': prename + ' ' + lastname,
            'extra_info': extra if extra else '',
            'date': date,
            'time': time,
            'filename': file.filename if file else None,
            'doctor': doctor
        }
        appointment_id = am.set_appointment(session_id, appointment, file)
    if appointment_id:
        return redirect(url_for('appointments', app_id=appointment_id, status='success'))
    else:
        return redirect(url_for('appointments', status='fail'))


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
            inserts, message = None, None
            status = request.args.get('status')
            app_id = request.args.get('app_id')
            if status:
                inserts = ['success.html'] if status == 'success' else ['failed.html']
                message = "Successfully made appointment <%s>" % app_id if app_id else "Could not make appointment"
            return render_template('appointments.html', user=username, cards=cards, inserts=inserts, message=message), 200
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/about')
def about():
    users = ou.get_online_users()
    return render_template('about.html', online_users='  -  '.join(users))


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
    return render_template('restore_username.html')


@app.route('/restore_username', methods=['POST'])
def restore_username_POST():
    email = request.form.get('email')
    if email:
        username = fu.get_username_for_email(email)
        if username:
            return render_template('restore_username.html', inserts=['username_success.html'],
                                   username=fu.get_username_for_email(email))
        else:
            return render_template('restore_username.html', inserts=['username_failed.html'],
                                   email=email)


@app.route('/get_id<appointment_id>')
def get_id(appointment_id):
    session_id = request.cookies.get('sessionID')
    if session_id and appointment_id:
        path = am.get_id_file(session_id, appointment_id)
        if path:
            return send_file(path, as_attachment=True)
    return "session and appointment id do not match or no ID uploaded!", 403


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
