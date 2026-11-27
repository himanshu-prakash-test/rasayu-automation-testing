from typing import Callable, Optional
from playwright.sync_api import Page, Dialog, expect
try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger


class ModalDialogHandler:
    """Manages browser native dialogs (alert/confirm/prompt) and HTML modal popups."""

    def __init__(self, page: Page):
        self.page = page
        self.logger = get_logger("ModalDialogHandler")

    def auto_accept_dialog(self, expected_message_substring: Optional[str] = None) -> None:
        """Configures the page to accept native JavaScript dialogs."""
        def handle_dialog(dialog: Dialog):
            self.logger.info(f"Native dialog triggered [{dialog.type}]: '{dialog.message}'")
            if expected_message_substring:
                assert expected_message_substring.lower() in dialog.message.lower()
            dialog.accept()

        self.page.on("dialog", handle_dialog)

    def auto_dismiss_dialog(self) -> None:
        """Configures the page to dismiss native JavaScript dialogs."""
        def handle_dialog(dialog: Dialog):
            self.logger.info(f"Dismissing dialog [{dialog.type}]: '{dialog.message}'")
            dialog.dismiss()

        self.page.on("dialog", handle_dialog)

    def is_modal_open(self, modal_selector: str = ".modal.show, .grp-modal, div[role='dialog']") -> bool:
        """Checks if an HTML modal is open."""
        target = self.page.locator(modal_selector).first
        try:
            return target.is_visible()
        except Exception:
            return False

    def close_modal(self, close_btn_selector: str = ".modal .close, button:has-text('Close'), .grp-modal-close") -> None:
        """Closes an active HTML modal dialog."""
        self.logger.info("Closing modal dialog")
        btn = self.page.locator(close_btn_selector).first
        btn.click()
        self.page.wait_for_timeout(300)
