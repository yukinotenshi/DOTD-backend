from flask import Flask


app = Flask(__name__)


@app.route('/')
def index():
    return 'DOTD Backend Service Runnning'


if __name__ == '__main__':
    app.run()
