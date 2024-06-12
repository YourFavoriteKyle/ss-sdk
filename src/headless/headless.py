from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from smartsheet_sdk import Smartsheet

import requests
from requests import Response
import logging
from typing import Literal, Dict
from urllib.parse import urlparse, parse_qs
import re

from playwright.sync_api import Browser
from ratelimit import limits, sleep_and_retry
from datetime import timedelta

from .auth import Login
from .workflow import Workflow
from .column import Column
from .sheet import Sheet


class Headless:
    def __init__(self, manager: Smartsheet):
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

        self.__session = requests.Session()

        self.login = Login(self)
        self.workflows = Workflow(self)
        self.columns = Column(self)
        self.sheets = Sheet(self)

    # TODO: Add exponential backoff strategy here so it does not infinitely retry
    # @on_exception(backoff_retry, RateLimitException, max_tries=8)
    @sleep_and_retry
    @limits(calls=300, period=60)
    def request(
        self,
        operation: Literal["GET", "POST", "PUT", "DELETE"],
        params: dict[str, str | int | bool] = {},
        json: dict = None,
        headers: dict = {},
        stream: bool = False,
        **kwargs,
    ) -> Response:
        # TODO: Set Smartsheet-Change-Agent header

        _params = self.params.copy()
        _params.update(**params)
        _headers = self.headers.copy()
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

        r = self.__session.send(prepped, stream=stream)

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
        # TODO: Error check for None or empty string permalink arg, should throw exception
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

    def get_line_in_ajax(self, ajax: str, search_term: str) -> list[str]:
        """
        Finds and returns a line in an ajax response.

        Parameters
        ----------
        ajax : str
            The ajax response from Smartsheet
        search_term : str
            The term to search for in the ajax response, usually a jsdSchema prop

        Returns
        -------
        list : [str]

        Raises
        ------
        Exception
            If the search term is not found in the ajax response
        """
        ajax = re.split(r"(?!\B'[^']*);(?![^']*'\B)", ajax)
        result = [s for s in ajax if search_term in s]

        if len(result) == 0:
            # TODO: Better error message and loggging
            raise Exception(f"Search term not found in ajax response -> {search_term}")

        return result
