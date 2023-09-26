from database import get_db
import logging
from nanoid import generate
from quart import jsonify, request
from utils.user import get_user_info
from utils.utils import getBaseContext, checkResponseSuccess, format_qns_for_fe

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
        question_id = generate_unique_question_id(questions)
        questions[question_id] = question
    logging.info(questions)
    return questions

def generate_unique_question_id(questions):
    question_id = generate(size=3)
    if not questions:
        return question_id
    while True:
        if question_id not in questions.keys():
            break
        question_id = generate(size=3)
    return question_id

# assumes csc or bb game type; check if fields are different for quiz
def save_contexts(user_email, request_json, game_type):
    purpose, relationship, description  = getBaseContext(request_json.get('baseContext'))

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

async def get_questions(game_type):
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message

    user_email = user_info[0].get("email")

    user = await get_db()['Users'].find_one({"_id": user_email})
    if not user:
        return jsonify({"error": "User not found"}), 404
    questions = user[game_type]['questions']
    if not questions:
        return {"questions": []}, 200
    return format_qns_for_fe(questions), 200

async def update_question(id, game_type):
    request_data = await request.json
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    content = request_data.get('content')

    if not user_email:
        return jsonify({"error": "Invalid user"}), 401

    if not content:
        return jsonify({"error": "No content data"}), 400

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user[game_type]['questions']
        questions_field = f"{game_type}.questions"
        questions[id] = content
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {questions_field: questions}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
async def create_question(game_type):
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user[game_type]['questions']
        # generate empty new question
        question_id = generate_unique_question_id(questions)
        questions[question_id] = ""
        questions_field = f"{game_type}.questions"
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {questions_field: questions}})

        return jsonify({"id": question_id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
async def delete_question(id, game_type):
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user[game_type]['questions']
        del questions[id]

        questions_field = f"{game_type}.questions"
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {questions_field: questions}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

