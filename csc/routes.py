import json
import logging
from quart import Blueprint, request
import prompts.prompts as prompts
from utils.user import authenticate
from utils.entities import save_bb_csc_contexts, get_questions_contexts

csc_bp = Blueprint('csc_bp', __name__, url_prefix='/csc')

# Get csc context from user whose access token is in response header
@csc_bp.route('/context', methods=["GET"])
@authenticate
async def get_csc_context(user_info):
    user_email = user_info.get('email')
    return await get_questions_contexts(user_email, 'csc')

# creates or updates a user's csc (and/or base) context
@csc_bp.route('/context', methods=["POST"])
@authenticate
async def save_csc_context(user_info):
    request_json = await request.json
    user_email = user_info.get('email')

    return await save_bb_csc_contexts(user_email, request_json, 'csc')
