import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from models import Fixture
from datetime import datetime
import logging
from tqdm import tqdm

# NOTE: the file/class needs a lot of logging because I want to know what is happening.
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class GoogleSheetManager:
    def __init__(self, credentials_file, sheet_name):
        """
        Initialize the GoogleSheetManager with the path to the credentials JSON file
        and the name of the Google Sheet.
        """
        logging.info("Initializing GoogleSheetManager...")
        self.credentials_file = credentials_file
        self.sheet_name = sheet_name
        logging.info("Attempting to authenticate...")
        self.client = self._authenticate()
        logging.info("Opening Google Sheet: %s", self.sheet_name)
        self.sheet = self.client.open(sheet_name)
        logging.info("Google Sheet opened successfully.")

    def _authenticate(self):
        """
        Authenticates and returns a gspread client using the service account credentials.
        """
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        logging.info("Loading credentials from file: %s", self.credentials_file)
        credentials = None
        with tqdm(
            total=100,
            desc="Authenticating",
            bar_format="{desc}: {percentage:.0f}% |{bar}| ",
            colour="green",
        ) as pbar:
            credentials = Credentials.from_service_account_file(
                self.credentials_file, scopes=scopes
            )
            pbar.update(50)
            client = gspread.authorize(credentials)
            pbar.update(50)
        logging.info("Authentication successful.")
        return client

    def get_worksheet(self, worksheet_name):
        """
        Returns a worksheet
        """
        logging.info("Retrieving worksheet: %s", worksheet_name)
        with tqdm(
            total=100,
            desc="Retrieving Worksheet",
            bar_format="{desc}: {percentage:.0f}% |{bar}| ",
            colour="blue",
        ) as pbar:
            worksheet = self.sheet.worksheet(worksheet_name)
            pbar.update(100)
        logging.info("Worksheet %s retrieved successfully.", worksheet_name)
        return worksheet

    def write_assignments(self, worksheet_name, fixtures):
        """
        Writes fixture assignments to the specified worksheet in the required structure using a pandas DataFrame. This is a really complex function that is hardcoded to manipulate a Pandas DataFrame precisely so that it can be written to the target Google Sheet.

        Parameters:
            worksheet_name (str): The name of the worksheet to write data to.
            fixtures (List[Fixture]): A list of Fixture objects with covering_team assignments to be written to the sheet.
        """
        logging.info("Preparing to write assignments to worksheet: %s", worksheet_name)
        worksheet = self.get_worksheet(worksheet_name)

        teams = sorted({fixture.home for fixture in fixtures})
        logging.info("Identified teams: %s", teams)

        df = pd.DataFrame(columns=["Day", "Date"] + teams)

        current_date = None
        row_data = {}

        for fixture in tqdm(fixtures, desc="Preparing Assignments", unit="fixture"):
            fixture_date = fixture.start_time.strftime("%d/%m/%Y")
            fixture_day = fixture.start_time.strftime("%A")

            if fixture.start_time.date() != current_date:
                # If there's a current row being processed, append it to the DataFrame
                if row_data:
                    # Append the row with the fixture info
                    df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
                    # Append the row with the covering team info directly below the fixture info
                    covering_row = {key: "" for key in df.columns}
                    covering_row["Date"] = "Buzzbot cover recommendation"
                    for team in teams:
                        if team in row_data:
                            covering_row[team] = row_data[team + "_cover"]
                    df = pd.concat(
                        [df, pd.DataFrame([covering_row])], ignore_index=True
                    )
                    # Append the row with the eligible teams info directly below the covering team info
                    eligible_row = {key: "" for key in df.columns}
                    eligible_row["Date"] = "All eligible covering teams"
                    for team in teams:
                        if team in row_data:
                            eligible_row[team] = ", ".join(
                                row_data.get(team + "_eligible", [])
                            )
                    df = pd.concat(
                        [df, pd.DataFrame([eligible_row])], ignore_index=True
                    )
                    # Add two blank rows after the eligible teams row
                    df = pd.concat(
                        [df, pd.DataFrame([{}]), pd.DataFrame([{}])], ignore_index=True
                    )

                # Start a new row for a new date
                current_date = fixture.start_time.date()
                row_data = {"Day": fixture_day, "Date": fixture_date}

            fixture_info = f"{fixture.away} {fixture.start_time.strftime('%H:%M')} PB @ {fixture.location}"

            row_data[fixture.home] = fixture_info
            row_data[fixture.home + "_cover"] = fixture.covering_team
            row_data[fixture.home + "_eligible"] = fixture.eligible_teams

        # Append the last processed row
        if row_data:
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
            covering_row = {key: "" for key in df.columns}
            covering_row["Date"] = "Buzzbot cover recommendation"
            for team in teams:
                if team in row_data:
                    covering_row[team] = row_data[team + "_cover"]
            df = pd.concat([df, pd.DataFrame([covering_row])], ignore_index=True)

            eligible_row = {key: "" for key in df.columns}
            eligible_row["Date"] = "All eligible covering teams"
            for team in teams:
                if team in row_data:
                    eligible_row[team] = ", ".join(row_data.get(team + "_eligible", []))
            df = pd.concat([df, pd.DataFrame([eligible_row])], ignore_index=True)
            # Add two blank rows after the last eligible teams row
            df = pd.concat(
                [df, pd.DataFrame([{}]), pd.DataFrame([{}])], ignore_index=True
            )

        # HACK: Remove any columns that contain "cover" or "eligible" in the name
        df = df.drop(
            columns=[col for col in df.columns if "cover" in col or "eligible" in col]
        )

        logging.info("Writing DataFrame to worksheet: %s", worksheet_name)
        worksheet.update([df.columns.values.tolist()] + df.fillna("").values.tolist())
        logging.info(
            "Assignments written successfully to worksheet: %s", worksheet_name
        )

    def read_sheet_as_dataframe(self, worksheet_name) -> pd.DataFrame:
        """
        Reads data from the specified worksheet and returns it as a pandas DF.

        Parameters:
            worksheet_name (str): The name of the worksheet to read data from.

        Returns:
            DataFrame: The data from the worksheet as a pandas DataFrame.
        """
        logging.info("Reading data from worksheet: %s", worksheet_name)
        worksheet = self.get_worksheet(worksheet_name)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        logging.info("Data read successfully from worksheet: %s", worksheet_name)
        return df

    def read_sheet_as_fixtures(self, worksheet_name):
        """
        Reads data from the specified worksheet and returns a list of Fixture objects.
        """
        logging.info("Reading fixture data from worksheet: %s", worksheet_name)
        worksheet = self.get_worksheet(worksheet_name)
        data = worksheet.get_all_records()

        fixtures = []
        for row in data:
            fixture = Fixture(
                home_=row["uni_team"],
                away_=row["opposition"],
                start_time_=datetime.strptime(row["start_time"], "%Y-%m-%d %H:%M:%S"),
                umpires_required_=int(row["umpires_needed"]),
                location_=row["location"],
            )
            fixtures.append(fixture)

        logging.info("Fixtures read successfully from worksheet: %s", worksheet_name)
        return fixtures
