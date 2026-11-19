from typing import Optional
from playwright.sync_api import Page, Locator, expect

from base.base_page import BasePage
from utils.env_config import config


class LoginPage(BasePage):
    """Page Object for the Django Grappelli admin login page."""

    def __init__(self, page: Page):
        super().__init__(page, context_name="LoginPage")

    @property
    def username_input(self) -> Locator:
        return self.page.locator("#id_username, input[name='username']")

    @property
    def password_input(self) -> Locator:
        return self.page.locator("#id_password, input[name='password']")

    @property
    def submit_button(self) -> Locator:
        return self.page.locator("input[type='submit'], button[type='submit'], .grp-button.grp-default")

    @property
    def error_message(self) -> Locator:
        return self.page.locator("p.errornote, ul.errorlist, .grp-errors, .alert-danger")

    def open(self) -> None:
        """Navigates to the portal login page."""
        self.navigate_to(config.base_url)
        self.wait_for_ready()

    def login(self, username: Optional[str] = None, password: Optional[str] = None) -> None:
        """Logs into the system with either provided or default environment credentials."""
        user = username if username is not None else config.admin_username
        pwd = password if password is not None else config.admin_password

        self.logger.info(f"Attempting login for user: '{user}'")
        self.safe_fill(self.username_input, user, "Username Field")
        self.safe_fill(self.password_input, pwd, "Password Field")
        self.safe_click(self.submit_button, "Log In Button")
        self.wait_for_ready()

    def verify_login_success(self) -> None:
        """Verifies that login succeeded and user redirected to the administration dashboard."""
        self.logger.info("Verifying login success")
        expect(self.page).not_to_have_url(r".*/admin/login/.*", timeout=10000)
        dashboard_header = self.page.locator(
            "h1:has-text('Site administration'), h1:has-text('Rasayu Ayurved Clinics')"
        ).first
        expect(dashboard_header).to_be_visible(timeout=10000)

    def verify_login_failure(self, expected_substring: str = "Please enter the correct username and password") -> None:
        """Verifies that an error alert appears rejecting the invalid login attempt."""
        self.logger.info(f"Verifying login failure contains: '{expected_substring}'")
        expect(self.error_message.first).to_be_visible(timeout=5000)
        actual_text = self.error_message.first.inner_text()
        assert expected_substring.lower() in actual_text.lower(), (
            f"Expected '{expected_substring}' in '{actual_text}'"
        )
