# backend

## Setup
1. Run `python3 -m venv env` to create a virtual environment called "env"
2. Run `source env/bin/activate` to change your environment
3. `pip install -r requirements.txt` to install dependencies
4. Update `.env` file with required variables

## Start Server
1. Run `python3 main.py`

## TRADE OFFER

### User
```
Checks if you're the owner of the room
GET /user/room/:id
You receive:
{}
I receive:
200: {
  is_owner: True
}
```

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
    "number_of_questions": 10
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
    "number_of_questions": 10
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
    "number_of_questions": 10
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
    "number_of_questions": 10
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
{}
I receive:
200: {
  "fields": [
    {"id": 1234165341, "content": "Gender"},
    {"id": 1237890452, "content": "Favourite brand of chocolate"}
  ]
}

POST /bingo/fields/create
Description:
Should function the same as csc/questions/create
You receive:
{}
I receive:
{
  "id": 1237849
}

PUT /bingo/fields/:id
You receive:
{
  "content": "Favourite colour"
}
I receive:
200: {}

DELETE /bingo/fields/:id
You receive:
{}
I receive:
200: {}

POST /room/bingo/create
Description:
Creates a game room, but don't have the questions yet.
You receive:
{
  "fields": [
    {"id": 1234165341, "content": "Gender"},
    {"id": 1237890452, "content": "Favourite brand of chocolate"}
  ]
}
I receive:
200: {
  "id": 12358934
}

GET /bingo/:id/fields
Description:
Gets the fields for the players to fill in.
You receive:
{}
I receive:
200: {
  "fields": [
    {"id": 1234165341, "content": "Gender"},
    {"id": 1237890452, "content": "Favourite brand of chocolate"}
  ]
}

POST /bingo/:id/join
Description:
Players submit their form which should contain their personal information. Everything in "data" is meant to be pushed wholesale into ChatGPT. Other information is always a field.
Guarantees:
Length of each field doesn't exceed X characters.
You receive:
{
  "name": "Clement Tee",
  "Gender": "Apache Attack Helicopter",
  "Favourite Colour": "Oil",
  "other_information": "I like to eat cheese"
}
I receive:
200: {}
409: {}

GET /bingo/:id/players
Description:
Get a list of people who have submitted a form. Should only return if you are the owner.
You receive:
{}
I receive:
200: {
  "players": [
    "Amirah Tan",
    "Nicholas Tan Bin",
    "Nicole Hai Wei Ting"
  ]
}

POST /bingo/:id/generate
You receive:
{}
I receive:
201: {
  "squares": [
    { "description": "Obsessed with K-dramas and Gong Woo", "name": "Jonathan","title": "K-drama Fanatic" },
    { "description": "Enthusiastic about flying and making woosh sounds", "name": "Icarus \"Icky\" Iguana", "title": "Helicopter Gender" }
  ]
}

GET /bingo/:id
Description:
A bunch of boolean checks. Refer to slide 4 of https://jamboard.google.com/d/12MSzDJFqMhkudXLiaPwagLfFOeWUaTKtW5S2eAtJKyo/viewer?pli=1&mtt=oy63w2r8f9f&f=3
You receive:
{}
I receive:
200: {
  "isOwner": true,
  "hasStarted": false
}

GET /bingo/:id/squares
You receive:
{}
I receive:
200: {
  "squares": [
    { "description": "Obsessed with K-dramas and Gong Woo", "name": "Jonathan", "title": "K-drama Fanatic" },
    { "description": "Enthusiastic about flying and making woosh sounds", "name": "Icarus \"Icky\" Iguana", "title": "Helicopter Gender" }
  ]
}

POST /bingo/:id/submit
Description:
The player submits what they currently have.
You receive:
{
  "name": "Linus Richards",
  "score": 2,
  "total_score": 10,
  "timestamp": 1238491346790826854
}
I receive:
200: {}

GET /bingo/:id/leaderboard
Description:
Host presses a button that shows top 3 people, with time as tie-breaker.
You receive:
{}
I receive:
200: {
  "players": [
    {"name": "George Richards", "score": 4},
    {"name": "Ang Mei Hua", "score": 4},
    {"name": "Wu Si Ling", "score": 3}
  ]
}

POST /bingo/:id/start
Description:
Host presses a button to start the game.
You receive:
{}
I receive:
200: {}

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
    "number_of_questions": 10
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
    "number_of_questions": 10
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
