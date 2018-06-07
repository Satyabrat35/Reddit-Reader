from pymongo import MongoClient
import bcrypt

try:
	print("connecting to mongo")
	cluster_uri = "mongodb+srv://analytics:analytics-password@mycluster-zuqqr.mongodb.net/test?retryWrites=true"
	client = MongoClient(cluster_uri)
	db = client['test']
	print("connected")
except:
	print("Could not connect")

userz = db.users
#salt = bcrypt.gensalt(14)
#print(salt)
salt = b'$2b$14$LuZHIFa5Gx8/4FNWI4WOBe'

def create():
	username = input("Username: ")
	psword = input("Password: ")
	#psword.encode('utf-8')
	p_word = psword.encode('utf-8')
	password = bcrypt.hashpw(p_word, salt)

	new_user = {
		'username': username,
		'password': password
	}

	user = userz.find_one({'username': username})

	if user is not None:
		print("Already exists")
		return 

	try:
		userz.insert_one(new_user).inserted_id
		print("Acc created")
	except:
		print("Could nor insert new user")

def login():
	username = input("Whats ur username: ")
	p_word = input("Whats ur password: ")
	psword = p_word.encode('utf-8')

	"""filter = {
		'password': {'$eq': username}
	}
	user = db.users.find(filter)
	#print(user.count())
	"""
	user = userz.find_one({'username': username})
	if user is not None:
		password_chk = bcrypt.hashpw(psword, salt)
		if password_chk == user['password']:
			print("Hello "+user['username'])
		else:
			print(password_chk)
			print(user['password'])
			print("Wrong password")
	else:
		print("User not exist")



def delete():
	username = input("Whats ur username: ")
	user = userz.find_one({'username': username})

	if user is None:
		print("User does not exists")
	else:
		userz.delete_one(user)
		user = userz.find_one({'username': username})

		if user is None:
			print("User deleted")
		else:
			print("User not deleted")

def show_all():
    try:
    	str1 = ""
    	cursor = userz.find({})
    	for doc in cursor:
    		str1 = str1 + doc['username'] + " "
    	str1 = "List of users: " + str1
    	print(str1)
    except:
        print("Could not show users collection.")


accessing = True

while(accessing):
    choice = input("\
1 - create, \
2 - login, \
3 - delete, \
4 - Show all, \
else to exit. Enter: \
")
    if choice == '1':
        create()
    elif choice == '2':
        login()
    elif choice == '3':
        delete()
    elif choice == '4':
        show_all()
    else:
        accessing = False

