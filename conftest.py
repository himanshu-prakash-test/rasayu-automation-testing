import os
import re
import sys
import webbrowser
from pathlib import Path

# Add project root, shared-tools, and module roots to sys.path
ROOT_DIR = Path(__file__).resolve().parent
SHARED_TOOLS_DIR = ROOT_DIR / "shared-tools"
BASELINE_MODULE_DIR = ROOT_DIR / "transaction-management" / "update" / "baseline-module"

for p in (str(ROOT_DIR), str(SHARED_TOOLS_DIR), str(BASELINE_MODULE_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

from utils.env_config import config
from auth.login_page import LoginPage
from components.navigation_menu import NavigationMenu
from popup.modal_handler import ModalDialogHandler
from popup.toast_handler import ToastHandler
from popup.confirmation_popup import ConfirmationPopup
from popup.summary_popup import show_summary_popup
from reporter import PytestReporterPlugin
from utils.screenshot_manager import (
    capture_test_screenshot,
    get_page_from_item,
    clear_screenshots_folder,
)

# Global session reporter plugin instance
reporter_plugin = PytestReporterPlugin(suite_title="Rasayu Clinical Portal Automation")


def pytest_addoption(parser):
    """Adds CLI flags for headed/headless mode and summary popup control."""
    try:
        parser.addoption(
            "--headed",
            action="store_true",
            default=False,
            help="Run browser in visible (headed) GUI window mode."
        )
    except ValueError:
        pass
    try:
        parser.addoption(
            "--headless",
            action="store_true",
            default=False,
            help="Run browser in headless background mode."
        )
    except ValueError:
        pass
    try:
        parser.addoption(
            "--popup",
            action="store_true",
            default=False,
            help="Display desktop summary popup."
        )
    except ValueError:
        pass


def pytest_sessionstart(session):
    """
    Session initialization hook: vanishes and cleans the screenshots folder
    before running a new automation test suite (ignored during collect-only).
    """
    if getattr(session.config.option, "collectonly", False):
        return

    screenshots_dir = ROOT_DIR / "screenshots"
    clear_screenshots_folder(screenshots_dir)


@pytest.fixture(scope="session")
def playwright_instance():
    """Initializes Playwright engine."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance, request) -> Browser:
    """
    Launches Chromium browser.
    By default: runs in HEADLESS mode (background, no visible GUI window).
    When --headed is passed: runs in HEADED mode (visible browser window).
    """
    cli_headed = request.config.getoption("--headed")

    # Strict default: headless unless --headed is explicitly passed on the command line
    if cli_headed:
        is_headless = False
    else:
        is_headless = True

    launch_args = [
        "--disable-web-security",
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--start-maximized"
    ]
    b = playwright_instance.chromium.launch(
        headless=is_headless,
        slow_mo=300 if not is_headless else 0,
        args=launch_args,
    )
    yield b
    b.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> BrowserContext:
    """Creates an isolated browser context per test."""
    ctx = browser.new_context(
        base_url=config.base_url,
        viewport=None if not config.is_headless else {"width": config.viewport_width, "height": config.viewport_height},
        no_viewport=True if not config.is_headless else False,
        ignore_https_errors=True,
    )
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Page:
    """Provides a fresh browser page."""
    p = context.new_page()
    p.set_default_timeout(config.browser_timeout)
    yield p
    p.close()


@pytest.fixture(scope="function")
def login_page(page: Page) -> LoginPage:
    """Provides an initialized LoginPage object."""
    return LoginPage(page)


@pytest.fixture(scope="function")
def authenticated_page(page: Page, login_page: LoginPage) -> Page:
    """Logs into the clinical portal and yields an authenticated session page."""
    login_page.open()
    login_page.login(config.admin_username, config.admin_password)
    login_page.verify_login_success()
    return page


@pytest.fixture(scope="function")
def nav_menu(page: Page) -> NavigationMenu:
    return NavigationMenu(page)


@pytest.fixture(scope="function")
def modal_handler(page: Page) -> ModalDialogHandler:
    return ModalDialogHandler(page)


@pytest.fixture(scope="function")
def toast_handler(page: Page) -> ToastHandler:
    return ToastHandler(page)


@pytest.fixture(scope="function")
def confirmation_popup(page: Page) -> ConfirmationPopup:
    return ConfirmationPopup(page)


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Captures test outcome per test case, takes visual validation screenshots
    upon completion of each test case (named by Test Case ID, with a 100-file ceiling),
    and records detailed execution metadata into the HTML reporter plugin.
    """
    outcome = yield
    report = outcome.get_result()

    # Capture when test execution finishes or if setup failed / skipped
    if report.when == "call" or (report.when == "setup" and (report.failed or report.skipped)):
        status = "PASS" if report.passed else "FAIL" if report.failed else "SKIPPED"

        screenshot_path = None
        page_fixture = get_page_from_item(item)
        if page_fixture:
            screenshots_dir = ROOT_DIR / "screenshots"
            screenshot_path = capture_test_screenshot(
                item=item,
                page=page_fixture,
                screenshots_dir=screenshots_dir,
                max_limit=100,
            )

        reporter_plugin.record_test(
            item=item,
            report=report,
            status=status,
            screenshot_path=screenshot_path,
            duration=getattr(report, "duration", 0.0),
        )


def _display_summary_popup(config, was_interrupted: bool = False):
    """
    Displays the styled execution summary popup window upon test completion or early termination.
    Guarded to run only once per session.
    """
    if getattr(config, "_summary_popup_handled", False):
        return
    config._summary_popup_handled = True

    if getattr(config.option, "collectonly", False):
        return

    results = reporter_plugin.reporter.results
    total = len(results)

    # If no tests were run and execution was not terminated, skip popup
    if total == 0 and not was_interrupted:
        return

    # Finalize rich Playwright HTML report
    try:
        report_file = reporter_plugin.finalize_report(filename_prefix="rasayu_clinical_report")
    except Exception:
        report_file = str(Path("reports/latest_report.html").resolve())

    passed = sum(1 for r in results if "PASS" in r.status.upper())
    failed = sum(1 for r in results if "FAIL" in r.status.upper())
    skipped = sum(1 for r in results if "SKIP" in r.status.upper())

    try:
        summary = reporter_plugin.reporter.compile_summary()
        duration_str = summary.formatted_duration
    except Exception:
        duration_str = "0s"

    failed_tests = [r.name for r in results if "FAIL" in r.status.upper()]
    if was_interrupted:
        failed_tests.append("Session Terminated / Interrupted by User")

    # Display styled desktop summary popup (HTML report opens when user clicks '🌐 View HTML Report')
    show_summary_popup(
        total=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        duration_str=duration_str,
        failed_tests=failed_tests,
        suite_title="RASAYU CLINICAL PORTAL AUTOMATION",
        report_path=report_file,
    )


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Triggered upon normal test session summary completion."""
    was_interrupted = exitstatus in (2, 3)  # ExitCode.INTERRUPTED = 2
    _display_summary_popup(config, was_interrupted=was_interrupted)


def pytest_unconfigure(config):
    """
    Guaranteed teardown hook: ensures summary popup displays even if the user
    abruptly terminates the test run early (Ctrl+C, SIGINT, or system kill).
    """
    _display_summary_popup(config, was_interrupted=True)



