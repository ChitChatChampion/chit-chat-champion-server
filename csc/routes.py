import json
import logging
from quart import Blueprint, request, websocket
import prompts.prompts as prompts
from utils.user import authenticate
from utils.entities import save_bb_csc_contexts, get_questions_contexts

csc_bp = Blueprint('csc_bp', __name__, url_prefix='/csc')

# Get csc context from user whose access token is in response header
@csc_bp.route('/context', methods=["GET"])
@authenticate
async def get_csc_context(user_info):
    user_email = user_info.get('email')
    return await get_questions_contexts(user_email, 'csc')

# creates or updates a user's csc (and/or base) context
@csc_bp.route('/context', methods=["POST"])
@authenticate
async def save_csc_context(user_info):
    request_json = await request.json
    user_email = user_info.get('email')

    return await save_bb_csc_contexts(user_email, request_json, 'csc')

def add_player_to_room(room_id):
    if room_id in room_to_socket:
        room_to_socket[room_id].append(websocket._get_current_object())
    else:
        room_to_socket[room_id] = [websocket._get_current_object()]

room_to_socket = {}
@csc_bp.websocket('/ws')
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
