import requests
import logging

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
        operation: str,
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
