from flask import Flask
from flask_ask import Ask, statement, question, session
from random import choice

app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def start_skill():
    welcome_message = "Welcome to Flash Learner! Would you like to study, be tested on, or create a flash card set?"
    session.attributes["sets"] = {
        "english": {
            "ascertain": "discover through examination or experimentation; determine",
            "avenge": "take revenge on or get satisfaction for; take vengeance on behalf of",
            "chicanery": "deception by trickery; trick",
            "remiss": "lax in attending to duty; exhibiting carelessness",
            "ruminate": "meditate at length; ponder; muse; chew cud"
        },
        "economics": {
            "consumer": "someone who buys and uses goods and services",
            "expansion": "a period of time during which the amount of business (GDP) increases"
        },
        "biology": {
            "diploid": "an organism or cell having two sets of chromosomes or twice the haploid number",
            "nucleus": "a part of the cell containing DNA and RNA and responsible for growth and reproduction",
            "pedigree": "a diagram that shows the occurrence of a genetic trait in several generations of a family",
            "heredity": "the biological process whereby genetic factors are transmitted from one generation to the next"
        },
        "chemistry": {
            "suspension": "Heterogeneous mixture containing a liquid where visible particles settle.",
            "distillation": "A process for separating substances by evaporating a liquid and recondensing its vapor.",
            "diffusion": "Spreading of particles throughout a given volume until they are distributed.",
            "viscosity": "The resistance to flow by a fluid."
        },
        "my set": {}
    }
    session.attributes["prev"] = "anything"
    session.attributes["currentword"] = ""
    session.attributes["currentset"] = {}
    session.attributes["currentkey"] = ""
    session.attributes["recentMessage"] = welcome_message
    session.attributes["testmode"] = False
    session.attributes["testscore"] = 0
    session.attributes["testtotal"] = 0
    return question(welcome_message)

@ask.intent("StudyIntent")
def study(setname):
    return begin(setname, False)

@ask.intent("TestIntent")
def test(setname):
    return begin(setname, True)

def begin(setname, testmode):
    if (session.attributes["prev"] == "anything"):
        if not setname:
            msg = "Please say study followed by a set name. Current available sets are: " + ", ".join(list(session.attributes["sets"].keys()))
            session.attributes["recentMessage"] = msg
            return question(msg)
        if setname not in session.attributes["sets"].keys():
            msg = "I cannot find that study set."
            session.attributes["recentMessage"] = msg
            return question(msg)
        if len(session.attributes["sets"][setname]) == 0:
            msg = "That study set is empty."
            session.attributes["recentMessage"] = msg
            return question(msg)
        session.attributes["currentset"] = session.attributes["sets"][setname].copy()
        if testmode:
            session.attributes["testscore"] = 0
            session.attributes["testtotal"] = len(session.attributes["sets"][setname])
            session.attributes["prev"] = "test"
        else:
            session.attributes["prev"] = "study"
        return decider()
    else:
        msg = "Please continue the function or stop."
        session.attributes["recentMessage"] = msg
        return question(msg)

def decider(correctness=None):
    msg = ""
    if correctness != None:
        if session.attributes["prev"] == "test":
            if correctness:
                msg += "Correct! "
                session.attributes["testscore"] += 1
            else:
                msg += "Incorrect. The answer was: " + session.attributes["currentword"] + ". "
            session.attributes["currentset"].pop(session.attributes["currentword"])
            if len(session.attributes["currentset"]) == 0:
                session.attributes["prev"] = "anything"
                return question("Congratulations! You finished the test! Your score was " + str(session.attributes["testscore"]) + " out of " + str(session.attributes["testtotal"]) + ". ")
        else:
            if correctness:
                msg += "Correct! "
                session.attributes["currentset"].pop(session.attributes["currentword"])
                if len(session.attributes["currentset"]) == 0:
                    session.attributes["prev"] = "anything"
                    msg3 = "Congratulations! You finished the study set!"
                    session.attributes["recentMessage"] = msg3
                    return question(msg3)
            else:
                msg += "Incorrect. The answer was: " + session.attributes["currentword"] + ". "
    session.attributes["currentword"] = choice(list(session.attributes["currentset"].keys()))
    msg += "What is the word for: " + session.attributes["currentset"][session.attributes["currentword"]]
    session.attributes["recentMessage"] = msg
    return question(msg)

