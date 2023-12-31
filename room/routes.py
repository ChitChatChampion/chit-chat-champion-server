import json
from quart import Blueprint, request, websocket
import prompts.prompts as prompts
from database import get_db
from utils.utils import checkResponseSuccess, format_entities_for_fe
from utils.user import authenticate
from utils.room import create_questions_room, set_room_published_status, create_bingo_room_helper


room_bp = Blueprint('room_bp', __name__, url_prefix='/room')

# Creates a CSC room with the user's questions
@room_bp.route('/csc/create', methods=["POST"])
@authenticate
async def create_csc_room(user_info):
    return await create_questions_room(user_info, 'csc')

@room_bp.route('/bb/create', methods=["POST"])
@authenticate
async def create_bb_room(user_info):
    return await create_questions_room(user_info, 'bb')

@room_bp.route('/bingo/create', methods=["POST"])
@authenticate
async def create_bingo_room(user_info):
    return await create_bingo_room_helper(user_info)

# GET
# /room/:id
# Returns:
# {
# 	game_type: "csc",
# }
@room_bp.route('/<room_id>', methods=["GET"])
async def get_room(room_id):
    room = await get_db()["Rooms"].find_one({"_id": room_id})
    if not room:
        return {"message": "Room not found"}, 404
    game_type = room["game_type"]
    if game_type == 'csc' or game_type == 'bb':
        formatted_qns = format_entities_for_fe(room["questions"])
        return {"game_type": game_type, "questions": formatted_qns}, 200
    elif game_type == 'bingo':
        return {"game_type": game_type}, 200
    elif game_type == 'quiz':
        # likely different format of return with questions having solutions etc
        return {"message": f"not yet implemented for {game_type}"}, 404     
    else:
        return {"message": f"Unrecognised game type {game_type}"}, 404
        

# create room: POST /room/publish, return success/failure
@room_bp.route('/publish', methods=["POST"])
@authenticate
async def publish_room(user_info):
    request_json = await request.json
    room_id = request_json.get('room_id')

    user_email = user_info.get("email")

    updated_result = await update_room_before_publish(user_email, room_id)
    if not checkResponseSuccess(updated_result):
        return updated_result

    return await set_room_published_status(room_id, True)

async def update_room_before_publish(user_email, room_id):
    db = get_db()
    user = await db["Users"].find_one({"_id": user_email})
    if not user:
        return {"message": "User not found"}, 404
    room = await db["Rooms"].find_one({"_id": room_id})
    if not room:
        return {"message": "Room not found"}, 404

    if room['game_type'] == 'csc':
        questions = user["csc"]["questions"]
        await db["Rooms"].update_one({"_id": room_id}, {'$set': {'questions': questions}})
        return {"message": "success"}, 200
    elif room['game_type'] == 'bb':
        questions = user["bb"]["questions"]
        await db["Rooms"].update_one({"_id": room_id}, {'$set': {'questions': questions}})
        return {"message": "success"}, 200
    else:
        return {"message": "Room has invalid game_type"}, 400

# unpublish room
@room_bp.route('/unpublish', methods=["POST"])
async def unpublish_room():
    request_json = await request.json
    room_id = request_json.get('room_id')

    existing_room = await get_db()["Rooms"].find_one({"_id": room_id})
    if not existing_room:
        return {"message": "Room not found"}, 404

    await get_db()["Rooms"].delete_one({"_id": room_id})

    return {"message": f"Room {room_id} unpublished successfully"}, 200

def add_player_to_room(room_id):
    if room_id in room_to_socket:
        room_to_socket[room_id].append(websocket._get_current_object())
    else:
        room_to_socket[room_id] = [websocket._get_current_object()]

room_to_socket = {}

@room_bp.websocket('/ws')
async def ws():
    while True:
        data = json.loads(await websocket.receive())

        # Add all players to rooms upon joining
        if "room_id" in data:
            room_id = data["room_id"]
            add_player_to_room(room_id)

        print(room_to_socket)

        # Send message to all players in room to close the room when the room is closed
        if data.get("type", "") == "close_room":
            for socket in room_to_socket[data.get("room_id")]:
                await socket.send_json({"type": "close_room", "message": "Room closed."})
            del room_to_socket[data.get("room_id")]
