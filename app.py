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
    matches = buzzbot.load_fixtures_from_csv("input.csv")
    umpiring_count = {team: 0 for team in teams}

    bot = buzzbot.BuzzBot(matches, teams, umpiring_count)
    bot.assign_covering_teams(print_results=False)

    games = bot.matches
    games.sort(key=lambda x: x.start_time)
    games_by_date = {date: list(games) for date, games in groupby(games, key=lambda x: x.start_time.date())}
    return render_template('assignments.html', games_by_date=games_by_date, taglines=utils.taglines)


@app.errorhandler(Exception)
def handle_exception(e):
    # You can differentiate between types of exceptions to customize the response
    if isinstance(e, ValueError):
        error_message = "A ValueError occurred."
    else:
        # For other types of exceptions or errors, you can use a generic message
        # or log the exception and return its text or type
        error_message = str(e)  # or "An unexpected error has occurred."

    # You can also decide to return different templates based on the error
    return render_template('error.html', error_message=error_message), 500


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == '__main__':
    # threading.Timer(1, open_browser).start()
    app.run(debug=True)
