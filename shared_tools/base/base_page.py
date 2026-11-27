from typing import Optional, Union
from playwright.sync_api import Page, Locator, expect
try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger


class BasePage:
    """Base class for all Page Objects providing resilient actions and explicit waiting."""

    def __init__(self, page: Page, context_name: str = "BasePage"):
        self.page = page
        self.logger = get_logger(context_name)

    def navigate_to(self, url: str) -> None:
        """Navigates to an absolute or relative URL."""
        self.logger.info(f"Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded")

    def safe_click(self, locator: Union[Locator, str], description: Optional[str] = None) -> None:
        """Scrolls into view, waits for visibility, and clicks the element."""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        desc = description or (locator if isinstance(locator, str) else "element")
        self.logger.info(f"Clicking: {desc}")

        first_el = target.first
        first_el.scroll_into_view_if_needed()
        expect(first_el).to_be_visible(timeout=10000)
        first_el.click()

    def safe_fill(self, locator: Union[Locator, str], value: str, description: Optional[str] = None) -> None:
        """Clears and fills text into an input element."""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        desc = description or (locator if isinstance(locator, str) else "input")
        preview = value if len(value) <= 25 else value[:25] + "..."
        self.logger.info(f"Entering text in {desc}: '{preview}'")

        first_el = target.first
        first_el.scroll_into_view_if_needed()
        expect(first_el).to_be_visible(timeout=10000)
        first_el.fill("")
        first_el.fill(value)

    def safe_select(self, locator: Union[Locator, str], label_or_value: str, description: Optional[str] = None) -> None:
        """Selects an option from a <select> dropdown by visible label or value."""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        desc = description or "dropdown"
        self.logger.info(f"Selecting '{label_or_value}' in {desc}")

        first_el = target.first
        first_el.scroll_into_view_if_needed()
        expect(first_el).to_be_visible(timeout=10000)
        try:
            first_el.select_option(label=label_or_value)
        except Exception:
            first_el.select_option(value=label_or_value)

    def select_grappelli_autocomplete(self, input_locator: Union[Locator, str], search_text: str) -> None:
        """Handles Django Grappelli UI autocomplete dropdowns."""
        target = self.page.locator(input_locator) if isinstance(input_locator, str) else input_locator
        self.logger.info(f"Selecting '{search_text}' in Grappelli autocomplete")

        first_el = target.first
        first_el.click()
        first_el.fill(search_text)
        self.page.wait_for_timeout(500)

        option = self.page.locator(f"ul.ui-autocomplete li a:has-text('{search_text}')").first
        if option.is_visible():
            option.click()
        else:
            first_el.press("Enter")

    def is_visible(self, locator: Union[Locator, str], timeout_ms: int = 5000) -> bool:
        """Checks if an element is visible on the page within timeout."""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        try:
            expect(target.first).to_be_visible(timeout=timeout_ms)
            return True
        except Exception:
            return False

    def get_text(self, locator: Union[Locator, str]) -> str:
        """Returns the trimmed text content of an element."""
        target = self.page.locator(locator) if isinstance(locator, str) else locator
        return target.first.inner_text().strip()

    def wait_for_ready(self) -> None:
        """Waits for the DOM and network state to settle."""
        self.page.wait_for_load_state("domcontentloaded")

    def take_screenshot(self, name: str) -> bytes:
        """Captures a screenshot of the current page."""
        self.logger.info(f"Capturing screenshot: {name}")
        return self.page.screenshot(path=f"test-results/{name}.png", full_page=True)
