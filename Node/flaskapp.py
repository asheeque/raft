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

app = Flask(__name__)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'Your_Secret_Key'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)

currentDb = os.getenv('DBNAME')
print(currentDb,file=sys.stderr)

class FlaskApp():

    def __init__(self,port):
        self.port = port

        self.startApp()


    def startApp(self):
        print("started")
        app.run(host=("0.0.0.0"), port=int(self.port), debug=False, use_reloader=False)

    @app.route('/')
    def default(self):

        return {"asdsad":"asd"}

        # @app.route('/')
# def index():
#     todos = users.find()
#     output = [{item: data[item] for item in data if item != '_id'} for data in todos]
#     print(output,file = sys.stderr)
   
    