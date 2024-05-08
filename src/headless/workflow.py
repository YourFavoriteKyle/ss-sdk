class Workflow:
    def __init__(self, headless):
        self.headless = headless

    def list_workflows(self, sheetId: str) -> dict:
        """
        Parameters
        ----------
        sheetId : str
            The id of the sheet to list workflows from. This ID is not the
            properties ID, but a custom ID found in frontend requests.
            This is not user friendly to obtain.
        """

        self.headless.request(
            "POST",
            {"formName": "webop", "formAction": "GetWorkflowsBySheet"},
            {"sheetId": sheetId},
        )
