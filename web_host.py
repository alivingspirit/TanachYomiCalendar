from flask import Flask, render_template

app = Flask(__name__, template_folder="./")
@ app.route ('/')
def index ():
    return render_template ('./results.html')
if __name__ == '__main__':
    app.debug = True
    #Where PermissionError
    app.run (host = '127.0.0.1', port = 8000)