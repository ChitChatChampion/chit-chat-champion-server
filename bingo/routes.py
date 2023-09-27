from quart import Blueprint
import prompts.prompts as prompts
from database import get_db
import logging
from utils.user import authenticate
from utils.utils import checkResponseSuccess, openai_generate_response

bingo_bp = Blueprint('bingo_bp', __name__, url_prefix='/bingo')

# This function is called when the creator clicks the "Generate Bingo" button
# IF THERE ARE EXISTING SQUARES, THIS FUNCTION WILL DELETE/OVERWRITE THEM
# It generates bingo squares for players (not game creator) with data that are already stored in the room
# This data should come from the forms that users submit before the game starts
@bingo_bp.route('/<id>/generate', methods=['POST'])
@authenticate
async def ai_generate_bingo_squares(id, user_info):
    user_email = user_info.get('email')

    bingo_room = await get_db()['Rooms'].find_one({'_id': id})
    is_valid_room = check_bingo_room(bingo_room)
    if not checkResponseSuccess(is_valid_room):
        return is_valid_room

    player_contexts = get_bingo_player_contexts(bingo_room)
    messages = craft_openai_bingo_messages(player_contexts)

    bingo_squares_arr, message = openai_generate_response(user_email, messages)

    logging.info(f"{user_email}: OpenAI response: {bingo_squares_arr}")

    await get_db()['Rooms'].update_one({"_id": id},
                                        {'$set': {
                                            'bingo.squares': bingo_squares_arr
                                        }})

    return {"squares": bingo_squares_arr}, 201

def check_bingo_room(bingo_room):
    if not bingo_room or not bingo_room['game_type'] == 'bingo':
        return {"message": "Room not found"}, 404
    if not bingo_room['bingo'] or not bingo_room['bingo']['players']:
        return {"message": "No players found"}, 404
    return {"message": "Success"}, 200

def get_bingo_player_contexts(bingo_room):
    return bingo_room['bingo']['players']

def craft_openai_bingo_messages(contexts):
    prompt = f"Help me generate squares for each player in a bingo game. \
    Generate something interesting with a title and a description. \
    Try to keep the title and description as short as possible. The description must be less than 10 words. \
    Pick the most obscure fact that makes it hard for others to guess who belongs in that square. \
    Try to avoid including anything similar between players in the bingo squares. \
    The following json objects contain the players' details: \
    {contexts}"

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example_bingo},
        {"role": "assistant", "content": prompts.assistant_example_bingo},
        {"role": "user", "content": prompt}
    ]
    return messages

@bingo_bp.route('/<id>/squares', methods=['GET'])
async def get_bingo_squares(id):
    db = get_db()
    room = await db['Rooms'].find_one({'_id': id})
    squares = room['bingo']['squares']
    logging.info(squares)
    return squares, 200