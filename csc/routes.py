from quart import Blueprint, request
import prompts.prompts as prompts
from database import get_db
from utils.user import get_user_info
from utils.utils import checkResponseSuccess, getBaseContext, getCscContext, prettify_questions

csc_bp = Blueprint('csc_bp', __name__, url_prefix='/csc')

# Get csc context from user whose access token is in response header
@csc_bp.route('/context', methods=["GET"])
async def get_csc_context():
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")
    db = get_db()
    user = await db["Users"].find_one({"_id": user_email})
    # assumes user should have been added to db upon first login
    if not user:
        return {"error": "User not found"}, 404
    return {
        "baseContext": user["baseContext"],
        "cscContext": user["csc"]["cscContext"],
        "questions": prettify_questions(user["csc"]["questions"])
    }, 200

# creates or updates a user's csc (and/or base) context
@csc_bp.route('/context', methods=["POST"])
async def save_csc_context():
    request_json = await request.json
    purpose, relationship, description = getBaseContext(request_json.get('baseContext'))
    numberOfCards = getCscContext(request_json.get('cscContext')).get('numberOfCards')
    user_info = get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    user = await get_db()["Users"].find_one({"_id": user_email})
    if not user:
        return {"message": "User not found"}, 404

    await get_db()["Users"].update_one({"_id": user_email},
                                    {'$set': {
                                        'baseContext': {
                                            'purpose': purpose,
                                            'relationship': relationship,
                                            'description': description
                                        },
                                        'csc': {
                                            'cscContext': {
                                                'numberOfCards': numberOfCards
                                            }
                                        }
                                    }}, upsert=True
                                )
    return {"message": "success"}