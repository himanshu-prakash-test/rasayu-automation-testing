"""
Shared Masters navigation and DWC/RAC switcher fixtures.
"""
import pytest
from playwright.sync_api import Page

try:
    from shared_tools.utils.env_config import config
except ImportError:
    from utils.env_config import config


@pytest.fixture(scope="function")
def rac_clinic_switcher(page: Page):
    """Ensures RAC clinic toggle is selected in Master Management."""
    rac_btn = page.locator("button.master-clinic-picker-btn:has-text('RAC'), .mm-sidebar-clinics button:has-text('RAC')").first
    if rac_btn.is_visible() and "active" not in (rac_btn.get_attribute("class") or ""):
        rac_btn.click()
        page.wait_for_timeout(500)
    return page


@pytest.fixture(scope="function")
def dwc_clinic_switcher(page: Page):
    """Ensures DWC clinic toggle is selected in Master Management."""
    dwc_btn = page.locator("button.master-clinic-picker-btn:has-text('DWC'), .mm-sidebar-clinics button:has-text('DWC')").first
    if dwc_btn.is_visible() and "active" not in (dwc_btn.get_attribute("class") or ""):
        dwc_btn.click()
        page.wait_for_timeout(500)
    return page
