import bcrypt
from pymongo import MongoClient

client = MongoClient("mongodb+srv://Satwik2:satwik213@chatapp.y7qfp.mongodb.net/?retryWrites=true&w=majority&appName=ChatApp")
db = client['chat_db']

def register_user(username, password):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db.users.insert_one({'username': username, 'password': password_hash})

def login_user(username, password):
    user = db.users.find_one({'username': username})
    if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return True
    return False


