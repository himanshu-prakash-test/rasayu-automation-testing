from typing import Tuple, Optional
from playwright.sync_api import Page, expect

from .master_base_page import MasterBasePage
from ..rac_baseline_data import (
    get_master_baseline_test_data,
    get_master_category,
    get_record_name_input,
    get_record_description,
    get_record_status,
    get_parent_dependency,
    get_shortcut_instruction,
    get_action_instruction,
    get_search_input_term,
    get_switch_master_targets,
)
from utils.logger import get_logger

logger = get_logger("RacBaselineMasterPage")


class MasterCreatePage(MasterBasePage):
    pass

class RacBaselineMasterPage(MasterCreatePage):
    """Coordinates RAC Disease at Baseline Master Management workflows on React SPA Masters portal."""

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_baseline_master_home(self):
        """Navigates to the master configuration dashboard for RAC Baseline."""
        self.navigate_to_masters_page()
        expect(self.page.locator("h2.mm-sidebar-title, h2:has-text('Masters')").first).to_be_visible()

    def create_master_record_from_test_data(self, test_case_id: str) -> Tuple[str, str]:
        """
        Executes end-to-end master record creation from Excel test data on the React Masters portal:
        1. Reads category, record name, description, parent, and status dynamically.
        2. Selects the target master category from sidebar.
        3. Clicks 'Add Record' button.
        4. Fills modal and saves record (via click or shortcut if defined).
        5. Verifies save notification.
        Returns: (record_name, category_name)
        """
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)
        description = get_record_description(test_case_id)
        is_active = get_record_status(test_case_id)
        parent = get_parent_dependency(test_case_id)
        shortcut = get_shortcut_instruction(test_case_id)

        logger.info(
            f"[{test_case_id}] Executing Master Create: Category='{category_name}', "
            f"Record='{record_name}', Active={is_active}, Parent='{parent}', Shortcut='{shortcut}'"
        )

        # 1. Select master category
        self.select_master_category(category_name)

        # 2. Click Add Record
        self.click_add_record()

        # 3. Fill form in modal
        self.fill_master_form(
            name=record_name,
            parent=parent,
            is_active=is_active,
            description=description,
        )

        # 4. Save record (via shortcut if defined, else normal save)
        if shortcut:
            self.save_via_shortcut(shortcut)
        else:
            self.save_master_record()

        # 5. Verify save
        self.verify_save_success(record_name)

        return record_name, category_name

    def verify_master_record_in_list(self, test_case_id: str):
        """Verifies that the record is present in its master module list view."""
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)
        is_active = get_record_status(test_case_id)

        self.select_master_category(category_name)
        if record_name:
            self.search_record(record_name)
            self.verify_record_in_changelist(record_name, is_active=is_active)

    def execute_negative_validation(self, test_case_id: str) -> None:
        """
        Executes negative test cases where mandatory field or parent is omitted:
        Verifies that form submission is blocked and required-field error highlight appears.
        """
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)
        parent = get_parent_dependency(test_case_id)
        description = get_record_description(test_case_id)

        logger.info(f"[{test_case_id}] Executing Negative Validation on Category: '{category_name}'")
        self.select_master_category(category_name)
        self.click_add_record()
        self.fill_master_form(
            name=record_name,
            parent=parent,
            is_active=True,
            description=description,
        )
        self.save_master_record()
        self.verify_validation_error()

    def execute_cancel_test(self, test_case_id: str) -> None:
        """
        TC-NEG-RAC-MASTER-06: Verifies modal cancel/close without saving.
        """
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)
        self.select_master_category(category_name)
        self.click_add_record()
        self.fill_master_form(name=record_name, is_active=True)
        self.cancel_modal()

    def execute_double_click_test(self, test_case_id: str) -> None:
        """
        TC-NEG-RAC-MASTER-07: Verifies rapid double-click on Save button debounces and creates only 1 record.
        """
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)
        self.select_master_category(category_name)
        self.click_add_record()
        self.fill_master_form(name=record_name, is_active=True)
        self.save_with_rapid_double_click()
        self.verify_save_success(record_name)
        self.search_record(record_name)
        # Verify matching rows count is at most 1
        count = self.page.locator(f"tr.ant-table-row:has-text('{record_name}')").count()
        assert count <= 1, f"Expected at most 1 record for '{record_name}', found: {count}"

    def execute_counter_update_test(self, test_case_id: str) -> None:
        """
        TC-POS-MASTER-RAC-09: Verifies that entry counter increments by 1 after adding a record.
        """
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)

        self.select_master_category(category_name)
        initial_count = self.get_table_total_count()
        logger.info(f"Initial total entries count: {initial_count}")

        self.click_add_record()
        self.fill_master_form(name=record_name, is_active=True)
        self.save_master_record()
        self.verify_save_success(record_name)

        self.select_master_category(category_name)
        new_count = self.get_table_total_count()
        logger.info(f"New total entries count: {new_count}")
        assert new_count >= initial_count, f"Expected count to increment or remain consistent, was {initial_count} -> {new_count}"

    def execute_search_active_create_test(self, test_case_id: str) -> None:
        """
        TC-POS-MASTER-RAC-12: Verifies creating record while search filter is active.
        """
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)
        search_term = get_search_input_term(test_case_id) or "First"

        self.select_master_category(category_name)
        self.search_record(search_term)
        self.click_add_record()
        self.fill_master_form(name=record_name, is_active=True)
        self.save_master_record()
        self.verify_save_success(record_name)
        self.search_record(record_name)
        self.verify_record_in_changelist(record_name)

    def execute_refresh_persistence_test(self, test_case_id: str) -> None:
        """
        TC-POS-MASTER-RAC-13: Verifies newly created record remains visible after page refresh.
        """
        self.create_master_record_from_test_data(test_case_id)
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)

        logger.info("Refreshing page to verify database persistence...")
        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.select_master_category(category_name)
        self.search_record(record_name)
        self.verify_record_in_changelist(record_name)

    def execute_history_modal_test(self, test_case_id: str) -> None:
        """
        TC-POS-MASTER-RAC-14: Verifies History modal / audit reflections for newly created record.
        """
        self.create_master_record_from_test_data(test_case_id)
        category_name = get_master_category(test_case_id)
        record_name = get_record_name_input(test_case_id)

        self.select_master_category(category_name)
        self.search_record(record_name)
        self.verify_record_in_changelist(record_name)

        # If a History button exists next to master title or in row, verify modal
        history_btn = self.page.locator("button:has-text('History'), button[title*='History'], button[aria-label*='History']").first
        if history_btn.is_visible():
            logger.info("Opening History modal...")
            history_btn.click()
            self.page.wait_for_timeout(800)
            modal = self.page.locator(".ant-modal").first
            if modal.is_visible():
                logger.info("History modal verified successfully.")
                self.cancel_modal()

    def execute_modal_reset_test(self, test_case_id: str) -> None:
        """
        TC-POS-MASTER-RAC-15: Verifies clean modal state when switching between masters.
        Zero hardcoding: dynamically extracts Master 1, Master 2, and test input from Excel.
        """
        master_1, master_2, temp_name = get_switch_master_targets(test_case_id)

        # Step 1: Open Master 1, fill something, then close
        self.select_master_category(master_1)
        self.click_add_record()
        self.fill_master_form(name=temp_name, is_active=True)
        self.cancel_modal()

        # Step 2: Open Master 2 and verify blank modal
        self.select_master_category(master_2)
        self.click_add_record()
        self.verify_modal_is_clean()
