from quart import Blueprint
from database import get_db
from utils.user import get_user_info
from utils.utils import checkResponseSuccess

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')

# POST
# /user
# header
# {
# 	access_token: ""
# }
# RETURN
# {
# 	status: "success"
# }
# Test route
@user_bp.route("/", methods=["POST"])
async def get_user_info_test():
    return await get_user_info()

# Endpoint to check if the user is an owner of a room
@user_bp.route("/room/<room_id>", methods=["GET"])
async def is_owner(room_id):
    user_info = await get_user_info()
    if not checkResponseSuccess(user_info):
        return user_info # will contain error and status message
    user_email = user_info[0].get("email")
    room = await get_db()["Rooms"].find_one({"_id": room_id})

    if room.get('user_id') == user_email:
        return {"is_owner": True}, 200
    else:
        return {"is_owner": False}, 200
