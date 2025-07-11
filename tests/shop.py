import pytest
import logging
import time
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.fixture(scope="session", autouse=True)
def setup_and_tear_down_suite():
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
        page.goto("https://automationexercise.com")

        logging.info("test log form")
        page.locator("a[href='/login']").click()

        logging.info("checking registration fields")
        page.locator("input[data-qa='login-email']").fill("bahirmasha@gmail.com")
        page.locator("input[data-qa='login-password']").fill("parola2006")
        page.locator("button[data-qa='login-button']").click()

        logging.info("category selection")
        page.locator("a[href='#Women']").click()

        logging.info("closet selection")
        page.locator("a[href='/category_products/1']").click()

        logging.info("product selection")
        page.locator('a[href="/product_details/3"]').click()

        logging.info("add product in cart")
        page.locator('button.btn.btn-default.cart').click()

        logging.info("view cart")
        page.locator('a[href="/view_cart"]').first.click()

        time.sleep(30)




