import os
import re
import shutil
from pathlib import Path
from typing import Any, Optional
from playwright.sync_api import Page
try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

logger = get_logger("ScreenshotManager")


def clear_screenshots_folder(directory: Path) -> None:
    """
    Vanishes/clears all existing screenshots from the directory before a new test run starts.
    Recreates a fresh, clean directory.
    """
    try:
        if directory.exists():
            shutil.rmtree(directory, ignore_errors=True)
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Screenshots folder vanished and reset for new test run: {directory}")
    except Exception as exc:
        logger.warning(f"Could not reset screenshots folder: {exc}")


def extract_test_case_id(item: Any) -> str:
    """
    Extracts the official Test Case ID from test markers, parametrization, or function name.
    e.g. 'test_tc_base_pos_01_admin_login' -> 'TC-BASE-POS-01'
    """
    # 1. Custom marker: @pytest.mark.tc_id("TC-...")
    marker = item.get_closest_marker("tc_id")
    if marker and marker.args:
        return str(marker.args[0]).strip()

    # 2. Parameterized test data dictionary
    if hasattr(item, "callspec"):
        for param_val in item.callspec.params.values():
            if isinstance(param_val, dict) and "Test Case ID" in param_val:
                return str(param_val["Test Case ID"]).strip()

    # 3. Regex matching TC-... up to the trailing numeric index
    match = re.search(r"(TC(?:[-_][A-Za-z0-9]+)*?[-_]\d+)", item.name, re.IGNORECASE)
    if match:
        return match.group(1).upper().replace("_", "-")

    # 4. Fallback: clean function name
    return re.sub(r"[^\w\-_\.]", "_", item.name)


def enforce_screenshot_limit(directory: Path, max_limit: int = 100) -> None:
    """
    Enforces a strict maximum file limit on the screenshot directory.
    When the limit is reached or exceeded, automatically deletes the oldest
    screenshots (FIFO sorted by file modification timestamp).
    """
    if not directory.exists():
        directory.mkdir(parents=True, exist_ok=True)
        return

    image_extensions = {".png", ".jpg", ".jpeg", ".webp"}
    files = [
        f for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if len(files) >= max_limit:
        # Sort oldest first (FIFO)
        files.sort(key=lambda x: x.stat().st_mtime)
        delete_count = len(files) - max_limit + 1
        for i in range(delete_count):
            try:
                logger.info(
                    f"Screenshot folder limit reached ({max_limit}). "
                    f"Deleting older screenshot: {files[i].name}"
                )
                files[i].unlink(missing_ok=True)
            except Exception as e:
                logger.warning(f"Could not delete old screenshot {files[i].name}: {e}")


def get_page_from_item(item: Any) -> Optional[Page]:
    """
    Dynamically discovers the active Playwright Page instance across test fixtures,
    Page Objects, or custom session contexts.
    """
    if not hasattr(item, "funcargs"):
        return None

    # 1. Direct page fixture
    page = item.funcargs.get("page")
    if page and hasattr(page, "screenshot"):
        return page

    # 2. Authenticated page fixture
    auth_page = item.funcargs.get("authenticated_page")
    if auth_page and hasattr(auth_page, "screenshot"):
        return auth_page

    # 3. Inspect Page Objects (e.g. baseline_page, login_page, or custom Page Objects)
    for val in item.funcargs.values():
        if hasattr(val, "page") and hasattr(val.page, "screenshot"):
            return val.page
        if hasattr(val, "screenshot") and callable(getattr(val, "screenshot")):
            return val

    return None


def capture_test_screenshot(
    item: Any,
    page: Page,
    screenshots_dir: Path,
    max_limit: int = 100,
) -> Optional[str]:
    """
    Captures a full-page screenshot upon test case completion for validation evidence.
    Names the screenshot file as per the official Test Case ID (e.g. 'TC-BASE-POS-01.png').
    Enforces a 100-file ceiling by automatically deleting older screenshots.
    Returns the absolute string path of the saved screenshot.
    """
    try:
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        enforce_screenshot_limit(screenshots_dir, max_limit=max_limit)

        tc_id = extract_test_case_id(item)

        # Handle parameterized variations if present e.g. [param]
        param_match = re.search(r"\[(.*)\]", item.name)
        if param_match:
            safe_param = re.sub(r"[^\w\-_\.]", "_", param_match.group(1))
            filename = f"{tc_id}_{safe_param}.png"
        else:
            filename = f"{tc_id}.png"

        screenshot_path = screenshots_dir / filename

        # Ensure page DOM is ready and any loading shimmers/skeletons have settled
        try:
            page.wait_for_selector(
                ".ant-skeleton, .ant-spin-spinning, .spinner-border, .loading-indicator",
                state="detached",
                timeout=15000,
            )
        except Exception:
            pass
        try:
            page.wait_for_load_state("networkidle", timeout=2000)
        except Exception:
            pass
        page.wait_for_timeout(600)

        # Capture full page screenshot
        page.screenshot(path=str(screenshot_path), full_page=True)
        logger.info(f"Captured test validation screenshot: {screenshot_path.name}")
        return str(screenshot_path.resolve())
    except Exception as exc:
        logger.warning(f"Could not capture screenshot for '{item.name}': {exc}")
        return None
