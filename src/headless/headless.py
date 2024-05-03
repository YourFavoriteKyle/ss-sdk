from requests import request, PreparedRequest

from .auth import Login
from .workflow import Workflow


class Headless:
    def __init__(self, driver):
        self.chrome = driver.chrome
        self.base_url = "https://app.smartsheet.com/b/home"
        self.headers = {"Content-Type": "application/json", "Accept": "application/json", "User-Agent": ""}

        self.login = Login(self)
        self.workflows = Workflow(self)
    
    def __add_query_params(self, params: dict):

        # These seem to be in every frontend request and seem to be required.
        # They are set in the frontend as a default but can be overriden.
        if "to" not in params:
            params["to"] = "68000"
        # FIXME: This version number changes frequently, I think it is browser version? Need to determine a way to check for this update.
        # It SEEMS to be errorCode -14 is returned when this value is incorrect.
        if "ss_v" not in params:
            params["ss_v"] = "307.0.0"

        query_params = "?" + "&".join(f"{k}={v}" for k, v in params.items())

        return query_params
        
    def request(self, operation: str, params: dict, data: dict = None):

        prepped = {"method": operation, "url": f"{self.base_url}{self.__add_query_params(params)}", "json": data, "headers": self.headers}
        r = request(**prepped)
        print(r.request.__dict__)
        print()
        print(r.json())