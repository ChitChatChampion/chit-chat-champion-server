# backend

## Setup
1. Run `python3 -m venv env`
2. Run `source env/bin/activate` to change your environment
3. `pip install -r requirements.txt` to install dependencies
4. Go to http://127.0.0.1:8000/api/user/create/ to create a new user in the system
5. Go to http://127.0.0.1:8000/api/user/token/ and log in using that user to get the token
6. Use ModHeader to change the header `Authorization` to `Token <your_token_here>`, where `your_token_here` refers to the token gotten in step 5

## Start Server
1. Run `source env/bin/activate` to change your environment
2. `python3 manage.py migrate`
3. `python3 manage.py runserver`
