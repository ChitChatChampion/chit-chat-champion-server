from __main__ import app, MODEL
from quart import request, jsonify
from csc.questions.routes import generate_unique_room_id, openai_generate_qns_add_db, set_room_published_status
import prompts.prompts as prompts
from ast import literal_eval
from database import get_db, insert_questions
from nanoid import generate
from utils.utils import getBaseContext, getCscContext

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

    app.add_background_task(openai_generate_qns_add_db, room_id, messages)

    return {"room_id": room_id}

# GET
# /room/:id
# Returns:
# {
# 	game_type: "csc",
# }
@app.route('/room/<room_id>', methods=["GET"])
def get_room(room_id):
    room = get_db()["Rooms"].find_one({"_id": room_id})
    if room:
        return {"game_type": room["game_type"], "questions": room["questions"]}
    else:
        return {"error": "Room not found"}, 404

# create room: POST /publish/room/, return success/failure
@app.route('/publish/room', methods=["POST"])
async def publish_room():
    request_json = await request.json
    room_id = request_json.get('room_id')

    return await set_room_published_status(room_id, True)

# unpublish room
@app.route('/unpublish/room', methods=["POST"])
async def unpublish_room():
    request_json = await request.json
    room_id = request_json.get('room_id')

    return await set_room_published_status(room_id, False)
