from ast import literal_eval
from database import get_db
import logging
from nanoid import generate
import openai
from quart import current_app, jsonify

def openai_generate_qns(user_email, messages):
    logging.info(f"{user_email}: Querying OpenAI")
    response = openai.ChatCompletion.create(
        model=current_app.config['MODEL'],
        messages=messages,
        temperature=0.7,
    )
    questions = response['choices'][0]['message']['content']

    question_arr = parse_questions(questions)

    return question_arr


def parse_questions(questions):
    if questions[0] == "[" and questions[-1] == "]":
        # This may be dangerous in the case of prompt injection
        return literal_eval(questions)
    else:
        # We want to remove the quotation marks for a single question
        if questions[0] == "\"" and questions[-1] == "\"":
            questions = questions[1:-1]
        return [questions]

async def add_questions_to_user_collection(ai_questions_arr, user_email, game_type):
    try:
        logging.info(f"{user_email}: Adding questions to collection")
        user = await get_db()["Users"].find_one({"_id": user_email})

        existing_questions = user[game_type]["questions"]
        formatted_questions = format_qns_for_db(existing_questions, ai_questions_arr)

        field_to_add = f"{game_type}.questions"
        await get_db()["Users"].update_one({"_id": user_email},
                                        {'$set': {
                                            field_to_add: formatted_questions
                                        }})
        return formatted_questions, 201
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: adding questions to collection"}), 500

# Format the questions as a dictionary where keys are ids and values are questions' contents
def format_qns_for_db(existing_questions, ai_questions):
    questions = existing_questions
    for question in ai_questions:
        question_id = generate_unique_question_id(questions)
        questions[question_id] = question
    logging.info(questions)
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