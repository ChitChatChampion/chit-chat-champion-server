def getBaseContext(baseContext):
    purpose = baseContext.get('purpose')
    relationship = baseContext.get('relationship')
    description = baseContext.get('description')
    return purpose, relationship, description

def getCscContext(cscContext):
    number_of_questions = cscContext.get('number_of_questions')
    return number_of_questions

def checkResponseSuccess(response):
    status = response[1]
    return status == 200 or status == 201

def prettify_questions(questions):
    return [{"id": id, "content": content} for id, content in questions.items()]