import psycopg2
from flask import render_template

from theapp import app

@app.route('/')
def index():
    return '<h1>hello world!</h1>'

@app.route('/query')
def query():

    conn_string = "host='localhost' dbname='postgres' user='postgres' password='rufus'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    cursor.execute("select * from stations;")
    records = cursor.fetchall()

    return str(records)

@app.route('/home', methods=['GET', 'POST'])
@app.route('/home/<name>')
def home(name=None):
    if(name!=None):
	return '<h1>'+name+'</h1>'
    return render_template("home.html")

@app.route('/sample')
def sample():
    return render_template("sample.html")
