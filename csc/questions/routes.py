from nanoid import generate
from quart import Blueprint, request, jsonify
import prompts.prompts as prompts
from database import check_db, get_db
from utils.user import get_user_info
from utils.utils import checkResponseSuccess, prettify_questions

csc_questions_bp = Blueprint('csc_questions_bp', __name__, url_prefix='/csc/questions')


# FOR TESTING PURPOSES ONLY
# Define a route to check if the database is accessible
@csc_questions_bp.route('/check_database', methods=['GET'])
async def check_database():
    res = await check_db()
    return res

@csc_questions_bp.route('/', methods=['GET'])
async def get_csc_questions():
    # TODO: check if this works
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
    return prettify_questions(questions), 200


@csc_questions_bp.route('/<id>', methods=['PUT'])
async def update_csc_question(id):
    request_data = await request.json
    content = request_data.get('content')

    # TODO: check if this works
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

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
    # TODO: check if this works
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

def generate_unique_question_id(questions):
    question_id = generate(size=3)
    if not questions:
        return question_id
    while True:
        if question_id not in questions.keys():
            break
        question_id = generate(size=3)
    return question_id

@csc_questions_bp.route('/<id>', methods=['DELETE'])
async def delete_csc_question(id):
    # TODO: check if this works
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