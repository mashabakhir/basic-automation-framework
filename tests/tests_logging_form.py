import pytest
import logging
import time
from playwright.sync_api import sync_playwright  #import playwright sync API for browser automation

#configure logging to show timestamp, log level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def pytest_addoption(parser):
    parser.addoption(
        "--headless",  #option name
        action="store_true", #store true if flag is provided? jtherwise false
        default=False, #default value when flag is not used
        help="Run browser in headless mode" #help message for this option
    )

@pytest.fixture(scope="session", autouse=True)
def SetupAndTearDownSuite():
    # fixture that runs once before the entire test session
    logging.info("Setup before test suite execution")
    yield #point at which tests start running
    # code after yield runs once after all tests have finished
    logging.info("TearDown after test suite execution")

@pytest.fixture(scope="session")
def browser_context_args(pytestconfig):
    # read the --headless flag value from pytest configuration
    headless = pytestconfig.getoption("--headless", default=False)
    # launch playwright in synchronous mode
    with sync_playwright() as p:
        # launch Chromium browser; headless=true means no GUI, false shows the browser window
        browser = p.chromium.launch(headless=headless)
        # create a new browser context
        context = browser.new_context()
        # provide the context to tests
        yield context
        # close the browser after all tests using this fixture have completed
        browser.close()

class TestRegistrationForm:
    def test_registration(self, browser_context_args):
        page = browser_context_args.new_page() #open new tab in the browser
        logging.info("Navigating to onliner.by")
        page.goto("https://onliner.by") #go to the target website

        logging.info("Clicking the login button")
        page.click("div.auth-bar__item.auth-bar__item--text >> text=Вход")  #click on the login link

        logging.info("Checking registration fields")
        assert page.locator("input[placeholder='Ник или e-mail']").is_visible(), "Username field not visible"
        assert page.locator("input[placeholder='Пароль']").is_visible(), "Password field not visible"

        logging.info("All registration fields are present")
        logging.info("Filling registration form with test data")
        page.locator("input[placeholder='Ник или e-mail']").fill("bahirmasha@gmail.com")
        page.locator("input[placeholder='Пароль']").fill("bnparola2006")

        logging.info("Attempting to submit the registration form")
        page.locator("button[type='submit']", has_text="Войти").click()

        time.sleep(30)

        logging.info("Registration form submitted (if no validation errors occurred)")
