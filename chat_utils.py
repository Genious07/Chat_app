from pymongo import MongoClient
import datetime

client = MongoClient("mongodb+srv://Satwik2:satwik213@chatapp.y7qfp.mongodb.net/?retryWrites=true&w=majority&appName=ChatApp")
db = client['chat_db']

def send_message(sender, recipient, message):
    db.messages.insert_one({
        'sender': sender,
        'recipient': recipient,
        'message': message,
        'timestamp': datetime.datetime.utcnow()
    })

def get_messages(username, recipient):
    return list(db.messages.find({
        '$or': [
            {'sender': username, 'recipient': recipient},
            {'sender': recipient, 'recipient': username}
        ]
    }).sort("timestamp", -1).limit(100))

def clear_messages(username, recipient):
    # Clear messages between the two users
    db.messages.delete_many({
        '$or': [
            {'sender': username, 'recipient': recipient},
            {'sender': recipient, 'recipient': username}
        ]
    })