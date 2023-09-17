#!/usr/bin/env python
# encoding: utf-8
import configparser
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import openai
import prompts
from utils import getBaseContext, getCscContext
from dotenv import load_dotenv
from question import Question
from database import check_db, get_all_questions, add_question_db, insert_questions, update_question_db, \
    delete_question_db


app = Flask(__name__)
MODEL = "gpt-3.5-turbo-16k"
cors = CORS(app) # Update to specific origins for production

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
async def create_csc_room():
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

    try:
        # get the response from the model asynchronously
        response = await openai.ChatCompletion.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,  # this is the degree of randomness of the model's output
        )
        
        generated_questions = []

        # Extract and store the generated questions
        for choice in response.choices:
            generated_question = Question(choice['message']['content'])
            generated_questions.append(generated_question)

        inserted_qn_ids = insert_questions(generated_questions)

        return response
    except Exception as e:
        print("error")
        return jsonify({"message": f"Error: {str(e)}"})


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

app.run(port=8080, debug=True)