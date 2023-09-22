from __main__ import app, MODEL
from quart import request, jsonify
from csc.questions.routes import generate_unique_room_id, openai_generate_qns_add_db, set_room_published_status
import prompts.prompts as prompts
from ast import literal_eval
from database import get_db, insert_questions
from nanoid import generate
from utils.utils import getCscContext
from user.routes import get_user_info

# creates or updates a user's csc (and/or base) context
@app.route('/csc/context', methods=["POST"])
async def save_csc_context():
    request_json = await request.json
    purpose, relationship, description = getBaseContext(request_json.get('baseContext'))
    numberOfCards = getCscContext(request_json.get('cscContext')).get('numberOfCards')
    # TODO: check header access token, get user email
    # user_email = get_user_info().get('email')
    user_email = "user@example.com"
    # find user with email in db and see if basecontext exists
    # if exists, update
    # else, create
    user = get_db()["Users"].find_one({"_id": user_email})
    if user:
        get_db()["Users"].update_one({"_id": user_email},
                                            {'$set': {
                                             'baseContext': {
                                                 'purpose': purpose,
                                                 'relationship': relationship,
                                                 'description': description
                                             },
                                             'cscContext': {
                                                 'numberOfCards': numberOfCards
                                             }
                                            }}, upsert=True
                                     )
    else:
        return {"message": "User not found"}, 404
    return {"message": "success"}


def getBaseContext(baseContext):
    purpose = baseContext.get('purpose')
    relationship = baseContext.get('relationship')
    description = baseContext.get('description')
    return purpose, relationship, description
