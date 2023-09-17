from flask import Blueprint, jsonify, current_app, g, request
from flask_pymongo import PyMongo
from werkzeug.local import LocalProxy
from bson import ObjectId

def get_db():
    """
    Configuration method to return db instance
    """
    db = getattr(g, "_database", None)

    if db is None:

        db = g._database = PyMongo(current_app).db
       
    return db

def get_questions_collection():
    """
    Configuration method to return questions collection
    """
    return get_db().Questions

# Use LocalProxy to read the global db instance with just `db`
db = LocalProxy(get_db)
questions_collection = LocalProxy(get_questions_collection)

# Define routes within the blueprint
def check_db():
    try:
        # Use the PyMongo connection to ping the database
        db.command('ping')
        return jsonify({"message": "Database is accessible"})
    except Exception as e:
        return jsonify({"message": f"Database is not accessible: {str(e)}"})
    

def get_all_questions():
    try:
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

# Returns inserted qn ids for now
def insert_questions(generated_questions):
    inserted_qn_ids = []
    # Insert the generated questions into the database
    for question in generated_questions:
        inserted_qn = questions_collection.insert_one({
                'content': question.content
        })
        inserted_qn_ids.append(str(inserted_qn.inserted_id))
    return inserted_qn_ids

def add_question_db(question):
    inserted_qn = questions_collection.insert_one({
        'content': question.content
    })
    return str(inserted_qn.inserted_id)

def update_question_db(question_id, new_question):
    questions_collection.update_one({'_id': ObjectId(question_id)}, {
        '$set': {
            'content': new_question.content
        }
    })
    return str(question_id)

def delete_question_db(question_id):
    questions_collection.delete_one({'_id': ObjectId(question_id)})
    return str(question_id)