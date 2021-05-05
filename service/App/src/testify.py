from flask import Flask, render_template, json, request

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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000)
