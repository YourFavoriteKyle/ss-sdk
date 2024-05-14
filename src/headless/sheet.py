from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .headless import Headless


class Sheet:
    def __init__(self, headless: Headless):
        self.headless = headless

    def get_grid_by_direct_id(
        self, *, direct_id: str = None, permalink: str = None
    ) -> object:
        """
        Gets a sheets metadata from its direct id (permalink path id).

        Parameters
        ----------
            direct_id : str
                The direct id of the sheet
            permalink : str
                The permalink of the sheet

        Returns
        -------
            object : {
                data: {
                    gatewayResponse: {
                        body: [
                            {
                                name: str
                                containerType: int
                                displayObjectID: int,
                                containerID: int,
                                directID: str
                            }
                        ]
                        statusCode: int
                        },
                    errorCode: int,
                    errors: [],
                    isLicensingError: bool,
                    serverStatus: bool,
                    serverStatusText: str
                    }
            }

        Raises
        ------
            Exception
                If either direct_id or permalink is not specified
        """

        if direct_id is None and permalink is None:
            raise Exception("Either direct_id or permalink must be specified")

        if direct_id is None and permalink is not None:
            direct_id = self.headless.get_url_details(permalink)["paths"][1]

        r = self.headless.gateway_request(
            json={
                "gatewayRequest": {
                    "body": direct_id,
                    "method": "POST",
                    "path": "/2.0/serviceprivate/grid/getGridsByDirectId",
                    "service": "WEB2RAPI",
                    "encodedQueryParams": "",
                }
            }
        )

        # TODO: Error checking and logging

        return r.json()
