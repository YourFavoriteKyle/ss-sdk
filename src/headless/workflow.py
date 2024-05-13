from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .headless import Headless


class Workflow:
    def __init__(self, headless: Headless):
        self.headless = headless

    def list_workflows(self, permalink: str) -> dict:
        """
        List all workflows and their properties from a sheet.

        Note
        ----
        This request will make additional background requests in
        order to map the user accessible sheet permalink to the WebAPI sheetId.

        Parameters
        ----------
        permalink : str
            The permalink of the sheet
        """

        url_details = self.headless.get_url_details(permalink)

        metadata = self.headless.gateway_request(
            "GET", f"/2.0/internal/navigation/metadata/{url_details["paths"][1]}", "WEB2RAPI"
        )

        return self.headless.request(
            "POST",
            {"formName": "webop", "formAction": "GetWorkflowsBySheet"},
            {"sheetId": metadata["data"]["gatewayResponse"]["body"]["id"]},
        )
