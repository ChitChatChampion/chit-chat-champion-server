from database import get_db
import logging
from nanoid import generate


async def generate_unique_room_id_from(game_type, user_email):
    # Find room that may have been created by the same user for the same game_type
    room = await get_db()["Rooms"].find_one({'user_id': user_email, 'game_type': game_type})
    if room:
        return room['_id']
    # If no room found, generate a new room id
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
        return {"message": "Room not found"}, 404

    await get_db()["Rooms"].update_one({"_id": room_id},
                                        {'$set': {
                                        'is_published': set_is_published
                                        }})
    
    return {"message": f"Room {room_id} {'published' if set_is_published else 'unpublished'} successfully"}

# This create room should only be used for csc, bb 
# and other games with 'questions'/format
async def create_room(user_info, game_type):
    user_email = user_info.get('email')

    logging.info(f"{user_email}: Creating {game_type} room")

    # Check if there are any blank questions. If there are, return error
    user = await get_db()['Users'].find_one({"_id": user_email})
    questions = user[game_type]['questions']
    for _, content in questions.items():
        if content == "":
            return {"message": "Cannot create room with blank questions"}, 400

    room_id = await generate_unique_room_id_from(game_type, user_email)

    # update user with room_id. Do we need this?
    await get_db()['Users'].update_one({'_id': user_email},
                                    {'$set': {
                                        'room_id': room_id
                                    }}, upsert=True
                                )

    questions = user[game_type]['questions']
    # create room with all of user's details
    await get_db()['Rooms'].update_one(
        {'_id': room_id},
        {'$set': {'user_id': user_email,
        'game_type': game_type,
        'is_published': True,
        'questions': questions
        }}, upsert=True)
    return {"id": room_id}, 201