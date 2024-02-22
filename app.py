from itertools import groupby
from operator import attrgetter

from flask import Flask, render_template
import buzzbot
import utils

app = Flask(__name__)


@app.route('/')
def home():
    teams = ["1s", "2s", "3s", "4s", "5s", "6s", "7s"]
    matches = buzzbot.load_fixtures_from_csv("input.csv")
    umpiring_count = {team: 0 for team in teams}

    bot = buzzbot.BuzzBot(matches, teams, umpiring_count)
    bot.assign_covering_teams(print_results=False)
    games = bot.matches
    games.sort(key=lambda x: x.start_time)
    games_by_date = {date: list(games) for date, games in groupby(games, key=lambda x: x.start_time.date())}
    return render_template('assignments.html', games_by_date=games_by_date, tagline_text=utils.get_opening_tagline())


if __name__ == '__main__':
    app.run(debug=True)
