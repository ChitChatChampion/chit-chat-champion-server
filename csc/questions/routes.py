from __main__ import app
from ast import literal_eval
import json
import logging
from nanoid import generate
import openai
from quart import request, jsonify
from main import MODEL
import prompts.prompts as prompts
from database import check_db, get_all_questions, add_question_db, get_db, update_question_db, delete_question_db
from user.routes import get_user_info
from utils.utils import checkResponseSuccess

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

@app.route('/csc/questions', methods=['GET'])
async def get_csc_questions():
    # TODO: check if this works
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message

    user_email = user_info[0].get("email")
    user = await get_db()['Users'].find_one({"_id": user_email})
    if not user:
        return jsonify({"error": "User not found"}), 404
    questions = user['csc']['questions']
    if not questions:
        return {"questions": []}, 200
    return {"questions": [{"id": id, "content": content} for id, content in questions.items()]}, 200


@app.route('/csc/questions/<id>', methods=['PUT'])
async def update_csc_question(id):
    request_data = await request.json
    content = request_data.get('content')

    # TODO: check if this works
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    if not user_email:
        return jsonify({"error": "Invalid user"}), 401

    if not content:
        return jsonify({"error": "No content data"}), 400

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user['csc']['questions']
        questions[id] = content
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {'csc.questions': questions}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

@app.route('/csc/questions/create', methods=['POST'])
async def create_csc_question():
    # get all questions from user from db
    user_email = "user@example.com"
    # TODO: check if this works
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")
    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user['csc']['questions']
        while True:
            
            if id not in questions:
                break
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {'csc.questions': questions}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

@app.route('/csc/questions/<id>', methods=['DELETE'])
async def delete_csc_question(id):
    # TODO: check if this works
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user['csc']['questions']
        del questions[id]
        await get_db()['Users'].update_one({"_id": user_email}, {'$set': {'csc.questions': questions}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500