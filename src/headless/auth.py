from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from headless import Headless

from typing import Dict
import re

from playwright.sync_api import BrowserContext, expect, Request


class Login:
    def __init__(self, headless: Headless):
        self.headless = headless
        self.context: BrowserContext = headless.chrome.new_context(
            **self.headless.manager.pcm.devices["Desktop Chrome"]
        )

        # Intialize a listener for requests
        self.context.on("request", lambda r: self.__handle_request(r))

    def __handle_request(self, request: Request):
        # Many requests have the ss_v param, we don't want to set headers on every request
        if (
            "formAction=loadData&ss_v=" in request.url
            and "cookie" not in self.headless.headers
        ):
            self.__set_auth(request.all_headers())
            self.__set_params(request.url)

    def __set_params(self, url: str):
        """
        Set's the required auth parameters for WebAPI requests.

        Parameters
        ----------
        url : str
            The url to pull the params from
        """

        params = ["ss_v"]

        parsed = self.headless.get_url_details(url)
        for param in params:
            # We do not want to override a user defined param from instantiation, so if it already exists, leave it be.
            if param not in self.headless.params:
                self.headless.params[param] = parsed["params"][param]

    def __set_auth(self, headers: Dict[str, str]):
        """
        Set's the required auth headers for WebAPI requests.

        Parameters
        ----------
        headers : Dict[str, str]
            Headers dict to pull auth headers from.
        """

        # TODO: Implement error checking/logging here
        # Need to make sure we are actually setting headers

        self.headless.headers["cookie"] = headers["cookie"]
        self.headless.headers["x-smar-xsrf"] = headers["x-smar-xsrf"]
        self.headless.headers["user-agent"] = headers["user-agent"]

    def with_user_pass(self):
        # Reset all cookies for a clean slate. Should not be necessary but just in case.
        self.context.clear_cookies()
        p = self.context.new_page()

        p.goto("https://app.smartsheet.com/b/home")

        p.get_by_label("Email").fill(self.headless.manager.username)

        button = p.locator("input[type='submit']")
        expect(button).to_have_attribute("value", "Continue")
        button.click()

        p.get_by_label("Password").fill(self.headless.manager.password)

        button = p.locator("input[type='submit']")
        expect(button).to_have_attribute("value", "Sign in")
        button.click()

        # Use regex matching to ignore the notification count in the title
        # We HAVE to wait here to make sure a request with all the headers we need is made
        expect(p).to_have_title(re.compile(r"Home - Smartsheet\.com"), timeout=30000)

        # Typically we would close a listener when we don't need it anymore,
        # but it seems like there is no method to close listeners. Closing the context will handle this for us.
        self.context.close()

    def with_microsoft(self):
        # TODO: Test this. What happens if MS cookies don't exist? Need to use email pass fallback but MS login specific
        self.driver.delete_all_cookies()
        self.driver.get("https://app.smartsheet.com/b/azurelogin?sua=home")

        self.cookies = self.driver.get_cookies()

    def with_google(self):
        # TODO: Implement this. Should be similar to MS but with different selectors.
        pass

    def with_existing_session(self, port: int = 9222):
        self.headless.manager.chrome = (
            self.headless.manager.pcm.chromium.connect_over_cdp(
                f"http://127.0.0.1:{str(port)}"
            )
        )
        self.headless.chrome = self.headless.manager.chrome

        ctx = self.headless.chrome.contexts[0]

        ctx.on("request", lambda r: self.__handle_request(r))

        p = ctx.new_page()

        p.goto("https://app.smartsheet.com/b/home")

        # NOTE: Repeat check from self.with_user_pass()
        expect(p).to_have_title(re.compile(r"Home - Smartsheet\.com"), timeout=30000)

        p.close()
