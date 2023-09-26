#!/usr/bin/env python
# encoding: utf-8
import os
from quart import Quart
from quart_cors import cors
from motor.motor_asyncio import AsyncIOMotorClient
import openai
import logging
from bb.questions.routes import bb_questions_bp
from csc.questions.routes import csc_questions_bp
from bb.routes import bb_bp
from bingo.routes import bingo_bp
from csc.routes import csc_bp
from room.routes import room_bp
from user.routes import user_bp

from dotenv import load_dotenv

app = Quart(__name__)

MODEL = "gpt-3.5-turbo"

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
app.config['MONGODB_URI'] = os.getenv("MONGODB_URI")
app.config['MODEL'] = MODEL

# Configure CORS policies
# TODO: update this to only allow requests from the frontend app
app = cors(
    app,
    allow_origin="*"
)

# Create an AsyncIOMotorClient within the app context
@app.before_serving
async def setup_mongodb():
    app.db = AsyncIOMotorClient(app.config['MONGODB_URI']).get_database("ChitChatChampions")

@app.route('/', methods=['GET'])
def query_records():
    return {"message": "Hello World!"}

# Register all blueprints
app.register_blueprint(bb_bp)
app.register_blueprint(bb_questions_bp)
app.register_blueprint(bingo_bp)
app.register_blueprint(csc_bp)
app.register_blueprint(csc_questions_bp)
app.register_blueprint(user_bp)
app.register_blueprint(room_bp)


logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    app.run(port=8080, debug=True)