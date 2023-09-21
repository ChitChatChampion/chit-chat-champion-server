from __main__ import app, MODEL
from quart import request, jsonify
import prompts.prompts as prompts
from ast import literal_eval
import logging
import openai
from database import get_db, insert_questions
from nanoid import generate
from utils.utils import getBaseContext, getCscContext

async def query_openai(room_id, messages):
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

    logging.info(f"{room_id}: Done adding questions to database")

def parse_questions(questions):
    if questions[0] == "[" and questions[-1] == "]":
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

# Creates a CSC room
@app.route('/room/csc', methods=["POST"])
async def create_csc_room():
    request_json = await request.json
    age, familiarity, purpose, group_description = getBaseContext(request_json.get('baseContext'))
    number_of_cards = getCscContext(request_json.get('cscContext'))

    if number_of_cards > 20:
        return {"message": "Too many cards requested"}, 400

    prompt = f"The age range of the participants in the ice-breaker session is {age} years old, they are currently {familiarity}, and the purpose of the ice-breaker session is {purpose}. Other information about the ice-breaker session is that: {group_description}. The number of questions I want you to generate is {number_of_cards}."

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example_csc},
        {"role": "assistant", "content": prompts.assistant_example_csc},
        {"role": "user", "content": prompt}
    ]

    room_id = await generate_unique_room_id()

    app.add_background_task(query_openai, room_id, messages)

    return {"room_id": room_id}