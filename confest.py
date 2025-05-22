import pytest
import logging
from playwright.sync_api import (sync_playwright) #import playwright sync API for browser automation

#configure logging to show timestamp, log level, and message
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def pytest_addoption(parser):
    parser.addoption(
        "--headless", #option name
        action="store_true", #store true if flag is provided, otherwise False
        default=False,     #default value when flag is not used
        help="Run browser in headless mode"  #help message for this option
              )

@pytest.fixture(scope="session", autouse=True)
def SetupAndTearDownSuite():
    #fixture that runs once before the entire test session
    logging.info("Setup before test suite execution")
    yield #point at which tests start running
    #code after yield runs once after all tests have finished
    logging.info("TearDown after test suite execution")

@pytest.fixture(scope="session")
def browser_context_args(pytestconfig):
    #read the --headless flag value from pytest configuration
    headless = pytestconfig.getoption("--headless")
    #launch playwright in synchronous mode
    with sync_playwright() as p:
        #launch Chromium browser; headless=true means no GUI, false shows the browser window
        browser = p.chromium.launch(headless=headless)
        #create a new browser context
        context = browser.new_context()
        yield context #provide the context to tests
        #close the browser after all tests using this fixture have completed
        browser.close()

        class TestRegistrationForm:
            def test_registration(self, browser_context_args):
                page = browser_context_args.new_page() #open new tab in the browser
                logging.info("Navigating to onliner.by")
                page.goto("https://onliner.by") #go to the target website

                logging.info("Clicking the login button")
                page.click("a[href*='login']")  #click on the login link

                logging.info("Waiting for the iframe with login form to appear")
                page.wait_for_selector("iframe") #wait until iframe appears in DOM

                logging.info("Switching to the iframe")
                iframe = page.frame_locator("iframe").first #access the first iframe

                logging.info("Clicking the 'Registration' tab/link inside the iframe")
                iframe.locator("text='Вход'").click() #click on the registration link

                logging.info("Checking registration fields")
                #verify that each field is visible and accessible
                assert iframe.locator("input[name='user[login]']").is_visible(), "Username field not visible"
                assert iframe.locator("input[name='user[password]']").is_visible(), "Password field not visible"
                assert iframe.locator(
                    "input[name='user[password_confirmation]']").is_visible(), "Password confirmation field not visible"
                assert iframe.locator("input[name='user[email]']").is_visible(), "Email field not visible"

                logging.info("All registration fields are present") 
                #log the beginning of the form process
                logging.info("Filling registration form with test data")
                #input username
                iframe.locator("input[name='user[login]']").fill("bahirmasha@gmail.com")
                #input password
                iframe.locator("input[name='user[password]']").fill("bnparola2006")
                logging.info("Attempting to submit the registration form")
                iframe.locator("button[type='submit']").click()

                logging.info("Registration form submitted (if no validation errors occurred)")
