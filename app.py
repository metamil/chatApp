from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from pymongo import MongoClient
from datetime import datetime





app = Flask(__name__)
cors = CORS(app) # allow CORS for all domains on all routes.
app.config['CORS_HEADERS'] = 'Content-Type'

client = MongoClient('mongodb+srv://tamil:tamil@chatapp.kp271.mongodb.net/')  # Replace with your MongoDB connection string
db = client['Users']
users_collection = db['user']

@app.route("/login", methods = ["POST"])
@cross_origin()
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = users_collection.find_one({'user': username, 'password': password})
    if user:
         user_data = {'id': str(user['_id']), 'username': user['user']}
         return jsonify({'success': True, 'user': user_data})
    else:
        return jsonify({'success': False}), 401
    
@app.route("/users", methods=["POST"])
@cross_origin()
def getUser():
    data = request.json
    user_id = data.get("user_id")
    print(user_id)
    users = list(users_collection.find())
    userss = []
    print(users)
    for user in users:
        if str(user["_id"]) != user_id:
          userss.append({"id" : str(user["_id"]),"name" : user["user"]})
    print(userss)

    return jsonify({"users" : userss})


@app.route('/get_messages', methods=['GET'])
def get_messages():
    sender_id = request.args.get('sender')
    receiver_id = request.args.get('receiver')
    
    # Fetch messages between sender and receiver from the database
    chat_collection = db['chats']
    chat_session = chat_collection.find_one({
        '$or': [
            {'sender_id': sender_id, 'receiver_id': receiver_id},
            {'sender_id': receiver_id, 'receiver_id': sender_id}
        ]
    })
    
    if chat_session:
        return jsonify({'messages': chat_session['messages']})
    else:
        return jsonify({'messages': []})

@app.route('/send_message', methods=['POST'])
@cross_origin()
def send_message():
    data = request.json
    sender_id = data.get('senderId')
    receiver_id = data.get('receiverId')
    message = data.get('message')

    # Find chat session
    chat_collection = db['chats']
    chat_session = chat_collection.find_one({
        '$or': [
            {'sender_id': sender_id, 'receiver_id': receiver_id},
            {'sender_id': receiver_id, 'receiver_id': sender_id}
        ]
    })

    if chat_session:
        # Add new message to the existing chat session
        chat_collection.update_one(
            {'_id': chat_session['_id']},
            {'$push': {'messages': {'sender_id': sender_id, 'message': message, 'timestamp': datetime.utcnow()}}}
        )
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 404
    
@app.route("/t", methods=["GET"])
@cross_origin()
def get():
    return jsonify({"success" : True})

if __name__ == "__main__":
    app.run()
