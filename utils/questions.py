from ast import literal_eval
from database import get_db
import logging
from nanoid import generate
import openai
from quart import current_app, jsonify

async def openai_generate_and_save_qns(user_email, messages):
    logging.info(f"{user_email}: Querying OpenAI")
    response = openai.ChatCompletion.create(
        model=current_app.config['MODEL'],
        messages=messages,
        temperature=0.7,
    )
    questions = response['choices'][0]['message']['content']

    question_arr = parse_questions(questions)

    db_response = await add_questions_to_user_csc_collection(question_arr, user_email)

    return db_response

def parse_questions(questions):
    if questions[0] == "[" and questions[-1] == "]":
        # This may be dangerous in the case of prompt injection
        return literal_eval(questions)
    else:
        return [questions]

async def add_questions_to_user_csc_collection(ai_questions_arr, user_email):
    try:
        formatted_questions = format_qns_for_db(ai_questions_arr)
        await get_db()["Users"].update_one({"_id": user_email},
                                        {'$set': {
                                            'csc.questions': formatted_questions,
                                        }})
        return formatted_questions, 201
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: adding questions to collection"}), 500

# Format the questions as a dictionary where keys are ids and values are questions' contents
def format_qns_for_db(ai_questions):
    questions = {}
    for question in ai_questions:
        question_id = generate_unique_question_id(questions)
        questions[question_id] = question
    return questions


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

def generate_unique_question_id(questions):
    question_id = generate(size=3)
    if not questions:
        return question_id
    while True:
        if question_id not in questions.keys():
            break
        question_id = generate(size=3)
    return question_id