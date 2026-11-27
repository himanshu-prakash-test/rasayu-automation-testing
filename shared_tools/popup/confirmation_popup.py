from playwright.sync_api import Page, expect
try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger


class ConfirmationPopup:
    """Handles confirmation dialogs for delete, discard, or overwrite actions."""

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger("ConfirmationPopup")

    def confirm_action(self, button_selector: str = "button:has-text('Yes, I\\'m sure'), input[type='submit'][value*='Yes']") -> None:
        """Confirms the active action."""
        self.logger.info("Confirming action on confirmation popup")
        btn = self.page.locator(button_selector).first
        expect(btn).to_be_visible(timeout=5000)
        btn.click()
        self.page.wait_for_load_state("domcontentloaded")

    def cancel_action(self, button_selector: str = "button:has-text('No'), a:has-text('Cancel'), .grp-cancel-link") -> None:
        """Cancels the action."""
        self.logger.info("Cancelling action on confirmation popup")
        btn = self.page.locator(button_selector).first
        expect(btn).to_be_visible(timeout=5000)
        btn.click()
