from driver import SmartsheetWebDriver

def main():
    sd = SmartsheetWebDriver()
    sd.headless.login.with_user_pass("user", "pass")
    sd.headless.workflows.list_workflows(0)

if __name__ == "__main__":
    main()

