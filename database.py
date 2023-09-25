from quart import current_app, jsonify
from motor.motor_asyncio import AsyncIOMotorClient

def get_db():
    if not hasattr(current_app, 'db'):
        current_app.db = AsyncIOMotorClient(current_app.config['MONGODB_URI']).get_database("ChitChatChampions")
    return current_app.db

async def check_db():
    try:
        # Use the MongoDB client to ping the database
        get_db().command('ping')
        return jsonify({"message": "Database is accessible"})
    except Exception as e:
        return jsonify({"message": f"Database is not accessible: {str(e)}"})