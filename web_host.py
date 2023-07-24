from flask import Flask, render_template

import main

app = Flask(__name__)
TEMPLATES_AUTO_RELOAD = True

@app.route('/')
def index():
    return render_template('./calendar.html', days_data=main.get_days())


if __name__ == '__main__':
    app.debug = True
    # Where PermissionError
    app.run(host='127.0.0.1', port=8000)
