import os
import re
import sys
import time
import webbrowser
from pathlib import Path
from typing import Optional

# Add project root, shared_tools, and module roots to sys.path
ROOT_DIR = Path(__file__).resolve().parent
SHARED_TOOLS_DIR = ROOT_DIR / "shared_tools"
TEST_DATA_DIR = ROOT_DIR / "test_data"
MASTER_MGMT_DIR = ROOT_DIR / "master_management"
TRANS_MGMT_DIR = ROOT_DIR / "transaction_management"

for p in (
    str(ROOT_DIR),
    str(SHARED_TOOLS_DIR),
    str(TEST_DATA_DIR),
    str(MASTER_MGMT_DIR),
    str(TRANS_MGMT_DIR),
):
    if p not in sys.path:
        sys.path.insert(0, p)

import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

try:
    from shared_tools.utils.env_config import config
    from shared_tools.auth.login_page import LoginPage
    from shared_tools.components.navigation_menu import NavigationMenu
    from shared_tools.popup.modal_handler import ModalDialogHandler
    from shared_tools.popup.toast_handler import ToastHandler
    from shared_tools.popup.confirmation_popup import ConfirmationPopup
    from shared_tools.popup.summary_popup import show_summary_popup
    from shared_tools.reporter import PytestReporterPlugin
    from shared_tools.utils.screenshot_manager import (
        capture_test_screenshot,
        get_page_from_item,
        clear_screenshots_folder,
    )
except ImportError:
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


AUTH_DIR = ROOT_DIR / ".auth"
SESSION_AUTH_FILE = AUTH_DIR / "session_storage_state.json"


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

    # Allow configuring SLOW_MO via environment variable (default: 0 in headless, 50ms in headed instead of 300ms)
    env_slow_mo = os.getenv("SLOW_MO")
    if env_slow_mo is not None and env_slow_mo.isdigit():
        slow_mo_val = int(env_slow_mo)
    else:
        slow_mo_val = 50 if cli_headed else 0

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
        slow_mo=slow_mo_val,
        args=launch_args,
    )
    yield b
    b.close()


@pytest.fixture(scope="session")
def session_storage_state(browser: Browser) -> Optional[str]:
    """
    Session-level authentication: logs in once at session start and saves
    cookies/localStorage tokens to session_storage_state.json so individual test
    contexts can reuse the authenticated session instantly.
    100% production-safe: works across local, staging, and production domains.
    """
    disable_cache = os.environ.get("DISABLE_AUTH_CACHE", "").lower() in ("1", "true", "yes")
    if disable_cache:
        return None

    AUTH_DIR.mkdir(parents=True, exist_ok=True)

    # If an existing storage state is fresh (< 2 hours old), reuse it directly
    if SESSION_AUTH_FILE.exists():
        try:
            file_age_seconds = time.time() - SESSION_AUTH_FILE.stat().st_mtime
            if file_age_seconds < 7200:
                return str(SESSION_AUTH_FILE)
        except Exception:
            pass

    try:
        ctx = browser.new_context(
            base_url=config.base_url,
            ignore_https_errors=True,
        )
        p = ctx.new_page()
        lp = LoginPage(p)
        lp.open()
        lp.login(config.admin_username, config.admin_password)
        lp.verify_login_success()
        lp.redirect_to_main_website()

        # Save session storage state
        ctx.storage_state(path=str(SESSION_AUTH_FILE))
        ctx.close()
        return str(SESSION_AUTH_FILE)
    except Exception as e:
        print(f"\n[Auth Cache] Session pre-auth notice: {e}. Will authenticate on demand.")
        return None


