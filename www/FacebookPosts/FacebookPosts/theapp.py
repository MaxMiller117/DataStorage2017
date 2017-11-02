from flask import Flask

app = Flask(__name__)

app.config['DEBUG'] = True

from views import *

if __name__ == '__main__':
    #app.debug = True
    app.run(host='0.0.0.0')
