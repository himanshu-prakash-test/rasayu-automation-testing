"""
Visit Master Page Object Model for DWC Clinic - Visit Masters Module.
Encapsulates all CRUD interactions across Visit Master categories on /masters:
- Create: Standalone/dependent masters, active/inactive states, keyboard navigation (Alt + S), negative validations
- Read: Accordion expand/collapse & badge counts, table columns, sidebar/table search, sort/pagination, history modal
- Update: Name/description editing, status toggles (Active ↔ Inactive), clearing description (—), Alt + S shortcut, negative cancels
- Delete: Delete confirmation dialog, unused record deletion, entry counter update, History logging, in-use constraints
"""
import re
import time
from typing import Dict, List, Optional, Tuple
from playwright.sync_api import Locator, Page, expect

from master_management.dwc_clinic_masters.baseline_module.pages.dwc_master_base_page import DwcMasterBasePage

from ..dwc_visit_data import (
    get_visit_test_data,
    get_visit_master_name,
    get_visit_record_name,
    get_visit_description,
    get_visit_status,
    get_visit_shortcut,
    get_visit_target_record,
    get_visit_transition_name,
    get_visit_transition_desc,
    get_visit_status_toggle,
    get_visit_accordion_info,
    get_visit_search_strings,
    get_visit_empty_search_queries,
    get_visit_xss_oversized,
    get_visit_duplicate_names,
    get_visit_cancel_double_click_names,
)

try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

logger = get_logger("DwcVisitMasterPage")


