#!/usr/bin/env python
# encoding: utf-8
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def query_records():
    return "hi"


# Creates a CSC room
@app.route('/room/csc', methods=["POST"])
def create_csc_room():
    response = jsonify()

    

    return response


app.run(debug=True)