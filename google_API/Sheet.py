import os
from uuid import UUID

import googleapiclient.errors as google_exception
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


__ABS_PATH__ = os.getcwd()

##TODO: __ABS_PATH__ is not work on crontab because the script run in /home/user/ not in the project folder and it reurn
#   /home/user/ else /filepath/

class Spreadsheet():
    r"""
    Class to simplify access to data from a spreadsheet google API.

    This class allows access to the data of a goolge sheet given the id and range

    Notes:
        For credentials:
            - You must have created a project (https://console.cloud.google.com/welcome)
            - You must enable google sheet api (https://console.cloud.google.com/apis/library/sheets.googleapis.com)
            - You need to configure the OAuth allow screen (see Quickstart)
            - You have to authorize credentials for the desktop api (https://console.cloud.google.com/apis/credentials/oauthclient/)
            - Finally, you need to download the credentials

        For tokens:
            - Upon creation of the token you will be asked for account authorization to view, edit, create and delete
            all your google worksheets (only if the token does not exist)
            - The token is automatically downloaded to the path of the attribute token (defaults to the current directory)

    References:
        - Quickstart: https://developers.google.com/sheets/api/quickstart/python
        - API: https://console.cloud.google.com/apis

    Attributes:
        UUID(str,optional): this is the alphanumeric string that appears within the url of the sheet you are using example:

            `https://docs.google.com/spreadsheets/d/{YOUR UUID}/edit#gid=0`

        range(str,optional):this is the name of the sheet in use (by default it is Sheet1) followed by the
            values of the columns you want to select as an example range:

            **Sheet1!A:C** -> selects all rows present from column A through C

            **Sheet1!A1:F5** -> selects only rows 1 through 5, from column A through F

        credentials(str,optional): refers to the location of the API credentials file (OAuth 2.0 client ID).
            default search in the current folder of the class instance

        token(str,optional):as with credentials refers to the location of where the token is or where it will be
            entered if it does not exist. default search in the current folder of the class instance

    """

    __SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
    __SAMPLE_SPREADSHEET_ID: str = None
    __SAMPLE_RANGE_NAME: str = None

    def __init__(self, UUID: str | None = None,
                 range: str | None = None,
                 credentials: str = f"{__ABS_PATH__}/credentials.json",
                 token: str = f"{__ABS_PATH__}/token.json"
                 ) -> None:
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

    def __str__(self):
        if self.__SAMPLE_SPREADSHEET_ID is None:
            raise AttributeError('you have to specify a UUID in order to access the data to see them')
        return f"""<Spreadsheet Object>\n\t Connected to https://docs.google.com/spreadsheets/d/{self.__SAMPLE_SPREADSHEET_ID}/edit in Range {self.__SAMPLE_RANGE_NAME}"""

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

    def set_UUID(self, UUID: str):
        """Setter method to set identifier of the curren spreadsheet
        https://docs.google.com/spreadsheets/d/{UUID}/edit
        :param: UUID, the identifier of the spreadsheet
        """
        self.__SAMPLE_SPREADSHEET_ID = UUID
        try:
            self.check_status()
        except google_exception.HttpError as e:
            self.__SAMPLE_SPREADSHEET_ID = None
            raise ConnectionError('the UUID you entered is invalid')

        return self

    def set_range(self, RANGE: str):
        """
        Setter method to take sheet and columns
        :param: RANGE, sheet and range es: "sheet1!A2:Z"
        """
        self.__SAMPLE_RANGE_NAME = RANGE
        return self

    def fetch(self, range: str = None) -> list:
        """
        Getter method to take columns value
        :return: List of element divide by row [[A1,B1],[A2,B2]]
        """
        if self.__SAMPLE_SPREADSHEET_ID is None or (self.__SAMPLE_RANGE_NAME is None and range is None):
            raise AttributeError('you have to specify a UUID and a range to access the data')

        result = self.__sheet.values().get(
            spreadsheetId=self.__SAMPLE_SPREADSHEET_ID,
            range=range or self.__SAMPLE_RANGE_NAME,
            valueRenderOption="FORMATTED_VALUE",
        ).execute()

        return result.get("values", [])

    def upload(self, data: list):
        """
        set values into the cell
        :param: data, list of values to set
        """
        if self.__SAMPLE_SPREADSHEET_ID is None:
            raise AttributeError('you have to specify a UUID and a range to access the data')
        self.__sheet.values().append(
            spreadsheetId=self.__SAMPLE_SPREADSHEET_ID,
            range=self.__SAMPLE_RANGE_NAME,
            responseValueRenderOption="FORMATTED_VALUE",
            valueInputOption="USER_ENTERED",
            body={"values": data}
        ).execute()
        return self

    def check_status(self) -> bool:
        if self.fetch('A1'):
            return True


class NotSetException(TypeError):
    def __init__(self, message: str) -> None:
        super().__init__(message)
