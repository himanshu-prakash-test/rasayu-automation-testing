"""
Selects DWC toggle & shared master table helpers.
"""
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="function")
def dwc_active(page: Page):
    dwc_btn = page.locator("button.master-clinic-picker-btn:has-text('DWC'), .mm-sidebar-clinics button:has-text('DWC')").first
    if dwc_btn.is_visible() and "active" not in (dwc_btn.get_attribute("class") or ""):
        dwc_btn.click()
        page.wait_for_timeout(500)
    return page
