from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .headless import Headless

import csv
from io import StringIO


class Column:
    def __init__(self, headless: Headless):
        self.headless = headless

    def get_column_defs(self, permalink: str):
        """
        Retreives a sheets column definitions from the direct id (permalink path id).

        Parameters
        ----------
        permalink : str
            The permalink or direct id of the sheet


        Returns
        -------
        list : [
            [
                unknown: boolean,       # Index 0
                unknown: int,                # Index 1
                containerID: int,            # Index 2
                displayID?: int,              # Index 3
                unknown: int,                # Index 4
                name: str,                      # Index 5
                unknown: int,                # Index 6
                description: str,            # Index 7
                unknown: null,              # Index 8
                unknown: int,                # Index 9
                unknown: int,                # Index 10
                unknown: boolean,       # Index 11
                unknown: int,                # Index 12
                unknown: int,                # Index 13
                unknown: boolean,       # Index 14
                unknown: int,                # Index 15
                unknown: int,                # Index 16
                unknown: null,              # Index 17
                unknown: int,                # Index 18
                unknown: null,              # Index 19
                publicAPI_ID: int,         # Index 20
                unknown: int,                # Index 21
                unknown: int,                # Index 22
                unknown: null,              # Index 23
                unknown: int,                # Index 24
                unknown: null               # Index 25
            ]
        ]
        """

        metadata = self.headless.sheets.get_grid_by_direct_id(permalink=permalink)

        url_encoded_data = [
            ("formName", "ajax"),
            ("formAction", "fa_loadSheet"),
            ("sk", self.headless.headers["x-smar-xsrf"]),
            ("to", self.headless.params["to"]),
            ("parm1", metadata["data"]["gatewayResponse"]["body"][0]["containerID"]),
            ("parm2", 2),
            ("parm3", ""),
            ("parm4", 1),
            ("errorAsJson", "true"),
        ]

        r = self.headless.request(
            "POST",
            {"formName": "ajax", "formAction": "fa_loadSheet"},
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "*/*",
            },
            data=url_encoded_data,
            stream=True,
        )

        # NOTE: Slice off last two char since it is breaking things
        grid_column_def = self.headless.get_line_in_ajax(
            r.text, "TABLE_INDEX_GRIDCOLUMNDEF"
        )
        grid_column_def = grid_column_def[0].replace(
            "\r\n\r\njsdSchema.ajaxMegaBulkRecordInsert([jsdSchema.TABLE_INDEX_GRIDCOLUMNDEF,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73],",
            "",
        )[:-1]

        # NOTE: Now it should just be a standard csv format. Use the built in csv library, parse it down into an array.
        reader = csv.reader(
            StringIO(grid_column_def), quotechar="'", escapechar="\\", delimiter=","
        )
        column_def = list(reader)

        # NOTE: Split the line into lists of 25 elements for each column. Column defs seem to always be 25 defs
        column_def = [
            column_def[0][x : x + 25] for x in range(0, len(column_def[0]), 25)
        ]

        return column_def
