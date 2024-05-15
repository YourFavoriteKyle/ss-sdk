import json

from src.smartsheet_sdk import Smartsheet

import csv


def main():
    sd = Smartsheet()
    sd.headless.login.with_user_pass()
    workflows = sd.headless.workflows.list_workflows()

    column_names = [
        "Workflow Name",
        "Workflow ID",
        "Enabled",
        "Referenced Columns",
        "Contacts",
    ]
    workflows_data = []

    for workflow in workflows["data"]["workflows"]:
        ref_col = [str(c["columnID"]) for c in workflow["sheetColumns"]]
        ref_contact = [c["emailAddress"] for c in workflows["data"]["userContacts"]]
        workflows_data.append(
            [
                workflow["name"],
                workflow["id"],
                workflow["enabled"],
                ", ".join(ref_col),
                ", ".join(ref_contact),
            ]
        )

    with open("demo_workflows.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(column_names)
        for workflow in workflows_data:
            writer.writerow(workflow)


if __name__ == "__main__":
    main()
