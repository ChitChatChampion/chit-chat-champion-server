import json
from quart import Blueprint, request, websocket
import prompts.prompts as prompts
from database import get_db
import logging
from utils.user import authenticate, bingo_auth
from utils.utils import checkResponseSuccess, openai_generate_response
from utils.entities import format_entities_for_fe, create_entity, update_entity, delete_entity
from utils.room import check_is_room_owner

bingo_bp = Blueprint('bingo_bp', __name__, url_prefix='/bingo')

# This function is called when the creator clicks the "Generate Bingo" button
# IF THERE ARE EXISTING SQUARES, THIS FUNCTION WILL DELETE/OVERWRITE THEM
# It generates bingo squares for players (not game creator) with data that are already stored in the room
# This data should come from the forms that users submit before the game starts
@bingo_bp.route('/<room_id>/generate', methods=['POST'])
@authenticate
async def ai_generate_bingo_squares(room_id, user_info):
    user_email = user_info.get('email')

    bingo_room = await get_db()['Rooms'].find_one({'_id': room_id})
    is_valid_room = check_is_bingo_room(bingo_room) and check_bingo_room_has_players(bingo_room)
    if not is_valid_room:
        return {"message": "Room not found"}, 404
    if not check_is_room_owner(bingo_room, user_email):
        return {"message": "Authentication error"}, 401

    player_contexts = get_bingo_player_contexts(bingo_room)
    messages = craft_openai_bingo_messages(player_contexts)

    bingo_squares_arr, message = openai_generate_response(user_email, messages)
    if message != "success":
        return {"message": "Invalid query given."}, 400

    logging.info(f"{user_email}: OpenAI response: {bingo_squares_arr}")

    await get_db()['Rooms'].update_one({"_id": room_id},
                                        {'$set': {
                                            'bingo.squares': bingo_squares_arr
                                        }})

    return {"squares": bingo_squares_arr}, 201

def check_is_bingo_room(room):
    if not room or not room['game_type'] == 'bingo':
        return {"message": "Room not found"}, 404
    return {"message": "Success"}, 200

def check_bingo_room_has_players(bingo_room):
    if not bingo_room['bingo'] or not bingo_room['bingo']['player_info']:
        return {"message": "No players found"}, 404
    return {"message": "Success"}, 200

def get_bingo_player_contexts(bingo_room):
    return bingo_room['bingo']['player_info']

def craft_openai_bingo_messages(contexts):
    prompt = f"Help me generate squares for each player in a bingo game. \
    Generate something interesting with a title and a description. \
    Try to keep the title and description as short as possible. The description must be less than 10 words. \
    Pick the most obscure fact that makes it hard for others to guess who belongs in that square. \
    Try to avoid including anything similar between players in the bingo squares. \
    The following array of json objects contain the players' details: \
    {contexts}"

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example_bingo},
        {"role": "assistant", "content": prompts.assistant_example_bingo},
        {"role": "user", "content": prompt}
    ]
    return messages

@bingo_bp.route('/context', methods=['GET'])
@authenticate
async def get_bingo_context(user_info):
    user_email = user_info.get('email')
    db = get_db()
    user = await db['Users'].find_one({'_id': user_email})
    bingo_context = user['bingo']['fields']
    fields = format_entities_for_fe(bingo_context)

    return {"fields": fields}, 200

@bingo_bp.route('/fields/create', methods=['POST'])
@authenticate
async def create_bingo_fields(user_info):
    return await create_entity(user_info, 'bingo', 'fields')

@bingo_bp.route('/fields/<id>', methods=['PUT'])
@authenticate
async def update_bingo_field(id, user_info):
    return await update_entity(id, user_info, 'bingo', 'fields')

@bingo_bp.route('/fields/<id>', methods=['DELETE'])
@authenticate
async def delete_bingo_field(id, user_info):
    return await delete_entity(id, user_info, 'bingo', 'fields')

# unauthenticated
@bingo_bp.route('/<id>/fields', methods=['GET'])
async def get_bingo_fields(id):
    db = get_db()
    room = await db['Rooms'].find_one({'_id': id})
    if not room or not room['bingo']:
        return {"message": "Room not found"}, 404
    fields = room['bingo']['fields']
    if not fields:
        return {"message": "Fields not found"}, 404

    fe_formatted_fields = format_entities_for_fe(fields)
    return {"fields": fe_formatted_fields}, 200

# unauthenticated
@bingo_bp.route('/<id>/join', methods=['POST'])
async def join_bingo_room(id):
    request_json = await request.json
    name = request_json.get('name')
    logging.info("user form received: " + str(request_json))
    if not name:
        return {"message": "Invalid form data"}, 400
    room = await get_db()['Rooms'].find_one({'_id': id})
    if not check_is_bingo_room(room):
        return {"message": "Room not found"}, 404
    # add player to room
    player_names = room['bingo']['player_names']
    if name in player_names:
        return {"message": "Player name already exists"}, 409
    player_names.append(name)
    player_info = room['bingo']['player_info']
    player_info.append(request_json)
    await get_db()['Rooms'].update_one({"_id": id},
                                        {'$set': {
                                            'bingo.player_info': player_info,
                                            'bingo.player_names': player_names
                                        }})
    return {"message": "success"}, 200

