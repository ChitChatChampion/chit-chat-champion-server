from quart import Blueprint, current_app, request, jsonify
import prompts.prompts as prompts
from database import check_db, get_db
import logging
from utils.user import get_user_info
from utils.utils import checkResponseSuccess, getBaseContext, getCscContext, format_questions_for_fe
from utils.questions import generate_unique_question_id, generate_unique_room_id, openai_generate_and_save_qns

csc_questions_bp = Blueprint('csc_questions_bp', __name__, url_prefix='/csc/questions')


# FOR TESTING PURPOSES ONLY
# Define a route to check if the database is accessible
@csc_questions_bp.route('/check_database', methods=['GET'])
async def check_database():
    res = await check_db()
    return res

@csc_questions_bp.route('/', methods=['GET'])
async def get_csc_questions():
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message

    user_email = user_info[0].get("email")
    # user_email = "user@example.com"

    user = await get_db()['Users'].find_one({"_id": user_email})
    if not user:
        return jsonify({"error": "User not found"}), 404
    questions = user['csc']['questions']
    if not questions:
        return {"questions": []}, 200
    return format_questions_for_fe(questions), 200


@csc_questions_bp.route('/<id>', methods=['PUT'])
async def update_csc_question(id):
    request_data = await request.json
    user_info = get_user_info()
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
        questions = user['csc']['questions']
        questions[id] = content
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {'csc.questions': questions}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

@csc_questions_bp.route('/csc/questions/create', methods=['POST'])
async def create_csc_question():
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user['csc']['questions']
        # generate empty new question
        question_id = generate_unique_question_id(questions)
        questions[question_id] = ""
        await get_db()['Users'].update_one({"_id": user_email},
                                           {'$set': {'csc.questions': questions}})

        return jsonify({"id": question_id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

@csc_questions_bp.route('/<id>', methods=['DELETE'])
async def delete_csc_question(id):
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    try:
        user = await get_db()['Users'].find_one({"_id": user_email})
        if not user:
            return jsonify({"error": "User not found"}), 404
        questions = user['csc']['questions']
        del questions[id]
        await get_db()['Users'].update_one({"_id": user_email}, {'$set': {'csc.questions': questions}})

        return jsonify({"id": id}), 200
    except Exception as e:
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
# This function is called when the user clicks the "Generate Questions" button
# It saves the baseContext and cscContext in the database in the Users collection
# It also generates the questions in the background and saves them in the database in the Users collection
@csc_questions_bp.route('/generate', methods=['POST'])
async def ai_generate_csc_questions():
    request_json = await request.json
    user_info = get_user_info()
    logging.error(user_info)
    if not checkResponseSuccess(user_info):
        logging.error("here User not found")
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")
    user = await get_db()['Users'].find_one({"_id": user_email})
    # add user to db if user does not exist
    if not user:
        await get_db()['Users'].insert_one({"_id": user_email})
    
    contexts_info = save_contexts(user_email, request_json)
    if not checkResponseSuccess(contexts_info):
        return contexts_info

    # generate questions
    messages = craft_openai_messages(contexts_info[0])

    openai_returned = await openai_generate_and_save_qns(user_email, messages)
    if not checkResponseSuccess(openai_returned):
        return openai_returned
    db_formatted_questions = openai_returned[0]
    fe_formatted_questions = format_questions_for_fe(db_formatted_questions)
    logging.info({"questions": fe_formatted_questions})

    return {"questions": fe_formatted_questions}, 201

def craft_openai_messages(contexts):
    purpose = contexts.get("purpose")
    relationship = contexts.get("relationship")
    description = contexts.get("description")
    number_of_questions = contexts.get("number_of_questions")

    prompt = f"The participants are {relationship}, and the purpose of the ice-breaker session is {purpose}. \
        Other information about the participants is that: {description}. \
        The number of questions I want you to generate is {number_of_questions}."

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example_csc},
        {"role": "assistant", "content": prompts.assistant_example_csc},
        {"role": "user", "content": prompt}
    ]
    return messages


def save_contexts(user_email, request_json):
    purpose, relationship, description  = getBaseContext(request_json.get('baseContext'))
    number_of_questions = getCscContext(request_json.get('cscContext'))
    if number_of_questions > 20:
        return {"message": "Too many questions requested"}, 400

    db = get_db()
    db["Users"].update_one({"_id": user_email},
                                    {'$set': {
                                        'baseContext': {
                                            'purpose': purpose,
                                            'relationship': relationship,
                                            'description': description
                                        },
                                        'csc': {
                                            'cscContext': {
                                                'numberOfQuestions': number_of_questions
                                            }
                                        }
                                    }}, upsert=True
                                )
    return {"purpose": purpose, "relationship": relationship, "description": description,
            "number_of_questions": number_of_questions}, 200