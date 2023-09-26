# backend

## Setup
1. Run `python3 -m venv env` to create a virtual environment called "env"
2. Run `source env/bin/activate` to change your environment
3. `pip install -r requirements.txt` to install dependencies
4. Update `.env` file with required variables

## Start Server
1. Run `python3 main.py`

## TRADE DEAL

### Room
```
GET /room/:id
You receive:
{}
I receive:
200: {
  "game_type": "csc"
}
```

### CSC
```
GET /csc/context
You receive:
{}
I receive:
200: {
  "baseContext": {
    "purpose": "first date",
    "relationship": "acquaintances",
    "description": "20-year-old singaporean university computing students who have no social life"
  },
  "cscContext": {
    "numberOfQuestions": 10
  },
  "questions": [
    {"id": 123, "content": "What is your favorite food?"},
    {"id": 234, "content": "What is your favorite icecream?"}
  ]
}

POST /csc/questions/generate
You receive:
{
  "baseContext": {
    "purpose": "first date",
    "relationship": "acquaintances",
    "description": "20-year-old singaporean university computing students who have no social life"
  },
  "cscContext": {
    "numberOfQuestions": 10
  },
}
I receive:
201: {
  "questions": [
    {"id": 123, "content": "Who is more likely to burn down the computing building?"},
    {"id": 123, "content": "Who is the most likely to use Haskel?"}
  ]
}

POST /csc/questions/create
You receive:
{}
I receive:
200: {
  "id": 11357890,
}

PUT /csc/questions/:id
You receive:
{
  "content": "Who is more likely to burn down the computing building?"
}
I receive:
200: {}

DELETE /csc/questions/:id
You receive:
{}
I receive:
201: {}

POST /room/csc/create
You receive:
{}
I receive:
200: {
  "id": "ABGED"
}
```

### BB
```
GET /bb/context
You receive:
{}
I receive:
200: {
  "baseContext": {
    "purpose": "first date",
    "relationship": "acquaintances",
    "description": "20-year-old singaporean university computing students who have no social life"
  },
  "bbContext": {
    "numberOfQuestions": 10
  },
  "questions": [
    {"id": 123, "content": "What is your favorite food?"},
    {"id": 234, "content": "What is your favorite icecream?"}
  ]
}

POST /bb/questions/generate
You receive:
{
  "baseContext": {
    "purpose": "first date",
    "relationship": "acquaintances",
    "description": "20-year-old singaporean university computing students who have no social life"
  },
  "bbContext": {
    "numberOfQuestions": 10
  },
}
I receive:
201: {
  "questions": [
    {"id": 123, "content": "Who is more likely to burn down the computing building?"},
    {"id": 123, "content": "Who is the most likely to use Haskel?"}
  ]
}

POST /bb/questions/create
You receive:
{}
I receive:
200: {
  "id": 11357890,
}

PUT /bb/questions/:id
You receive:
{
  "content": "Who is more likely to burn down the computing building?"
}
I receive:
200: {}

DELETE /bb/questions/:id
You receive:
{}
I receive:
201: {}

POST /room/b/create
You receive:
{}
I receive:
200: {
  "id": "ABGED"
}
```
