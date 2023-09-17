#!/usr/bin/env python
# encoding: utf-8
import os
from flask import Flask, request, json
import openai
import prompts
from utils import getBaseContext, getCscContext
from dotenv import load_dotenv

app = Flask(__name__)
MODEL = "gpt-3.5-turbo"

load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")

@app.route('/', methods=['GET'])
def query_records():
    return {"message": "Hello World!"}

# Creates a CSC room
@app.route('/room/csc', methods=["POST"])
def create_csc_room():
    age, familiarity, purpose, group_description = getBaseContext(request.json.get('baseContext'))
    # TODO: limit the number of cards for our token sanity
    number_of_cards = getCscContext(request.json.get('cscContext'))
    if number_of_cards > 20:
        return {"message": "Too many cards requested"}, 400

    prompt = f"The age range of the participants in the ice-breaker session is {age} years old, they are currently {familiarity}, and the purpose of the ice-breaker session is {purpose}. Other information about the ice-breaker session is that: {group_description}. The number of questions I want you to generate is {number_of_cards}."

    messages = [
        {"role": "system", "content": prompts.system_prompt},
        {"role": "user", "content": prompts.user_example_csc},
        {"role": "assistant", "content": prompts.assistant_example_csc},
        {"role": "user", "content": prompt}
    ]

    # TODO: create a promise for this that adds something to the db when it resolves. 
    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,  # this is the degree of randomness of the model's output
    )
    result = response.get('choices')[0].get('message').get('content')

    return result

app.run(port=8080, debug=True)