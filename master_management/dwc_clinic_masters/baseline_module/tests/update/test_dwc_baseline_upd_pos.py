"""
Master Management Automation Test Suite: DWC Clinic - Baseline Module (UPDATE Positive Operations).
Validates TC-UPD-POS-MASTER-DWC-01 to TC-UPD-POS-MASTER-DWC-15.
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
@pytest.mark.positive
@pytest.mark.baseline
class TestDwcBaselineUpdPos:
    """Positive test cases for DWC Baseline Master Update operations (Zero Hardcoded Data)."""

    def test_tc_upd_pos_master_dwc_01_edit_modal_prepopulated(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-01: Pre-populated Edit Modal Verification."""
        update_page.verify_edit_modal_prepopulated("TC-UPD-POS-MASTER-DWC-01")

    def test_tc_upd_pos_master_dwc_02_mandatory_field_only(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-02: Mandatory Field Only Update (Standalone Master)."""
        update_page.execute_mandatory_field_update("TC-UPD-POS-MASTER-DWC-02")

    def test_tc_upd_pos_master_dwc_03_update_and_clear_description(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-03: Update & Clear Optional Description Field."""
        update_page.execute_description_update_and_clear("TC-UPD-POS-MASTER-DWC-03")

    def test_tc_upd_pos_master_dwc_04_dependent_master_update(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-04: Dependent Master Update — Reassign Parent & Update Name."""
        update_page.execute_dependent_master_update("TC-UPD-POS-MASTER-DWC-04")

    def test_tc_upd_pos_master_dwc_05_hetu_sevan_update(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-05: Hetu Sevan Master Update — Mandatory + Optional Fields."""
        update_page.execute_hetu_sevan_update("TC-UPD-POS-MASTER-DWC-05")

    def test_tc_upd_pos_master_dwc_06_pharmacology_update(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-06: Pharmacology Master Update — Multi-Parent Linkage & Name."""
        update_page.execute_pharmacology_update("TC-UPD-POS-MASTER-DWC-06")

    def test_tc_upd_pos_master_dwc_07_status_toggle(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-07: Toggle Status Active ↔ Inactive."""
        update_page.execute_status_toggle_update("TC-UPD-POS-MASTER-DWC-07")

    def test_tc_upd_pos_master_dwc_08_preserve_id_and_counter(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-08: Preserve System ID, Counter & Action Icons on Update."""
        update_page.execute_counter_preserved_update("TC-UPD-POS-MASTER-DWC-08")

    def test_tc_upd_pos_master_dwc_09_save_via_shortcut(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-09: Save Master Update via Keyboard Shortcut (Alt + S)."""
        update_page.execute_shortcut_update("TC-UPD-POS-MASTER-DWC-09")

    def test_tc_upd_pos_master_dwc_10_filtered_update(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-10: Update Record While Search / Sort Filter Is Active."""
        update_page.execute_filtered_update("TC-UPD-POS-MASTER-DWC-10")

    def test_tc_upd_pos_master_dwc_11_page2_update(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-11: Update Record on Paginated Grid (Page 2)."""
        update_page.execute_page2_update("TC-UPD-POS-MASTER-DWC-11")

    def test_tc_upd_pos_master_dwc_12_refresh_persistence(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-12: Verify Update Persistence Across Browser Refresh."""
        update_page.execute_refresh_persistence("TC-UPD-POS-MASTER-DWC-12")

    def test_tc_upd_pos_master_dwc_13_history_modal_audit(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-13: Audit Trail / History Log Verification After Update."""
        update_page.execute_history_modal_update("TC-UPD-POS-MASTER-DWC-13")

    def test_tc_upd_pos_master_dwc_14_switch_masters(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-14: Switch Masters Immediately After Saving Update."""
        update_page.execute_clean_modal_switching("TC-UPD-POS-MASTER-DWC-14")

    def test_tc_upd_pos_master_dwc_15_save_without_modification(self, update_page: DwcBaselineMasterUpdatePage):
        """TC-UPD-POS-MASTER-DWC-15: Open Edit Modal and Save Without Modifying Any Fields."""
        update_page.execute_save_without_modification("TC-UPD-POS-MASTER-DWC-15")
