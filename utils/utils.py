import json
import logging
import openai
from quart import current_app

def getBaseContext(baseContext):
    purpose = baseContext.get('purpose')
    relationship = baseContext.get('relationship')
    description = baseContext.get('description')
    return purpose, relationship, description

def getCscContext(cscContext):
    number_of_questions = cscContext.get('number_of_questions')
    return number_of_questions

def getBbContext(bbContext):
    number_of_questions = bbContext.get('number_of_questions')
    return number_of_questions

def getGameContext(request_json, game_type):
    if game_type == "csc":
        return getCscContext(request_json.get(f'{game_type}Context'))
    elif game_type == "bb":
        return getBbContext(request_json.get(f'{game_type}Context'))

def checkResponseSuccess(response):
    status = response[1]
    return status == 200 or status == 201

def format_qns_for_fe(questions):
    return [{"id": id, "content": content} for id, content in questions.items()]

def openai_generate_response(user_email, messages):
    # escape special characters in messages
    logging.info(f"{user_email}: Querying OpenAI")
    response = openai.ChatCompletion.create(
        model=current_app.config['MODEL'],
        messages=messages,
        temperature=0.7,
    )
    openai_response = response['choices'][0]['message']['content']

    response_arr = parse_openai_response(openai_response)
    logging.info("SUCCESSFULLY PARSED OPENAI RESPONSE")

    return response_arr

def parse_openai_response(openai_response):
    if openai_response[0] == '[' and openai_response[-1] == ']':
        try:
            return json.loads(openai_response)
        except json.JSONDecodeError as e:
            logging.info(f"Openai response JSON parsing error: {e}")
            return []
    else:
        # We just remove the quotation marks for a single question response
        if openai_response[0] == '"' and openai_response[-1] == '"':
            openai_response = openai_response[1:-1]
        return [openai_response]