#!/usr/bin/env python
# encoding: utf-8
from concurrent.futures import process
import json
from flask import Flask
from flask_pymongo import PyMongo
import sys
from flask import Flask, request, jsonify
import flask
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

import os
import json
import bcrypt
import hashlib
import datetime
from node import Node

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

currentDb = os.getenv('DBNAME')
print(currentDb,file=sys.stderr)
# app.config["MONGO_URI"] = "mongodb://"+currentDb+":27017/distributed"
# mongo = PyMongo(app)
# # bcrypt = Bcrypt(app)

# users = mongo.db.users

@app.route('/')
def index():
#     todos = users.find()
#     output = [{item: data[item] for item in data if item != '_id'} for data in todos]
#     print(output,file = sys.stderr)
   
    return {"asdsad":"asd"}


# @app.route('/user/signup', methods=['POST'])
# def signup():
#     # print(request.json)
#     # u = request.json
#     new_user = request.get_json()
#     new_user["password"] = hashlib.sha256(new_user["password"].encode("utf-8")).hexdigest()
#     doc = users.find_one({"name": new_user["name"]})
#     if not doc:
#         users.insert_one(new_user)
#         return jsonify({'msg': 'User created successfully'}), 201
#     else:
#         return jsonify({'msg': 'Username already exists'}), 409

@app.route('/user/login', methods=['POST'])
def login():
    print('56')
    n.handlePut('content')
    return {'a':'as'}
#     # print(request.json)
#     # u = request.json
#     print(currentDb,file=sys.stderr)
#     user_data = request.get_json()
#     user_from_db = users.find_one({'name': user_data['name']})
    
#     if user_from_db:
#         encrpted_password = hashlib.sha256(user_data['password'].encode("utf-8")).hexdigest()
#         if encrpted_password == user_from_db['password']:
#             access_token = create_access_token(identity=user_from_db['name'])
#             return jsonify(access_token=access_token), 200
            
    
#     return jsonify({'msg': 'The username or password is incorrect'}), 401
    
  
if __name__ == "__main__":
    PORT = os.getenv('PORT')
    print(PORT,file=sys.stderr)
    print("76",file=sys.stderr)
    ip = os.getenv('IP')
    
    n = Node()
    n.getRandomElectionTime()  
    n.init_timeout()
    print("76",file=sys.stderr)
    n.sock = n.init_socket()
    n.startListener()
    # n.listener()
    # n.init_socket
    # app.run(host=("0.0.0.0"), port=int(PORT), debug=False, use_reloader=False)