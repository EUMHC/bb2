import csv
import datetime
import utils
import logging

from itertools import groupby
from operator import attrgetter

from DistanceMatrixAPI import DistanceMatrixInterface, LocationManager
from buzzbot_constants import buzzbotConfiguration
from heuristics import SelectionFunction
from models import Fixture


# Configuring logger
logger = logging.getLogger("TheBuzzBot Logger")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("buzzbot.log", mode="a")  # "a" for append
fh.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def load_fixtures_from_csv(csv_path):
    matches_ = []
    errors_exist, error_messages = utils.validate_csv_format(csv_path)
    if errors_exist:
        raise utils.ExceptionWithList(error_messages)

    try:
        with open(csv_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                home = row["uni_team"].strip()
                away = row["opposition"].strip()
                start_time = datetime.datetime.strptime(
                    row["start_time"].strip(), "%Y-%m-%d %H:%M:%S"
                )
                umpires_needed = int(row["umpires_needed"].strip())
                location = row["location"].strip()
                matches_.append(
                    Fixture(home, away, start_time, umpires_needed, location)
                )
        return matches_
    except Exception as e:
        raise Exception(
            f"You have been an idiot somewhere with the input.csv file. Read the following message to "
            f"gauge what the issue is : '{str(e)}'"
        )


class BuzzBot:
    """
    The meat of it all.
    """

    def __init__(
        self,
        matches_: [Fixture],
        teams_: [str],
        umpiring_count_: dict,
        criteria_: SelectionFunction,
        locations_df=None,
    ):
        self.matches: [Fixture] = matches_
        self.teams: [str] = teams_
        self.umpiring_count: dict = umpiring_count_
        self.location_manager: LocationManager = LocationManager(
            df=(locations_df if locations_df is not None else None)
        )
        self.api: DistanceMatrixInterface = DistanceMatrixInterface(
            buzzbotConfiguration.settings["distance_matrix_ai"]
        )
        self.bootstrap_api()
        self.travel_time_table: dict = self.api.get_travel_time_table()
        self.assignments: dict = {}
        self.selection_criteria: SelectionFunction = criteria_

    def extract_location_names(self) -> [str]:
        return [m.location for m in self.matches]

    def extract_location_coordinates(self, location_names_: [str]) -> [(float, float)]:
        """
        Returns a list of coordinates from a list of given location names
        :param location_names_: List of strings representing location names
        :return: List of tuples of floats representing the lat long pairs for each location
        """
        coords = []
        for name in location_names_:
            coord = self.location_manager.get_location(name)
            coords.append(coord)
        return coords

    def bootstrap_api(self) -> None:
        """
        Initialising the Distance Matrix API with the match day locations
        """
        matchday_locations = self.extract_location_names()
        matchday_locations_dict = (
            self.location_manager.return_matchday_location_subdictionary(
                matchday_locations
            )
        )
        self.api.import_from_LocationManager(matchday_locations_dict)

    def group_matches_by_date(self) -> dict:
        """
        Groups the matches by date
        :return: a dictionary where key is the date, and the values are list of Fixture objects
        """
        self.matches.sort(key=lambda x: x.start_time.date())
        grouped_matches = groupby(self.matches, key=lambda x: x.start_time.date())
        return {date: list(matches) for date, matches in grouped_matches}

    def assign_covering_teams(self, print_results: bool) -> None:
        """
        Assigns umpiring teams to matches, processed by individual match days.
        :param print_results: If true, prints the results
        """
        if len(self.matches) == 0:
            return
        matches_by_date = self.group_matches_by_date()

        for match_date, day_matches in matches_by_date.items():
            for match in day_matches:
                self.assign_team_to_match_single_matchday(match)

        if print_results:
            self.print_results()

    def assign_team_to_match_single_matchday(self, match: Fixture) -> None:
        """
        Assigns a covering team to a single match, using only the matches on that match day.
        :param match: Fixture object
        """
        if match.umpires_required == 0:
            match.covering_team = "COVERED"
            return

        selected_team = self.find_umpiring_team(match)
        match.covering_team = selected_team
        if selected_team != "No available umpire":
            self.umpiring_count[selected_team] = (
                self.umpiring_count.get(selected_team, 0) + match.umpires_required
            )

    def print_results(self) -> None:
        """
        Prints the results of the umpiring assignments
        :return: None
        """
        print("\n")
        print(("#" * 20) + " ASSIGNMENTS " + ("#" * 20))
        utils.print_warning(
            "DISCLAIMER: Always doublecheck and cross reference umpiring assignments given by The Buzzbot"
        )
        for match in self.matches:
            print(
                f"{match.home} vs {match.away}, PB: {match.start_time}, END: {match.end_time} @ {match.location} - "
                f"Umpiring"
                f"Team: {match.covering_team} providing {match.umpires_required} umpire(s)\n\tAll eligible teams: {match.eligible_teams}\n"
            )
        utils.print_warning(
            "DISCLAIMER: Always doublecheck and cross reference umpiring assignments given by The Buzzbot"
        )
        print("#" * 53)
        print("\n")
        print(f"TOTAL UMPIRES SUPPLIED: {self.get_total_umpires_supplied()}")

    def find_umpiring_team(self, match: Fixture) -> str:
        """
        Finds the best team to cover a match based on defined criteria
        :param match: Fixture object
        :return: String name of the best team to cover a match
        """
        eligible_teams = self.get_eligible_teams(match)
        eligible_teams.sort()
        match.eligible_teams = eligible_teams
        if not eligible_teams:
            return "No available umpire"

        best_team = self.selection_criteria.evaluate(
            eligible_teams, umpiring_count=self.umpiring_count
        )
        # Greedy heuristic that takes the team with the least assignments first, then the strongest team.
        return best_team

    def get_eligible_teams(self, match: Fixture) -> [str]:
        """
        Computes the list of teams eligible for covering a match
        :param match: Fixture object representing the match
        :return: List of strings representing the names of eligible teams
        """
        # teams_playing_same_day = self.get_teams_playing_same_day(match)
        # eligible_playing_teams = [team for team in teams_playing_same_day if self.is_eligible(team, match)]
        #
        # if eligible_playing_teams:
        #     return eligible_playing_teams
        # else:
        #     return [team for team in self.teams if team not in teams_playing_same_day and self.is_eligible(team, match)]
        return [team for team in self.teams if self.is_eligible(team, match)]

    def get_teams_playing_same_day(self, match: Fixture) -> [str]:
        """
        # TODO: this could probably be independent of argument match (almost certainly)
        Computes the subset of teams playing that don't include the teams playing in the input match
        :param match: Fixture object representing the match
        :return: List of strings representing the names of teams playing
        """
        teams_playing_same_day = {
            m.home for m in self.matches if m != match and m.home in self.teams
        }
        teams_playing_same_day.update(
            {m.away for m in self.matches if m != match and m.away in self.teams}
        )
        return teams_playing_same_day

    def is_eligible(self, team: str, match: Fixture) -> bool:
        """
        Checks eligibility of a team to umpire a given fixture - the important function. Functions based on the three
        following conditions:
        - A team can't umpire a game it's playing in.
        - A team can't umpire a game that overlaps with it's own game.
        - A team can only umpire a game if there is enough travel time between it's own game and the umpiring game.

        :param team: Name as a string representing the team to check if eligible to umpire
        :param match: Fixture object representing the match to check eligibility against.
        :return: True if the team can cover umpiring, False if not
        """

        """
        The team cannot be playing in the match it is supposed to umpire. This is checked by ensuring that the 
        team's name does not match either the home or away team involved in the match. If the team is playing in the 
        match, it is deemed ineligible for umpiring."""
        if team in [match.home, match.away]:
            logger.debug(
                f"Not eligible - team {team} is playing in fixture with {match.home} v {match.away}"
            )
            return False

        """
        The team cannot be playing in another match that overlaps with the given match. The method iterates 
        through other matches to check if the team is playing in any of them. If the team is found to 
        be playing in another match that overlaps in time with the given match, 
        it cannot umpire the given match due to the time conflict."""
        for other_match in self.matches:
            if team in [other_match.home, other_match.away] and match.overlaps_with(
                other_match
            ):
                return False

        """
        The team must have enough travel time between the end of any match they are playing and the start of the 
        match they are to umpire. For each match the team is playing that does not overlap with the given match, 
        the method calculates the travel time from the location of that match to the location of the match to be 
        umpired. If there isn't enough time for the team to travel between venues (the travel time is greater than 
        the time difference between matches), the team is considered ineligible to umpire."""
        for other_match in self.matches:
            if team in [other_match.home, other_match.away]:
                # Extract coordinates for both matches
                origin_coords = self.extract_location_coordinates(
                    [other_match.location]
                )[0]
                destination_coords = self.extract_location_coordinates(
                    [match.location]
                )[0]

                travel_time_minutes = self.get_travel_time(
                    origin_coords, destination_coords
                )

                # Calculate the time difference between the matches in both directions
                buffer_after = (
                    match.start_time - other_match.end_time
                ).total_seconds() / 60 - travel_time_minutes
                buffer_before = (
                    other_match.start_time - match.end_time
                ).total_seconds() / 60 - travel_time_minutes

                if buffer_after < 0 and buffer_before < 0:
                    return False

        return True

    def get_travel_time(self, origin: tuple, destination: tuple) -> int:
        origin_str = ",".join([str(x) for x in origin])
        destination_str = ",".join([str(x) for x in destination])

        if origin_str == destination_str:  # Same location
            return 0  # No travel time

        key_forward = f"{origin_str}_{destination_str}"
        key_reverse = f"{destination_str}_{origin_str}"

        if key_forward in self.travel_time_table:
            travel_time = self.travel_time_table[key_forward]
        elif key_reverse in self.travel_time_table:
            travel_time = self.travel_time_table[key_reverse]
        else:
            raise ValueError(
                f"Travel time not found for the given origin `{origin_str}` and destination {destination_str}."
            )

        return travel_time // 60

    def get_total_umpires_supplied(self):
        return sum(self.umpiring_count.values())


utils.print_ascii_header()
print(f'TheBuzzBot says, "{utils.get_opening_tagline()}"\n')
# utils.get_opening_tagline_with_cowsay()
