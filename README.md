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
200: {}

POST /room/bb/create
You receive:
{}
I receive:
200: {
  "id": "ABGED"
}
```

### Bingo
```
GET /bingo/context
You receive:

POST /bingo/<id>/generate
You receive:
{}
I receive:
201: {
  "squares": [ { "description": "Obsessed with K-dramas and Gong Woo", "name": "Jonathan", "title": "K-drama Fanatic" }, { "description": "Enthusiastic about flying and making woosh sounds", "name": "Icarus \"Icky\" Iguana", "title": "Helicopter Gender" } ]
}

GET /bingo/<id>/squares
You receive:
{}
I receive:
200: {
  "squares": [ { "description": "Obsessed with K-dramas and Gong Woo", "name": "Jonathan", "title": "K-drama Fanatic" }, { "description": "Enthusiastic about flying and making woosh sounds", "name": "Icarus \"Icky\" Iguana", "title": "Helicopter Gender" } ]
}
```

### Quiz
```
POST /room/quiz/create
You receive:
{}
I receive:
201: {
  "id": 123413534253
}

GET /quiz/:room_id/context
You receive:
{}
I receive:
200: {
  "baseContext": {
    "purpose": "first date",
    "relationship": "acquaintances",
    "description": "20-year-old singaporean university computing students who have no social life"
  },
  "quizContext": {
    "numberOfQuestions": 10
  }
}

POST /quiz/:room_id/questions/generate
You receive:
{
  "baseContext": {
    "purpose": "first date",
    "relationship": "acquaintances",
    "description": "20-year-old singaporean university computing students who have no social life"
  },
  "quizContext": {
    "numberOfQuestions": 10
  }
}
I receive:
201: {
  "questions": [
    {
      "id": 123,
      "content": "Who has burned down the computing building?",
      "options": [
        "Jason", // First option is always the correct one
        "Jason",
        "Jason",
        "Jason"
      ]
    },
  ]
}

POST /quiz/:room_id/questions/create
You receive:
{}
I receive:
200: {
  "id": 11357890,
}

PUT /quiz/:room_id/questions/:id
You receive:
{
  "content": "Who is more likely to burn down the computing building?"
}
I receive:
200: {}

DELETE /quiz/:room_id/questions/:id
You receive:
{}
I receive:
200: {}

POST /quiz/:room_id/join
You receive:
{
  "name": "Jason",
  "information": "I am a mega-brained individual"
}
I receive:
200: {}

POST /quiz/:room_id/start
You receive:
{}
I receive:
200: {}
```
