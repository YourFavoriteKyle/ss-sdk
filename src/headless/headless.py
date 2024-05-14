import requests
from requests import Response
import logging
from typing import Literal, Dict
from urllib.parse import urlparse, parse_qs

from playwright.sync_api import Browser

from .auth import Login
from .workflow import Workflow
from .sheet import Sheet


class Headless:
    def __init__(self, manager):
        self.manager = manager
        self.chrome: Browser = manager.chrome
        self.base_url = "https://app.smartsheet.com/b/home"
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "",
        }
        # NOTE: ss_v param is required for every request, but change frequently. Set in auth module.
        self.params = {"to": "68000"}

        self.login = Login(self)
        self.workflows = Workflow(self)
        self.sheets = Sheet(self)

    def request(
        self,
        operation: Literal["GET", "POST", "PUT", "DELETE"],
        params: dict[str, str | int | bool] = {},
        json: dict = None,
        headers: dict = {},
        **kwargs,
    ) -> Response:
        # TODO: Set Smartsheet-Change-Agent header

        _params = self.params
        _params.update(**params)
        _headers = self.headers
        _headers.update(**headers)

        req = requests.Request(
            operation,
            url=self.base_url,
            params=_params,
            json=json,
            headers=_headers,
            **kwargs,
        )

        prepped = req.prepare()

        r = requests.Session().send(prepped)

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            # TODO: Log prepped request and repsonse
            pass

        return r

    def gateway_request(
        self,
        operation: Literal["GET", "POST", "PUT", "DELETE"] = "GET",
        path: str = None,
        service: Literal["WEB2RAPI", "DISCUSSION"] = "WEB2RAPI",
        json: dict = None,
    ) -> Response:
        """
        Sends a gateway request to Smartsheet.

        Note
        ----
        Gateway requests are often used to obtain metadata about a specified resource within Smartsheet.

        Parameters
        ----------
        operation : Literal["GET", "POST", "PUT", "DELETE"]
            The operation to perform. Usually "GET".
        path : str
            The path to the resource. This one

        Returns
        -------
        object : {
            data: {
                gatewayResponse: {
                    body: {
                        id: str,
                        name: str,
                        type: str
                        },
                    statusCode: int
                    },
                errorCode: int,
                errors: [],
                isLicensingError: bool,
                serverStatus: bool,
                serverStatusText: str
                }
            }
        """

        if json is None:
            return self.request(
                "POST",
                {"formName": "webop", "formAction": "SendGatewayRequest"},
                json={
                    "gatewayRequest": {
                        "method": operation,
                        "path": path,
                        "service": service,
                    }
                },
            )
        else:
            return self.request(
                "POST",
                {"formName": "webop", "formAction": "SendGatewayRequest"},
                json=json,
            )

    def get_url_details(
        self, permalink: str
    ) -> Dict["paths" : list[str], "params" : Dict[str, str]]:
        # TODO: Parse url to pull out the baseURL and return paths in array as well as parameters in array of tuples
        """
        Gets details from a Smartsheet URL.

        Parameters
        ----------
        permalink : str
            The permalin link of the sheet, including the domain

        Returns
        -------
        dict : {paths: list[str], params: Dict[str, str]}
        """

        url = urlparse(permalink)

        # Remove the empty path the preceeding slash creates via array slicing (first element)
        paths = url.path.split("/")[1:]
        params = parse_qs(url.query)

        return {"paths": paths, "params": params}
