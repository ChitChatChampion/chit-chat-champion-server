#!/usr/bin/env python
# encoding: utf-8
import configparser
import os
from flask import Flask, request, json, jsonify
from flask_pymongo import PyMongo
import openai
import prompts
from utils import getBaseContext, getCscContext
from dotenv import load_dotenv

app = Flask(__name__)
MODEL = "gpt-3.5-turbo-16k"

# Configure database
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))
app.config['MONGO_URI'] = config['TEST']['DB_URI']
mongo = PyMongo(app)

load_dotenv()

print(os.getenv("OPENAI_KEY"))

@app.route('/', methods=['GET'])
def query_records():
    return {"message": "Hello World!"}

# Creates a CSC room
@app.route('/room/csc', methods=["POST"])
def create_csc_room():
    age, familiarity, purpose, group_description = getBaseContext(request.json.get('baseContext'))
    number_of_cards = getCscContext(request.json.get('cscContext'))

    prompt = str({
        "baseContext": f"The age range of the participants in the ice-breaker session is {age} years old, they are currently {familiarity}, and the purpose of the ice-breaker session is {purpose}. Other information about the ice-breaker session is that: {group_description}.",
        "cscContext": f"The number of questions I want you to generate is {number_of_cards}.",
    })

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example},
        {"role": "assistant", "content": prompts.assistant_example},
        {"role": "user", "content": prompt}
    ]

    # TODO: create a promise for this that adds something to the db when it resolves
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,  # this is the degree of randomness of the model's output
    )

    return response

# Define a route to check if the database is accessible
@app.route('/check_database', methods=['GET'])
def check_database():
    try:
        # Use the PyMongo connection to ping the database
        mongo.db.command('ping')
        return jsonify({"message": "Database is accessible"})
    except Exception as e:
        return jsonify({"message": f"Database is not accessible: {str(e)}"})


app.run(port=8080, debug=True)