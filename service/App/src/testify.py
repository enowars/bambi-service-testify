from flask import Flask, render_template, request
import userDBConnecter as db

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
    print(request.form['username'])
    print(request.form['password'])
    print(request.form['login'])
    if request.form['login'] == 'Sign in':
        if db.check_user(request.form['username'], request.form['password']):
            return 'login success', 200
        else:
            return 'login failure', 401
    elif request.form['login'] == 'Sign up':
        if db.create_user(request.form['username'], request.form['password']):
            return 'login success', 200
        else:
            return 'login failure', 401


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
