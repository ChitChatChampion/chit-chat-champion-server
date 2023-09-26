from quart import Blueprint, request
import prompts.prompts as prompts
from database import get_db
import logging
from utils.user import get_user_info
from utils.utils import checkResponseSuccess
from utils.questions import save_contexts, get_contexts

bb_bp = Blueprint('bb_bp', __name__, url_prefix='/bb')

# Get bb context from user whose access token is in response header
@bb_bp.route('/context', methods=["GET"])
async def get_bb_context():
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")
    return await get_contexts(user_email, 'bb')

# creates or updates a user's bb (and/or base) context
@bb_bp.route('/context', methods=["POST"])
async def save_bb_context():
    request_json = await request.json
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    return await save_contexts(user_email, request_json, 'bb')