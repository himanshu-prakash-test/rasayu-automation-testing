"""
DWC Baseline Module Test Fixtures.
"""
import pytest
from playwright.sync_api import Page

try:
    from master_management.dwc_clinic_masters.baseline_module.pages.dwc_create_page import DwcBaselineMasterCreatePage
    from master_management.dwc_clinic_masters.baseline_module.pages.dwc_update_page import DwcBaselineMasterUpdatePage
    from master_management.dwc_clinic_masters.baseline_module.pages.dwc_delete_page import DwcBaselineMasterDeletePage
except ImportError:
    from ..pages.dwc_create_page import DwcBaselineMasterCreatePage
    from ..pages.dwc_update_page import DwcBaselineMasterUpdatePage
    from ..pages.dwc_delete_page import DwcBaselineMasterDeletePage


@pytest.fixture
def master_create_page(authenticated_page: Page) -> DwcBaselineMasterCreatePage:
    mp = DwcBaselineMasterCreatePage(authenticated_page)
    mp.navigate_to_baseline_master_home()
    return mp


@pytest.fixture
def master_page(master_create_page: DwcBaselineMasterCreatePage) -> DwcBaselineMasterCreatePage:
    return master_create_page


@pytest.fixture
def update_page(authenticated_page: Page) -> DwcBaselineMasterUpdatePage:
    up = DwcBaselineMasterUpdatePage(authenticated_page)
    up.navigate_to_masters_page()
    return up


@pytest.fixture
def delete_page(authenticated_page: Page) -> DwcBaselineMasterDeletePage:
    dp = DwcBaselineMasterDeletePage(authenticated_page)
    dp.navigate_to_masters_page()
    return dp
