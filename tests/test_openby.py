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

class Test_logForm:
    def test_logging(self, browser_context):
        page = browser_context.new_page()
        logging.info("Navigating to website")
        page.goto("https://open.by")

        logging.info("Checking log fields")
        assert page.locator("input#email").is_visible(), "Username field not visible"
        assert page.locator("input#password").is_visible(), "Password field not visible"

        logging.info("Filling login form with test data")
        page.locator("input#email").fill("bahirmasha@gmail.com")
        page.locator("input#password").fill("12365478")

        logging.info("Attempting to submit the login form")
        page.locator("button.bg-indigo-600:has-text('Вход')").click()
