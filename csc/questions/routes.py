from __main__ import app
from ast import literal_eval
import logging
from nanoid import generate
import openai
from quart import request, jsonify
from main import MODEL
import prompts.prompts as prompts
from database import check_db, get_all_questions, add_question_db, get_db, update_question_db, delete_question_db

async def openai_generate_qns_add_db(room_id, messages):
    logging.info("{room_id}: Querying OpenAI")
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
    )
    questions = response['choices'][0]['message']['content']

    # # add questions in the form of room-id to questions key value pairs
    logging.info(f"{room_id}: Adding questions to database: {questions}")

    question_arr = parse_questions(questions)
    
    await add_questions_to_room_collection(question_arr, room_id, "csc")
    await add_questions_to_user_collection(question_arr, room_id, "csc")

    logging.info(f"{room_id}: Done adding questions to database")

def parse_questions(questions):
    if questions[0] == "[" and questions[-1] == "]":
        return literal_eval(questions)
    else:
        return [questions]

async def add_questions_to_user_collection(questions, room_id, game_type):
    # TODO: do get_user_info
    print("not done")
    # email = await get_user_info()
    # await get_db()["Users"].update_one({"_id": email},
    #                                        {'$set': {
    #                                         '_id': email,
    #                                         'csc': {
    #                                             'room_id': room_id,
    #                                             'is_published': False,
    #                                             'questions': questions
    #                                         }
    #                                        }}, upsert=True
    #                                 )

async def add_questions_to_room_collection(questions, room_id, game_type):
    try:
        await get_db()["Rooms"].insert_one({
            '_id': room_id,
            'game_type': game_type,
            'is_published': False,
            'questions': questions
        })
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: adding questions to collection"}), 500

async def generate_unique_room_id():
    while True:
        room_id = generate(size=6)
        room = await get_db()["Rooms"].find_one({'_id': room_id})
        if not room:
            logging.info(f"Unique room {room_id} found")
            break
    return room_id

async def set_room_published_status(room_id, set_is_published):
    existing_room = await get_db()["Rooms"].find_one({"_id": room_id})
    if not existing_room:
        return {"error": "Room not found"}, 404

    await get_db()["Rooms"].update_one({"_id": room_id},
                                        {'$set': {
                                        'is_published': set_is_published
                                        }})
    
    return {"message": f"Room {room_id} {'published' if set_is_published else 'unpublished'} successfully"}


# FOR TESTING PURPOSES ONLY
# Define a route to check if the database is accessible
@app.route('/check_database', methods=['GET'])
async def check_database():
    res = await check_db()
    return res

# Define a route to get all the questions in the database
@app.route('/questions', methods=['GET'])
async def get_questions():
    res = await get_all_questions()
    return res

# Define a route to add a question to the database
@app.route('/questions/add', methods=['POST'])
async def add_question():
    try:
        # Get the question from the request body
        # e.g. for testing: {"question": "What is your favorite programming language?"}
        question_data = await request.json
        question = question_data.get('question')

        # Insert the question into the database
        await add_question_db(question)

        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question added successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

# Define a route to update a question in the database
@app.route('/questions/update/<question_id>', methods=['PUT'])
async def update_question(question_id):
    try:
        # Get the question from the request body
        # e.g. for testing: {"question": "What is your favorite programming language?"}
        question_data = await request.json
        new_question = question_data.get('question')

        # Update the question in the database with the question_id
        await update_question_db(question_id, new_question)
        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question updated successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
# Define a route to delete a question from the database
@app.route('/questions/delete/<question_id>', methods=['DELETE'])
async def delete_question(question_id):
    try:
        # Delete the question from the database with the question_id
        await delete_question_db(question_id)
        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question deleted successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
