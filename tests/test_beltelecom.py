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
def Setup_And_Tear_Down_Suite():
    logging.info("setup before test suite execution")
    yield
    logging.info("tearDown after test suite execution")

@pytest.fixture(scope="session")
def browser_context_args(pytestconfig):
    headless = pytestconfig.getoption("--headless", default=False)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        yield context
        browser.close()

class TestLoggingForm:
    def test_logging(self, browser_context_args):
        page = browser_context_args.new_page()
        logging.info("navigating to website")
        page.goto("https://beltelecom.by")

        logging.info("clicking the login button")
        page.locator("#account-link").click()

        logging.info("select new version")
        page.click("a", has_text="Новая версия")

        logging.info("checking registration fields")
        assert page.locator("input[name='user_phone']").is_visible(), "username field not visible"
        assert page.locator("input#log_password").is_visible(), "password field not visible"

        logging.info("All registration fields are present")
        logging.info("Filling registration form with test data")
        page.locator("input[name='user_phone']").fill("292178666")
        page.locator("input#log_password").fill("bmparola2006")

        logging.info("Attempting to submit the registration form")
        page.locator("button[type='submit']", has_text="Войти").click()

        logging.info("Registration form submitted (if no validation errors occurred)")
