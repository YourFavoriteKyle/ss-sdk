import subprocess

from playwright.sync_api import sync_playwright, PlaywrightContextManager

from headless.headless import Headless

class SmartsheetWebDriver(PlaywrightContextManager):
    """
    Parameters
    ------------

    Returns
    -------
        WebDriverManager
    """
    def __init__(self):

        # Run a subprocess to update and install drivers since it does not seem there is a way to do it within the script process
        subprocess.run(["playwright", "install", "chromium"])

        self.pcm = sync_playwright().start()
        self.chrome = self.pcm.chromium.launch(headless=False, timeout=10000)
        # self.implicitly_wait(10)
        # self.wait = WebDriverWait(self, timeout=5)
        # self.set_script_timeout(10)

        self.headless = Headless(self)
        

        

    