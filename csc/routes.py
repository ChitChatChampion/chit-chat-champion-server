from __main__ import app, MODEL
from quart import request, jsonify
from csc.questions.routes import generate_unique_room_id, openai_generate_qns_add_db, set_room_published_status
import prompts.prompts as prompts
from ast import literal_eval
from database import get_db, insert_questions
from nanoid import generate
from utils.utils import getBaseContext, getCscContext
from user.routes import get_user_info

# Get csc context from user whose access token is in response header
@app.route('/csc/context', methods=["GET"])
async def get_csc_context():
    # user_or_error = await get_user_info()
    user_or_error = {"email": "user@example.com"}
    if not user_or_error.get("email"):
        return user_or_error
    user_email = user_or_error.get("email")
    db = await get_db()
    user = db["Users"].find_one({"email": user_email})
    # assumes user should have been added to db upon first login
    if not user:
        return {"error": "User not found"}, 404
    # find a room where game type is csc and user_id is user's id
    room = db["Rooms"].find_one({"game_type": "csc", "user_id": user["_id"]})
    if not room:
        return {"error": "Csc room for user not found"}, 404
    return {
        "baseContext": user["baseContext"],
        "cscContext": room["cscContext"],
        "questions": room["questions"]
    }, 200

# creates or updates a user's csc (and/or base) context
@app.route('/csc/context', methods=["POST"])
async def save_csc_context():
    request_json = await request.json
    purpose, relationship, description = getBaseContext(request_json.get('baseContext'))
    numberOfCards = getCscContext(request_json.get('cscContext')).get('numberOfCards')
    # TODO: check header access token, get user email
    # user_email = get_user_info().get('email')
    user_email = "user@example.com"

    user = await get_db()["Users"].find_one({"_id": user_email})
    if not user:
        return {"message": "User not found"}, 404

    await get_db()["Users"].update_one({"_id": user_email},
                                    {'$set': {
                                        'baseContext': {
                                            'purpose': purpose,
                                            'relationship': relationship,
                                            'description': description
                                        },
                                        'cscContext': {
                                            'numberOfCards': numberOfCards
                                        }
                                    }}, upsert=True
                                )
    return {"message": "success"}


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
async def get_room(room_id):
    room = await get_db()["Rooms"].find_one({"_id": room_id})
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
