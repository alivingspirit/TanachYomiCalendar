from flask import Flask, render_template, jsonify, send_file

import main

app = Flask(__name__)
TEMPLATES_AUTO_RELOAD = True

@app.route('/')
def index():
    return render_template('./calendar.html', days_data=main.get_days())


@app.route('/data')
def data():
    return jsonify(list(main.get_days()))


@app.route('/calculation.json')
def calculation():
    return send_file('./calculation.json')


if __name__ == '__main__':
    app.debug = True
    # Where PermissionError
    app.run(host='127.0.0.1', port=8000)
