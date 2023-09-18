#!/usr/bin/env python
# encoding: utf-8
import configparser
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import openai

from utils.utils import getBaseContext, getCscContext
from dotenv import load_dotenv
from question import Question
from quart import Quart
from database import check_db, get_all_questions, add_question_db, insert_questions, update_question_db, \
    delete_question_db

app = Quart(__name__)

MODEL = "gpt-3.5-turbo"

@app.route('/', methods=['GET'])
def query_records():
    return {"message": "Hello World!"}

# TODO: temporarily remove this as it's causing an error on my side
# cors = CORS(app) # Update to specific origins for production

# Configure database
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))
app.config['MONGO_URI'] = config['TEST']['DB_URI']
mongo = PyMongo(app)

load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")

# FOR TESTING PURPOSES ONLY
# Define a route to check if the database is accessible
@app.route('/check_database', methods=['GET'])
def check_database():
    return check_db()

# Define a route to get all the questions in the database
@app.route('/questions', methods=['GET'])
def get_questions():
    return get_all_questions()

# Define a route to add a question to the database
@app.route('/questions/add', methods=['POST'])
def add_question():
    try:
        # Get the question from the request body
        # e.g. for testing: {"question": "What is your favorite programming language?"}
        question = Question(request.json.get('question'))

        # Insert the question into the database
        inserted_qid = add_question_db(question)

        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question added successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

# Define a route to update a question in the database
@app.route('/questions/update/<question_id>', methods=['PUT'])
def update_question(question_id):
    try:
        # Get the question from the request body
        # e.g. for testing: {"question": "What is your favorite programming language?"}
        new_question = Question(request.json.get('question'))

        # Update the question in the database with the question_id
        update_question_db(question_id, new_question)
        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question updated successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
# Define a route to delete a question from the database
@app.route('/questions/delete/<question_id>', methods=['DELETE'])
def delete_question(question_id):
    try:
        # Delete the question from the database with the question_id
        delete_question_db(question_id)
        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question deleted successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

import csc.routes

app.run(port=8080, debug=True)