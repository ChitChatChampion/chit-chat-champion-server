from quart import current_app
from motor.motor_asyncio import AsyncIOMotorClient
from werkzeug.local import LocalProxy

def get_db():
    if not hasattr(current_app, 'db'):
        current_app.db = AsyncIOMotorClient(current_app.config['MONGODB_URI']).get_database("ChitChatChampions")
    return current_app.db

def get_questions_collection():
    db = get_db()
    return db['Questions']

db = LocalProxy(get_db)
questions_collection = LocalProxy(get_questions_collection)