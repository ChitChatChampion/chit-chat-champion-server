from database import get_db
import logging
from nanoid import generate
from quart import jsonify, request
from utils.utils import getBaseContext, format_entities_for_fe

MIN_INPUT_PROMPT_LENGTH = 3
MAX__INPUT_PROMPT_LENGTH = 100

async def add_questions_to_user_collection(ai_questions_arr, user_email, game_type):
    try:
        logging.info(f"{user_email}: Adding questions to collection")
        user = await get_db()["Users"].find_one({"_id": user_email})

        existing_questions = user[game_type]["questions"]
        formatted_questions = format_qns_for_db(existing_questions, ai_questions_arr)

        field_to_add = f"{game_type}.questions"
        await get_db()["Users"].update_one({"_id": user_email},
                                        {'$set': {
                                            field_to_add: formatted_questions
                                        }})
        return formatted_questions, 201
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: adding questions to collection"}), 500

# Format the questions as a dictionary where keys are ids and values are questions' contents
def format_qns_for_db(existing_questions, ai_questions):
    questions = existing_questions
    for question in ai_questions:
        question_id = generate_unique_entity_id(questions)
        questions[question_id] = question
    logging.info(questions)
    return questions

def generate_unique_entity_id(entities: dict):
    question_id = generate(size=3)
    if not entities:
        return question_id
    while True:
        if question_id not in entities.keys():
            break
        question_id = generate(size=3)
    return question_id

# assumes csc or bb game type; check if fields are different for quiz
def save_bb_csc_contexts(user_email, request_json, game_type):
    baseContext = request_json.get('baseContext')
    if not baseContext:
        return {"message": "No baseContext data"}, 400
    
    purpose, relationship, description  = getBaseContext(request_json.get('baseContext'))

    if not MIN_INPUT_PROMPT_LENGTH <= len(purpose) <= MAX__INPUT_PROMPT_LENGTH or \
        not MIN_INPUT_PROMPT_LENGTH <= len(description) <= MAX__INPUT_PROMPT_LENGTH:
        return {"message": "Invalid input prompt length"}, 400

    number_of_questions = request_json.get(f'{game_type}Context').get('number_of_questions')

    if number_of_questions > 20:
        return {"message": "Too many questions requested"}, 400

    db = get_db()
    
    num_questions_field = f'{game_type}.{game_type}Context.numberOfQuestions'
    db["Users"].update_one({"_id": user_email},
                                    {'$set': {
                                        'baseContext': {
                                            'purpose': purpose,
                                            'relationship': relationship,
                                            'description': description
                                        },
                                        num_questions_field: number_of_questions
                                    }}, upsert=True
                                )
    return {"purpose": purpose, "relationship": relationship, "description": description,
            "number_of_questions": number_of_questions}, 201

async def get_entities(user_info, game_type, entity_type="questions"):
    user_email = user_info.get("email")

    user = await get_db()['Users'].find_one({"_id": user_email})
    if not user:
        return jsonify({"message": "User not found"}), 404
    entities = user[game_type][entity_type]
    if not entities:
        return {"questions": []}, 200
    return format_entities_for_fe(entities), 200

async def update_entity(id, user_info, game_type, entity_type="questions"):
    request_data = await request.json
    user_email = user_info.get("email")

    content = request_data.get('content')

    if not user_email:
        return jsonify({"message": "Invalid user"}), 401

    if not content:
        return jsonify({"message": "No content data"}), 400

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"message": "User not found"}), 404
        entities = user[game_type][entity_type]
        entities_field = f"{game_type}.{entity_type}"
        entities[id] = content
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {entities_field: entities}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
async def create_entity(user_info, game_type, entity_type="questions"):
    user_email = user_info.get("email")

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"message": "User not found"}), 404
        entities = user[game_type][entity_type]
        # generate empty new entity
        entity_id = generate_unique_entity_id(entities)
        entities[entity_id] = ""
        entity_field = f"{game_type}.{entity_type}"
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {entity_field: entities}})

        return jsonify({"id": entity_id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
async def delete_entity(id, user_info, game_type, entity_type="questions"):
    user_email = user_info.get("email")

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"message": "User not found"}), 404
        entities = user[game_type][entity_type]
        del entities[id]

        entity_field = f"{game_type}.{entity_type}"
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {entity_field: entities}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

async def get_questions_contexts(user_email, game_type):
    if game_type not in ['csc', 'bb']:
        logging.error(f"Invalid game type {game_type} in get_contexts")
        return {"message": "message"}, 400
    db = get_db()
    user = await db['Users'].find_one({'_id': user_email})
    if not user:
        logging.error(f"User {user_email} not found")
        return {"message": "User not found"}, 404
    gameContext = f"{game_type}Context"
    return {
        "baseContext": user["baseContext"],
        gameContext: user[game_type][gameContext],
        "questions": format_entities_for_fe(user[game_type]["questions"])
    }, 200

async def get_bingo_context(user_email):
    db = get_db
    user = await db['Users'].find_one({'_id': user_email})
    if not user:
        logging.error(f"User {user_email} not found")
        return {"message": "User not found"}, 404
    fields = user["bingo"]["fields"]
    return {"fields": fields}, 200