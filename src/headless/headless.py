import requests
import logging
from typing import Literal

from playwright.sync_api import Browser

from .auth import Login
from .workflow import Workflow


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

    def request(
        self,
        operation: Literal["GET", "POST", "PUT", "DELETE"],
        params: dict[str, str | int | bool],
        json: dict = None,
        **kwargs,
    ):
        # TODO: Set Smartsheet-Change-Agent header

        params.update(**self.params)

        req = requests.Request(
            operation,
            url=self.base_url,
            params=params,
            json=json,
            headers=self.headers,
            **kwargs,
        )

        prepped = req.prepare()

        r = requests.Session().send(prepped)

        if logging.getLogger().getEffectiveLevel() == logging.DEBUG:
            # TODO: Log prepped request and repsonse
            pass

        return r.json()

    def gateway_request(
        self,
        operation: Literal["GET", "POST", "PUT", "DELETE"],
        path: str,
        service: Literal["WEB2RAPI", "DISCUSSION"],
    ):
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
        """
        return self.request(
            "POST",
            {"formName": "webop", "formAction": "SendGatewayRequest"},
            json={"service": service, "path": path, "operation": operation},
        )
