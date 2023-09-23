from ast import literal_eval
from database import get_db
import logging
from nanoid import generate
import openai
from quart import current_app, jsonify


async def openai_generate_qns_add_db(room_id, messages):
    logging.info("{room_id}: Querying OpenAI")
    response = openai.ChatCompletion.create(
        model=current_app.config['MODEL'],
        messages=messages,
        temperature=0.7,
    )
    questions = response['choices'][0]['message']['content']

    # # add questions in the form of room-id to questions key value pairs
    logging.info(f"{room_id}: Adding questions to database: {questions}")

    question_arr = parse_questions(questions)
    
    await add_questions_to_room_collection(question_arr, room_id, "csc")

    logging.info(f"{room_id}: Done adding questions to database")

def parse_questions(questions):
    if questions[0] == "[" and questions[-1] == "]":
        # This may be dangerous in the case of prompt injection
        return literal_eval(questions)
    else:
        return [questions]

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
