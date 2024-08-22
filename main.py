import time
import buzzbot
import buzzbot_constants
import gspread_interface
from buzzbot_constants import buzzbotConfiguration


def main():
    total_start_time = time.time()

    # Read
    manager = gspread_interface.GoogleSheetManager(
        credentials_file=buzzbotConfiguration.settings["google_credentials_filename"],
        sheet_name=buzzbotConfiguration.settings["google_sheet_doc_name"],
    )
    matches = manager.read_sheet_as_fixtures("Fixtures List")
    locations = manager.read_locations_sheet("Locations")

    # Compute
    compute_start_time = time.time()
    teams = buzzbotConfiguration.settings["teams"]
    umpiring_count = {team: 0 for team in teams}
    selection_criteria = buzzbot_constants.get_selection_criteria()
    bot = buzzbot.BuzzBot(
        matches,
        teams,
        umpiring_count,
        criteria_=selection_criteria,
        locations_df=locations,
    )
    bot.assign_covering_teams(print_results=False)

    # Sort
    games = bot.matches
    games.sort(key=lambda x: x.start_time)
    compute_end_time = time.time()

    # Write
    manager.write_assignments("Assignments", games)

    total_end_time = time.time()
    total_time = total_end_time - total_start_time
    total_compute_time = compute_end_time - compute_start_time
    print(
        f"Total runtime: {total_time:.2f} seconds\nTotal compute time: {total_compute_time:.2f} seconds"
    )


if __name__ == "__main__":
    main()
