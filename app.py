import os
from itertools import groupby

from flask import Flask, render_template, url_for, request, redirect
from werkzeug.utils import secure_filename

import DistanceMatrixAPI
from buzzbot_constants import buzzbotConfiguration
import webbrowser
import threading
import buzzbot
import buzzbot_constants
import utils

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'csv'}

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/', methods=['GET', 'POST'])
def upload_and_process_file():
    games_by_date = {}
    taglines = buzzbotConfiguration.settings['taglines']
    lm = DistanceMatrixAPI.LocationManager()

    if request.method == 'POST':
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files['file']

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                matches = buzzbot.load_fixtures_from_csv(filepath)


        elif 'uni_team[]' in request.form and 'opposition[]' in request.form and 'location[]' in request.form and 'time[]' in request.form:
            matches = buzzbot.load_fixtures_from_html_form(request.form)


        teams = buzzbotConfiguration.settings['teams']
        umpiring_count = {team: 0 for team in teams}
        selection_criteria = buzzbot_constants.get_selection_criteria()
        bot = buzzbot.BuzzBot(matches, teams, umpiring_count, criteria_=selection_criteria)
        bot.assign_covering_teams(print_results=False)

        games = bot.matches
        games.sort(key=lambda x: x.start_time)
        games_by_date = {date: list(games) for date, games in groupby(games, key=lambda x: x.start_time.date())}
        taglines = utils.taglines

    return render_template('assignments.html', games_by_date=games_by_date, taglines=taglines, config=buzzbotConfiguration, locs=lm.get_all_locations())


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        data = request.json
        # API Key
        buzzbotConfiguration.settings['distance_matrix_ai']['api_key'] = data['dm_ai_api_key']

        # Taglines
        taglines_input = data['taglines_input']
        taglines_array = taglines_input.splitlines()
        buzzbotConfiguration.settings['taglines'] = taglines_array

        # Teams
        teams_input = data['teams_input']
        teams_array = teams_input.splitlines()
        buzzbotConfiguration.settings['teams'] = teams_array

        buzzbotConfiguration.save()
        return redirect(url_for('settings'))

    return render_template('settings.html', config=buzzbotConfiguration)

@app.route('/locations')
def locations():
    lm = DistanceMatrixAPI.LocationManager()
    return render_template('locations.html', config=buzzbotConfiguration, locs=lm.get_all_locations())

@app.route('/about')
def about():
    return render_template('about.html', config=buzzbotConfiguration)


@app.errorhandler(Exception)
def handle_exception(e):
    error_messages = []
    if isinstance(e, utils.ExceptionWithList):
        error_messages = e.messages
    else:
        error_messages.append(str(e))
    return render_template('error.html', error_messages=error_messages, config=buzzbotConfiguration), 500


def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')


if __name__ == '__main__':
    threading.Timer(1, open_browser).start()
    app.run(debug=False)
