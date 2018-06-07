from flask import Flask, render_template, redirect, url_for, request, flash
from pymongo import MongoClient
#from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import os
import json
import datetime
import requests
import bcrypt
import random


app = Flask(__name__)
#mongo = PyMongo(app)

#MONGO_URI = "mongodb+srv://analytics:xxx@mycluster-zuqqr.mongodb.net/test?retryWrites=true"
#MONGO_DB = "test"



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
redditz = db.reddit


subreddits = {
	'Liverpool FC: You will Never Walk Alone': 'LiverpoolFC',
    'Frontpage': 'FrontPage',
    'Explain Like Im 5': 'explainlikeimfive',
    'LifeProTips': 'LPT',
    'Technology': 'technology',
    'Mildly Interesting': 'mildlyinteresting',
    'Today I Learned': 'todayilearned',
    'Space': 'space',
    'Science': 'science',
    'Learn Python': 'learnpython',
    'Politics': 'politics',
    'World News': 'worldnews',
    'Dank Memes': 'dankmemes',
    'Football - The People Sport': 'football'
}



@app.route('/')
def index():
	return render_template('welcome.html')

@app.route('/go')
def go():
	print("Its all choked up")
	return render_template('login.html')


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
		return render_template('login.html')
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

		if str(password_chk) == str(user['password']):
			#news_stories = redditz.find().sort([('created', -1)])
			return redirect(url_for('reddit'))
		else:
			flash("Wrong password")
			return render_template('login.html')
	else:
		flash("User does not exists")
		return render_template('login.html')



@app.route('/reddit',methods=['GET'])
def reddit():
	news_stories = redditz.find().sort([('created', -1)])
	return render_template('index.html',news_stories=news_stories,reddits=subreddits)

@app.route('/reddit/new')
def reddit_new():
	subreddit = random.choice(subreddits.values())
	url = "http://www.reddit.com/r/"+  str(subreddit) +"/.json"
	header = {'user-agent': 'r_superbot by gravity'}
	resp = requests.get(url,headers=header)
	
	if resp.status_code == 200:
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
			redditz.insert(pipeline)

		flash("Database updated")

	return redirect(url_for('reddit'))


@app.route('/reddit/<string:subreddit>',methods=['GET'])
def reddit_filter():
	filter_result = redditz.find({'subreddit': subreddit}).sort([('created', -1)])

	return render_template('subreddit.html',filter_result=filter_result,reddits=subreddits,reddit_cat=subreddit)



@app.route('/reddit/delete/<string:reddit_id>',methods=['GET'])
def reddit_delete(reddit_id):
	reddit_story = redditz.find_one({'_id': ObjectId(reddit_id)})
	if reddit_story:
		try:
			result = redditz.delete_one({'_id': ObjectId(reddit_id)})
		except ValueError as e:
			flash("Selected article cannot be found ",'error')


	flash("Reddit article removed ",'success')
	return redirect(url_for('reddit'))



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)