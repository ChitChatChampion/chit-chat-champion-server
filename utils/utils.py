def getBaseContext(baseContext):
    age = baseContext.get('age')
    familiarity = baseContext.get('familiarity')
    purpose = baseContext.get('purpose')
    group_description = baseContext.get('group_description')
    return age, familiarity, purpose, group_description

def getCscContext(cscContext):
    number_of_cards = cscContext.get('number_of_cards')
    return number_of_cards

def checkResponseSuccess(response):
    return response[1] == 200

def prettify_questions(questions):
    return [{"id": id, "content": content} for id, content in questions.items()]