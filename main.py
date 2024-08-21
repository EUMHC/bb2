import time
import buzzbot
import buzzbot_constants
import gspread_interface
from buzzbot_constants import buzzbotConfiguration

start_time = time.time()

# TODO: have these as config variables rather than hardcoded.
manager = gspread_interface.GoogleSheetManager(
    "buzzbot2-2d1f4bb04d1a.json", "Copy of Fixtures Umpiring combo 2022/23"
)
matches = manager.read_sheet_as_fixtures("Fixtures List")

teams = buzzbotConfiguration.settings["teams"]
umpiring_count = {team: 0 for team in teams}
selection_criteria = buzzbot_constants.get_selection_criteria()
bot = buzzbot.BuzzBot(matches, teams, umpiring_count,
                      criteria_=selection_criteria)
bot.assign_covering_teams(print_results=False)

games = bot.matches
games.sort(key=lambda x: x.start_time)

manager.write_assignments("Assignments", games)

end_time = time.time()
total_time = end_time - start_time
print(f"Total runtime: {total_time:.2f} seconds")
