from quart import Blueprint, request
import prompts.prompts as prompts
from database import get_db
import logging
from utils.utils import checkResponseSuccess, format_qns_for_fe
from utils.user import get_user_info
from utils.room import create_room, set_room_published_status


room_bp = Blueprint('room_bp', __name__, url_prefix='/room')

# Creates a CSC room with the user's questions
@room_bp.route('/csc/create', methods=["POST"])
async def create_csc_room():
    return await create_room('csc')

@room_bp.route('/bb/create', methods=["POST"])
async def create_bb_room():
    return await create_room('bb')

# GET
# /room/:id
# Returns:
# {
# 	game_type: "csc",
# }
@room_bp.route('/<room_id>', methods=["GET"])
async def get_room(room_id):
    room = await get_db()["Rooms"].find_one({"_id": room_id})
    if not room or not room['is_published']:
        return {"error": "Room not found"}, 404
    game_type = room["game_type"]
    if game_type == 'csc' or 'bb':
        formatted_qns = format_qns_for_fe(room["questions"])
        return {"game_type": game_type, "questions": formatted_qns}, 200
    else:
        return {"error": f"Unrecognised game type {game_type}"}, 404
        

# create room: POST /room/publish, return success/failure
@room_bp.route('/publish', methods=["POST"])
async def publish_room():
    request_json = await request.json
    room_id = request_json.get('room_id')

    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info
    user_email = user_info[0].get("email")

    updated_result = await update_room_before_publish(user_email, room_id)
    if not checkResponseSuccess(updated_result):
        return updated_result

    return await set_room_published_status(room_id, True)

async def update_room_before_publish(user_email, room_id):
    db = get_db()
    user = await db["Users"].find_one({"_id": user_email})
    if not user:
        return {"error": "User not found"}, 404
    room = await db["Rooms"].find_one({"_id": room_id})
    if not room:
        return {"error": "Room not found"}, 404

    if room['game_type'] == 'csc':
        questions = user["csc"]["questions"]
        await db["Rooms"].update_one({"_id": room_id}, {'$set': {'questions': questions}})
        return {"message": "success"}, 200
    elif room['game_type'] == 'bb':
        questions = user["bb"]["questions"]
        await db["Rooms"].update_one({"_id": room_id}, {'$set': {'questions': questions}})
        return {"message": "success"}, 200
    else:
        return {"error": "Room has invalid game_type"}, 400

# unpublish room
@room_bp.route('/unpublish', methods=["POST"])
async def unpublish_room():
    request_json = await request.json
    room_id = request_json.get('room_id')

    return await set_room_published_status(room_id, False)
