import logging
import os

import pytest
import allure

from time import sleep
from allure import severity_level

from os.path import expandvars as ev
from _utils.proc import processes_pid, processes_up
from zang_manager import ARManager
from core.common.screen_rec import RecordScreen
from gui_manager.observers.detections_pannels.ransom_detection import ArDetectionWindow
from gui_manager.observers.remediation.quarantine import Quarantine
from core import (
    log_test_headline,
    log_svc_line,
    report_fail,
    report_passed,
    Proctest,
    ResetAREngine,
    EFRStatus,
    Healthcheck,
    PidWatcher,
    HOST
)

# --------------------------------------------------- VARS -------------------------------------------------------------
flags = {"detection": False, "incident_id": "", "recover": False, "recover_id": ""}


# -------------------------------------------------- FIXTURES ----------------------------------------------------------


@pytest.fixture(scope='class')
def screen_rec():
    rec = RecordScreen("AR_Incident_Detection_Suite")
    rec.start()
    yield rec
    rec.stop()


@pytest.fixture(scope='class')
def setup():
    log_svc_line("SETUP: Reset AR & add automation into exclusions")
    ResetAREngine().reset_ar()
    ar = ARManager()
    ar.init()
    ar.add_automation_exclusions()
    ar.stop()
    yield
    log_svc_line("TEARDOWN: Clear exclusions and reset AR engine")
    ar = ARManager()
    ar.init()
    ar.clear_exclusion_list()
    ar.stop()


@pytest.fixture(scope="class")
def pid_monitor():
    log_svc_line("SETUP: CAPTURE PROCESSES PID`s")
    PidWatcher().setup()
    yield


# --------------------------------------------------- TESTS ------------------------------------------------------------

