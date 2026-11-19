from typing import List, Optional
from playwright.sync_api import Page, Locator, expect
from utils.logger import get_logger


class ToastHandler:
    """Handles notification messages, error notes, and Grappelli message lists."""

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger("ToastHandler")

    @property
    def success_banner(self) -> Locator:
        return self.page.locator("ul.grp-messagelist li.grp-success, .alert-success, .toast-success, li.success")

    @property
    def error_banner(self) -> Locator:
        return self.page.locator("ul.grp-messagelist li.grp-error, .alert-danger, .toast-error, li.error, .errornote")

    def verify_success_message(self, expected_substring: Optional[str] = None) -> None:
        """Verifies that a success notification banner is displayed."""
        self.logger.info(f"Verifying success message banner{': ' + expected_substring if expected_substring else ''}")
        expect(self.success_banner.first).to_be_visible(timeout=8000)
        if expected_substring:
            expect(self.success_banner.first).to_contain_text(expected_substring)

    def verify_error_message(self, expected_substring: Optional[str] = None) -> None:
        """Verifies that an error notification banner is displayed."""
        self.logger.info(f"Verifying error banner{': ' + expected_substring if expected_substring else ''}")
        expect(self.error_banner.first).to_be_visible(timeout=8000)
        if expected_substring:
            expect(self.error_banner.first).to_contain_text(expected_substring)

    def get_all_messages(self) -> List[str]:
        """Collects all messages present in the messagelist."""
        items = self.page.locator("ul.grp-messagelist li, ul.messagelist li")
        count = items.count()
        return [items.nth(i).inner_text().strip() for i in range(count)]
