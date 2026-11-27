"""
Selects RAC toggle & shared master table helpers.
"""
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="function")
def rac_active(page: Page):
    rac_btn = page.locator("button.master-clinic-picker-btn:has-text('RAC'), .mm-sidebar-clinics button:has-text('RAC')").first
    if rac_btn.is_visible() and "active" not in (rac_btn.get_attribute("class") or ""):
        rac_btn.click()
        page.wait_for_timeout(500)
    return page
