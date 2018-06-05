from flask import Flask, render_template, redirect, url_for, request, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json
import datetime
import requests
import bcrypt

app = Flask(__name__)

app.secret_key = os.urandom(30)
#salt = bcrypt.gensalt(14)
#print(salt)
salt = b'$2b$14$LuZHIFa5Gx8/4FNWI4WOBe'


try:
	print("Connecting to database")
	cluster_uri = "mongodb+srv://analytics:analytics-password@mycluster-zuqqr.mongodb.net/test?retryWrites=true"
	client = MongoClient(cluster_uri)
	db = client['test']
	print("Connected to Atlas")
except:
	print("Could not connect")

users = db.users

@app.route('/')
def index():
	return render_template('index.html')



@app.route('/create', methods=['POST'])
def create():
	username = request.form['username']
	email = request.form['email']
	p_word = request.form['password']
	psword = p_word.encode('utf-8')
	password = bcrypt.hashpw(psword, salt)

	new_user = {
		'username': username,
		'email': email,
		'password': password
	}
	user = users.find_one({'username': username})
	if user is not None:
		flash("Username already taken")
		return render_template('login.html')

	try:
		users.insert_one(new_user)
		print("acc created")
		flash("Account created, login to continue")
		return render_template('login.html', user=new_user)
	except:
		print("Could not create")
		flash("User could not be created")
		return render_template('login.html')


@app.route('/login',methods=['POST'])
def login():
	username = request.form['username']
	p_word = request.form['password']
	psword = p_word.encode('utf-8')
	user = users.find_one({'username': username})

	if user is not None:
		password_chk = bcrypt.hashpw(psword, salt)
		if password_chk == user['password']:
			return render_template('index.html')
		else:
			flash("Wrong password")
			return redirect(url_for('login'))
	else:
		flash("User does not exists")
		return redirect(url_for('login'))

@app.route('/reddit',methods=['GET'])
def reddit():
	news_stories = db.reddit.find().sort({'created': -1})
	return render_template('index.html',news_stories=news_stories)

@app.route('/reddit/new')
def reddit_new():
	url = "http://www.reddit.com/r/technology/.json"
	header = {'user-agent': 'r_superbot by gravity'}
	resp = requests.get(url,headers=header)
	doc = resp.json()
	for item in doc['data']['children']:
		pipeline = {
			'id': item['data']['id'],
			'subreddit': item['data']['subreddit'],
			'title': item['data']['title'],
			'link': item['data']['url'],
			'name': item['data']['name'],
			'likes': item['data']['likes'],
			'domain': item['data']['domain'],
			'created': datetime.datetime.fromtimestamp(item['data']['created'])
		}
		db.reddit.insert(pipeline)

	flash("Database updated")
	return redirect(url_for('reddit'))

@app.route('/reddit/delete/<reddit_id>',methods=['GET'])
def reddit_delete():
	result = db.reddit.deleteOne({'_id': ObjectId(reddit_id)})
	flash("Reddit article removed")
	return redirect(url_for('reddit'))

