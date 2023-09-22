#!/usr/bin/env python
# encoding: utf-8
import configparser
import os
from quart import Quart, request, jsonify
from motor.motor_asyncio import AsyncIOMotorClient
import openai
import logging

from dotenv import load_dotenv

app = Quart(__name__)

MODEL = "gpt-3.5-turbo"

# Configure database
config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))
app.config['MONGO_URI'] = config['TEST']['DB_URI']

# Create an AsyncIOMotorClient within the app context
@app.before_serving
async def setup_mongodb():
    app.db = AsyncIOMotorClient(app.config['MONGO_URI']).get_database("ChitChatChampions")

load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")

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