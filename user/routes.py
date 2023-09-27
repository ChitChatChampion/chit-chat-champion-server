from database import get_db
from quart import Blueprint
from utils.user import authenticate

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
@authenticate
async def get_user_info_test(_):
    return {"message": "success"}, 200

# Endpoint to check if the user is an owner of a room
@user_bp.route("/room/<room_id>", methods=["GET"])
@authenticate
async def is_owner(room_id, user_info):
    user_email = user_info.get("email")
    room = await get_db()["Rooms"].find_one({"user_id": user_email})

    if room.get('_id') == room_id:
        return {"is_owner": True}, 200
    else:
        return {"is_owner": False}, 200
