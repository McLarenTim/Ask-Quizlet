from flask import Flask
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")

state_map = {
    "start": ["create", "study", "exit"],
    "study": ["await_ans", "exit"],
    "await_ans": ["study", "exit"]
}

test_questions = ["ant", "bob", "cow", "dog"]

@ask.launch
def start_skill():
    welcome_message = "Welcome to Ask Quizlet! Would you like to study or create a flash card set?"
    session.attributes["test_num"] = 0
    session.attributes["state"] = "start"
    return question(welcome_message)

@ask.intent("CreateIntent")
def create():
    print("create")
    if session.attributes["state"] not in ["start"]:
        return question("Invalid Input.")
    msg = "Not implemented."
    return question(msg)

@ask.intent("StudyIntent")
def study():
    print("study")
    if session.attributes["state"] not in ["start", "study"]:
        return question("Invalid Input.")
    msg = "Please say back the word: "
    msg += test_questions[session.attributes["test_num"]]
    session.attributes["state"] = "await_ans"
    return question(msg)

@ask.intent("AnswerIntent")
def answer(ans):
    if session.attributes["state"] not in ["await_ans"]:
        return question("Invalid Input.")
    if ans == test_questions[session.attributes["test_num"]]:
        session.attributes['test_num'] += 1
        if session.attributes["test_num"] == len(test_questions):
            return statement("Congrats, you said all the words.")
        session.attributes["state"] = "study"
        return study()
    return question("You fucked up.")

@ask.intent("AMAZON.StopIntent")
def exit():
    msg = "Quitting Ask Quizlet."
    return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)