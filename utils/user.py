from quart import request, jsonify
import logging
import requests
from database import get_db


USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

async def signup_user(user_info):
    user = user_info
    email = user.get("email")
    name = user.get("name")
    db = get_db()
    # if user with email does not exist, add user to db
    try:
        if not await db["Users"].find_one({"_id": email}):
            await db["Users"].insert_one({
                '_id': email,
                'name': name,
                'baseContext': {},
                'bb': {
                    'bbContext': {},
                    'questions': {}
                },
                'csc': {
                    'cscContext': {},
                    'questions': {}
                },
                'quiz': {
                    'quizContext': {},
                    'questions': {}
                }
            })
            logging.info(f"Added user {email} to database")
        else:
            logging.info("User already exists in database")
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 500

async def get_user_info():
    # Get the access token from the request headers
    # logging.error(request.headers)
    access_token =  request.headers.get("Access-Token")

    if not access_token:
        logging.error("Access token missing")
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
            await signup_user(user_info)
            logging.info("Successfully fetched user info")
            return {"status": "success", "name": name, "email": email}, response.status_code
        else:
            return jsonify({"error": "Failed to fetch user info"}), response.status_code
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 500