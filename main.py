from src.smartsheet import Smartsheet


def main():
    sd = Smartsheet()
    sd.headless.login.with_user_pass()
    sd.headless.workflows.list_workflows(0)


if __name__ == "__main__":
    main()
