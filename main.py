import time

from src.smartsheet_sdk import Smartsheet

import csv


def main():
    start_time = time.perf_counter()

    sd = Smartsheet()
    sd.headless.login.with_existing_session()

    sheets = sd.api.Sheets.list_sheets(include_all=True)

    column_names = [
        "Sheet Name",
        "Sheet ID",
        "Workflow Name",
        "Workflow ID",
        "Enabled",
        "Referenced Columns",
        "Contacts",
    ]

    write_row_to_csv(column_names)

    for sheet in sheets.data:
        try:
            for wf in get_workflow_data(sd, sheet.permalink):
                wf.insert(0, sheet.id)
                wf.insert(0, sheet.name)
                write_row_to_csv(wf)
        except Exception as e:
            print(
                f"Error getting information for sheet {sheet.name} with Id {sheet.id}: {sheet.permalink}",
                {e},
            )

    end_time = time.perf_counter()
    run_time = (end_time - start_time) / 60
    print(f"Run time: {run_time} minutes")


def get_workflow_data(smartsheet: Smartsheet, permalink: str):
    workflows = smartsheet.headless.workflows.list_workflows(permalink)

    for workflow in workflows["data"]["workflows"]:
        ref_col = [str(c["columnID"]) for c in workflow["sheetColumns"]]
        ref_contact = [c["emailAddress"] for c in workflows["data"]["userContacts"]]

        yield [
            workflow["name"],
            workflow["id"],
            workflow["enabled"],
            ", ".join(ref_col),
            ", ".join(ref_contact),
        ]


def write_row_to_csv(row: list[any]):
    with open("demo_workflows.csv", "a+", newline="", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(row)


if __name__ == "__main__":
    main()
