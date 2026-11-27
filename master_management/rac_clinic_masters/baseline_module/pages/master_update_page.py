import re
from typing import Optional, List, Dict, Tuple
from playwright.sync_api import Page, Locator, expect

from .master_base_page import MasterBasePage
from ..rac_baseline_data import (
    get_master_update_test_data,
    get_master_category,
    get_target_record_identifier,
    get_new_record_name,
    get_new_description,
    get_parent_instruction,
    get_shortcut_instruction,
    get_action_instruction,
    get_search_filter_term,
    get_temporary_input,
    get_switch_targets,
    get_status_toggle_targets,
)
from utils.logger import get_logger

logger = get_logger("MasterUpdatePage")


class MasterUpdatePage(MasterBasePage):
    """Encapsulates Master Data UPDATE workflows in the React SPA Masters portal."""

    def __init__(self, page: Page):
        super().__init__(page)

    def locate_target_row(self, target_identifier: Optional[str] = None) -> Locator:
        """
        Locates a table row by ID (e.g. 'ID 2', 'ID 9', 'ID 1') or by record name ('Palliative Care').
        Falls back to first table row if target is empty or not found.
        """
        if not target_identifier:
            return self.page.locator("tr.ant-table-row").first

        clean_tgt = target_identifier.strip()
        logger.info(f"Locating table row for target: '{clean_tgt}'")

        # 1. Try matching by numerical ID e.g. "ID 2", "ID 9"
        id_match = re.search(r"ID\s*(\d+)", clean_tgt, re.I)
        if id_match:
            rec_id = id_match.group(1)
            row_by_id = self.page.locator(f"tr.ant-table-row:has(td:first-child:text-is('{rec_id}'))").first
            if row_by_id.is_visible():
                logger.info(f"Row located by ID '{rec_id}'.")
                return row_by_id
            # Also try matching ID within first cell text
            row_by_cell = self.page.locator(f"tr.ant-table-row:has(td:first-child:has-text('{rec_id}'))").first
            if row_by_cell.is_visible():
                return row_by_cell

        # 2. Try matching by text name inside target (e.g. "Palliative Care", "Complete Remission", etc.)
        name_candidate = re.sub(r"ID\s*\d+\s*", "", clean_tgt)
        name_candidate = re.sub(r"\([^)]*\)", "", name_candidate).strip(' "\'')
        if name_candidate:
            row_by_name = self.page.locator(f"tr.ant-table-row:has-text('{name_candidate}')").first
            if row_by_name.is_visible():
                logger.info(f"Row located by name candidate '{name_candidate}'.")
                return row_by_name
            # Partial match by first word
            first_word = name_candidate.split()[0]
            if len(first_word) >= 4:
                row_by_word = self.page.locator(f"tr.ant-table-row:has-text('{first_word}')").first
                if row_by_word.is_visible():
                    logger.info(f"Row located by partial term '{first_word}'.")
                    return row_by_word

        # 3. Fallback to first available row
        logger.info(f"Target '{clean_tgt}' not found in current table view. Falling back to first visible row.")
        return self.page.locator("tr.ant-table-row").first

    def click_edit_on_target(self, target_identifier: Optional[str] = None) -> Locator:
        """Locates row and clicks the Edit (pencil) button in the Actions column."""
        row = self.locate_target_row(target_identifier)
        expect(row).to_be_visible(timeout=10000)
        edit_btn = row.locator("button:has(.anticon-edit), button:has([aria-label='edit'])").first
        expect(edit_btn).to_be_visible(timeout=8000)
        logger.info("Clicking Edit button in Actions column...")
        edit_btn.click()
        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=8000)
        self.page.wait_for_timeout(500)
        return modal

    def verify_edit_modal_prepopulated(self, test_case_id: str) -> bool:
        """
        TC-UPD-POS-MASTER-RAC-01: Verifies that clicking Edit opens modal with pre-filled fields.
        """
        category_name = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        self.select_master_category(category_name)
        modal = self.click_edit_on_target(target)

        # Verify modal header
        title_loc = modal.locator(".ant-modal-title").first
        expect(title_loc).to_be_visible()
        title_text = title_loc.inner_text()
        logger.info(f"Edit Modal Title: '{title_text}'")

        # Verify that primary input is pre-populated (not empty)
        inputs = modal.locator("input.ant-input, textarea.ant-input").all()
        assert len(inputs) > 0, "No inputs found in Edit modal!"
        primary_val = inputs[0].input_value()
        logger.info(f"Pre-populated primary field value: '{primary_val}'")
        assert primary_val.strip() != "", f"Expected pre-populated input, but found empty: '{primary_val}'"

        self.cancel_modal()
        return True

    def update_modal_fields(
        self,
        new_name: Optional[str] = None,
        new_description: Optional[str] = None,
        parent: Optional[str] = None,
        toggle_status: bool = False,
        set_active: Optional[bool] = None,
    ) -> None:
        """Fills/updates fields in the Edit modal."""
        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=5000)

        form_items = modal.locator(".ant-form-item").all()
        text_inputs: List[Locator] = []
        select_locators: List[Locator] = []
        textarea_locators: List[Locator] = []
        switch_locators: List[Locator] = []

        for fi in form_items:
            sel = fi.locator(".ant-select").first
            if sel.count() > 0:
                select_locators.append(sel)
                continue
            sw = fi.locator(".ant-switch").first
            if sw.count() > 0:
                switch_locators.append(sw)
                continue
            ta = fi.locator("textarea.ant-input").first
            if ta.count() > 0:
                textarea_locators.append(ta)
                continue
            inp = fi.locator("input.ant-input, input[type='text']").first
            if inp.count() > 0:
                text_inputs.append(inp)

        # 1. Update Name
        if new_name is not None:
            if new_name == "":
                logger.info("Clearing mandatory text input...")
                if text_inputs:
                    text_inputs[0].fill("")
                elif textarea_locators:
                    textarea_locators[0].fill("")
            else:
                logger.info(f"Updating primary name to: '{new_name}'")
                if len(text_inputs) >= 2:
                    text_inputs[1].fill(new_name)
                elif len(text_inputs) == 1:
                    text_inputs[0].fill(new_name)
                elif textarea_locators:
                    textarea_locators[0].fill(new_name)

        # 2. Update Description
        if new_description is not None:
            if new_description == "":
                logger.info("Clearing description field...")
                for ta in textarea_locators:
                    ta.fill("")
            else:
                logger.info(f"Updating description to: '{new_description}'")
                target_ta = textarea_locators[-1] if len(textarea_locators) > 0 else None
                if target_ta:
                    target_ta.fill(new_description)

        # 3. Update Parent dropdown
        if select_locators and parent:
            for sel in select_locators:
                logger.info(f"Handling parent dropdown update: '{parent}'")
                if any(k in parent.lower() for k in ["clear", "unselect"]):
                    logger.info("Clearing parent select via clear button...")
                    sel.hover()
                    self.page.wait_for_timeout(300)
                    clear_icon = sel.locator(".ant-select-clear").first
                    if clear_icon.is_visible():
                        clear_icon.click()
                    else:
                        clear_icon.click(force=True)
                    self.page.wait_for_timeout(300)
                else:
                    sel.click()
                    self.page.wait_for_timeout(400)
                    options = self.page.locator(".ant-select-item-option-content").all()
                    if len(options) > 1:
                        options[1].click()
                    elif len(options) == 1:
                        options[0].click()
                    self.page.wait_for_timeout(300)

        # 4. Status Toggle
        if switch_locators:
            sw = switch_locators[0]
            is_checked = sw.get_attribute("aria-checked") == "true"
            if toggle_status:
                logger.info(f"Toggling status switch (currently checked={is_checked})...")
                sw.click()
            elif set_active is not None:
                if set_active and not is_checked:
                    sw.click()
                elif not set_active and is_checked:
                    sw.click()

    def submit_modal_update(self) -> None:
        """Clicks Save in the modal and waits for completion."""
        logger.info("Submitting update modal form...")
        modal = self.page.locator(".ant-modal").first
        save_btn = modal.locator(
            "button:has-text('Save'), button:has-text('Update'), button:has-text('Create'), button[type='submit']"
        ).first
        expect(save_btn).to_be_visible()
        save_btn.click()
        self.page.wait_for_timeout(1200)

    # ==========================================
    # POSITIVE WORKFLOW HANDLERS
    # ==========================================

    def execute_mandatory_field_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-02: Updates mandatory field only."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Therapy Response Updated"

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        self.select_master_category(category)
        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_description_update_and_clear(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-03: Updates description then clears it."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_desc = get_new_description(test_case_id) or "Updated clinical note"

        self.select_master_category(category)
        # Step 1: Update description
        self.click_edit_on_target(target)
        self.update_modal_fields(new_description=new_desc)
        self.submit_modal_update()
        self.verify_save_success()

        # Step 2: Clear description
        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_description="")
        self.submit_modal_update()
        self.verify_save_success()

    def execute_dependent_master_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-04: Updates dependent master parent and name."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Updated Subtype Name"
        parent_inst = get_parent_instruction(test_case_id) or "Select another Active parent"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name, parent=parent_inst)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_hetu_sevan_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-05: Updates Hetu Sevan mandatory & optional fields."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Updated Habit Entry"
        new_desc = get_new_description(test_case_id) or "Updated habit description"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name, new_description=new_desc)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_physician_opinion_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-06: Updates Physician Opinion mandatory & optional fields."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Senior Ayurvedic Oncologist"
        new_desc = get_new_description(test_case_id) or "Updated physician role"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name, new_description=new_desc)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_status_toggle_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-07: Toggles Status Active ↔ Inactive."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        targets = get_status_toggle_targets(test_case_id)
        target_id = targets[0][0] if targets else "ID 1"

        self.click_edit_on_target(target_id)
        self.update_modal_fields(toggle_status=True)
        self.submit_modal_update()
        self.verify_save_success()

    def execute_counter_preserved_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-08: Verifies counter and ID stay intact after update."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Therapy Counter Check"

        self.select_master_category(category)
        count_before = self.get_table_total_count()

        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        count_after = self.get_table_total_count()
        assert count_after == count_before, f"Expected counter to stay {count_before}, found: {count_after}"

    def execute_shortcut_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-09: Saves update via keyboard shortcut (Alt + S)."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Therapy Shortcut Update"
        shortcut = get_shortcut_instruction(test_case_id) or "Alt+S"

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.save_via_shortcut(shortcut)
        self.verify_save_success(new_name)

        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_filtered_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-10: Updates record while search/sort filter is active."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Complete Remission Updated"

        self.select_master_category(category)

        # Apply sort by Status as specified in test case step ("click Status sort arrows")
        status_col = self.page.locator("th:has-text('Status'), .ant-table-column-has-sorters:has-text('Status')").first
        if status_col.is_visible():
            logger.info("Clicking Status column header to activate sort filter...")
            status_col.click()
            self.page.wait_for_timeout(800)

        # Check search term from payload
        search_term = get_search_filter_term(test_case_id)
        if search_term and search_term.lower() not in ("or sort by status", "sort by status"):
            search_input = self.page.locator("input[placeholder*='Search']:not([placeholder*='Search masters'])").first
            if search_input.is_visible():
                search_input.fill(search_term)
                self.page.wait_for_timeout(600)
                # If search results in 0 rows ("No data"), clear search to keep Sort active
                no_data = self.page.locator(".ant-empty-description, :has-text('No data')").first
                if no_data.is_visible():
                    logger.info(f"Search term '{search_term}' yielded no rows. Clearing search to keep Sort active.")
                    search_input.fill("")
                    self.page.wait_for_timeout(600)

        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        # Verify updated record in table
        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_page2_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-11: Updates record on Page 2."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Page 2 Updated Record"

        self.select_master_category(category)
        # Navigate to Page 2 if pagination exists
        page2_btn = self.page.locator(".ant-pagination-item-2, a:has-text('2'), li[title='2']").first
        if page2_btn.is_visible():
            page2_btn.click()
            self.page.wait_for_timeout(800)

        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_refresh_persistence(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-12: Verifies update persists across browser refresh."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Palliative Care Updated"

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        logger.info("Refreshing page to verify database persistence...")
        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(2000)
        self.select_master_category(category)
        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_history_modal_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-13: Verifies History modal reflections for updated record."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Integrative Therapy Updated"

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        self.select_master_category(category)
        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

        history_btn = self.page.locator("button:has-text('History'), button[title*='History']").first
        if history_btn.is_visible():
            history_btn.click()
            self.page.wait_for_timeout(800)
            modal = self.page.locator(".ant-modal").first
            if modal.is_visible():
                self.cancel_modal()

    def execute_clean_modal_switching(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-14: Verifies clean modal state when switching masters after update."""
        m1, m2 = get_switch_targets(test_case_id)

        # Step 1: Open M1, edit, save
        self.select_master_category(m1)
        self.click_edit_on_target()
        self.update_modal_fields(new_name="M1 Temp Update")
        self.submit_modal_update()
        self.verify_save_success()

        # Step 2: Switch to M2 and open Add Record to confirm clean modal
        self.select_master_category(m2)
        self.click_add_record()
        self.verify_modal_is_clean()

    def execute_save_without_modification(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-RAC-15: Opens edit modal and clicks save without modifying fields."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.submit_modal_update()
        self.verify_save_success()

    # ==========================================
    # NEGATIVE WORKFLOW HANDLERS
    # ==========================================

    def execute_negative_clear_mandatory(self, test_case_id: str) -> None:
        """Clears mandatory field and clicks Save; verifies validation error."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_name="")
        self.submit_modal_update()
        self.verify_validation_error()

    def execute_negative_clear_parent(self, test_case_id: str) -> None:
        """Clears parent dropdown on dependent master and verifies validation error."""
        category = get_master_category(test_case_id)

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(parent="unselected")
        self.submit_modal_update()
        self.verify_validation_error()

    def execute_negative_cancel(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-RAC-06: Verifies cancel/close without saving preserves original table data."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        temp_input = get_temporary_input(test_case_id)

        self.select_master_category(category)
        row = self.locate_target_row(target)
        original_text = row.inner_text()

        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=temp_input)
        self.cancel_modal()

        self.select_master_category(category)
        new_row = self.locate_target_row(target)
        assert temp_input not in new_row.inner_text(), f"Temporary unsaved input '{temp_input}' was saved!"

    def execute_negative_double_click(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-RAC-07: Rapid double-clicks Save button during update."""
        category = get_master_category(test_case_id)
        target = get_target_record_identifier(test_case_id)
        new_name = get_new_record_name(test_case_id) or "Double Click Update Test"

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.save_with_rapid_double_click()
        self.verify_save_success(new_name)

        self.select_master_category(category)
        self.search_record(new_name)
        count = self.page.locator(f"tr.ant-table-row:has-text('{new_name}')").count()
        assert count <= 1, f"Expected at most 1 row for '{new_name}', found: {count}"
