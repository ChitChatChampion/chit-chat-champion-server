from quart import request, jsonify
import logging
import requests


USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def get_user_info():
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
            return {"status": "success", "name": name, "email": email}, response.status_code
        else:
            return jsonify({"error": "Failed to fetch user info"}), response.status_code
    except Exception as e:
        logging.error(e)
        return jsonify({"error": str(e)}), 500