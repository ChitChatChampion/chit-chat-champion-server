#!/usr/bin/env python
# encoding: utf-8
import configparser
import os
from quart import Quart, request, jsonify
from motor.motor_asyncio import AsyncIOMotorClient
import openai
import logging

from dotenv import load_dotenv
from quart import Quart

app = Quart(__name__)

MODEL = "gpt-3.5-turbo"

load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")
app.config['MONGODB_URI'] = os.getenv("MONGODB_URI")

# Create an AsyncIOMotorClient within the app context
@app.before_serving
async def setup_mongodb():
    app.db = AsyncIOMotorClient(app.config['MONGODB_URI']).get_database("ChitChatChampions")

@app.route('/', methods=['GET'])
def query_records():
    return {"message": "Hello World!"}

# Import all routes
import csc.routes
import csc.questions.routes
import user.routes

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    app.run(port=8080, debug=True)