@allure.epic("Anti-Ransomware Blade")
@allure.suite('Anti-Ransomware Blade - Incident Detection')
@allure.sub_suite(f'{HOST}')
@allure.label("package", f'{HOST}.tests_ar.tests_inc_detection')
@allure.severity(severity_level.BLOCKER)
@pytest.mark.usefixtures('screen_rec', 'setup', 'pid_monitor')
class TestsArIncidentDetection:
    """
    Desc:
        Tests to check AR detection and recovering flow (standard use case)
    """

    @allure.title("Forensics is ready for detection")
    def test_forensics_ready(self):
        """
        Desc:
            Sometimes EFR service restarts a few times after clean installation. EFR requires some time to be
            completely loaded: load policies, configuration etc.
            If EFR just was started - in most of the cases AR incident will not be detected.

        Steps:
            Request the latest timestamp when EFR Service was started
            Compare with current time

        Assertion:
            EFR Service was started less than 5 min ago

        Teardown:
            Wait for time difference: continue the testing while timeout after EFR startup will be not less than 5 min
        """
        log_test_headline("AR Incident Detection: EFR is ready.")
        _timeout = 300
        logging.info(f"Checking if EFRService was restarted less than {_timeout / 60} min ago")
        _efr_ready = EFRStatus.efr_service_ready(required_timeout=300)

        if not _efr_ready:
            EFRStatus.wait_for_efr_up(required_timeout=300)
            report_fail("EFR was not ready for AR detection - by some reason service was restarted less than "
                        f"{_timeout / 60} min ago")

        report_passed(f"EFRService was started more than {_timeout / 60} min. ago.")

    @allure.title("Ransom incident was detected")
    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4754"
                  "ZANG | B040020140 | Windows 7 x86 x64 ONLY | Ransomware incident was not detected")
    @pytest.mark.flaky(reruns=1, reruns_delay=300)
    def test_ransom_detected(self):
        """
        Data:
            Trigger: proctest ransom simulator

        Steps:
            Trigger AR incident
            Wait for detection

        Assertion:
            Ransom incident was not detected
        """
        log_test_headline("AR Incident Detection: Ransomware incident is detected")
        ransom = Proctest()
        ransom.run()
        sleep(2)
        logging.debug("[PROCTEST_AUTO] Try to catch RANSOMWARE PID")
        try:
            process_pid = processes_pid("a1.exe")
            logging.debug(f"A1.exe process PID after triggering the incident: {process_pid}")
        except Exception as err:
            logging.debug(f"Unable to extract a1.exe PID: {err}")
            pass

        event = ArDetectionWindow().detection_window()
        if event is None or not event:
            report_fail("Ransomware incident was not detected. No detection window found.")

        flags["detection"] = True
        report_passed("Ransomware incident was detected.")

    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4627",
                  "ZANG | B040020105 | The ransomware process has not been terminated immediately after the incident")
    @allure.title("Ransomware process terminated by SBA")
    @pytest.mark.flaky(reruns=1, reruns_delay=300)
    def test_ransom_process_killed(self):
        """
        Steps:
            Request ransomware status from Proctest object

        Assertion:
            Ransomware process is running and / or ransomware binary exists on disk
        """
        log_test_headline("AR Incident Detection: Ransomware process is terminated")
        pytest.skip("Conditional Skip: Ransomware incident was not detected") if not flags["detection"] else True
        logging.debug("Sleep for 60 sec.")
        sleep(60)
        status = Proctest()
        report = str()
        status.view_processes()
        # TODO: DEBUG PART -> START
        logging.debug("[PROCTEST_AUTO] Separate method called")
        logging.debug("[PROCTEST_AUTO] Checking ransomware processes outside PROCTEST class")
        ransom_exists = os.path.exists(ev("%USERPROFILE%\\Downloads\\proctest\\a1.exe"))
        logging.debug(f"[PROCTEST_AUTO] Ransomware binary exists: {ransom_exists}")
        ransom_running = processes_up(["a1.exe"])
        logging.debug(f"[PROCTEST_AUTO] Process A1.exe is running: {ransom_running}")
        if ransom_running:
            ransom_pid = processes_pid("a1.exe")
            logging.debug(f"[PROCTEST_AUTO] Process A1.exe - PID: {ransom_pid}")
        logging.debug("[PROCTEST_AUTO] Complete validation under debug")
        # TODO: DEBUG PART -> END
        if status.running:
            logging.warning("Ransomware process was not terminated")
            report += "Ransomware process was found among running processes. "
        if status.exists:
            logging.warning("Ransomware binary was found on disk. ")
            report += "Ransomware process was found on disk! "

        if report:
            report_fail(report)

        report_passed("Ransom process is not running and binary does not exist.")

    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4643",
                  "AUTO | ZANG | B040020113 | Post-Upgrade from 4.0.148 | 2 Ransomware detections for 1 incident and "
                  "as a result - no option to recover affected files")
    @allure.title("Incident details - trigger process name was defined by client correctly")
    def test_incident_details_correct(self):
        """
        Steps:
            Request to detection window in UI
            Collect all the incident details

        Assertion:
            Trigger process name is incorrect
        """
        log_test_headline("AR Incident Detection: Incident Details -> trigger process")
        pytest.skip("Conditional Skip: There is no detection to perform this case") if not flags["detection"] else True

        details = ArDetectionWindow().incident_details()

        if details is None:
            report_fail("Ransomware blocked window does not contain any data. Manual verification required.")

        logging.info(f"Trigger Process: {details['trigger_process']}")
        logging.info(f"Timestamp of the incident: {details['timestamp']}")
        logging.info(f"Count of affected files: {details['file_count']}")

        if Proctest().trigger.lower() != details['trigger_process'].lower():
            report_fail(f"The trigger process is not correct. "
                        f"Expected: {Proctest().trigger}; UI shows: {details['trigger_process']}")

        report_passed("All info about the incident was found.")

    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4643",
                  "AUTO | ZANG | B040020113 | Post-Upgrade from 4.0.148 | 2 Ransomware detections for 1 incident and "
                  "as a result - no option to recover affected files")
    @allure.title("Affected files window - verify all encrypted files were shown")
    def test_view_encrypted_files(self):
        """
        Steps:
            On Ransomware Blocked window click '+ $NUM more'
            Go over the window and check all encrypted files were shown

        Assertion:
            Affected files window is empty or contains only honeypot files
        """
        log_test_headline("AR Incident Detection: Review Affected Files Window")
        pytest.skip("Conditional Skip: There is no detection to perform this case") if not flags["detection"] else True
        affected_files = ArDetectionWindow().view_encrypted_files()
        file_paths = list()

        if affected_files == 0:
            report_fail("UI shows 'No affected files' ")

        if affected_files is None:
            report_fail("Ransomware Detection window shows 'No Affected Files'")

        for file in affected_files:
            logging.info(f"File found in Affected Files window: {file['full_path']}")
            file_paths.append(file["full_path"])

        incorrect_data = Proctest().affected_files(file_paths)

        if incorrect_data:
            report_fail(f"Actual: Affected files window contains: {incorrect_data[0]}; Expected: {incorrect_data[1]}")

        report_passed("Affected files window contains the same num of files as was encrypted.")

    @allure.title("Recover affected files")
    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4752",
                  "ZANG | B040020140 | Engine initialization during ransomware incident")
    def test_recover_files(self):
        """
        Steps:
            Go to UI Main
            On Ransomware Blocked window - click [RECOVER AFFECTED FILES]
            Wait until recovered files window will be appeared
            Check Recovered Files Window:
                File Status and File Path

        Assertion:
            Recovered files window was not opened during 5 min.
            At least one of the file has status "FAILED" in Recovered Files List
        """
        log_test_headline("AR Incident Detection: Recover Affected Files and Check Recovered File Status")
        pytest.skip("Conditional Skip: There is no incident detection") if not flags["detection"] else True

        recovered_data = ArDetectionWindow().recover_affected_files()
        if not recovered_data:
            report_fail(f"No Recovered Files data in Recovered files window found. Looks like Recovered files window "
                        f"is empty.")

        recovering_failed = list()
        logging.info("Go over recovered files window")
        for recovered_file in recovered_data:
            logging.info(f"{recovered_file['status']} - {recovered_file['full_path']}")
            if not "Recovered" in recovered_file["status"]:  # or recovered_file["status"] != "Восстановлено"
                recovering_failed.append(f"Failed status: {recovered_file['full_path']}")

        incorrect_data = Proctest().recovered_files(recovered_data)
        report = ""

        if recovering_failed:
            report += f"STATUS FAILED IN UI: {recovering_failed}. "

        # actual recovered on disk
        recover_failed = Proctest().recovered_on_disk()
        if recover_failed:
            report += f"NOT RECOVERED ON DISK: {recover_failed}. "

        if incorrect_data:
            report += f" NUM OF FILES: Recovered files window shows num of files: " \
                      f"{incorrect_data[0]}; Expected: {incorrect_data[1]}"

        if report:
            report_fail(report)

        # TODO: DEBUG PART -> START
        logging.debug("[PROCTEST_AUTO] Separate method called")
        logging.debug("[PROCTEST_AUTO] Checking ransomware processes outside PROCTEST class")
        ransom_exists = os.path.exists(ev("%USERPROFILE%\\Downloads\\proctest\\a1.exe"))
        logging.debug(f"[PROCTEST_AUTO] Ransomware binary exists: {ransom_exists}")
        ransom_running = processes_up(["a1.exe"])
        logging.debug(f"[PROCTEST_AUTO] Process A1.exe is running: {ransom_running}")
        if ransom_running:
            ransom_pid = processes_pid("a1.exe")
            logging.debug(f"[PROCTEST_AUTO] Process A1.exe - PID: {ransom_pid}")
        logging.debug("[PROCTEST_AUTO] Complete validation under debug")
        # TODO: DEBUG PART -> END

        flags["recover"] = True
        report_passed("Affected files were recovered successful.")

    @allure.title("Quarantined File List - Ransomware binary quarantined")
    def test_quarantined_files_list(self):
        """
        Steps
            Get all the quarantined files related to the incident
            Check status of quarantined files

        Assertion:
            At least one of the files is not in quarantine
        """
        log_test_headline("AR Incident Detection: Ransomware binary quarantined")
        pytest.skip("Conditional Skip: Recover was not success") if not flags["recover"] else True

        ransom_quarantined = Quarantine().file_quarantined(file_to_find=Proctest().ransom_proc)
        if not ransom_quarantined:
            report_fail("Cannot find ransomware binary among quarantined files.")

    @pytest.mark.skip(reason="Covered by another test case.")
    @allure.title("Files recovered on disk successful")
    def test_files_recovered_on_disk(self):
        """
        Steps:
            Read saved to json file all files from the incident
            Verify files were recovered on disk

        Assertion:
            At least on of the files was not found on disk (was not recovered)
        """
        log_test_headline("AR Incident Detection: Files actually recovered on disk")
        pytest.skip("Conditional Skip: Recover was not success") if not flags["recover"] else True

        recover_failed = Proctest().recovered_on_disk()

        if recover_failed:
            report_fail(f"Actual: Not found recovered on disk files: {recover_failed}. Expected: Have all recovered")

        report_passed("All files were recovered on disk.")

    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4560",
                  "AUTO_SMOKE | ZANG | B040020083 | Not all the encrypted files were removed from disk after AR incident")
    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4643",
                  "AUTO | ZANG | B040020113 | Post-Upgrade from 4.0.148 | 2 Ransomware detections for 1 incident and "
                  "as a result - no option to recover affected files")
    @allure.title("Encrypted files by ransomware removed from disk")
    def test_encrypted_files_removed(self):
        """
        Steps:
            Verify that all files which were encrypted by ransomware were removed from disk

        Assertion:
            No encrypted by ransom files were found
        """
        log_test_headline("AR Incident Detection: Encrypted files were removed")
        pytest.skip("Conditional Skip: Recover was not success") if not flags["recover"] else True

        not_removed = Proctest().encrypted_removed()

        if not_removed:
            report_fail(f"Files were not removed from disk after incident detection: {len(not_removed)}")

        report_passed("All encrypted files where removed.")

    @allure.title("Client health-check post suite execution")
    def test_health_check_post_detection(self):
        """
        Steps:
            Verify that processes, services and drivers are running which should be run and
            verify that proc, svc, and drv are not running if it is applicable for SKU

        Assertion:
            Expected running -> not running; expected down -> running
        """
        log_test_headline("AR Incident Detection: Regular client health post suite execution")
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