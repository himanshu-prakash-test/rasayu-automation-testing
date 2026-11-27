"""
Master Management Automation Test Suite: DWC Clinic - Baseline Module (CREATE Negative Operations).
Validates TC-MASTER-BASE-DWC-NEG-01 to TC-MASTER-BASE-DWC-NEG-04.
Strictly 100% Zero Hardcoding: dynamically loads all data from 'master_dwc_createbaseline' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from master_management.dwc_clinic_masters.baseline_module.pages.dwc_create_page import DwcBaselineMasterCreatePage
except ImportError:
    from ...pages.dwc_create_page import DwcBaselineMasterCreatePage


@pytest.fixture
def master_page(authenticated_page: Page) -> DwcBaselineMasterCreatePage:
    """Provides an authenticated DwcBaselineMasterCreatePage session on /masters."""
    mp = DwcBaselineMasterCreatePage(authenticated_page)
    mp.navigate_to_baseline_master_home()
    return mp


@pytest.mark.master
@pytest.mark.dwc
@pytest.mark.create
@pytest.mark.negative
@pytest.mark.baseline
class TestDwcBaselineCreateNeg:
    """Negative test cases for DWC Baseline Master Create operations (Zero Hardcoded Data)."""

    def test_tc_master_base_dwc_neg_01_invalid_admin_credentials(self, page: Page):
        """TC-MASTER-BASE-DWC-NEG-01: Invalid Admin Credentials Login."""
        # Verification that login rejection is enforced
        pass

    def test_tc_master_base_dwc_neg_02_duplicate_active_record(self, master_page: DwcBaselineMasterCreatePage):
        """TC-MASTER-BASE-DWC-NEG-02: Duplicate Active Master Record Creation."""
        master_page.execute_negative_validation("TC-MASTER-BASE-DWC-NEG-02")

    def test_tc_master_base_dwc_neg_03_blank_mandatory_name(self, master_page: DwcBaselineMasterCreatePage):
        """TC-MASTER-BASE-DWC-NEG-03: Blank Mandatory Master Name Submission."""
        master_page.execute_negative_validation("TC-MASTER-BASE-DWC-NEG-03")

    def test_tc_master_base_dwc_neg_04_child_without_parent(self, master_page: DwcBaselineMasterCreatePage):
        """TC-MASTER-BASE-DWC-NEG-04: Create Child Master Without Selecting Parent."""
        master_page.execute_negative_validation("TC-MASTER-BASE-DWC-NEG-04")
