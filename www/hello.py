from flask import Flask
app = Flask(__name__)

@app.route('/FacebookPosts')
def hello_world():
	return 'Hello, Worldd!'
