"""
Master Management Automation Test Suite: DWC Clinic - Baseline Module (CREATE Positive Operations).
Validates TC-MASTER-BASE-DWC-01 to TC-MASTER-BASE-DWC-68 (68 Test Cases).
Strictly 100% Zero Hardcoding: dynamically loads all data from 'master_dwc_createbaseline' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from master_management.dwc_clinic_masters.baseline_module.pages.dwc_create_page import DwcBaselineMasterCreatePage
    from master_management.dwc_clinic_masters.baseline_module.dwc_baseline_data import (
        get_master_baseline_test_data,
        get_master_category,
    )
except ImportError:
    from ...pages.dwc_create_page import DwcBaselineMasterCreatePage
    from ...dwc_baseline_data import (
        get_master_baseline_test_data,
        get_master_category,
    )

POSITIVE_CREATE_IDS = [f"TC-MASTER-BASE-DWC-{i:02d}" for i in range(2, 69)]


@pytest.fixture
def master_page(authenticated_page: Page) -> DwcBaselineMasterCreatePage:
    """Provides an authenticated DwcBaselineMasterCreatePage session on /masters."""
    mp = DwcBaselineMasterCreatePage(authenticated_page)
    mp.navigate_to_baseline_master_home()
    return mp


@pytest.mark.master
@pytest.mark.dwc
@pytest.mark.create
@pytest.mark.positive
@pytest.mark.baseline
class TestDwcBaselineCreatePos:
    """Master Management test suite for DWC Clinic Create Baseline (68 Positive Test Cases)."""

    def test_tc_master_base_dwc_01_admin_navigation(self, master_page: DwcBaselineMasterCreatePage):
        """TC-MASTER-BASE-DWC-01: Verify Admin Login and Navigation to DWC Clinic Disease at Baseline Master Module."""
        master_page.verify_admin_navigation("TC-MASTER-BASE-DWC-01")

    @pytest.mark.parametrize("test_case_id", POSITIVE_CREATE_IDS, ids=lambda tc: tc)
    def test_tc_master_base_dwc_create_positive(self, master_page: DwcBaselineMasterCreatePage, test_case_id: str):
        """TC-MASTER-BASE-DWC-02 to 68: Create and verify DWC Master Record (Active vs Inactive)."""
        rec = get_master_baseline_test_data(test_case_id)
        # 1. Create Active record
        master_page.create_master_record_from_test_data(test_case_id, create_inactive=False)
        master_page.verify_master_record_in_list(test_case_id, is_active=True)

        # 2. If inactive input is specified, create Inactive record as well
        if rec.inactive_record_input and rec.inactive_record_input.strip():
            master_page.create_master_record_from_test_data(test_case_id, create_inactive=True)
            master_page.verify_master_record_in_list(test_case_id, is_active=False)
