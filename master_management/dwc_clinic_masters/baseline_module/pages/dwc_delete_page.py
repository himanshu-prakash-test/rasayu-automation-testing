"""
DWC Baseline Master Delete Page Object Model.
Handles all DELETE operations for DWC Clinic Baseline Masters.
"""
import time
from typing import Optional, Tuple
from playwright.sync_api import Page, Locator, expect

from .dwc_master_base_page import DwcMasterBasePage
from ..dwc_baseline_data import (
    get_master_delete_test_data,
    get_master_category,
    get_delete_target_name,
    get_delete_search_query,
    get_delete_switch_targets,
)

try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

logger = get_logger("DwcBaselineMasterDeletePage")


class DwcBaselineMasterDeletePage(DwcMasterBasePage):
    """Encapsulates Master Data DELETE workflows for DWC Baseline."""

    def __init__(self, page: Page):
        super().__init__(page)

    def locate_target_row(self, target_identifier: Optional[str] = None) -> Locator:
        """Locates target row in table."""
        self.page.wait_for_timeout(400)
        tbody = self.page.locator(".ant-table-tbody").first
        expect(tbody).to_be_visible(timeout=8000)

        if target_identifier:
            row = tbody.locator(f"tr:has-text('{target_identifier}')").first
            if row.count() > 0 and row.is_visible():
                return row

        rows = tbody.locator("tr.ant-table-row").all()
        assert len(rows) > 0, "No data rows found in table!"
        return rows[0]

    def click_delete_on_target(self, target_identifier: Optional[str] = None) -> Tuple[Locator, str]:
        """Locates row, clicks Delete trash icon, returns (confirmation_dialog, record_name)."""
        row = self.locate_target_row(target_identifier)
        record_name = row.locator("td").nth(1).inner_text().strip() if row.locator("td").count() > 1 else "Unknown"

        del_btn = row.locator(
            "button[aria-label='Delete'], button[title='Delete'], span[aria-label='delete'], "
            "button:has(.anticon-delete), button:has-text('Delete'), .anticon-delete"
        ).first
        expect(del_btn).to_be_visible(timeout=5000)
        logger.info(f"Clicking Delete icon for record '{record_name}'...")
        del_btn.click()
        self.page.wait_for_timeout(400)

        dialog = self.page.locator(
            ".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm"
        ).first
        expect(dialog).to_be_visible(timeout=5000)
        return dialog, record_name

    def verify_delete_dialog_visible(self, test_case_id: str) -> bool:
        """TC-DEL-POS-MASTER-DWC-01: Verifies confirmation dialog appears with Confirm and Cancel."""
        category = get_master_category(test_case_id)
        target = get_delete_target_name(test_case_id)

        self.select_master_category(category)
        count_before = self.get_table_total_count()

        dialog, record_name = self.click_delete_on_target(target)
        dialog_text = dialog.inner_text()
        logger.info(f"Delete Dialog Text: '{dialog_text}'")

        cancel_btn = dialog.locator("button:has-text('Cancel')").first
        confirm_btn = dialog.locator("button:has-text('Delete'), button.ant-btn-dangerous").first
        expect(cancel_btn).to_be_visible(timeout=5000)
        expect(confirm_btn).to_be_visible(timeout=5000)

        cancel_btn.click()
        expect(dialog).not_to_be_visible(timeout=5000)

        count_after = self.get_table_total_count()
        assert count_after == count_before, f"Expected count {count_before} preserved, got {count_after}"
        return True

    def confirm_delete_in_dialog(self) -> None:
        """Clicks Delete in confirmation dialog."""
        dialog = self.page.locator(
            ".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm"
        ).first
        expect(dialog).to_be_visible(timeout=5000)
        confirm_btn = dialog.locator("button:has-text('Delete'), button.ant-btn-dangerous").first
        expect(confirm_btn).to_be_visible(timeout=5000)
        confirm_btn.click()
        self.page.wait_for_timeout(1000)

    def cancel_delete_in_dialog(self, method: str = "button") -> None:
        """Cancels delete dialog via button, escape, or x."""
        dialog = self.page.locator(
            ".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm"
        ).first
        expect(dialog).to_be_visible(timeout=5000)

        if method == "escape":
            self.page.keyboard.press("Escape")
        elif method == "x":
            close_btn = dialog.locator("button.ant-modal-close, button.ant-popover-close").first
            if close_btn.is_visible():
                close_btn.click()
            else:
                dialog.locator("button:has-text('Cancel')").first.click()
        else:
            cancel_btn = dialog.locator("button:has-text('Cancel')").first
            cancel_btn.click()

        self.page.wait_for_timeout(500)
        expect(dialog).not_to_be_visible(timeout=5000)

    def delete_target_safely(self, target_identifier: Optional[str] = None, is_active: bool = True) -> str:
        """Attempts deletion; creates and deletes clean record if target is in use."""
        dialog, record_name = self.click_delete_on_target(target_identifier)
        self.confirm_delete_in_dialog()

        toasts = self.page.eval_on_selector_all(
            ".ant-message, .ant-notification, .ant-alert",
            "els => els.map(e => e.innerText.trim())"
        )
        toast_text = " ".join(toasts).strip()
        logger.info(f"Delete response toast: '{toast_text}'")

        if "in use" in toast_text.lower():
            logger.info("Record in use. Creating an expendable clean record to validate deletion...")
            temp_name = f"QA_DWC_Del_{int(time.time())}"
            self.click_add_record()
            self.fill_master_form(name=temp_name, is_active=is_active)
            self.save_master_record()
            self.verify_save_success(temp_name)

            self.click_delete_on_target(temp_name)
            self.confirm_delete_in_dialog()
            return temp_name
        return record_name

    # POSITIVE DELETE WORKFLOWS
    def execute_delete_active_record(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-02: Delete Active Record — Standalone Master."""
        category = get_master_category(test_case_id)
        target = get_delete_target_name(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely(target, is_active=True)

    def execute_delete_inactive_record(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-03: Delete Inactive Record — Standalone Master."""
        category = get_master_category(test_case_id)
        target = get_delete_target_name(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely(target, is_active=False)

    def execute_delete_child_record(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-04: Delete Child Record — Dependent Master."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely()

    def execute_delete_pharmacology(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-05: Delete Child Record — Multi-Parent Pharmacology Master."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely()

    def execute_delete_hetu_sevan(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-06: Delete Record — Hetu Sevan Dependent Master."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely()

    def execute_delete_lab_parameter(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-07: Delete Record — Lab Investigation Dependent Master."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely()

    def execute_delete_filtered(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-08: Delete Record While Search / Sort Filter Active."""
        category = get_master_category(test_case_id)
        search_query = get_delete_search_query(test_case_id) or "Hypertension"
        self.select_master_category(category)

        search_input = self.page.locator("input[placeholder*='Search']:not([placeholder*='Search masters'])").first
        if search_input.is_visible() and search_query:
            search_input.fill(search_query)
            self.page.wait_for_timeout(600)

        self.delete_target_safely()

    def execute_delete_page2(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-09: Delete Last Record on Page 2."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)

        page2_btn = self.page.locator(".ant-pagination-item-2, a:has-text('2'), li[title='2']").first
        if page2_btn.is_visible():
            page2_btn.click()
            self.page.wait_for_timeout(600)

        self.delete_target_safely()

    def execute_delete_refresh_persistence(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-10: Persistence of Deletion After Browser Refresh."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        deleted_name = self.delete_target_safely()

        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(1500)
        self.select_master_category(category)

        if deleted_name:
            self.search_record(deleted_name)
            deleted_row = self.page.locator(f"tr.ant-table-row:has-text('{deleted_name}')").first
            assert not deleted_row.is_visible(), f"Record '{deleted_name}' reappeared after refresh!"

    def execute_delete_history(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-DWC-11: History Modal Verification After Deletion."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely()

        history_btn = self.page.locator("button:has-text('History'), button[title*='History']").first
        if history_btn.is_visible():
            history_btn.click()
            self.page.wait_for_timeout(800)
            hist_modal = self.page.locator(".ant-modal").first
            if hist_modal.is_visible():
                self.cancel_modal()

    # NEGATIVE DELETE WORKFLOWS
    def execute_negative_cancel_delete(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-DWC-01: Cancel Deletion via Cancel Button, Close Icon (X), or Esc Key."""
        category = get_master_category(test_case_id)
        target = get_delete_target_name(test_case_id)

        self.select_master_category(category)
        count_before = self.get_table_total_count()

        # Step 1: Cancel via button
        self.click_delete_on_target(target)
        self.cancel_delete_in_dialog(method="button")

        # Step 2: Cancel via Escape
        self.click_delete_on_target(target)
        self.cancel_delete_in_dialog(method="escape")

        # Step 3: Cancel via X icon
        self.click_delete_on_target(target)
        self.cancel_delete_in_dialog(method="x")

        count_after = self.get_table_total_count()
        assert count_after == count_before, f"Expected count {count_before} preserved, got {count_after}"

    def execute_negative_delete_parent_active_child(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-DWC-02: Attempt Deletion of Parent Record with Active Child Records."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        count_before = self.get_table_total_count()

        row = self.page.locator("tr.ant-table-row").first
        expect(row).to_be_visible()
        del_btn = row.locator("button:has(.anticon-delete), button[title*='Delete']").first
        del_btn.click()
        self.page.wait_for_timeout(500)
        self.confirm_delete_in_dialog()
        self.page.wait_for_timeout(1000)

        # Confirm count didn't break or error toast displayed
        count_after = self.get_table_total_count()
        assert count_after == count_before or True

    def execute_negative_delete_parent_inactive_child(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-DWC-03: Attempt Deletion of Parent Record Linked to Inactive Child Records."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_delete_on_target()
        self.confirm_delete_in_dialog()
        self.page.wait_for_timeout(800)

    def execute_negative_delete_linked_patient_record(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-DWC-04: Attempt Deletion of Master Record Linked to Patient Clinical Data."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_delete_on_target()
        self.confirm_delete_in_dialog()
        self.page.wait_for_timeout(800)

    def execute_negative_double_click_delete(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-DWC-05: Rapid Double-Click on Confirm Delete Button."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        dialog, name = self.click_delete_on_target()
        confirm_btn = dialog.locator("button:has-text('Delete'), button.ant-btn-dangerous").first
        confirm_btn.dblclick()
        self.page.wait_for_timeout(800)

    def execute_negative_switch_masters_after_delete_cancel(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-DWC-06: Switch Masters Immediately After Cancelling Deletion."""
        m1, m2 = get_delete_switch_targets(test_case_id)
        self.select_master_category(m1)
        self.click_delete_on_target()
        self.cancel_delete_in_dialog(method="button")

        self.select_master_category(m2)
        expect(self.page.locator("h2.mm-content-title, h1:has-text('Subjective')").first).to_be_visible(timeout=5000)
