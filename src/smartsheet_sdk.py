import subprocess
import os

from smartsheet import Smartsheet as SSClient

from playwright.sync_api import sync_playwright, PlaywrightContextManager

from src.headless.headless import Headless


class Smartsheet(PlaywrightContextManager):

    def __init__(
        self,
        *,
        username: str = None,
        password: str = None,
        access_token: str = None,
        **kwargs
    ):
        """
        Creates a new client for interacting with both the WebAPI and the API.

        It is recommended to provide the username and password from the
        same account that the access_token is associated with to ensure
        equal access when interacting with assets. This manager does not
        check for equal access rights.

        Parameters
        ------------
        access_token : str
            Access Token for making client requests. This may also be set as
            an environment variable in SMARTSHEET_ACCESS_TOKEN.
        username : str
            Username for making browser requests. This may also be set as
            an environment variable in SMARTSHEET_USERNAME.
        password: str
            Password for making browser requests. This may also be set as
            an environment variable in SMARTSHEET_PASSWORD.
        **kwargs: dict[str, Any]
            Additional parameters to pass to the library. These arguments will
            be passed into sublibraries as well. See the sublibraries for more
            supported parameters.

        Returns
        -------
            WebDriverManager
        """

        if access_token and username and password:
            self.access_token = access_token
            self.username = username
            self.password = password
        else:
            self.access_token = os.environ.get("SMARTSHEET_ACCESS_TOKEN", None)
            self.username = os.environ.get("SMARTSHEET_USERNAME", None)
            self.password = os.environ.get("SMARTSHEET_PASSWORD", None)

        # Run a subprocess to update and install drivers since it does not
        # seem there is a way to do it within the script process
        subprocess.run(["playwright", "install", "chromium"])

        self.pcm = sync_playwright().start()
        self.chrome = self.pcm.chromium.launch(headless=False, timeout=10000)

        self.headless = Headless(self)
        self.api: SSClient = SSClient(access_token=self.access_token)
