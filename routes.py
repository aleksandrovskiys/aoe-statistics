from flask import render_template, request, redirect

import aoe_api
from main import app
from player import Player, START_OF_PERIOD


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/search")
def search():
    username = request.args.get('username')
    profile_id = aoe_api.get_profile_id_by_username(username)
    return redirect(f'/user/{profile_id}')


@app.route("/user/<profile_id>")
def user_profile(profile_id):
    player = Player(profile_id)
    period_start = START_OF_PERIOD.strftime('%d-%m-%Y %H:%M:%S')
    return render_template('profile.html', player=player, period_start=period_start)