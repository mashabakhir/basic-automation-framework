import pytest
import logging

@pytest.fixture(scope="session", autouse=True)
def SetupAndTearDownSuite():
    logging.info("Setup before test suite execution")

    yield

    logging.info("TearDown after test suite execution")