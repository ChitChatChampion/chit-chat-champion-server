from __main__ import app, MODEL
from quart import request, jsonify
import prompts.prompts as prompts
import asyncio
import json
import logging
import openai
from database import insert_questions
from nanoid import generate
from utils.utils import getBaseContext, getCscContext

async def background_task():
    # sleep for 2 seconds
    await asyncio.sleep(2)
    print("Hello")

@app.route('/hello', methods=['GET'])
async def hello():
    app.add_background_task(background_task)
    return 'hello'

async def query_openai(room_id, messages):
    logging.info("{room_id}: Querying OpenAI")
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
    )
    questions = response['choices'][0]['message']['content']

    logging.info(f"{room_id}: Response obtained from OpenAI: {questions}")

    # add questions in the form of room-id to questions key value pairs
    logging.info(f"{room_id}: Adding questions to database")
    
    await add_gpt_questions_to_db(questions)

    logging.info(f"{room_id}: Done adding questions to database")

async def add_gpt_questions_to_db(questions):
    try:
        if questions[0] != "[":
            # if there is only one question we make it a list
            await insert_questions([questions])
        else:
            # else convert string of questions to list of questions
            await insert_questions(json.loads(questions))
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return jsonify({"message": f"Error: {str(e)}"}), 500

# Creates a CSC room
@app.route('/room/csc', methods=["POST"])
async def create_csc_room():
    request_json = await request.json
    age, familiarity, purpose, group_description = getBaseContext(request_json.get('baseContext'))
    number_of_cards = getCscContext(request_json.get('cscContext'))

    if number_of_cards > 20:
        return {"message": "Too many cards requested"}, 400

    prompt = f"The age range of the participants in the ice-breaker session is {age} years old, they are currently {familiarity}, and the purpose of the ice-breaker session is {purpose}. Other information about the ice-breaker session is that: {group_description}. The number of questions I want you to generate is {number_of_cards}."

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example_csc},
        {"role": "assistant", "content": prompts.assistant_example_csc},
        {"role": "user", "content": prompt}
    ]

    # TODO: check for collisions in room id
    room_id = generate(size=6)

    await query_openai(room_id, messages)

    return {room_id: room_id}