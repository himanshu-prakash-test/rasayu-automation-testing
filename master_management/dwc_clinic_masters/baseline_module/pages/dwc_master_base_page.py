"""
DWC Master Base Page Object Model.
Inherits from MasterBasePage and ensures DWC Clinic toggle is selected.
"""
from playwright.sync_api import Page, expect

try:
    from master_management.rac_clinic_masters.baseline_module.pages.master_base_page import MasterBasePage
except ImportError:
    from pages.master_base_page import MasterBasePage

try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

try:
    from shared_tools.utils.env_config import config
except ImportError:
    from utils.env_config import config

logger = get_logger("DwcMasterBasePage")


class DwcMasterBasePage(MasterBasePage):
    """Encapsulates DWC Master Data management interactions in React SPA Masters portal."""

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_masters_page(self) -> None:
        """Navigates to the main website's Masters Management page and ensures DWC clinic is selected."""
        masters_url = f"{config.main_app_url.rstrip('/')}/masters"
        logger.info(f"Navigating to DWC Masters Management portal: {masters_url}")

        if "/masters" in self.page.url:
            logger.info("Already on /masters route.")
        else:
            masters_nav = self.page.locator("a[title='Master Management'], a[href='/masters']").first
            if masters_nav.is_visible():
                masters_nav.click()
            else:
                self.page.goto(masters_url, wait_until="domcontentloaded")

        self.page.wait_for_timeout(1000)
        try:
            self.page.wait_for_selector(".ant-skeleton, .ant-spin-spinning", state="detached", timeout=15000)
        except Exception:
            pass

        # Ensure DWC clinic toggle is active
        dwc_btn = self.page.locator(
            "button.master-clinic-picker-btn:has-text('DWC'), .mm-sidebar-clinics button:has-text('DWC')"
        ).first
        if dwc_btn.is_visible():
            classes = dwc_btn.get_attribute("class") or ""
            if "active" not in classes:
                logger.info("Activating DWC clinic picker button...")
                dwc_btn.click()
                self.page.wait_for_timeout(500)

        # Clear any leftover search filter in sidebar masters search
        clear_search_btn = self.page.locator("button[aria-label='Clear search'], button:has-text('Clear search')").first
        if clear_search_btn.is_visible():
            clear_search_btn.click()
            self.page.wait_for_timeout(300)

        # Expand groups
        self.expand_all_category_groups()
