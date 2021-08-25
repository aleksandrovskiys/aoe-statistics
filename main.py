from flask import Flask

from info import GameInfo

app = Flask(__name__)
game_info = GameInfo()
