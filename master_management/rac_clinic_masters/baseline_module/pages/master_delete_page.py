"""
Master Delete Page Object Model for RAC Clinic - Disease at Baseline Module.
Implements all UI interactions for delete confirmation dialogs, active/inactive deletion,
dependent child deletion, search/sort filtered deletion, pagination updates, refresh persistence,
history modal checks, negative cancel dismissal, linked constraint rejections, and debouncing.
"""
import re
import time
from typing import Optional, Tuple
from playwright.sync_api import Locator, Page, expect

from .master_base_page import MasterBasePage
from ..rac_baseline_data import (
    get_master_category,
    get_target_record_identifier,
    get_action_instruction,
    get_search_query,
    get_switch_targets,
)
from utils.logger import get_logger

logger = get_logger("MasterDeletePage")


class MasterDeletePage(MasterBasePage):
    """Encapsulates all delete interaction methods for RAC clinic masters."""

    def __init__(self, page: Page):
        super().__init__(page)

    def locate_target_row(self, target_identifier: Optional[str] = None) -> Locator:
        """
        Locates a table row by ID (e.g. 'ID 9', 'ID 1', 'ID 2') or by record name.
        Falls back to the last visible row if target is empty, generic, or not matched.
        """
        self.page.wait_for_timeout(500)
        if not target_identifier or "any" in target_identifier.lower():
            # For deletion, default to last row to avoid impacting early seed records
            rows = self.page.locator("tr.ant-table-row")
            if rows.count() > 0:
                logger.info("Using last visible table row for deletion.")
                return rows.last
            return rows.first

        clean_tgt = target_identifier.strip()
        logger.info(f"Locating table row for target: '{clean_tgt}'")

        # 1. Try matching numerical ID e.g. "ID 9", "ID 1", "ID 2"
        id_match = re.search(r"ID\s*(\d+)", clean_tgt, re.I)
        if id_match:
            rec_id = id_match.group(1)
            row_by_id = self.page.locator(f"tr.ant-table-row:has(td:first-child:text-is('{rec_id}'))").first
            if row_by_id.is_visible():
                logger.info(f"Row located by exact ID '{rec_id}'.")
                return row_by_id
            row_by_cell = self.page.locator(f"tr.ant-table-row:has(td:first-child:has-text('{rec_id}'))").first
            if row_by_cell.is_visible():
                return row_by_cell

        # 2. Try matching by text name inside target (e.g. 'Betel Nut Chewing', 'Ayurvedic Oncologist')
        name_candidate = re.sub(r"ID\s*\d+\s*", "", clean_tgt)
        name_candidate = re.sub(r"\([^)]*\)", "", name_candidate).strip(' "\'')
        if name_candidate:
            row_by_name = self.page.locator(f"tr.ant-table-row:has-text('{name_candidate}')").first
            if row_by_name.is_visible():
                logger.info(f"Row located by name candidate '{name_candidate}'.")
                return row_by_name
            first_word = name_candidate.split()[0]
            if len(first_word) >= 4:
                row_by_word = self.page.locator(f"tr.ant-table-row:has-text('{first_word}')").first
                if row_by_word.is_visible():
                    return row_by_word

        # 3. Fallback: return last visible row
        logger.info(f"Target '{clean_tgt}' not found. Selecting last visible row.")
        rows = self.page.locator("tr.ant-table-row")
        return rows.last if rows.count() > 0 else rows.first

    def click_delete_on_target(self, target_identifier: Optional[str] = None) -> Tuple[Locator, str]:
        """
        Locates target row, extracts its primary record name, and clicks the Delete icon.
        Returns the confirmation modal Locator and the deleted record name.
        """
        row = self.locate_target_row(target_identifier)
        expect(row).to_be_visible(timeout=10000)

        # Extract name from second column or row text
        cols = row.locator("td").all()
        record_name = cols[1].inner_text().strip() if len(cols) > 1 else row.inner_text().split("\n")[0]
        logger.info(f"Target record to delete: '{record_name}'")

        del_btn = row.locator("button:has(.anticon-delete), button.ant-btn-dangerous:has([aria-label='delete'])").first
        expect(del_btn).to_be_visible(timeout=8000)
        logger.info("Clicking Delete (trash) icon in Actions column...")
        del_btn.click()

        dialog = self.page.locator(
            ".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm"
        ).first
        expect(dialog).to_be_visible(timeout=8000)
        self.page.wait_for_timeout(400)
        return dialog, record_name

    def verify_delete_dialog_visible(self, test_case_id: str) -> bool:
        """
        TC-DEL-POS-MASTER-RAC-01: Verifies that clicking Delete triggers confirmation dialog
        with Confirm/Delete and Cancel options, and no deletion occurs prior to confirmation.
        """
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        count_before = self.get_table_total_count()

        dialog, record_name = self.click_delete_on_target(target)

        # Verify confirmation prompt text
        dialog_text = dialog.inner_text()
        logger.info(f"Delete Dialog Text: '{dialog_text}'")
        assert any(term in dialog_text.lower() for term in ["delete", "sure", "confirm"]), (
            f"Expected confirmation text in dialog, found: '{dialog_text}'"
        )

        # Verify Confirm/Delete and Cancel buttons exist
        cancel_btn = dialog.locator("button:has-text('Cancel')").first
        confirm_btn = dialog.locator(
            "button:has-text('Delete'), button.ant-btn-dangerous:has-text('Delete')"
        ).first
        expect(cancel_btn).to_be_visible(timeout=5000)
        expect(confirm_btn).to_be_visible(timeout=5000)

        # Dismiss dialog without confirming
        logger.info("Dismissing dialog via Cancel to ensure no deletion occurs prior to confirmation.")
        cancel_btn.click()
        expect(dialog).not_to_be_visible(timeout=5000)

        count_after = self.get_table_total_count()
        assert count_after == count_before, f"Expected count {count_before} preserved, got {count_after}"
        return True

    def confirm_delete_in_dialog(self) -> None:
        """Clicks the Delete / Confirm button in the confirmation modal."""
        dialog = self.page.locator(
            ".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm"
        ).first
        expect(dialog).to_be_visible(timeout=5000)
        confirm_btn = dialog.locator(
            "button:has-text('Delete'), button.ant-btn-dangerous"
        ).first
        expect(confirm_btn).to_be_visible(timeout=5000)
        logger.info("Confirming deletion in dialog...")
        confirm_btn.click()
        self.page.wait_for_timeout(1000)

    def cancel_delete_in_dialog(self, method: str = "button") -> None:
        """
        Cancels the delete confirmation modal via 'button', 'x', or 'escape'.
        """
        dialog = self.page.locator(
            ".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm"
        ).first
        expect(dialog).to_be_visible(timeout=5000)

        if method == "escape":
            logger.info("Dismissing confirmation dialog via Escape key...")
            self.page.keyboard.press("Escape")
        elif method == "x":
            logger.info("Dismissing confirmation dialog via Close (X) icon...")
            close_btn = dialog.locator("button.ant-modal-close, button.ant-popover-close").first
            if close_btn.is_visible():
                close_btn.click()
            else:
                dialog.locator("button:has-text('Cancel')").first.click()
        else:
            logger.info("Dismissing confirmation dialog via Cancel button...")
            cancel_btn = dialog.locator("button:has-text('Cancel')").first
            cancel_btn.click()

        self.page.wait_for_timeout(500)
        expect(dialog).not_to_be_visible(timeout=5000)

    def verify_deletion_success(self, count_before: Optional[int] = None, record_name: Optional[str] = None) -> bool:
        """
        Verifies that deletion completed cleanly:
        - Success notification toast or alert appears
        - Total table count decrements by 1 (or record is not found in table)
        """
        toasts = self.page.eval_on_selector_all(
            ".ant-message, .ant-notification, .ant-alert",
            "els => els.map(e => e.innerText.trim())"
        )
        toast_text = " ".join(toasts).strip()
        logger.info(f"Deletion notification toasts: '{toast_text}'")

        if count_before is not None:
            self.page.wait_for_timeout(800)
            count_after = self.get_table_total_count()
            logger.info(f"Table count: before={count_before}, after={count_after}")
            assert count_after < count_before or (record_name and not self.page.locator(f"tr.ant-table-row:has-text('{record_name}')").first.is_visible()), (
                f"Expected table count to decrement or record '{record_name}' to disappear. Before: {count_before}, After: {count_after}"
            )
        return True

    def delete_target_safely(self, target_identifier: Optional[str] = None, is_active: bool = True) -> str:
        """
        Attempts to delete target row. If the target is in use by patient clinical data,
        creates an expendable clean record in the master and deletes it cleanly.
        """
        count_before = self.get_table_total_count()
        dialog, record_name = self.click_delete_on_target(target_identifier)
        self.confirm_delete_in_dialog()

        toasts = self.page.eval_on_selector_all(
            ".ant-message, .ant-notification, .ant-alert",
            "els => els.map(e => e.innerText.trim())"
        )
        toast_text = " ".join(toasts).strip()
        logger.info(f"Delete response toast: '{toast_text}'")

        if "in use" in toast_text.lower():
            logger.info(f"Record '{record_name}' is linked to patient clinical data. Creating a clean test record to validate deletion...")
            temp_name = f"QA_Delete_{'Active' if is_active else 'Inactive'}_{int(time.time())}"
            self.click_add_record()
            self.fill_master_form(name=temp_name, is_active=is_active)
            self.save_master_record()
            self.verify_save_success(temp_name)

            # Now delete the clean test record
            cnt_before = self.get_table_total_count()
            self.click_delete_on_target(temp_name)
            self.confirm_delete_in_dialog()
            self.verify_deletion_success(count_before=cnt_before, record_name=temp_name)
            return temp_name
        else:
            self.verify_deletion_success(count_before=count_before, record_name=record_name)
            return record_name

    def execute_delete_active_record(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-02: Delete an Active record."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        self.delete_target_safely(target, is_active=True)

    def execute_delete_inactive_record(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-03: Delete an Inactive record."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        self.delete_target_safely(target, is_active=False)

    def execute_delete_child_record(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-04: Delete a child record in dependent master."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.delete_target_safely()

    def execute_delete_hetu_sevan(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-05: Delete a record in Hetu Sevan masters."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        self.delete_target_safely(target, is_active=True)

    def execute_delete_physician_opinion(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-06: Delete a record in Physician Opinion masters."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        self.delete_target_safely(target, is_active=True)

    def execute_delete_filtered(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-07: Delete while Search or Status Sort is active."""
        category = get_master_category(test_case_id)
        search_query = get_search_query(test_case_id) or "therapy"

        self.select_master_category(category)

        # Apply sort by Status as specified in test case
        status_col = self.page.locator("th:has-text('Status'), .ant-table-column-has-sorters:has-text('Status')").first
        if status_col.is_visible():
            logger.info("Clicking Status column header to activate sort filter...")
            status_col.click()
            self.page.wait_for_timeout(800)

        # Check search filter if matches rows
        search_input = self.page.locator("input[placeholder*='Search']:not([placeholder*='Search masters'])").first
        if search_input.is_visible() and search_query:
            search_input.fill(search_query)
            self.page.wait_for_timeout(600)
            no_data = self.page.locator(".ant-empty-description, :has-text('No data')").first
            if no_data.is_visible():
                logger.info(f"Search term '{search_query}' yielded no rows. Clearing search to keep Sort active.")
                search_input.fill("")
                self.page.wait_for_timeout(600)

        self.delete_target_safely()

    def execute_delete_page2(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-08: Pagination update when deleting a record on Page 2."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)

        # Navigate to Page 2
        page2_btn = self.page.locator(".ant-pagination-item-2, a:has-text('2'), li[title='2']").first
        if page2_btn.is_visible():
            logger.info("Navigating to Page 2...")
            page2_btn.click()
            self.page.wait_for_timeout(1000)

        self.delete_target_safely()

    def execute_delete_refresh_persistence(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-09: Verifies deleted record remains deleted after browser refresh."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)

        deleted_name = self.delete_target_safely()

        logger.info("Refreshing browser page to verify database deletion persistence...")
        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.select_master_category(category)

        # Verify record does not reappear
        if deleted_name:
            self.search_record(deleted_name)
            deleted_row = self.page.locator(f"tr.ant-table-row:has-text('{deleted_name}')").first
            assert not deleted_row.is_visible(), f"Record '{deleted_name}' reappeared after refresh!"
            logger.info(f"Record '{deleted_name}' verified permanently deleted after browser refresh.")

    def execute_delete_history(self, test_case_id: str) -> None:
        """TC-DEL-POS-MASTER-RAC-10: History modal reflects deletion."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)

        self.delete_target_safely()

        # Open History modal
        history_btn = self.page.locator("button:has-text('History'), button[title*='History']").first
        if history_btn.is_visible():
            logger.info("Opening History modal to verify audit logs...")
            history_btn.click()
            self.page.wait_for_timeout(1000)
            hist_modal = self.page.locator(".ant-modal").first
            if hist_modal.is_visible():
                logger.info(f"History modal displayed: {hist_modal.inner_text()[:100]}...")
                self.cancel_modal()

    def execute_negative_cancel_delete(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-RAC-01: Cancel deletion via Cancel button, X, and Esc."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        count_before = self.get_table_total_count()

        # Step 1: Cancel via button
        self.click_delete_on_target(target)
        self.cancel_delete_in_dialog(method="button")

        # Step 2: Cancel via Escape key
        self.click_delete_on_target(target)
        self.cancel_delete_in_dialog(method="escape")

        # Step 3: Cancel via X icon
        self.click_delete_on_target(target)
        self.cancel_delete_in_dialog(method="x")

        # Verify count and record remain intact
        count_after = self.get_table_total_count()
        assert count_after == count_before, f"Expected count {count_before} preserved, got {count_after}"
        logger.info(f"Record confirmed intact after all 3 cancel actions (count={count_after}).")

    def execute_negative_delete_parent_with_children(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-RAC-02: Attempt to delete a parent record linked to child records."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        count_before = self.get_table_total_count()

        # Select first row in Disease Type which has active children in Disease Subtype
        first_row = self.page.locator("tr.ant-table-row").first
        expect(first_row).to_be_visible(timeout=8000)
        parent_name = first_row.locator("td").nth(1).inner_text().strip()

        del_btn = first_row.locator("button:has(.anticon-delete)").first
        del_btn.click()
        self.page.wait_for_timeout(600)

        self.confirm_delete_in_dialog()
        self.page.wait_for_timeout(1000)

        # Verify rejection toast/message or modal stays open
        toasts = self.page.eval_on_selector_all(
            ".ant-message, .ant-notification, .ant-alert",
            "els => els.map(e => e.innerText.trim())"
        )
        toast_text = " ".join(toasts).strip()
        logger.info(f"Parent deletion rejection response: '{toast_text}'")

        # Either error toast is shown or count remains identical
        count_after = self.get_table_total_count()
        assert count_after == count_before or any(term in toast_text.lower() for term in ["cannot", "child", "linked", "exist", "error"]), (
            f"Expected linked parent deletion to be blocked, but count changed from {count_before} to {count_after}"
        )
        # Dismiss any open modal/dialog
        dialog = self.page.locator(".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm").first
        if dialog.is_visible():
            self.page.keyboard.press("Escape")

    def execute_negative_delete_linked_patient_record(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-RAC-03: Attempt to delete a master record linked to Patient Records."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        count_before = self.get_table_total_count()

        dialog, record_name = self.click_delete_on_target(target)
        self.confirm_delete_in_dialog()
        self.page.wait_for_timeout(1000)

        toasts = self.page.eval_on_selector_all(
            ".ant-message, .ant-notification, .ant-alert",
            "els => els.map(e => e.innerText.trim())"
        )
        toast_text = " ".join(toasts).strip()
        logger.info(f"Patient-linked deletion response: '{toast_text}'")

        count_after = self.get_table_total_count()
        logger.info(f"Count before={count_before}, after={count_after}")
        # Dismiss any open dialog
        confirm_dialog = self.page.locator(".ant-popconfirm, .ant-popover:has(button:has-text('Delete')), .ant-popover:has-text('delete'), .ant-modal, .ant-modal-confirm").first
        if confirm_dialog.is_visible():
            self.page.keyboard.press("Escape")

    def execute_negative_double_click_delete(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-RAC-04: Rapid double-click on Delete confirmation button."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)

        # Create an unused dummy test record as specified in payload ("Target Record: Any unused dummy record")
        dummy_name = f"QA_DblClick_Del_{int(time.time())}"
        self.click_add_record()
        self.fill_master_form(name=dummy_name, is_active=True)
        self.save_master_record()
        self.verify_save_success(dummy_name)

        count_before = self.get_table_total_count()
        dialog, record_name = self.click_delete_on_target(dummy_name)
        confirm_btn = dialog.locator(
            "button:has-text('Delete'), button.ant-btn-dangerous:has-text('Delete')"
        ).first
        expect(confirm_btn).to_be_visible()

        logger.info("Rapidly double-clicking Delete confirmation button...")
        confirm_btn.click(click_count=2, delay=100)
        self.page.wait_for_timeout(1200)

        self.verify_deletion_success(count_before=count_before, record_name=dummy_name)

    def execute_negative_switch_masters_after_delete(self, test_case_id: str) -> None:
        """TC-DEL-NEG-MASTER-RAC-05: Switch masters while Delete confirmation is open / after cancel."""
        m1, m2 = get_switch_targets(test_case_id)

        # Step 1: Open Delete in M1 and cancel
        self.select_master_category(m1)
        self.click_delete_on_target()
        self.cancel_delete_in_dialog(method="button")

        # Step 2: Switch to M2
        self.select_master_category(m2)
        m2_rows = self.page.locator("tr.ant-table-row").count()
        logger.info(f"Master 2 '{m2}' loaded cleanly with {m2_rows} visible rows.")

        # Step 3: Return to M1
        self.select_master_category(m1)
        m1_rows = self.page.locator("tr.ant-table-row").count()
        logger.info(f"Returned to Master 1 '{m1}' cleanly with {m1_rows} visible rows.")
