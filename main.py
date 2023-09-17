#!/usr/bin/env python
# encoding: utf-8
import configparser
import os
from flask import Flask, request, json, jsonify
from flask_cors import CORS
from flask_pymongo import PyMongo
import openai
import prompts
from utils import getBaseContext, getCscContext
from dotenv import load_dotenv
from question import Question


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

        # Insert the generated questions into the database
        for question in generated_questions:
            mongo.db.questions.insert_one({
                    'content': question.content
            })

        return response
    except Exception as e:
        print("error")
        return jsonify({"message": f"Error: {str(e)}"})


# Define a route to check if the database is accessible
@app.route('/check_database', methods=['GET'])
def check_database():
    try:
        # Use the PyMongo connection to ping the database
        mongo.db.command('ping')
        return jsonify({"message": "Database is accessible"})
    except Exception as e:
        return jsonify({"message": f"Database is not accessible: {str(e)}"})
    

# Define a route to get all the questions in the database
@app.route('/questions', methods=['GET'])
def get_all_questions():
    try:
        # Access the questions collection in your MongoDB
        questions_collection = mongo.db.Questions

        # Query the database to retrieve all questions
        all_questions = questions_collection.find({}, {'_id': 0})  # Exclude _id field in the result

        # Convert the result to a list of dictionaries
        questions_list = list(all_questions)

        # Return the list of questions as JSON
        return jsonify(questions_list)
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500  # Return a 500 Internal Server Error response

# Define a route to add a question to the database
@app.route('/questions', methods=['POST'])
def add_question():
    try:
        # Access the questions collection in your MongoDB
        questions_collection = mongo.db.Questions

        # Get the question from the request body
        # e.g. for testing: {"question": "What is your favorite programming language?"}
        question = request.json.get('question')

        # Insert the question into the database
        questions_collection.insert_one({
            'content': question
        })

        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question added successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

app.run(port=8080, debug=True)