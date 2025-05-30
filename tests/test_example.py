import logging
import pytest
import re
import json

from playwright.sync_api import Page, expect

from helpers.conf import load_json, LOGIN, SELECTORS


@pytest.fixture(scope="class")
def make_video():
    logging.info("Fixture setup - making video")
    yield
    logging.info("Fixture teardown - save video")


@pytest.fixture(autouse=True)
def load_login_page_fixture(page: Page):
    """
    This func to load the login page :)
    Should be executed before class / or / test if applicable
    """
    logging.info("Fixture setup - loading login page")
    page.goto(load_json(LOGIN)["loginUrl"])
    page.wait_for_timeout(2000)
    page.wait_for_load_state("networkidle")
    yield


@pytest.mark.usefixtures("make_video")
class TestsLoginPage:

    def test_page_welcome(self, page: Page):
        logging.info("Verify page loaded successfully")
        logging.info("Checking Welcome text")
        welcome_text = page.locator(load_json(SELECTORS)["login"]["welcome"]).text_content()
        logging.info(f"Welcome text: {welcome_text}")


    def test_get_started_link(self, page: Page):
        """
        Create following test:
        1. Input in input field data from config/login.json (LOGIN var)
        2. Input password
        3. Click Login button and check result
        NOTE: I don't know what is expected result - check by yourself
        """
        pass

    def test_input_login_without_pass(self, page: Page):
        """
        Input only login without password
        Verify error message was shown (smth like "Please enter your password") - check on site
        """
        pass

    def test_input_password_without_login(self, page: Page):
        pass