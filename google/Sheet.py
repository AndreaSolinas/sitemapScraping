import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

__ABS_PATH__ = os.path.dirname(os.path.abspath(__file__))


# TODO: __ABS_PATH__ secondo me è sbagliata perchè se la cambi fa un casino:
#   controlla se cambi path dove gesu ti mette il file token.json
class Spreadsheet():
    __SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    __SAMPLE_SPREADSHEET_ID: str = None
    __SAMPLE_RANGE_NAME: str = None

    def __init__(self, UUID: str | None = None,
                 range: str | None = None,
                 credentials: str = f"{__ABS_PATH__}/credentials.json",
                 token: str = f"{__ABS_PATH__}/token.json"
                 ):
        self.__SAMPLE_SPREADSHEET_ID = UUID
        self.__SAMPLE_RANGE_NAME = range
        self.creds = None

        if os.path.exists(token):
            self.creds = Credentials.from_authorized_user_file(token, scopes=self.__SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials, self.__SCOPES
                )
                self.creds = flow.run_local_server(port=0)

            with open(token, "w") as token:
                token.write(self.creds.to_json())

        service = build("sheets", "v4", credentials=self.creds)

        self.__sheet = service.spreadsheets()

    def get_UUID(self) -> str:
        """
        Getter method to take identifier of the curren spreadsheet
        :return: UUID of the document
        """
        if self.__SAMPLE_SPREADSHEET_ID:
            return self.__SAMPLE_SPREADSHEET_ID
        else:
            raise NotSetException(
                f'The variable UUID is not set \n Use the method set_UUID(UUID) or pass in the costructor argument to set your identifier')

    def get_range(self) -> str:
        """
        Getter method to take sheet and columns
        :return: Current range of data
        """
        if self.__SAMPLE_RANGE_NAME:
            return self.__SAMPLE_RANGE_NAME
        else:
            raise NotSetException(
                f'The variable range is not set \n Use the method set_range(range) or pass in the costructor argument to set your range')

    def set_UUID(self, UUID: str) -> None:
        """Setter method to set identifier of the curren spreadsheet
        https://docs.google.com/spreadsheets/d/{UUID}/edit
        :param: UUID, the identifier of the spreadsheet
        """
        self.__SAMPLE_SPREADSHEET_ID = UUID

    def set_range(self, RANGE: str) -> None:
        """
        Setter method to take sheet and columns
        :param: RANGE, sheet and range es: "sheet1!A2:Z"
        """
        self.__SAMPLE_RANGE_NAME = RANGE

    def get_data(self, range: str = None) -> list:
        """
        Getter method to take columns value
        :return: List of element divide by row [[A1,B1],[A2,B2]]
        """
        result = self.__sheet.values().get(
            spreadsheetId=self.__SAMPLE_SPREADSHEET_ID,
            range=range or self.__SAMPLE_RANGE_NAME,
            valueRenderOption="FORMATTED_VALUE",
        ).execute()

        return result.get("values", [])

    def set_data(self, data: list) -> None:
        """
        set values into the cell
        :param: data, list of values to set
        """
        self.__sheet.values().append(
            spreadsheetId=self.__SAMPLE_SPREADSHEET_ID,
            range=self.__SAMPLE_RANGE_NAME,
            responseValueRenderOption="FORMATTED_VALUE",
            valueInputOption="USER_ENTERED",
            body={"values": data}
        ).execute()

    def check_status(self):
        if self.get_data('A1'):
            return


class NotSetException(TypeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
