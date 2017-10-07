from flask import Flask
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")

@ask.launch
def start_skill():
    welcome_message = "Welcome to Ask Quizlet! Would you like to study or create a flash card set?"
    return question(welcome_message)

@ask.intent("StudyIntent")
def share_headlines():
    msg = "Not implemented."
    return statement(msg)

@ask.intent("CreateIntent")
def share_headlines():
    msg = "Not implemented."
    return statement(msg)

if __name__ == '__main__':
    app.run(debug=True)