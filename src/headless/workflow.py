from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .headless import Headless

import json

class Workflow:
    def __init__(self, headless: Headless):
        self.headless = headless

    def list_workflows(self, permalink: str, mapped: bool = True) -> object:
        """
        List all workflows and their properties from a sheet.

        Note
        ----
        This request will make additional background requests in
        order to map the user accessible sheet permalink to the WebAPI sheetId.

        Warning
        -------
        Only columnIDs are currently mapped to their publicAPI ids

        Parameters
        ----------
        permalink : str
            The permalink of the sheet
        mapped : bool
            Whether or not to map the containerIDs to their publicAPI ids
        
        Returns
        -------
        json object
        """

        url_details = self.headless.get_url_details(permalink)

        metadata = self.headless.gateway_request(
            "GET", f"/2.0/internal/navigation/metadata/{url_details["paths"][1]}", "WEB2RAPI"
        )

        metadata = metadata.json()


        r = self.headless.request(
            "POST",
            {"formName": "webop", "formAction": "GetWorkflowsBySheet"},
            {"sheetId": metadata["data"]["gatewayResponse"]["body"]["id"]},
        )

        response = r.json()

        if not mapped: 
            return response

        column_defs = self.headless.columns.get_column_defs(permalink)
        response_string = json.dumps(response)

        # NOTE: Maps the containerIDs to their publicAPI ids
        for column_def in column_defs:
            response_string = response_string.replace(column_def[2], column_def[20])
        
        return json.loads(response_string)

