import datetime


class Fixture:
    def __init__(
        self,
        home_: str,
        away_: str,
        start_time_: datetime.datetime,
        umpires_required_: int,
        location_: str,
    ):
        assert 0 <= umpires_required_ <= 2
        self.home: str = home_
        self.away: str = away_
        self.start_time: datetime.datetime = start_time_
        self.end_time: datetime.datetime = self.start_time + datetime.timedelta(
            hours=1.5
        )  # Length of a hockey
        # match is 1.5 hours
        self.location: str = location_
        self.covering_team: str = ""
        self.umpires_required: int = umpires_required_
        self.eligible_teams: [str] = []

    def overlaps_with(self, other_fixture):
        # Return True if the two fixtures overlap
        return (
            self.start_time < other_fixture.end_time
            and self.end_time > other_fixture.start_time
        )
