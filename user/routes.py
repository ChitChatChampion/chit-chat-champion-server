from __main__ import app, MODEL
from quart import request, jsonify
import prompts.prompts as prompts
from ast import literal_eval
import logging
import openai
from database import get_db, insert_questions
from nanoid import generate
from utils.utils import getBaseContext, getCscContext
import requests

USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

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
@app.route("/user", methods=["POST"])
def get_user_info():
    # Get the access token from the request headers
    access_token = request.headers.get("access_token")

    if not access_token:
        return jsonify({"error": "Access token missing"}), 401

    # Set up headers for the userinfo request
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        # Make a GET request to the userinfo endpoint
        response = requests.get(USERINFO_URL, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            user_info = response.json()
            name = user_info.get("name")
            email = user_info.get("email")
            return {"status": "success", "name": name, "email": email}
        else:
            return jsonify({"error": "Failed to fetch user info"}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500