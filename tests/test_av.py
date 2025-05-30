import pytest
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Run browser in headless mode"
    )

@pytest.fixture(scope="session", autouse=True)
def SetupAndTearDownSuite():
    logging.info("Setup before test suite execution")
    yield
    logging.info("TearDown after test suite execution")

@pytest.fixture(scope="session")
def browser_context_args(pytestconfig):
    headless = pytestconfig.getoption("--headless", default=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        yield context
        browser.close()

class TestRegistrationForm:
    def test_registration(self, browser_context_args):
        page = browser_context_args.new_page()
        logging.info("Navigating to av.by")
        page.goto("https://av.by")

        logging.info("Clicking the login button")
        page.locator("span.nav__link-text", has_text="Войти").click()

        logging.info("Checking registration fields")
        assert page.locator("#authPhone").is_visible(), "Username field not visible"
        assert page.locator("#passwordPhone").is_visible(), "Password field not visible"

        logging.info("All registration fields are present")
        logging.info("Filling registration form with test data")
        page.locator("#authPhone").fill("292178666")
        page.locator("#passwordPhone").fill("bmparola2006")

        logging.info("Attempting to submit the registration form")
        submit_button = page.locator("button.button--action:has(span.button__text)", has_text="Войти")
        submit_button.wait_for(state="attached")
        submit_button.wait_for(state="enabled")
        submit_button.click()

        logging.info("Registration form submitted (if no validation errors occurred)")
