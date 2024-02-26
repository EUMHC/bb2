import random
import time
from itertools import groupby
from operator import attrgetter

from flask import Flask, render_template
import webbrowser
import threading
import buzzbot
import buzzbot_constants
import utils

app = Flask(__name__)


@app.route('/')
def home():
    teams = buzzbot_constants.get_uni_teams()

    filename = "display_test_file.csv"
    # filename = "input.csv"
    utils.generate_csv(filename, 5)

    matches = buzzbot.load_fixtures_from_csv(filename)
    umpiring_count = {team: 0 for team in teams}

    bot = buzzbot.BuzzBot(matches, teams, umpiring_count)
    bot.assign_covering_teams(print_results=False)

    games = bot.matches
    games.sort(key=lambda x: x.start_time)
    games_by_date = {date: list(games) for date, games in groupby(games, key=lambda x: x.start_time.date())}
    return render_template('assignments.html', games_by_date=games_by_date, taglines=utils.taglines)


@app.errorhandler(Exception)
def handle_exception(e):
    error_messages = []
    if isinstance(e, utils.ExceptionWithList):
        error_messages = e.messages
    else:
        error_messages.append(str(e))
    return render_template('error.html', error_messages=error_messages), 500


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(debug=False)
