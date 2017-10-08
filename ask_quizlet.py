from flask import Flask
from flask_ask import Ask, statement, question, session
from random import choice

app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def start_skill():
    welcome_message = "Welcome to Ask Quizlet! Would you like to study or create a flash card set?"
    session.attributes["final_set"] = {}
    session.attributes["test_set"] = {
        "ascertain": "discover through examination or experimentation; determine",
        "avenge": "take revenge on or get satisfaction for; take vengeance on behalf of",
        "chicanery": "deception by trickery; trick",
        "remiss": "lax in attending to duty; exhibiting carelessness",
        "ruminate": "meditate at length; ponder; muse; chew cud"
    }
    session.attributes["prev"] = "anything"
    session.attributes["current_correctness"] = 0
    session.attributes["current_word"] = 0
    session.attributes["currentkey"] = ""
    return question(welcome_message)

@ask.intent("CreateIntent")
def create():
    if session.attributes["state"] not in ["start"]:
        return question("Invalid Input.")
    msg = "Not implemented."
    return question(msg)

@ask.intent("StudyIntent")
def study():
    if (session.attributes["prev"] == "anything"):
        # session.attributes["current_word"] = choice(list(session.attributes["final_set"].keys()))
        ####################
        if len(session.attributes["final_set"]) == 0:
            return question("Your study set is empty.")
        ####################
        msg = ""
        if session.attributes["current_correctness"] != 0:
            if session.attributes["current_correctness"] == 2:
                msg += "Correct! "
            else:
                msg += "Incorrect. The word was: " + session.attributes["current_word"] + ". "
        ####################
        session.attributes["current_word"] = choice(list(session.attributes["final_set"].keys()))
        msg += "What is the word for: " + session.attributes["final_set"][session.attributes["current_word"]]
        ####################
        session.attributes["prev"] = "answer"
        return question(msg)
    else:
        msg = "Please continue the function or stop."
        return question(msg)

#prev word = answer
@ask.intent("AnswerIntent")
def answer(ans):
    if (session.attributes["prev"] == "answer"):
        if ans == session.attributes["current_word"]:
            session.attributes["current_correctness"] = 2
        else:
            session.attributes["current_correctness"] = 1
        session.attributes["prev"] = "anything"
        return study()
    else:
        msg = "Please continue the function or stop."
        return question(msg)

#Trying to create and word with a definition
#prev word = create
@ask.intent("CreateIntent")
def create():
    if(session.attributes["prev"] == "anything"):
        session.attributes["prev"] = "create"
        msg = "Please say the word."
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
            msg = "Please say the definition of: " + realword
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
        msg = "Word and definition added: " + session.attributes["currentkey"] + " means " + definition + ". Say create to add a new word."
        return question(msg)
    else:
        msg = "Please continue the function or stop"
        return question(msg)

@ask.intent("DeleteEntryIntent")
def delete_word(wordToDelete):
    if(not session.attributes["final_set"]):
        msg = "Your set is empty!"
        return question(msg)
    else:
        if (wordToDelete in session.attributes["final_set"].keys()):
            session.attributes["final_set"].pop(wordToDelete)
            msg = "Deleted " + wordToDelete + " and its definition"
            return question(msg)
        else:
            msg = "No such word in the set!"
            return question(msg)


@ask.intent("AMAZON.HelpIntent")
def help():
    opening_help = "Choose create if you want to make a new set, or choose study if you want to study a pre existing set"
    create_help_word = "Please say the new word you want to set"
    create_help_def = "Please say the definition of the word you just added to the set"

    help_dictionary = {"anything": opening_help, "create": create_help_word, "newword":create_help_def}
    return question(help_dictionary.get(session.attributes["prev"], "No help available at the time!"))

@ask.intent("AMAZON.StopIntent")
def exit():
    # if (session.attributes["prev"] == "newword"):
    #     return start_skill()
    msg = "Quitting Ask Quizlet."
    return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)