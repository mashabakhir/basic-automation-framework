import logging
import os.path

import pytest
import allure

from time import sleep
from allure import severity_level

from os.path import expandvars as ev
from _utils.proc import processes_pid, processes_up
from gui_manager.observers.detections_pannels.ransom_detection import ArDetectionWindow
from gui_manager.observers.remediation.exclusions import Exclusions
from zang_manager import ARManager
from core.common.screen_rec import RecordScreen
from core import (
    log_test_headline,
    log_svc_line,
    report_fail,
    report_passed,
    Proctest,
    ResetAREngine,
    PidWatcher,
    Healthcheck,
    HOST
)

# --------------------------------------------------- VARS -------------------------------------------------------------
flags = {"detection": False, "incident_id": "", "restored": False, "restored_id": "", "excluded": False}


# -------------------------------------------------- FIXTURES ----------------------------------------------------------

@pytest.fixture(scope='class')
def screen_rec():
    rec = RecordScreen("AR_False_Positive_Incident")
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
@allure.suite('Anti-Ransomware Blade - False Positive & Exclusions')
@allure.sub_suite(f'{HOST}')
@allure.label("package", f'{HOST}.tests_ar.tests_false_positive')
@allure.severity(severity_level.BLOCKER)
@pytest.mark.usefixtures('screen_rec', 'setup', 'pid_monitor')
class TestsArReportFalsePositive:

    @allure.title("Perform incident detection for false positive")
    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4754" 
                  "ZANG | B040020140 | Windows 7 x86 x64 ONLY | Ransomware incident was not detected")
    @pytest.mark.flaky(reruns=1, reruns_delay=300)
    def test_prepare_detection(self):
        """
        Steps:
            Trigger AR incident
            Wait for Ransomware Detection Window (which shows incident details)

        Assertion:
            Ransomware detection window was not shown
            Exit by timeout to wait for Ransomware detection window
        """
        log_test_headline(f"AR False Positive: Prepare AR incident detection (proctest)")
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
            report_fail("Ransomware Detection window was not shown - incident was not detected.")

        flags["detection"] = True
        report_passed("Ransomware incident was successfully detected.")

    @allure.title("Ransomware process was terminated.")
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
        log_test_headline(f"AR False Positive: Ransomware process is terminated")
        pytest.skip("Conditional Skip: Ransomware incident was not detected") if not flags["detection"] else True
        logging.debug("Sleep for 60 sec.")
        sleep(60)
        status = Proctest()
        status.view_processes()
        running = status.running
        exists = status.exists
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
        report = str()
        if running:
            report += "Ransomware process was found among running processes. "
        if exists:
            report += "Ransomware process was not deleted from disk. "
        if report:
            report_fail(report)
        report_passed("Ransom process is not running and binary does not exist.")

    @allure.title("Incident details - trigger process name is correct")
    def test_trigger_process_name(self):
        """
        Steps:
            Get trigger process name of the incident

        Assertion:
            Could not receive a trigger process name
        """
        log_test_headline(f"AR False Positive: Trigger Process was shown")
        pytest.skip("Conditional Skip: There is no ID for the incident") if not flags["detection"] else True
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

    @allure.title("Encrypted by ransomware files were removed from disk")
    @pytest.mark.skip(reason="Encrypted files will not be removed after AR incident detection. ")
    def test_encrypted_files_removed(self):
        """
        Steps:
            Verify that all files which were encrypted by ransomware were removed from disk

        Assertion:
            No encrypted by ransom files were found
        """
        log_test_headline(f"AR False Positive: Encrypted files removed from disk.")
        pytest.skip("Conditional Skip: Incident ID was not received through API") if not flags["detection"] else True
        not_removed = Proctest().encrypted_removed()
        if not_removed:
            report_fail(f"Files were not removed from disk after incident detection: {len(not_removed)}")

    @allure.title("Affected files window - verify all encrypted files were shown")
    def test_view_encrypted_files(self):
        """
        Steps:
            On Ransomware Blocked window click '+ $NUM more'
            Go over the window and check all encrypted files were shown

        Assertion:
            Affected files window is empty or contains only honeypot files
        """
        log_test_headline("AR False Positive:: Review Affected Files Window")
        pytest.skip("Conditional Skip: There is no detection to perform this case") if not flags["detection"] else True
        affected_files = ArDetectionWindow().view_encrypted_files()
        file_paths = list()

        if affected_files == 0:
            report_fail("UI shows 'No affected files' ")

        for file in affected_files:
            logging.info(f"File found in Affected Files window: {file['full_path']}")
            file_paths.append(file["full_path"])

        incorrect_data = Proctest().affected_files(file_paths)

        if incorrect_data:
            report_fail(f"Actual: Affected files window contains: {incorrect_data[0]}; Expected: {incorrect_data[1]}")

        report_passed("Affected files window contains the same num of files as was encrypted.")

    @allure.title("Report false positive (Not a Ransomware) for the incident")
    def test_report_false_positive(self):
        """
        Steps:
            Click on [This is not a ransomware] button
            Wait until restoration process will be completed:
                Spinner will be running for a while
                Then restored files window will appear
        Note:
            GUI API handling while Restored Files window appears and returns
            List of restored files with statuses as a result of reporting false positive.
        Assertion:
            Restoration exit by timeout.
        """

        log_test_headline(f"AR False Positive: Report False Positive (click 'This is not a ransomware') "
                          f"and validate restored files statuses")
        pytest.skip("Conditional Skip: Incident ID was not received through API") if not flags["detection"] else True

        restored_files = ArDetectionWindow().report_false_positive()
        if not restored_files:
            report_fail("Cannot get restored files window: received emtpy window or cannot access to the "
                        "Restore Files Window.")

        report = str()
        logging.info(f"Num of restored files: {len(restored_files)}")
        status_restored_wrong = list()
        for each_file in restored_files:
            if each_file['status'] != "Restored":
                logging.warning(f"Status is not 'Restored' for a file: {each_file['full_path']}")
                status_restored_wrong.append(f"{each_file['status']} - {each_file['full_path']}")

        if status_restored_wrong:
            report += f"STATUS IS NOT CORRECT FOR FILES: {status_restored_wrong}"
        logging.info("Checking if ransomware binary was found in the list...")
        ransom_found = False
        for each_file in restored_files:
            if each_file['full_path'].lower() == Proctest().ransom_bin.lower():
                logging.info("Ransomware binary was found in restored files window.")
                ransom_found = True
                break

        if not ransom_found:
            report += "Ransomware binary was not found in Restored files window! "

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

        flags["restored"] = True
        report_passed("Report not a ransomware was success")

    @allure.title("Restored Files Window - Ransomware binary and encrypted files are exist on disk")
    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4752",
                  "ZANG | B040020140 | Engine initialization during ransomware incident")
    def test_files_restored_on_disk(self):
        """
        Steps:
            Check directory
            Verify:
                encrypted files are still in the directory
                ransomware binary exists

        Assertion:
            At least one file was not found
            Ransomware binary was not found on disk
        """
        log_test_headline("AR False Positive:: Files & Ransomware binary restored on disk ")
        pytest.skip("Conditional Skip: Incident ID was not received through API") if not flags["restored"] else True
        report = str()
        proctest = Proctest()
        files_not_restored = proctest.encrypted_not_restored()
        ransom_found = proctest.exists
        if files_not_restored:
            for _ in files_not_restored:
                logging.warning("File not restored: {_}")
            report += f"{len(files_not_restored)} were not restored on disk. "
        if not ransom_found:
            report += "Ransomware binary was not found on disk after restoration compelte. "
        if report:
            report_fail(report)

    @allure.title("Ransomware process found among excepted files")
    def test_ransom_process_excluded(self):
        """
        Steps:
            Verify ransom process is in exclusions
        Assertion:
            Ransomware binary was not found in Exceptions
        """
        log_test_headline(f"AR False Positive: Ransomware process was found in exceptions. ")
        pytest.skip("Conditional Skip: Restoration was not success") if not flags["restored"] else True
        excluded = Exclusions().item_excluded(Proctest().trigger)
        if not excluded:
            report_fail("Cannot find ransomware binary among excluded files!")
        flags["excluded"] = True
        report_passed("Ransomware binary was found among excluded files.")

    @allure.issue("https://jira-prd.checkpoint.com/browse/ZA-4643",
                  "AUTO | ZANG | B040020113 | Post-Upgrade from 4.0.148 | 2 Ransomware detections for 1 incident and "
                  "as a result - no option to recover affected files")
    @allure.title("No detection for excluded ransomware process")
    def test_no_detection_for_excluded_process(self):
        """
        Steps:
            Trigger AR incident

        Assertion:
            There is an AR incident for the process which is already in exclusions after reporting false positive.
        """
        log_test_headline("AR False Positive: No detection for the ransom after False Positive reported")
        pytest.skip("Conditional Skip: Restoration process was not success.") if not flags["restored"] else True
        ransom = Proctest()
        ransom.run()
        event = ArDetectionWindow().detection_window()
        if event or event is not None:
            report_fail("Ransomware Detection window was shown - incident was detected for excluded ransomware process.")
        report_passed("No detection while ransom process in exclusions after reporting false positive")

    @allure.title("Remove ransomware process binary from exclusion list")
    def test_remove_excluded_process(self):
        """
        Steps:
            Remove ransom binary from exclusion list

        Assertion:
            Process was not removed from exclusion center
        """
        log_test_headline(f"AR False Positive: Remove ransomware process from exceptions")
        pytest.skip("Conditional Skip: Restore ID was not received through API") if not flags["excluded"] else True

        removed = Exclusions().remove_exception(Proctest().trigger.split('.')[0])
        if not removed:
            logging.warning("Cannot remove ransomware trigger process from exceptions.")
            report_fail("Cannot remove ransomware process trigger from exceptions.")

    @allure.title("Incident Card was added into Events Timeline")
    @pytest.mark.skip(reason="The test case is in backlog")
    def test_incident_card_found_in_events_timeline(self):
        pass

    @allure.title("Client health-check post suite execution")
    def test_health_check_post_detection_and_report_false_positive(self):
        """
        Steps:
            Verify that processes, services and drivers are running which should be run and
            verify that proc, svc, and drv are not running if it is applicable for SKU

        Assertion:
            Expected running -> not running; expected down -> running
        """
        log_test_headline(f"TestsArReportFalsePositive::test_health_check_post_detection_and_report_false_positive")
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
