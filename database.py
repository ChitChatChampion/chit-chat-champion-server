from quart import Blueprint, jsonify, current_app, g, request
from quart_motor import Motor
from motor.motor_asyncio import AsyncIOMotorClient
from werkzeug.local import LocalProxy
from bson import ObjectId

def get_db():
    if not hasattr(current_app, 'db'):
        current_app.db = AsyncIOMotorClient(current_app.config['MONGODB_URI']).get_database("ChitChatChampions")
    return current_app.db

def get_questions_collection():
    db = get_db()
    return db['Questions']

db = LocalProxy(get_db)
questions_collection = LocalProxy(get_questions_collection)

async def check_db():
    try:
        # Use the MongoDB client to ping the database
        db.command('ping')
        return jsonify({"message": "Database is accessible"})
    except Exception as e:
        return jsonify({"message": f"Database is not accessible: {str(e)}"})

async def get_all_questions():
    try:
        # Query the database to retrieve all questions
        cursor = questions_collection.find({}, {'_id': 0})  # Exclude _id field in the result
        questions_list = []

        async for question in cursor:
            questions_list.append(question)

        # Return the list of questions as JSON
        return jsonify(questions_list)
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500  # Return a 500 Internal Server Error response

# Insert a list of questions e.g. ["Question 1?", "Question 2?", "Question 3?"]
async def insert_questions(generated_questions: list):
    # Insert the generated questions into the database
    for question in generated_questions:
        await add_question_db(question)

async def add_question_db(question):
    inserted_qn = await get_db()["Rooms"].insert_one({
        'content': question
    })
    return inserted_qn

async def update_question_db(question_id, new_question):
    questions_collection.update_one({'_id': ObjectId(question_id)}, {
        '$set': {
            'content': new_question.content
        }
    })
    return str(question_id)

async def delete_question_db(question_id):
    questions_collection.delete_one({'_id': ObjectId(question_id)})
    return str(question_id)