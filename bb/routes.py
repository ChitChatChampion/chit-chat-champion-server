from quart import Blueprint, request
import prompts.prompts as prompts
from utils.user import authenticate
from utils.entities import save_bb_csc_contexts, get_questions_contexts

bb_bp = Blueprint('bb_bp', __name__, url_prefix='/bb')

# Get bb context from user whose access token is in response header
@bb_bp.route('/context', methods=["GET"])
@authenticate
async def get_bb_context(user_info):
    user_email = user_info.get('email')
    return await get_questions_contexts(user_email, 'bb')

# creates or updates a user's bb (and/or base) context
@bb_bp.route('/context', methods=["POST"])
@authenticate
async def save_bb_context(user_info):
    request_json = await request.json
    user_email = user_info.get('email')

    return await save_bb_csc_contexts(user_email, request_json, 'bb')