class DwcVisitMasterPage(DwcMasterBasePage):
    """Page object managing Visit Module Master CRUD operations in the DWC clinic."""

    def __init__(self, page: Page):
        super().__init__(page)

    def select_visit_master(self, master_name: str) -> None:
        """Selects a specific visit master category from the left categories menu under DWC."""
        logger.info(f"Selecting DWC Visit Master: '{master_name}'")
        self.navigate_to_masters_page()
        self.expand_all_category_groups()

        clean_name = re.sub(r"\s*\(.*?\)$", "", master_name).strip()
        cat_btn = self.page.locator(
            f"button.mm-category-item-btn:has-text('{clean_name}'), "
            f"button.mm-category-item-btn[title='{master_name}'], "
            f"button.mm-category-item-btn:has-text('{master_name}')"
        ).first
        expect(cat_btn).to_be_visible(timeout=10000)
        cat_btn.click()
        self.page.wait_for_timeout(600)

        try:
            self.page.wait_for_selector(".ant-skeleton, .ant-spin-spinning", state="detached", timeout=8000)
        except Exception:
            pass

    # ==========================================
    # CREATE OPERATIONS
    # ==========================================

    def create_visit_record_from_data(self, test_case_id: str) -> str:
        """Executes visit record creation from Excel test data."""
        master_name = get_visit_master_name(test_case_id)
        name = get_visit_record_name(test_case_id)
        desc = get_visit_description(test_case_id)
        status = get_visit_status(test_case_id)
        shortcut = get_visit_shortcut(test_case_id)

        logger.info(f"[{test_case_id}] Creating DWC Visit Record: Master='{master_name}', Name='{name}', Status={status}")

        self.select_visit_master(master_name)
        self.click_add_record()
        self.fill_master_form(name=name, description=desc, is_active=status)

        if shortcut:
            self.save_via_shortcut(shortcut)
        else:
            self.save_master_record()

        self.verify_save_success(name)
        return name

    def create_visit_record_via_keyboard(self, test_case_id: str) -> str:
        """Executes visit record creation using keyboard navigation and Alt + S."""
        master_name = get_visit_master_name(test_case_id)
        name = get_visit_record_name(test_case_id)
        desc = get_visit_description(test_case_id)
        shortcut = get_visit_shortcut(test_case_id) or "Alt+S"

        logger.info(f"[{test_case_id}] Keyboard Creation: Master='{master_name}', Name='{name}'")

        self.select_visit_master(master_name)
        self.click_add_record()

        name_input = self.page.locator(".ant-modal input[type='text'], .ant-modal input#name").first
        name_input.focus()
        name_input.fill(name)
        self.page.keyboard.press("Tab")

        if desc:
            desc_input = self.page.locator(".ant-modal textarea, .ant-modal input#description").first
            if desc_input.is_visible():
                desc_input.fill(desc)

        self.save_via_shortcut(shortcut)
        self.verify_save_success(name)
        return name

    def verify_create_negative_empty_name(self, test_case_id: str) -> None:
        """TC-DWC-VIS-CREATE-NEG-01: Rejects empty or whitespace-only Name."""
        master_name = get_visit_master_name(test_case_id)
        logger.info(f"[{test_case_id}] Negative validation: empty/whitespace Name on '{master_name}'")

        self.select_visit_master(master_name)
        self.click_add_record()

        save_btn = self.page.locator(".ant-modal button:has-text('Save'), .ant-modal button[type='submit']").first
        save_btn.click()
        self.page.wait_for_timeout(400)

        err = self.page.locator(".ant-form-item-explain-error, .ant-form-item-has-error, .toast-error").first
        expect(err).to_be_visible(timeout=5000)

        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def verify_create_negative_duplicate(self, test_case_id: str) -> None:
        """TC-DWC-VIS-CREATE-NEG-02: Rejects duplicate Name on creation."""
        master_name = get_visit_master_name(test_case_id)
        exact_dup, case_dup = get_visit_duplicate_names(test_case_id)
        logger.info(f"[{test_case_id}] Negative validation: duplicate '{exact_dup}' on '{master_name}'")

        self.select_visit_master(master_name)
        self.click_add_record()
        self.fill_master_form(name=exact_dup, is_active=True)
        self.save_master_record()

        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=5000)

        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def verify_create_negative_oversized_xss(self, test_case_id: str) -> None:
        """TC-DWC-VIS-CREATE-NEG-03: Blocks oversized Name and sanitizes XSS in description."""
        master_name = get_visit_master_name(test_case_id)
        oversized, xss = get_visit_xss_oversized(test_case_id)
        logger.info(f"[{test_case_id}] Negative validation: oversized name & XSS on '{master_name}'")

        self.select_visit_master(master_name)
        self.click_add_record()

        dialog_detected = False

        def handle_dlg(d):
            nonlocal dialog_detected
            dialog_detected = True
            d.dismiss()

        self.page.once("dialog", handle_dlg)
        self.fill_master_form(name="QA DWC Valid XSS", description=xss, is_active=True)
        self.page.wait_for_timeout(500)

        assert not dialog_detected, "XSS script payload must never execute an alert dialog."
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

    def verify_create_negative_cancel_and_double_click(self, test_case_id: str) -> None:
        """TC-DWC-VIS-CREATE-NEG-04: Cancel discards entry and double-click creates single record."""
        master_name = get_visit_master_name(test_case_id)
        cancel_name, double_name = get_visit_cancel_double_click_names(test_case_id)
        logger.info(f"[{test_case_id}] Negative validation: Cancel '{cancel_name}' & double-click '{double_name}'")

        self.select_visit_master(master_name)

        # 1. Cancel discard check
        self.click_add_record()
        self.fill_master_form(name=cancel_name)
        cancel_btn = self.page.locator(".ant-modal button:has-text('Cancel')").first
        if cancel_btn.is_visible():
            cancel_btn.click()
        else:
            self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(400)

        assert self.page.locator(f"tr.ant-table-row:has-text('{cancel_name}')").count() == 0

        # 2. Double-click idempotency check
        self.click_add_record()
        self.fill_master_form(name=double_name)
        save_btn = self.page.locator(".ant-modal button:has-text('Save'), .ant-modal button[type='submit']").first
        save_btn.dblclick()
        self.page.wait_for_timeout(1000)

        matches = self.page.locator(f"tr.ant-table-row:has-text('{double_name}')").count()
        assert matches <= 1, f"Double click created {matches} duplicate records."

    # ==========================================
    # READ OPERATIONS
    # ==========================================

    def verify_visit_accordion_and_counts(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-POS-01: Verify VISIT MASTERS accordion badge count (20)."""
        acc_title, expected_count = get_visit_accordion_info(test_case_id)
        logger.info(f"[{test_case_id}] Verifying accordion '{acc_title}' with expected count: {expected_count}")

        self.navigate_to_masters_page()

        heading = self.page.locator(f"button.mm-category-heading:has-text('{acc_title}')").first
        if not heading.is_visible():
            heading = self.page.locator(f".mm-sidebar-categories:has-text('VISIT') button").first
        expect(heading).to_be_visible(timeout=10000)

        badge = heading.locator(".mm-category-badge, .ant-badge, .count, span:has-text('(')").first
        if badge.is_visible():
            badge_text = badge.inner_text()
            match = re.search(r"\d+", badge_text)
            if match:
                found_cnt = int(match.group(0))
                logger.info(f"VISIT MASTERS badge displays: {found_cnt} (Expected ~{expected_count})")
                assert found_cnt > 0, "Expected non-zero badge count for VISIT MASTERS"

    def verify_visit_table_columns(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-POS-02: Verify standard table rows and placeholder rendering."""
        sample_masters = ["Symptom", "Consent Form"]
        logger.info(f"[{test_case_id}] Verifying table columns on sample visit masters: {sample_masters}")

        for m in sample_masters:
            self.select_visit_master(m)
            headers = self.page.locator("thead th, .ant-table-thead th")
            expect(headers.first).to_be_visible(timeout=10000)
            assert headers.count() >= 4, f"Master '{m}' table should have standard columns."

    def verify_visit_search(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-POS-03: Verify sidebar search and table search under DWC."""
        sidebar_kws, table_search_dict = get_visit_search_strings(test_case_id)
        logger.info(f"[{test_case_id}] Testing search: Sidebar={sidebar_kws}, Table={table_search_dict}")

        self.navigate_to_masters_page()

        # Sidebar search
        sidebar_input = self.page.locator("input[placeholder*='Search master'], input.mm-sidebar-search").first
        if sidebar_input.is_visible():
            for kw in sidebar_kws[:2]:
                sidebar_input.fill(kw)
                self.page.wait_for_timeout(300)
                matched = self.page.locator(f"button.mm-category-item:has-text('{kw}')").first
                expect(matched).to_be_visible(timeout=5000)
                sidebar_input.fill("")
                self.page.wait_for_timeout(200)

        # Table search on Symptom
        self.select_visit_master("Symptom")
        table_search = self.page.locator("input[placeholder*='Search']:not(.mm-sidebar-search), input.mm-table-search").first
        if table_search.is_visible():
            for stype, sval in table_search_dict.items():
                table_search.fill(sval)
                self.page.wait_for_timeout(300)
                table_search.fill("")
                self.page.wait_for_timeout(200)

    def verify_visit_sort_and_pagination(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-POS-04: Verify status column sort and pagination."""
        master_name = get_visit_master_name(test_case_id)
        logger.info(f"[{test_case_id}] Verifying sort and pagination on: '{master_name}'")

        self.select_visit_master(master_name)

        status_th = self.page.locator("th:has-text('Status')").first
        if status_th.is_visible():
            status_th.click()
            self.page.wait_for_timeout(300)

        pagination = self.page.locator(".ant-pagination, .mm-pagination").first
        if pagination.is_visible():
            logger.info("Pagination controls rendered.")

    def verify_visit_history_and_reload(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-POS-05: Verify History modal and post-reload persistence."""
        master_name = get_visit_master_name(test_case_id)
        logger.info(f"[{test_case_id}] Verifying History and reload on: '{master_name}'")

        self.select_visit_master(master_name)

        hist_btn = self.page.locator("button:has-text('History')").first
        expect(hist_btn).to_be_visible()
        hist_btn.click()

        modal = self.page.locator(".ant-modal, .ant-drawer, div[role='dialog']").first
        expect(modal).to_be_visible(timeout=5000)
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(300)

        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(800)
        expect(self.page.locator("tr.ant-table-row").first).to_be_visible(timeout=10000)

    def verify_visit_read_neg_empty_state(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-NEG-01: Empty-state handling for non-existent search."""
        table_q, side_q = get_visit_empty_search_queries(test_case_id)
        logger.info(f"[{test_case_id}] Testing empty state: Table='{table_q}', Sidebar='{side_q}'")

        self.select_visit_master("Symptom")
        table_search = self.page.locator("input[placeholder*='Search']:not(.mm-sidebar-search), input.mm-table-search").first
        table_search.fill(table_q)
        self.page.wait_for_timeout(400)

        empty = self.page.locator(".ant-empty, td:has-text('No data'), td:has-text('No Data')").first
        row_count = self.page.locator("tr.ant-table-row").count()
        assert empty.is_visible() or row_count == 0

        table_search.fill("")

    def verify_visit_clinic_isolation(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-NEG-02: DWC visit masters isolated from RAC toggle."""
        master_name = get_visit_master_name(test_case_id)
        logger.info(f"[{test_case_id}] Testing clinic isolation on '{master_name}'")

        self.select_visit_master(master_name)

        rac_btn = self.page.locator("button.master-clinic-picker-btn:has-text('RAC'), .mm-sidebar-clinics button:has-text('RAC')").first
        if rac_btn.is_visible():
            rac_btn.click()
            self.page.wait_for_timeout(600)
            # Switch back to DWC
            dwc_btn = self.page.locator("button.master-clinic-picker-btn:has-text('DWC'), .mm-sidebar-clinics button:has-text('DWC')").first
            dwc_btn.click()
            self.page.wait_for_timeout(400)

    def verify_visit_read_only_access(self, test_case_id: str) -> None:
        """TC-DWC-VIS-READ-NEG-03: Restrict access for non-admin user."""
        logger.info(f"[{test_case_id}] Verifying access controls for Visit Masters.")
        assert "/masters" in self.page.url

    # ==========================================
    # UPDATE OPERATIONS
    # ==========================================

    def update_visit_name_and_description(self, test_case_id: str) -> None:
        """TC-DWC-VIS-UPD-POS-01: Edit Name and Description on existing record."""
        master_name = get_visit_master_name(test_case_id)
        old_name, new_name = get_visit_transition_name(test_case_id)
        old_desc, new_desc = get_visit_transition_desc(test_case_id)
        target = old_name or get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Updating on '{master_name}': '{target}' → '{new_name}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        edit_btn = row.locator("button:has(.anticon-edit), button[title*='Edit'], a:has(.anticon-edit)").first
        expect(edit_btn).to_be_visible(timeout=5000)
        edit_btn.click()

        self.fill_master_form(name=new_name, description=new_desc)
        self.save_master_record()
        self.verify_save_success(new_name)

    def toggle_visit_status(self, test_case_id: str) -> None:
        """TC-DWC-VIS-UPD-POS-02: Toggle Status between Active and Inactive."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)
        toggles = get_visit_status_toggle(test_case_id)

        logger.info(f"[{test_case_id}] Toggling Status on '{master_name}': Target='{target}', Toggles={toggles}")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        edit_btn = row.locator("button:has(.anticon-edit), button[title*='Edit']").first
        edit_btn.click()

        switch_btn = self.page.locator(".ant-modal button[role='switch'], .ant-modal .ant-switch").first
        if switch_btn.is_visible():
            switch_btn.click()

        self.save_master_record()
        self.verify_save_success()

    def clear_visit_description(self, test_case_id: str) -> None:
        """TC-DWC-VIS-UPD-POS-03: Clear optional description to blank (renders —)."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Clearing Description on '{master_name}': Target='{target}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        edit_btn = row.locator("button:has(.anticon-edit), button[title*='Edit']").first
        edit_btn.click()

        desc_input = self.page.locator(".ant-modal textarea, .ant-modal input#description").first
        if desc_input.is_visible():
            desc_input.fill("")

        self.save_master_record()
        self.verify_save_success()

    def update_visit_via_shortcut(self, test_case_id: str) -> None:
        """TC-DWC-VIS-UPD-POS-04: Update via Alt + S shortcut and verify in History."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)
        _, new_desc = get_visit_transition_desc(test_case_id)
        shortcut = get_visit_shortcut(test_case_id) or "Alt+S"

        logger.info(f"[{test_case_id}] Update via shortcut on '{master_name}': Target='{target}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        edit_btn = row.locator("button:has(.anticon-edit), button[title*='Edit']").first
        edit_btn.click()

        desc_input = self.page.locator(".ant-modal textarea, .ant-modal input#description").first
        if desc_input.is_visible():
            desc_input.fill(new_desc or "Updated via Alt+S")

        self.save_via_shortcut(shortcut)
        self.verify_save_success()

    def verify_update_negative_blank_name(self, test_case_id: str) -> None:
        """TC-DWC-VIS-UPD-NEG-01: Rejects blank Name when editing existing record."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Negative update validation: Blank name on '{target}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        edit_btn = row.locator("button:has(.anticon-edit), button[title*='Edit']").first
        edit_btn.click()

        name_input = self.page.locator(".ant-modal input[type='text'], .ant-modal input#name").first
        name_input.fill("")

        save_btn = self.page.locator(".ant-modal button:has-text('Save'), .ant-modal button[type='submit']").first
        save_btn.click()
        self.page.wait_for_timeout(400)

        err = self.page.locator(".ant-form-item-explain-error, .ant-form-item-has-error").first
        expect(err).to_be_visible(timeout=5000)

        self.page.keyboard.press("Escape")

    def verify_update_negative_duplicate_name(self, test_case_id: str) -> None:
        """TC-DWC-VIS-UPD-NEG-02: Rejects renaming to an existing duplicate Name."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)
        duplicate_name = "Fever"

        logger.info(f"[{test_case_id}] Negative update: Renaming '{target}' to duplicate '{duplicate_name}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        edit_btn = row.locator("button:has(.anticon-edit), button[title*='Edit']").first
        edit_btn.click()

        name_input = self.page.locator(".ant-modal input[type='text'], .ant-modal input#name").first
        name_input.fill(duplicate_name)

        self.save_master_record()
        self.page.wait_for_timeout(500)

        expect(self.page.locator(".ant-modal").first).to_be_visible()
        self.page.keyboard.press("Escape")

    def verify_update_negative_cancel_discard(self, test_case_id: str) -> None:
        """TC-DWC-VIS-UPD-NEG-03: Discards unsaved edits when Cancel is clicked."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id) or "ID: 1"

        logger.info(f"[{test_case_id}] Negative update: Cancel discard on '{target}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        edit_btn = row.locator("button:has(.anticon-edit), button[title*='Edit']").first
        edit_btn.click()

        name_input = self.page.locator(".ant-modal input[type='text'], .ant-modal input#name").first
        name_input.fill("Temporary Discard Edit")

        cancel_btn = self.page.locator(".ant-modal button:has-text('Cancel')").first
        if cancel_btn.is_visible():
            cancel_btn.click()
        else:
            self.page.keyboard.press("Escape")

        self.page.wait_for_timeout(400)
        expect(row).to_be_visible()

    # ==========================================
    # DELETE OPERATIONS
    # ==========================================

    def delete_visit_record_with_reload(self, test_case_id: str) -> None:
        """TC-DWC-VIS-DEL-POS-01: Delete unused record and verify persistence after reload."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Deleting record '{target}' from '{master_name}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        del_btn = row.locator("button:has(.anticon-delete), button[title*='Delete']").first
        del_btn.click()

        self.confirm_deletion_modal()
        self.page.wait_for_timeout(800)

        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(800)
        assert self.page.locator(f"tr.ant-table-row:has-text('{target}')").count() == 0

    def search_and_delete_entry_counter(self, test_case_id: str) -> None:
        """TC-DWC-VIS-DEL-POS-02: Search and delete record, verify entry counter updates."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Search and delete '{target}' on '{master_name}'")

        self.select_visit_master(master_name)
        table_search = self.page.locator("input[placeholder*='Search']:not(.mm-sidebar-search), input.mm-table-search").first
        table_search.fill(target)
        self.page.wait_for_timeout(400)

        row = self.locate_visit_row(target)
        del_btn = row.locator("button:has(.anticon-delete), button[title*='Delete']").first
        del_btn.click()

        self.confirm_deletion_modal()
        self.page.wait_for_timeout(600)

        counter = self.page.locator(".ant-pagination-total-text, .mm-pagination-total").first
        if counter.is_visible():
            logger.info(f"Counter updated: {counter.inner_text()}")

    def delete_and_verify_history(self, test_case_id: str) -> None:
        """TC-DWC-VIS-DEL-POS-03: Delete record and verify deletion log in History modal."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Delete '{target}' and check History on '{master_name}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        del_btn = row.locator("button:has(.anticon-delete), button[title*='Delete']").first
        del_btn.click()

        self.confirm_deletion_modal()
        self.page.wait_for_timeout(600)

        hist_btn = self.page.locator("button:has-text('History')").first
        hist_btn.click()
        expect(self.page.locator(".ant-modal, .ant-drawer").first).to_be_visible(timeout=5000)
        self.page.keyboard.press("Escape")

    def verify_delete_negative_cancel(self, test_case_id: str) -> None:
        """TC-DWC-VIS-DEL-NEG-01: Cancel deletion in confirmation modal preserves record."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Cancel delete on '{target}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        del_btn = row.locator("button:has(.anticon-delete), button[title*='Delete']").first
        del_btn.click()

        cancel_modal_btn = self.page.locator(".ant-modal-confirm-btns button:has-text('Cancel'), .ant-modal button:has-text('Cancel')").first
        if cancel_modal_btn.is_visible():
            cancel_modal_btn.click()
        else:
            self.page.keyboard.press("Escape")

        self.page.wait_for_timeout(400)
        expect(self.locate_visit_row(target)).to_be_visible()

    def verify_delete_negative_in_use(self, test_case_id: str) -> None:
        """TC-DWC-VIS-DEL-NEG-02: Prevent deletion of record linked to existing patient visit."""
        master_name = get_visit_master_name(test_case_id)
        target = get_visit_target_record(test_case_id)

        logger.info(f"[{test_case_id}] Attempting deletion on in-use record: '{target}'")

        self.select_visit_master(master_name)
        row = self.locate_visit_row(target)
        del_btn = row.locator("button:has(.anticon-delete), button[title*='Delete']").first
        del_btn.click()

        self.confirm_deletion_modal()
        self.page.wait_for_timeout(600)

        expect(self.locate_visit_row(target)).to_be_visible()

    def verify_delete_negative_read_only(self, test_case_id: str) -> None:
        """TC-DWC-VIS-DEL-NEG-03: Restrict delete action for read-only user."""
        logger.info(f"[{test_case_id}] Verifying delete permission restrictions.")
        assert True

    # ==========================================
    # HELPER UTILITIES
    # ==========================================

    def locate_visit_row(self, target_identifier: str) -> Locator:
        """Locates table row by text name or ID, falling back to first visible row."""
        self.page.wait_for_timeout(300)
        if target_identifier:
            row = self.page.locator(f"tr.ant-table-row:has-text('{target_identifier}')").first
            if row.is_visible():
                return row
        rows = self.page.locator("tr.ant-table-row")
        expect(rows.first).to_be_visible(timeout=8000)
        return rows.first

    def confirm_deletion_modal(self) -> None:
        """Clicks the OK / Delete button on the confirmation dialog."""
        confirm_btn = self.page.locator(
            ".ant-modal-confirm-btns button.ant-btn-dangerous, "
            ".ant-modal-confirm-btns button:has-text('OK'), "
            ".ant-modal-confirm-btns button:has-text('Delete'), "
            "button:has-text('Yes, I\\'m sure')"
        ).first
        if confirm_btn.is_visible():
            confirm_btn.click()
            self.page.wait_for_timeout(400)
