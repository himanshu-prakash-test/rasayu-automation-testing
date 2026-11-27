from playwright.sync_api import Page, expect
from base.base_page import BasePage


class NavigationMenu(BasePage):
    """
    Universal navigation menu component for the Django Grappelli admin portal.
    Encapsulates global dashboard links, breadcrumb validation, and module switching.
    """

    def __init__(self, page: Page):
        super().__init__(page, context_name="NavigationMenu")

    def go_to_admin_home(self) -> None:
        """Navigates to the portal administration home dashboard."""
        self.logger.info("Navigating to Admin Home")
        self.navigate_to("/admin/")
        self.wait_for_ready()

    def navigate_to_module(self, relative_path: str) -> None:
        """Navigates to any admin module by relative path (e.g. '/admin/crf/patient/')."""
        self.logger.info(f"Navigating to admin module: {relative_path}")
        self.navigate_to(relative_path)
        self.wait_for_ready()

    def verify_breadcrumb_contains(self, text: str) -> None:
        """Verifies breadcrumb navigation path contains expected text."""
        crumbs = self.page.locator("#grp-breadcrumbs, .breadcrumbs, ul.grp-breadcrumbs")
        expect(crumbs).to_contain_text(text)
