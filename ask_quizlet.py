from flask import Flask
from flask_ask import Ask, statement, question, session
from random import choice

app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def start_skill():
    welcome_message = "Welcome to Ask Quizlet! Would you like to study or create a flash card set?"
    session.attributes["sets"] = {
        "SAT Vocabulary": {
            "ascertain": "discover through examination or experimentation; determine",
            "avenge": "take revenge on or get satisfaction for; take vengeance on behalf of",
            "chicanery": "deception by trickery; trick",
            "remiss": "lax in attending to duty; exhibiting carelessness",
            "ruminate": "meditate at length; ponder; muse; chew cud"
        },
        "economics": {
            "deflation": "a decrease in the average price of all goods and services"
            "consumer": "someone who buys and uses goods and services"
            "embargo": "a government policy that cuts off trade with certain countries"
            "expansion": "a period of time during which the amount of business (GDP) increases"
        },

        "biology": {
            "diploid": "an organism or cell having two sets of chromosomes or twice the haploid number"
            "nucleus": "a part of the cell containing DNA and RNA and responsible for growth and reproduction"
            "pedigree": "a diagram that shows the occurrence of a genetic trait in several generations of a family"
            "heredity": "the biological process whereby genetic factors are transmitted from one generation to the next"
        },

        "chemistry": {
            "suspension": "Heterogeneous mixture containing a liquid where visible particles settle."
            "distillation": "A process for separating substances by evaporating a liquid and recondensing its vapor."
            "diffusion": "Spreading of particles throughout a given volume until they are distributed."
            "viscosity": "The resistance to flow by a fluid."
        }
    }
    session.attributes["prev"] = "anything"
    session.attributes["currentword"] = ""
    session.attributes["currentset"] = {}
    session.attributes["currentkey"] = ""
    return question(welcome_message)

@ask.intent("StudyIntent")
def study(setname):
    if (session.attributes["prev"] == "anything"):
        if not setname:
            return question("Please say study followed by a set name. Current available sets are: " + ", ".join(list(session.attributes["sets"].keys())))
        if setname not in session.attributes["sets"].keys():
            return question("I cannot find that study set.")
        if len(session.attributes["sets"][setname]) == 0:
            return question("That study set is empty.")
        session.attributes["currentset"] = session.attributes["sets"][setname].copy()
        return askword()
    else:
        msg = "Please continue the function or stop."
        return question(msg)

def askword(correctness=None):
    msg = ""
    if correctness != None:
        if correctness:
            msg += "Correct! "
            session.attributes["currentset"].pop(session.attributes["currentword"])
            if len(session.attributes["currentset"]) == 0:
                session.attributes["prev"] = "anything"
                return question("Congratulations! You finished the study set!")
        else:
            msg += "Incorrect. The word was: " + session.attributes["currentword"] + ". "
    session.attributes["currentword"] = choice(list(session.attributes["currentset"].keys()))
    msg += "What is the word for: " + session.attributes["currentset"][session.attributes["currentword"]]
    session.attributes["prev"] = "answer"
    return question(msg)

#prev word = answer
@ask.intent("AnswerIntent")
def answer(ans):
    if (session.attributes["prev"] == "answer"):
        if ans == session.attributes["currentword"]:
            return askword(True)
        else:
            return askword(False)
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
        if (newWord not in session.attributes["sets"]["my set"].keys()):
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
        session.attributes["sets"]["my set"][session.attributes["currentkey"]] = definition
        #setting the prev so one can access anything
        session.attributes["prev"] = "anything"
        msg = "Word and definition added: " + session.attributes["currentkey"] + " means " + definition + ". Say create to add a new word."
        return question(msg)
    else:
        msg = "Please continue the function or stop"
        return question(msg)

@ask.intent("DeleteEntryIntent")
def delete_word(wordToDelete):
    if(not session.attributes["sets"]["my set"]):
        msg = "Your set is empty!"
        return question(msg)
    else:
        if (wordToDelete in session.attributes["sets"]["my set"].keys()):
            session.attributes["sets"]["my set"].pop(wordToDelete)
            msg = "Deleted " + wordToDelete + " and its definition"
            return question(msg)
        else:
            msg = "No such word in the set!"
            return question(msg)


@ask.intent("AMAZON.HelpIntent")
def help():

    opening_help = "Choose create if you want to make a new set, or choose study if you want to study a pre existing set."
    create_help_word = "Please say the new word you want to set. For example. say: word. hackathon"
    create_help_def = "Please say the definition of the word you just added to the set. For example. say:" \
                      "definition. a place for coders to make cool stuff"
    answer_help = "Please say the correct word describing the statement."
    help_dictionary = {"anything": opening_help, "create": create_help_word, "newword":create_help_def, "answer":answer_help}
    return question(help_dictionary.get(session.attributes["prev"], "No help available at the time!"))

@ask.intent("AMAZON.StopIntent")
def exit():
    if (session.attributes["prev"] == "answer"):
        session.attributes["prev"] = "anything"
        return question("Ending study session.")
    return statement("Quitting Ask Quizlet.")

if __name__ == '__main__':
    app.run(debug=True)
