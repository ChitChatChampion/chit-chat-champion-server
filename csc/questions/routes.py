from quart import Blueprint, request, jsonify
import prompts.prompts as prompts
from database import check_db, get_db
import logging
from utils.user import get_user_info
from utils.utils import checkResponseSuccess, format_qns_for_fe
from utils.questions import openai_generate_qns, add_questions_to_user_collection, save_contexts, \
    get_questions, update_question, create_question, delete_question

csc_questions_bp = Blueprint('csc_questions_bp', __name__, url_prefix='/csc/questions')


# FOR TESTING PURPOSES ONLY
# Define a route to check if the database is accessible
@csc_questions_bp.route('/check_database', methods=['GET'])
async def check_database():
    res = await check_db()
    return res

@csc_questions_bp.route('/', methods=['GET'])
async def get_csc_questions():
    return await get_questions('csc')

@csc_questions_bp.route('/<id>', methods=['PUT'])
async def update_csc_question(id):
    return await update_question(id, 'csc')

@csc_questions_bp.route('/create', methods=['POST'])
async def create_csc_question():
    return await create_question('csc')

@csc_questions_bp.route('/<id>', methods=['DELETE'])
async def delete_csc_question(id):
    return await delete_question(id, 'csc')
    
# This function is called when the user clicks the "Generate Questions" button
# It saves the baseContext and cscContext in the database in the Users collection
# It also generates the questions in the background and saves them in the database in the Users collection
# Generated questions are added on to the user's existing questions
@csc_questions_bp.route('/generate', methods=['POST'])
async def ai_generate_csc_questions():
    request_json = await request.json
    user_info = await get_user_info()
    logging.error(user_info)
    if not checkResponseSuccess(user_info):
        logging.error("here User not found")
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    contexts_info = save_csc_contexts(user_email, request_json)
    if not checkResponseSuccess(contexts_info):
        return contexts_info
    # generate questions
    messages = craft_openai_csc_messages(contexts_info[0])

    question_arr = openai_generate_qns(user_email, messages)

    db_response = await add_questions_to_user_collection(question_arr, user_email, 'csc')
    if not checkResponseSuccess(db_response):
        return db_response

    db_formatted_questions = db_response[0]
    fe_formatted_questions = format_qns_for_fe(db_formatted_questions)

    logging.info({"questions": fe_formatted_questions})
    return {"questions": fe_formatted_questions}, 201

def craft_openai_csc_messages(contexts):
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


def save_csc_contexts(user_email, request_json):
    return save_contexts(user_email, request_json, 'csc')