from flask import Flask
from bot.action import Action
from mnet_plus_crawler import fetch_data

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.post("/__space/v0/actions")
def actions(action: Action):
    if action.event.id == "fetch":
        fetch_data()
