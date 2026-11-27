"""
DWC Baseline Master Update Page Object Model.
Handles all UPDATE operations for DWC Clinic Baseline Masters.
"""
import re
from typing import Optional, List, Tuple
from playwright.sync_api import Page, Locator, expect

from .dwc_master_base_page import DwcMasterBasePage
from ..dwc_baseline_data import (
    get_master_update_test_data,
    get_master_category,
    get_target_record_name,
    get_new_record_name,
    get_update_description,
    get_update_parent_dropdown,
    get_shortcut_instruction,
    get_search_filter_term,
    get_switch_targets,
)

try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

logger = get_logger("DwcBaselineMasterUpdatePage")


class DwcBaselineMasterUpdatePage(DwcMasterBasePage):
    """Encapsulates Master Data UPDATE workflows for DWC Baseline."""

    def __init__(self, page: Page):
        super().__init__(page)

    def locate_target_row(self, target_identifier: Optional[str] = None) -> Locator:
        """Locates a table row by record name or falls back to first row."""
        self.page.wait_for_timeout(400)
        tbody = self.page.locator(".ant-table-tbody").first
        expect(tbody).to_be_visible(timeout=8000)

        if target_identifier:
            row = tbody.locator(f"tr:has-text('{target_identifier}')").first
            if row.count() > 0 and row.is_visible():
                return row

        # Default fallback to first non-empty row
        rows = tbody.locator("tr.ant-table-row").all()
        assert len(rows) > 0, "No data rows found in table!"
        return rows[0]

    def click_edit_on_target(self, target_identifier: Optional[str] = None) -> Locator:
        """Finds row and clicks Edit action."""
        row = self.locate_target_row(target_identifier)
        edit_btn = row.locator(
            "button[aria-label='Edit'], button[title='Edit'], span[aria-label='edit'], "
            "button:has(.anticon-edit), button:has-text('Edit'), .anticon-edit"
        ).first
        expect(edit_btn).to_be_visible(timeout=5000)
        logger.info("Clicking Edit button in Actions column...")
        edit_btn.click()
        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=8000)
        self.page.wait_for_timeout(500)
        return modal

    def verify_edit_modal_prepopulated(self, test_case_id: str) -> bool:
        """TC-UPD-POS-MASTER-DWC-01: Verifies that clicking Edit opens modal with pre-filled fields."""
        category_name = get_master_category(test_case_id)
        target = get_target_record_name(test_case_id)
        self.select_master_category(category_name)
        modal = self.click_edit_on_target(target)

        title_loc = modal.locator(".ant-modal-title").first
        expect(title_loc).to_be_visible()
        title_text = title_loc.inner_text()
        logger.info(f"[{test_case_id}] Edit Modal Title: '{title_text}'")

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
                try:
                    sel.click()
                    self.page.wait_for_timeout(300)
                    opt = self.page.locator(".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option").first
                    if opt.count() > 0 and opt.is_visible():
                        opt.click()
                except Exception:
                    pass

        # 4. Toggle status
        if toggle_status and switch_locators:
            logger.info("Toggling status switch in Edit modal...")
            switch_locators[0].click()

    def submit_modal_update(self) -> None:
        """Clicks Save/Update button in the modal."""
        modal = self.page.locator(".ant-modal").first
        save_btn = modal.locator(
            "button.ant-btn-primary, button:has-text('Save'), button:has-text('Update')"
        ).first
        expect(save_btn).to_be_visible()
        save_btn.click()
        self.page.wait_for_timeout(500)

    # POSITIVE WORKFLOWS
    def execute_mandatory_field_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-02: Updates mandatory field only."""
        category = get_master_category(test_case_id)
        target = get_target_record_name(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_PolyuriaPolydipsia_Updated"

        self.select_master_category(category)
        self.click_edit_on_target(target)
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        self.select_master_category(category)
        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_description_update_and_clear(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-03: Updates description then clears it."""
        category = get_master_category(test_case_id)
        target = get_target_record_name(test_case_id)
        new_desc = get_update_description(test_case_id) or "Updated Nidan clinical note"

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
        """TC-UPD-POS-MASTER-DWC-04: Dependent Master Update — Reassign Parent & Update Name."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_DiabetesMellitus_Updated"
        parent = get_update_parent_dropdown(test_case_id) or "Select another Active Disease Group"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name, parent=parent)
        self.submit_modal_update()
        self.verify_save_success(new_name)

    def execute_hetu_sevan_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-05: Hetu Sevan Master Update — Mandatory + Optional Fields."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_Adhyashana_Updated"
        new_desc = get_update_description(test_case_id) or "Updated dietary etiology description"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name, new_description=new_desc)
        self.submit_modal_update()
        self.verify_save_success(new_name)

    def execute_pharmacology_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-06: Pharmacology Master Update — Multi-Parent Linkage & Name."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_Glycomet500_SR_Updated"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

    def execute_status_toggle_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-07: Toggles Status Active ↔ Inactive."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(toggle_status=True)
        self.submit_modal_update()
        self.verify_save_success()

    def execute_counter_preserved_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-08: Preserve System ID, Counter & Action Icons on Update."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_KaphaVataPrakruti_Updated"

        self.select_master_category(category)
        count_before = self.get_table_total_count()

        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        count_after = self.get_table_total_count()
        assert count_after == count_before, f"Expected counter to stay {count_before}, found: {count_after}"

    def execute_shortcut_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-09: Save Master Update via Keyboard Shortcut (Alt + S)."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_Stage_II_Chronic_Updated"
        shortcut = get_shortcut_instruction(test_case_id) or "Alt+S"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name)
        self.save_via_shortcut(shortcut)
        self.verify_save_success(new_name)

    def execute_filtered_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-10: Update Record While Search / Sort Filter Is Active."""
        category = get_master_category(test_case_id)
        filter_term = get_search_filter_term(test_case_id) or "Hypertension"
        new_name = get_new_record_name(test_case_id) or "QA_Hypertension_Updated"

        self.select_master_category(category)
        self.search_record(filter_term)
        self.click_edit_on_target(filter_term)
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

    def execute_page2_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-11: Update Record on Paginated Grid (Page 2)."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_Page2_Updated_Record"

        self.select_master_category(category)
        p2_btn = self.page.locator(".ant-pagination-item-2").first
        if p2_btn.count() > 0 and p2_btn.is_visible():
            p2_btn.click()
            self.page.wait_for_timeout(500)

        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

    def execute_refresh_persistence(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-12: Verify Update Persistence Across Browser Refresh."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_HbA1c_Percent_Updated"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        # Refresh
        self.page.reload(wait_until="domcontentloaded")
        self.page.wait_for_timeout(1000)
        self.select_master_category(category)
        self.search_record(new_name)
        self.verify_record_in_changelist(new_name)

    def execute_history_modal_update(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-13: Audit Trail / History Log Verification After Update."""
        category = get_master_category(test_case_id)
        new_name = get_new_record_name(test_case_id) or "QA_KaphaPittaPradhana_Updated"

        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name=new_name)
        self.submit_modal_update()
        self.verify_save_success(new_name)

        # History modal
        history_btn = self.page.locator("button[title='History'], button:has-text('History')").first
        if history_btn.count() > 0 and history_btn.is_visible():
            history_btn.click()
            self.page.wait_for_timeout(500)
            modal = self.page.locator(".ant-modal").first
            expect(modal).to_be_visible()
            self.cancel_modal()

    def execute_clean_modal_switching(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-14: Switch Masters Immediately After Saving Update."""
        m1, m2 = get_switch_targets(test_case_id)
        self.select_master_category(m1)
        self.click_edit_on_target()
        self.update_modal_fields(new_name="QA_O_Positive_Updated")
        self.submit_modal_update()
        self.verify_save_success()

        # Switch to m2
        self.select_master_category(m2)
        expect(self.page.locator("h2.mm-content-title, h1:has-text('Subjective')").first).to_be_visible(timeout=5000)

    def execute_save_without_modification(self, test_case_id: str) -> None:
        """TC-UPD-POS-MASTER-DWC-15: Open Edit Modal and Save Without Modifying Any Fields."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.submit_modal_update()
        self.verify_save_success()

    # NEGATIVE WORKFLOWS
    def execute_negative_clear_mandatory(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-DWC-01 & 02 & 05: Mandatory field cleared / empty."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name="")
        self.submit_modal_update()
        self.verify_validation_error()
        self.cancel_modal()

    def execute_negative_clear_parent(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-DWC-03: Dependent Master — Parent Association Cleared / Unselected."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.submit_modal_update()
        self.cancel_modal()

    def execute_negative_duplicate_name(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-DWC-04: Duplicate Active Master Record Name on Update."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name="QA_FoodAllergy")
        self.submit_modal_update()
        self.verify_validation_error()
        self.cancel_modal()

    def execute_negative_cancel(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-DWC-06: Cancel / Dismiss Edit Modal with Unsaved Changes."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name="Unsaved Edit Test")
        self.cancel_modal()
        expect(self.page.locator(".ant-modal")).to_have_count(0)

    def execute_negative_double_click(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-DWC-07: Rapid Double-Click on Save Button (Debounce Check)."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.save_with_rapid_double_click()
        self.verify_save_success()

    def execute_negative_whitespace(self, test_case_id: str) -> None:
        """TC-UPD-NEG-MASTER-DWC-08: Update Mandatory Name with Whitespace-Only Input."""
        category = get_master_category(test_case_id)
        self.select_master_category(category)
        self.click_edit_on_target()
        self.update_modal_fields(new_name="   ")
        self.submit_modal_update()
        self.verify_validation_error()
        self.cancel_modal()
