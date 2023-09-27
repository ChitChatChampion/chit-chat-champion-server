from quart import request, jsonify
import logging
import requests
from database import get_db
from functools import wraps


USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

async def signup_user(user_info):
    user = user_info
    email = user.get("email")
    name = user.get("name")
    db = get_db()
    # if user with email does not exist, add user to db
    try:
        if not await db["Users"].find_one({"_id": email}):
            # some functions expect these fields to exist even if empty
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
                }
            })
            logging.info(f"Added user {email} to database")
        else:
            logging.info("User already exists in database")
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 500

# Define the authentication decorator
def authenticate(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        access_token = request.headers.get("Access-Token")
        if not access_token:
            return jsonify({"error": "Access token missing"}), 401

        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        try:
            response = requests.get(USERINFO_URL, headers=headers)

            if response.status_code == 200:
                user_info = response.json()
                await signup_user(user_info)
                kwargs['user_info'] = user_info  # Pass user_info as a keyword argument
                return await func(*args, **kwargs)
            else:
                return jsonify({"error": "Failed to fetch user info"}), response.status_code
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return wrapper
