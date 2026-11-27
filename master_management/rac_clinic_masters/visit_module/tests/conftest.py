"""
Shared fixtures for RAC Clinic Visit Masters testing.
"""
import pytest
from playwright.sync_api import Page

try:
    from master_management.rac_clinic_masters.visit_module.pages.visit_master_page import VisitMasterPage
except ImportError:
    from pages.visit_master_page import VisitMasterPage


@pytest.fixture
def visit_page(authenticated_page: Page) -> VisitMasterPage:
    """Provides an authenticated VisitMasterPage session on https://rasayu-stg.corecotechnologies.com/masters."""
    vp = VisitMasterPage(authenticated_page)
    vp.navigate_to_masters_page()
    return vp
