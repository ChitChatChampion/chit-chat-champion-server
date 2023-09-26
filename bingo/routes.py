from quart import Blueprint, request
import prompts.prompts as prompts
from database import get_db
import json
import logging
from utils.user import get_user_info
from utils.utils import checkResponseSuccess, openai_generate_response

bingo_bp = Blueprint('bingo_bp', __name__, url_prefix='/bingo')

# This function is called when the creator clicks the "Generate Questions" button
# It generates bingo squares for players (not game creator) with data that are already stored in the room
# This data should come from the forms that users submit before the game starts
@bingo_bp.route('/<id>/generate', methods=['POST'])
async def ai_generate_bingo_squares(id):
    # user_info = await get_user_info()
    # if not checkResponseSuccess(user_info):
    #     logging.error("here User not found")
    #     return user_info # will contain error and status message
    # user_email = user_info[0].get('email')
    user_email = "example.com"

    # TODO: retrieve contexts from room in db
    # contexts will be the info input from form by users
    # I envision Room db: room: bingo: players: {
        # "name1": {"age": "12", "desc": "I like to eat"},
        # "name2": {"age": "12", "desc": "I like to eat"}
    # }
    # bingo_room = get_db()['Rooms'].find_one({'_id': id})
    # if not bingo_room or not bingo_room['game_type'] == 'bingo':
    #     return {"error": "Room not found"}, 404
    # if not bingo_room['bingo'] or not bingo_room['bingo']['players']:
    #     return {"error": "No players found"}, 404
    
    # bingo_players = ['bingo']['players']
    # for player in bingo_players:
    #     player_contexts = bingo_players[player]
    messages = craft_openai_bingo_messages("player_contexts")

    bingo_squares_arr = openai_generate_response(user_email, messages)
    logging.info(f"{user_email}: OpenAI response: {bingo_squares_arr}")

    # TODO: add bingo squares to room in db

    # TODO: return bingo squares to frontend

    return {"bingo_squares": bingo_squares_arr}, 201

def craft_openai_bingo_messages(contexts):
    # TODO: convert contexts into json format to send to openai?
    # should alr look similar when returned from db
    prompt = """
    Help me generate squares for each player in a bingo game. \
    Generate something interesting with a title and a description. \
    Try to keep the title and description as short as possible. The description must be less than 10 words. \
    Pick the most obscure fact that makes it hard for others to guess who belongs in that square. \
    Try to avoid including anything similar between players in the bingo squares. \
    The following json objects contain the players' details: 
    [
        {
            "name": "Jonathan",
            "gender": "male",
            "age": "22",
            "description": "NTU computing student, loves Honkai Star Rail. Loves watching Steven He. Kdramas are my fave. Gong Woo :)"
        },
        {
            "name": "Icarus \"Icky\" Iguana",
            "gender": "helicopter",
            "age": "23",
            "description": "I like flying. Woosh."
        }
    ]
    """

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example_bingo},
        {"role": "assistant", "content": prompts.assistant_example_bingo},
        {"role": "user", "content": prompt}
    ]
    return messages