#prev word = answer
@ask.intent("AnswerIntent")
def answer(ans):
    if (session.attributes["prev"] == "test" or session.attributes["prev"] == "study"):
        if ans == session.attributes["currentword"]:
            return decider(correctness=True)
        else:
            return decider(correctness=False)
    else:
        msg = "Please continue the function or stop."
        session.attributes["recentMessage"] = msg
        return question(msg)

#Trying to create and word with a definition
#prev word = create
@ask.intent("CreateIntent")
def create():
    if(session.attributes["prev"] == "anything"):
        session.attributes["prev"] = "create"
        msg = "Please say the word."
        session.attributes["recentMessage"] = msg
        return question(msg)
    else:
        msg = "Please continue the proper function or stop"
        session.attributes["recentMessage"] = msg
        return question(msg)

#For adding the word
#Have to say actualWord before word
#prev word = newword
@ask.intent("NewWordIntent")
def newWord(realword):
    if(session.attributes["prev"] == "create"):
        if (newWord not in session.attributes["sets"]["my set"].keys()):
            #setting prev to newWord, so can only access add_definition after this
            session.attributes["prev"] = "newword"
            session.attributes["currentkey"] = realword
            msg = "Please say the definition of: " + realword
            session.attributes["recentMessage"] = msg
            return question(msg)
    else:
        msg = "Please continue the function or stop"
        session.attributes["recentMessage"] = msg
        return question(msg)
    #return create()


#For adding the definition
#Have to say the definition
#prev word = anything
@ask.intent("NewDefinitionIntent")
def add_definition(definition):
    if(session.attributes["prev"] == "newword"):
        session.attributes["sets"]["my set"][session.attributes["currentkey"]] = definition
        #setting the prev so one can access anything
        session.attributes["prev"] = "anything"
        msg = "Word and definition added: " + session.attributes["currentkey"] + " means " + definition + ". Say create to add a new word."
        session.attributes["recentMessage"] = msg
        return question(msg)
    else:
        msg = "Please continue the function or stop"
        session.attributes["recentMessage"] = msg
        return question(msg)

@ask.intent("DeleteEntryIntent")
def delete_word(wordToDelete):
    if(not session.attributes["sets"]["my set"]):
        msg = "Your set is empty!"
        session.attributes["recentMessage"] = msg
        return question(msg)
    else:
        if (wordToDelete in session.attributes["sets"]["my set"].keys()):
            session.attributes["sets"]["my set"].pop(wordToDelete)
            msg = "Deleted " + wordToDelete + " and its definition"
            session.attributes["recentMessage"] = msg
            return question(msg)
        else:
            msg = "No such word in the set!"
            session.attributes["recentMessage"] = msg
            return question(msg)

@ask.intent("AMAZON.RepeatIntent")
def replay():
    return question(session.attributes["recentMessage"])


@ask.intent("AMAZON.HelpIntent")
def help():

    opening_help = "Choose create if you want to make a new set, or choose study if you want to study a pre existing set."
    create_help_word = "Please say the new word you want to set. For example. say: word. hackathon"
    create_help_def = "Please say the definition of the word you just added to the set. For example. say:" \
                      "definition. a place for coders to make cool stuff"
    answer_help = "Please say the correct word describing the definition."
    help_dictionary = {"anything": opening_help, "create": create_help_word, "newword":create_help_def, "test":answer_help, "study":answer_help}
    msg = help_dictionary.get(session.attributes["prev"], "No help available at the time!")
    session.attributes["recentMessage"] = msg
    return question(msg)

@ask.intent("AMAZON.StopIntent")
def exit():
    if (session.attributes["prev"] == "test" or session.attributes["prev"] == "study"):
        session.attributes["prev"] = "anything"
        return question("Ending study session.")
    return statement("Quitting Flash Learner.")

if __name__ == '__main__':
    app.run(debug=True)
