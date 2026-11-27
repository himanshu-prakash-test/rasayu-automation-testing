"""
DWC Visit Module Test Fixtures.
"""
import pytest
from playwright.sync_api import Page

try:
    from master_management.dwc_clinic_masters.visit_module.pages.dwc_visit_master_page import DwcVisitMasterPage
except ImportError:
    from ..pages.dwc_visit_master_page import DwcVisitMasterPage


@pytest.fixture
def visit_page(authenticated_page: Page) -> DwcVisitMasterPage:
    """Provides an authenticated DwcVisitMasterPage session on /masters with DWC clinic toggle active."""
    vp = DwcVisitMasterPage(authenticated_page)
    vp.navigate_to_masters_page()
    return vp