@bingo_bp.route('/<id>/players', methods=['GET'])
@authenticate
async def get_bingo_players(id, user_info):
    user_email = user_info.get('email')
    room = await get_db()['Rooms'].find_one({'_id': id})
    if not room or not check_is_bingo_room(room):
        return {"message": "Room not found"}, 404
    if not check_is_room_owner(room, user_email):
        return {"message": "Authentication error"}, 401
    player_names = room['bingo']['player_names']
    return {"players": player_names}, 200

# may be authenticated or unauthenticated. bingo_auth is used.
@bingo_bp.route('/<id>', methods=['GET'])
async def get_bingo_room_checks(id):
    room = await get_db()['Rooms'].find_one({'_id': id})
    if not room or not check_is_bingo_room(room):
        return {"message": "Room not found"}, 404
    
    bingo_auth_response = await bingo_auth()
    isOwner = False
    if checkResponseSuccess(bingo_auth_response):
        user_email = bingo_auth_response[0].get('email')
        isOwner = check_is_room_owner(room, user_email)
    hasStarted = room['bingo']['has_started']
    hasSubmitted = False
    player_name = request.headers.get('player_name')
    if player_name:
        form_submissions = room['bingo']['player_names']
        if player_name in form_submissions:
            hasSubmitted = True

    return {"isOwner": isOwner, "hasStarted": hasStarted,
            "hasSubmitted": hasSubmitted}, 200

# unauthenticated
@bingo_bp.route('/<id>/squares', methods=['GET'])
async def get_bingo_squares(id):
    room = await get_db()['Rooms'].find_one({'_id': id})
    if not room or not check_is_bingo_room(room):
        return {"message": "Room not found"}, 404
    squares = room['bingo']['squares']
    return {"squares": squares}, 200

# Overwrites previous submission if it exists (id is name)
# unauthenticated
@bingo_bp.route('/<id>/submit', methods=['POST'])
async def submit_bingo_squares(id):
    request_json = await request.json
    name = request_json.get('name')
    score = request_json.get('score')
    timestamp = request_json.get('timestamp')
    if not name or score is None or not timestamp:
        return {"message": "Invalid form data"}, 400

    room = await get_db()['Rooms'].find_one({'_id': id})
    if not room or not check_is_bingo_room(room):
        return {"message": "Room not found"}, 404
    submissions = room['bingo']['submissions']
    submissions[name] = request_json
    await get_db()['Rooms'].update_one({"_id": id},
                                        {'$set': {
                                            'bingo.submissions': submissions
                                        }})
    return {"message": "success"}, 200

@bingo_bp.route('/<id>/leaderboard', methods=['GET'])
@authenticate
async def get_bingo_leaderboard(id, user_info):
    room = await get_db()['Rooms'].find_one({'_id': id})
    if not room or not check_is_bingo_room(room):
        return {"message": "Room not found"}, 404
    user_email = user_info.get('email')
    if not check_is_room_owner(room, user_email):
        return {"message": "Authentication error"}, 401
    submissions = room['bingo']['submissions']
    players = get_players_sorted_by_score(submissions)
    players_without_timestamp = get_players_without_timestamp(players)
    
    return {"players": players_without_timestamp[:3]}, 200

def custom_sort(player):
    # Sort by descending score and then ascending timestamp
    return (-player["score"], player["timestamp"])

def get_players_sorted_by_score(submissions):
    players = []
    for name, submission in submissions.items():
        players.append({"name": name, "score": submission['score'], "timestamp": submission['timestamp']})
    players.sort(key=custom_sort)
    return players

def get_players_without_timestamp(players):
    players_without_timestamp = []
    for index, player in enumerate(players):
        players_without_timestamp.append({"position": index, "name": player['name'],
                                          "score": player['score']})
    return players_without_timestamp

@bingo_bp.route('/<id>/start', methods=['POST'])
@authenticate
async def start_bingo_game(id, user_info):
    user_email = user_info.get('email')
    room = await get_db()['Rooms'].find_one({'_id': id})
    if not room or not check_is_bingo_room(room):
        return {"message": "Room not found"}, 404
    if not check_is_room_owner(room, user_email):
        return {"message": "Authentication error"}, 401

    if room['bingo']['has_started']:
        return {"message": "Game has already started"}, 400
    await get_db()['Rooms'].update_one({"_id": id},
                                        {'$set': {
                                            'bingo.has_started': True
                                        }})
    return {"message": "success"}, 200

room_to_players_socket = {}
room_to_owner_socket = {}

def add_player_to_room(room_id):
    if room_id in room_to_players_socket:
        room_to_players_socket[room_id].append(websocket._get_current_object())
    else:
        room_to_players_socket[room_id] = [websocket._get_current_object()]

def add_owner_to_room(room_id):
    room_to_owner_socket[room_id] = websocket._get_current_object()

async def send_msg_to_owner_on_player_join(room_id, is_owner, msg_type):
    # TODO: send an access token and check whether they are the owner instead
    # Add owner to room
    if is_owner:
        add_owner_to_room(room_id)

    # Send message to owner to refresh his route when player joins
    if msg_type == "enter_room" and room_id in room_to_owner_socket:
        logging.info("Sending message to owner")
        await room_to_owner_socket[room_id].send_json({"type": "player_join", "message": "Player joined."})

@bingo_bp.websocket('/ws')
async def ws():
    while True:
        data = json.loads(await websocket.receive())

        await send_msg_to_owner_on_player_join(data.get("room_id"), data.get("is_owner", False), data.get("type", ""))
