from flask import Flask
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def start_skill():
    welcome_message = "Welcome to Ask Quizlet! Would you like to study or create a flash card set?"
    session.attributes["test_num"] = 0
    session.attributes["final_set"] = {}
    session.attributes["prev"] = "anything"
    #session.attributes["num_sets"] = 0

    #session.attributes["currentkey"] = null
    return question(welcome_message)

test_questions = ["ant", "bee", "cow", "dog"]
@ask.intent("StudyIntent")
def study():
    #only if have not called any other function
    if (session.attributes["prev"] == "anything" or session.attributes["prev"] == "answer"):
        msg = "Please say back the word: "
        msg += test_questions[session.attributes["test_num"]]
        session.attributes["prev"] = "study"
        return question(msg)
    else:
        msg = "Please continue the function or stop"
        return question(msg)

#prev word = answer
@ask.intent("AnswerIntent")
def answer(ans):
    if (session.attributes["prev"] == "study"):
        if ans == test_questions[session.attributes["test_num"]]:
            session.attributes['test_num'] += 1
            if session.attributes["test_num"] == len(test_questions):
                return statement("Congrats, you said all the words.")
            return study()
        return question("You fucked up.")
    else:
        msg = "Please continue the function or stop"
        return question(msg)

#Trying to create and word with a definition
#prev word = create
@ask.intent("CreateIntent")
def create():
    if(session.attributes["prev"] == "anything"):
        session.attributes["prev"] = "create"
        msg = "Please tell the word: "
        return question(msg)
    else:
        msg = "Please continue the proper function or stop"
        return question(msg)

#For adding the word
#Have to say actualWord before word
#prev word = newword
@ask.intent("NewWordIntent")
def newWord(realword):

    if(session.attributes["prev"] == "create"):
        if (newWord not in session.attributes["final_set"].keys()):
            #session.attributes["final_set"][actualWord] = null
            #setting prev to newWord, so can only access add_definition after this
            session.attributes["prev"] = "newword"
            session.attributes["currentkey"] = realword
            msg = "Please say the definition"
            return question(msg)
    else:
        msg = "Please continue the function or stop"
        return question(msg)
    #return create()


#For adding the definition
#Have to say the definition
#prev word = anything
@ask.intent("NewDefinitionIntent")
def add_definition(definition):
    if(session.attributes["prev"] == "newword"):
        session.attributes["final_set"][session.attributes["currentkey"]] = definition
        #setting the prev so one can access anything
        session.attributes["prev"] = "anything"
        msg = "Word and definition added " + session.attributes["currentkey"] + " means " + definition + " Say create to add a new word"
        return question(msg)
    else:
        msg = "Please continue the function or stop"
        return question(msg)

@ask.intent("DeleteEntryIntent")
def delete_word(wordToDelete):
    if(not session.attributes["final_set"]):
        msg = "Your set is empty!"
        return statement(msg)
    else:
        session.attributes["final_set"].pop(wordToDelete)
        msg = "Deleted " + wordToDelete + " and its definition"
        return statement(msg)


@ask.intent("AMAZON.HelpIntent")
def help():
    opening_help = "Chose create if you want to make a new set, or chose study if you want to study a pre existing set"
    create_help_word = "Please say the new word you want to set"
    create_help_def = "Please say the definition of the word you just added to the set"

    help_dictionary = {"anything": opening_help, "create": create_help_word, "newword":create_help_def}
    return statement(help_dictionary.get(session.attributes["prev"], "No help available at the time!"))

@ask.intent("AMAZON.StopIntent")
def exit():
    msg = "Quitting Ask Quizlet."
    return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)