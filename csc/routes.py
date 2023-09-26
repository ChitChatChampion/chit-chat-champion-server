from quart import Blueprint, request
import prompts.prompts as prompts
from database import get_db
from utils.user import get_user_info
from utils.utils import checkResponseSuccess, format_qns_for_fe
from utils.questions import save_contexts, get_contexts

csc_bp = Blueprint('csc_bp', __name__, url_prefix='/csc')

# Get csc context from user whose access token is in response header
@csc_bp.route('/context', methods=["GET"])
async def get_csc_context():
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")
    return await get_contexts(user_email, 'csc')

# creates or updates a user's csc (and/or base) context
@csc_bp.route('/context', methods=["POST"])
async def save_csc_context():
    request_json = await request.json
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")

    return await save_contexts(user_email, request_json, 'csc')