@pytest.fixture(scope="function")
def context(browser: Browser, session_storage_state: Optional[str]) -> BrowserContext:
    """Creates an isolated browser context per test, pre-hydrated with session auth tokens if available."""
    storage = session_storage_state if (session_storage_state and os.path.exists(session_storage_state)) else None
    ctx = browser.new_context(
        storage_state=storage,
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
def authenticated_page(page: Page, login_page: LoginPage, context: BrowserContext, session_storage_state: Optional[str]) -> Page:
    """
    Yields an authenticated session page.
    Fast Path: if session storage state was loaded, checks if user is already authenticated on main web app.
    Fallback Path: if session missing or expired on production, performs full login and refreshes storage state.
    """
    if session_storage_state and os.path.exists(session_storage_state):
        target_url = f"{config.main_app_url.rstrip('/')}/patients"
        try:
            page.goto(target_url, wait_until="domcontentloaded", timeout=15000)
            current_url = page.url.lower()
            if "/login" not in current_url and "/admin/login" not in current_url:
                # Successfully authenticated in < 1 second!
                return page
        except Exception:
            pass

    # Fallback: full authentication flow (resilient against expired tokens on production)
    login_page.open()
    login_page.login(config.admin_username, config.admin_password)
    login_page.verify_login_success()
    login_page.redirect_to_main_website()

    # Refresh cached storage state for subsequent tests
    try:
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        context.storage_state(path=str(SESSION_AUTH_FILE))
    except Exception:
        pass

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


def pytest_keyboard_interrupt(excinfo):
    """Mark session as interrupted when user stops execution via Ctrl+C."""
    os.environ["_PYTEST_INTERRUPTED"] = "1"


def _display_summary_popup(config, terminalreporter=None, was_interrupted: bool = False):
    """
    Displays the styled execution summary popup window upon test completion or early termination.
    Guarded to run only once per session.
    """
    if getattr(config, "_summary_popup_handled", False):
        return
    config._summary_popup_handled = True

    if getattr(config.option, "collectonly", False):
        return

    # In remote headless CI/CD runners (e.g. GitHub Actions, headless Linux), skip GUI popup to prevent runner hang.
    # On local Windows/macOS developer workstations, show the desktop summary popup.
    force_popup = os.environ.get("FORCE_POPUP", "").strip().lower() in ("1", "true", "yes")
    is_github_actions = os.environ.get("GITHUB_ACTIONS", "").strip().lower() in ("true", "1")
    is_headless_linux = sys.platform.startswith("linux") and not os.environ.get("DISPLAY")

    if (is_github_actions or is_headless_linux) and not force_popup:
        print(f"\n[CI/CD] Remote headless environment detected. Summary popup bypassed.")
        return

    # Check if interrupted via keyboard (Ctrl+C)
    if os.environ.pop("_PYTEST_INTERRUPTED", None) == "1":
        was_interrupted = True

    results = list(getattr(reporter_plugin.reporter, "results", []))
    passed = sum(1 for r in results if "PASS" in r.status.upper())
    failed = sum(1 for r in results if "FAIL" in r.status.upper())
    skipped = sum(1 for r in results if "SKIP" in r.status.upper())

    # Fallback to terminalreporter stats if custom reporter was interrupted before recording
    term = terminalreporter or getattr(config, "_terminalreporter", None)
    if term and hasattr(term, "stats"):
        term_passed = len([r for r in term.stats.get("passed", []) if getattr(r, "when", "") == "call"])
        term_failed = len([r for r in term.stats.get("failed", []) + term.stats.get("error", []) if getattr(r, "when", "") in ("call", "setup")])
        term_skipped = len([r for r in term.stats.get("skipped", []) if getattr(r, "when", "") in ("call", "setup")])
        if (term_passed + term_failed + term_skipped) > len(results):
            passed = max(passed, term_passed)
            failed = max(failed, term_failed)
            skipped = max(skipped, term_skipped)

    total = len(results)
    if total < (passed + failed + skipped):
        total = passed + failed + skipped

    failed_tests = [r.name for r in results if "FAIL" in r.status.upper()]
    if was_interrupted:
        failed_tests.append("Execution Stopped / Interrupted by User")

    # If 0 tests completed but user stopped execution, report total as 1 (interrupted test)
    if total == 0 and was_interrupted:
        total = 1

    try:
        summary = reporter_plugin.reporter.compile_summary()
        duration_str = summary.formatted_duration
    except Exception:
        duration_str = "0s"

    # Finalize rich Playwright HTML report
    try:
        report_file = reporter_plugin.finalize_report(filename_prefix="rasayu_clinical_report")
    except Exception:
        report_file = str(Path("reports/latest_report.html").resolve())

    # Display styled desktop summary popup (HTML report opens when user clicks '🌐 View HTML Report')
    try:
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
    except BaseException as exc:
        print(f"\n[POPUP] Execution popup finished or closed ({exc}).")


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Triggered upon normal or early test session summary completion."""
    config._terminalreporter = terminalreporter
    was_interrupted = exitstatus in (1, 2, 3) or getattr(terminalreporter, "interrupted", False) or os.environ.get("_PYTEST_INTERRUPTED") == "1"
    _display_summary_popup(config, terminalreporter=terminalreporter, was_interrupted=was_interrupted)


def pytest_unconfigure(config):
    """
    Guaranteed teardown hook: ensures summary popup displays even if the user
    abruptly terminates the test run early (Ctrl+C, SIGINT, or system kill).
    """
    was_interrupted = os.environ.get("_PYTEST_INTERRUPTED") == "1" or getattr(config, "_interrupted_by_user", False)
    _display_summary_popup(config, was_interrupted=was_interrupted)



