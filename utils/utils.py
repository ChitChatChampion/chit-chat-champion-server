def getBaseContext(baseContext):
    purpose = baseContext.get('purpose')
    relationship = baseContext.get('relationship')
    description = baseContext.get('description')
    return purpose, relationship, description

def getCscContext(cscContext):
    number_of_cards = cscContext.get('number_of_cards')
    return number_of_cards

def checkResponseSuccess(response):
    return response[1] == 200

def prettify_questions(questions):
    return [{"id": id, "content": content} for id, content in questions.items()]