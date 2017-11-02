from flask import Flask
from models import db

app = Flask(__name__)

app.config['DEBUG'] = True

POSTGRES = {
        'user': 'dgillman',
        'pw': 'rufus',
        'db': 'mydb',
        'host': 'localhost',
        'port': '5432',
    }
app.config['SQLALCHEMY_DATABASE_URI'] = \
                'postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s' % POSTGRES

db.init_app(app)

from views import *

if __name__ == '__main__':
    #app.debug = True
    app.run(host='0.0.0.0')
