"""
Master Management Automation Test Suite: DWC Clinic - Baseline Module (UPDATE Negative Operations).
Validates TC-UPD-NEG-MASTER-DWC-01 to TC-UPD-NEG-MASTER-DWC-08.
Strictly 100% Zero Hardcoding: dynamically loads all data from 'master_dwc_updatebaseline' sheet.
"""
import pytest
from playwright.sync_api import Page, expect

try:
    from master_management.dwc_clinic_masters.baseline_module.pages.dwc_update_page import DwcBaselineMasterUpdatePage
except ImportError:
    from ...pages.dwc_update_page import DwcBaselineMasterUpdatePage


@pytest.fixture
def update_page(authenticated_page: Page) -> DwcBaselineMasterUpdatePage:
    """Provides an authenticated DwcBaselineMasterUpdatePage session on /masters."""
    up = DwcBaselineMasterUpdatePage(authenticated_page)
    up.navigate_to_masters_page()
    return up


@pytest.mark.master
@pytest.mark.dwc
@pytest.mark.update
@pytest.mark.negative
@pytest.mark.baseline
class TestDwcBaselineUpdNeg:
    """Negative test cases for DWC Baseline Master Update operations (Zero Hardcoded Data)."""

    def test_tc_upd_neg_master_dwc_01_mandatory_field_cleared(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-01: Mandatory Field Cleared / Left Empty (Standalone Master)."""
        update_page.execute_negative_clear_mandatory("TC-UPD-NEG-MASTER-DWC-01")

    def test_tc_upd_neg_master_dwc_02_child_name_cleared(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-02: Dependent Master — Child Name Cleared / Empty."""
        update_page.execute_negative_clear_mandatory("TC-UPD-NEG-MASTER-DWC-02")

    def test_tc_upd_neg_master_dwc_03_parent_association_cleared(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-03: Dependent Master — Parent Association Cleared / Unselected."""
        update_page.execute_negative_clear_parent("TC-UPD-NEG-MASTER-DWC-03")

    def test_tc_upd_neg_master_dwc_04_duplicate_name_on_update(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-04: Duplicate Active Master Record Name on Update."""
        update_page.execute_negative_duplicate_name("TC-UPD-NEG-MASTER-DWC-04")

    def test_tc_upd_neg_master_dwc_05_clear_mandatory_complication(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-05: Dependent Master — Clear Mandatory Complication Name."""
        update_page.execute_negative_clear_mandatory("TC-UPD-NEG-MASTER-DWC-05")

    def test_tc_upd_neg_master_dwc_06_cancel_edit_modal(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-06: Cancel / Dismiss Edit Modal with Unsaved Changes."""
        update_page.execute_negative_cancel("TC-UPD-NEG-MASTER-DWC-06")

    def test_tc_upd_neg_master_dwc_07_save_debouncing_double_click(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-07: Rapid Double-Click on Save Button (Debounce Check)."""
        update_page.execute_negative_double_click("TC-UPD-NEG-MASTER-DWC-07")

    def test_tc_upd_neg_master_dwc_08_whitespace_only_name(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-NEG-MASTER-DWC-08: Update Mandatory Name with Whitespace-Only Input."""
        update_page.execute_negative_whitespace("TC-UPD-NEG-MASTER-DWC-08")
