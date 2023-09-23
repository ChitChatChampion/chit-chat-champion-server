from quart import Blueprint
from utils.user import get_user_info

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
def get_user_info_test():
    return get_user_info()
