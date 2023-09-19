from __main__ import app
from quart import request, jsonify
import prompts.prompts as prompts
from database import check_db, get_all_questions, add_question_db, update_question_db, delete_question_db


# FOR TESTING PURPOSES ONLY
# Define a route to check if the database is accessible
@app.route('/check_database', methods=['GET'])
async def check_database():
    res = await check_db()
    return res

# Define a route to get all the questions in the database
@app.route('/questions', methods=['GET'])
async def get_questions():
    res = await get_all_questions()
    return res

# Define a route to add a question to the database
@app.route('/questions/add', methods=['POST'])
async def add_question():
    try:
        # Get the question from the request body
        # e.g. for testing: {"question": "What is your favorite programming language?"}
        question_data = await request.json
        question = question_data.get('question')

        # Insert the question into the database
        await add_question_db(question)

        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question added successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500

# Define a route to update a question in the database
@app.route('/questions/update/<question_id>', methods=['PUT'])
async def update_question(question_id):
    try:
        # Get the question from the request body
        # e.g. for testing: {"question": "What is your favorite programming language?"}
        question_data = await request.json
        new_question = question_data.get('question')

        # Update the question in the database with the question_id
        await update_question_db(question_id, new_question)
        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question updated successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
    
# Define a route to delete a question from the database
@app.route('/questions/delete/<question_id>', methods=['DELETE'])
async def delete_question(question_id):
    try:
        # Delete the question from the database with the question_id
        await delete_question_db(question_id)
        # Return a 200 OK response if the operation succeeds
        return jsonify({"message": "Question deleted successfully"}), 200
    except Exception as e:
        # Handle any exceptions that might occur during the database operation
        error_message = f"Error: {str(e)}"
        return jsonify({"message": error_message}), 500
