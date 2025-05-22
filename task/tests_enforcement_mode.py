import logging
import time

import pytest
import allure
from time import sleep

from core.common.screen_rec import RecordScreen
from gui_manager.observers.hacking_protection_tab.anti_ransomware import AntiRansomware
from core import (
    log_test_headline,
    log_svc_line,
    report_fail,
    report_passed,
    HoneypotValidation,
    ArPolicies,
    PidWatcher,
    Healthcheck,
    HOST
)


# -------------------------------------------------- FIXTURES ----------------------------------------------------------

@pytest.fixture(scope='class')
def screen_rec():
    rec = RecordScreen("AR_Switch_Off_On_Suite")
    rec.start()
    yield
    rec.stop()

@pytest.fixture(scope='class')
def api():
    ar = AntiRansomware()
    yield ar
    del ar


@pytest.fixture(scope="class")
def pid_monitor():
    log_svc_line("SETUP: CAPTURE PROCESSES PID`s")
    PidWatcher().setup()
    yield
# --------------------------------------------------- TESTS ------------------------------------------------------------


@allure.epic("Anti-Ransomware Blade")
@allure.suite('Anti-Ransomware Blade - Switch to OFF')
@allure.sub_suite(f'{HOST}')
@allure.label("package", f'{HOST}.tests_ar.tests_enforcement_mode')
@pytest.mark.usefixtures('screen_rec', 'pid_monitor')
class TestsArEnforcementModeOffState:

    @allure.title("Disable blade in UI")
    @pytest.mark.flaky(reruns=2, reruns_delay=60)
    def test_disable_blade(self, api):
        """
        Steps:
            Disable AR
            Check blade state in UI

        Assertion:
            AR is still enabled
        """
        log_test_headline(f"AR Switch to OFF: Switch blade in UI to OFF state")
        disable = api.disable()
        sleep(5)
        enabled = api.enabled()
        if not disable:
            report_fail(f"Actual: AR was not disabled on UI level via API call. Expected: blade is disabled.")

        if enabled:
            report_fail(f"Anti-Ransomware is enabled: {enabled}.")

        report_passed("AR was successfully switched to OFF state")

    @pytest.mark.flaky(reruns=3, reruns_delay=180)
    @allure.title("Blade is disabled by policy")
    def test_policy(self):
        """
        Steps:
            Check AR policy in the logs

        Assertion:
            AR is enabled by policy
        """
        log_test_headline(f"AR Switch to OFF: AR is OFF by policy")
        _wrong_policy = ArPolicies(ar_enabled=False).wrong_policy()
        report_passed("AR policy corresponds to the policy which should be in AR OFF state (disabled)")

    @allure.title("Honeypots were not found")
    @pytest.mark.flaky(reruns=3, reruns_delay=180)
    def test_no_honeypots(self):
        """
        Steps:
            Iterate over honeypots directories
            Verify honeypots does not exist

        Assertion:
            Honeypots directories where found
        """
        log_test_headline(f"AR Switch to OFF: Honeypots were not found")
        HoneypotValidation(blade_enabled=False).check_honeypots()

    @allure.title("Client health-check post suite execution")
    def test_health_check_post_switch_to_off_state(self):
        """
        Steps:
            Verify that processes, services and drivers are running which should be run and
            verify that proc, svc, and drv are not running if it is applicable for SKU

        Assertion:
            Expected running -> not running; expected down -> running
        """
        log_test_headline(f"AR Switch to OFF: Regular client health check")
        fail_msg = ""

        _hcheck_fail = Healthcheck().failed
        _pid_fail = PidWatcher().changed()

        if _hcheck_fail:
            fail_msg += _hcheck_fail

        if _pid_fail:
            fail_msg += _pid_fail

        if fail_msg:
            report_fail(fail_msg)

        report_passed("All components which should be run -> run; which should not run -> down")


@allure.epic("Anti-Ransomware Blade")
@allure.suite('Anti-Ransomware Blade - Switch to ON')
@allure.sub_suite(f'{HOST}')
@allure.label("package", f'{HOST}.tests_ar.tests_enforcement_mode')
@pytest.mark.usefixtures('screen_rec', 'pid_monitor')
class TestsArEnforcementModeOnState:
    """
    Setup:
        Should be executed after TestsArEnforcementModeOffState()
    """

    @allure.title("Enable blade in UI")
    @pytest.mark.flaky(reruns=2, reruns_delay=60)
    def test_enable_blade(self, api):
        """
        Steps:
            Enable AR
            Get toggle state in UI

        Assertion:
            AR is OFF
        """
        log_test_headline(f"AR Switch to ON: Switch blade in UI to ON state")
        enable = api.enable()
        sleep(5)
        enabled = api.enabled()

        if not enable:
            report_fail(f"Could not enable in UI.")
        if not enabled:
            report_fail("AR was not switched to ON")

        report_passed("AR was enabled successful")

    @allure.title("Honeypots were found")
    @pytest.mark.flaky(reruns=3, reruns_delay=180)
    def test_honeypots_exists(self):
        """
        Steps:
            Iterate over honeypots directories
            Verify all honeypots does not exist

        Assertion:
            Honeypots were not found
        """
        log_test_headline(f"AR Switch to ON: Honeypots were found")
        sleep(60)
        HoneypotValidation(blade_enabled=True).check_honeypots()

    @allure.title("Blade is enabled by policy")
    @pytest.mark.flaky(reruns=3, reruns_delay=180)
    def test_policy(self):
        """
        Steps:
            Check AR policy in the logs

        Assertion:
            AR is disabled by policy
        """
        log_test_headline(f"AR Switch to ON: AR is enabled by policy")
        _wrong_policy = ArPolicies(ar_enabled=True).wrong_policy()
        report_passed("AR policy corresponds to the policy which should be in AR ON state (enabled)")

    @allure.title("Client health-check post suite execution")
    def test_health_check_post_switch_to_on_state(self):
        """
        Steps:
            Verify that processes, services and drivers are running which should be run and
            verify that proc, svc, and drv are not running if it is applicable for SKU

        Assertion:
            Expected running -> not running; expected down -> running
        """
        log_test_headline(f"AR Switch to ON: Regular client health check post suite execution")
        fail_msg = ""

        _hcheck_fail = Healthcheck().failed
        _pid_fail = PidWatcher().changed()

        if _hcheck_fail:
            fail_msg += _hcheck_fail

        if _pid_fail:
            fail_msg += _pid_fail

        if fail_msg:
            report_fail(fail_msg)

        report_passed("All components which should be run -> run; which should not run -> down")