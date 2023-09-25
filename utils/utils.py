def getBaseContext(baseContext):
    purpose = baseContext.get('purpose')
    relationship = baseContext.get('relationship')
    description = baseContext.get('description')
    return purpose, relationship, description

def getCscContext(cscContext):
    number_of_questions = cscContext.get('number_of_questions')
    return number_of_questions

def checkResponseSuccess(response):
    return response[1] == 200 or response[1] == 201

def format_questions_for_fe(questions):
    return [{"id": id, "content": content} for id, content in questions.items()]