#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # change for production to only IP address of front-end app

@app.route('/', methods=['GET'])
def query_records():
    return "hi"


# Creates a CSC room
@app.route('/room/csc', methods=["POST"])
def create_csc_room():
    response = jsonify()

    return response


app.run(debug=True)