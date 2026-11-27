"""
Physician & RAC Opinion Page Object:
Handles Tab 3 - Physician Opinion rows, Patient Opted toggles,
and RAC Management Plan (Approach, Intent, Objective, Treatment Criteria).
"""
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, Locator, expect

try:
    from shared_tools.base.base_page import BasePage
    from shared_tools.utils.logger import get_logger
except ImportError:
    from base.base_page import BasePage
    from utils.logger import get_logger

logger = get_logger("PhysicianRacPage")


class PhysicianRacPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page, context_name="PhysicianRacPage")

    # ---------- Physician Opinion ----------
    def fill_physician_opinion(self, ptype: str, opinion: str, patient_opted: str = "Yes", patient_reason: Optional[str] = None, physician_remark: Optional[str] = None, row_index: int = 0) -> None:
        logger.info(f"Filling Physician Opinion (row {row_index}): Type={ptype}, Opted={patient_opted}")
        # Type
        type_box = self.page.locator(".ant-form-item:has-text('Physician Type') .ant-select, select[name*='physician_type']").nth(row_index)
        if type_box.is_visible():
            type_box.click()
            self.page.wait_for_timeout(300)
            opt = self.page.locator(f".ant-select-item-option:has-text('{ptype}')").first
            if opt.is_visible():
                opt.click()

        # Opinion text
        op_input = self.page.locator("textarea[placeholder*='Opinion'], input[placeholder*='Opinion']").nth(row_index)
        if op_input.is_visible():
            self.safe_fill(op_input, opinion, "Physician Opinion")

        # Patient Opted toggle (Yes / No)
        opt_btn = self.page.locator(f".ant-form-item:has-text('Opted') button:has-text('{patient_opted}'), .ant-form-item:has-text('Opted') label:has-text('{patient_opted}')").nth(row_index)
        if opt_btn.is_visible():
            opt_btn.click()
            self.page.wait_for_timeout(300)

        # Patient Reason (if No or provided)
        if patient_reason:
            reason_box = self.page.locator("input[placeholder*='Reason'], textarea[placeholder*='Reason']").nth(row_index)
            if reason_box.is_visible():
                self.safe_fill(reason_box, patient_reason, "Patient Reason")

        # Physician Remark
        if physician_remark:
            rem_box = self.page.locator("textarea[placeholder*='Physician Remark']").nth(row_index)
            if rem_box.is_visible():
                self.safe_fill(rem_box, physician_remark, "Physician Remark")

    # ---------- RAC Management Plan ----------
    def fill_rac_management(self, approach: str, intent: Optional[str] = None, objective: Optional[str] = None, remark: Optional[str] = None, rac_comment: Optional[str] = None, treatment_criteria: Optional[str] = None) -> None:
        logger.info(f"Filling RAC Management: Approach={approach}, Intent={intent}, Objective={objective}")
        # Approach
        app_box = self.page.locator(".ant-form-item:has-text('Approach') .ant-select, select[name*='approach']").first
        if app_box.is_visible():
            app_box.click()
            self.page.wait_for_timeout(300)
            opt = self.page.locator(f".ant-select-item-option:has-text('{approach}')").first
            if opt.is_visible():
                opt.click()

        # Intent
        if intent:
            intent_box = self.page.locator(".ant-form-item:has-text('Intent') .ant-select, select[name*='intent']").first
            if intent_box.is_visible():
                intent_box.click()
                self.page.wait_for_timeout(300)
                opt = self.page.locator(f".ant-select-item-option:has-text('{intent}')").first
                if opt.is_visible():
                    opt.click()

        # Objective
        if objective:
            obj_box = self.page.locator(".ant-form-item:has-text('Objective') .ant-select, select[name*='objective']").first
            if obj_box.is_visible():
                obj_box.click()
                self.page.wait_for_timeout(300)
                opt = self.page.locator(f".ant-select-item-option:has-text('{objective}')").first
                if opt.is_visible():
                    opt.click()

        # Treatment Criteria
        if treatment_criteria:
            crit_box = self.page.locator("input[placeholder*='Criteria'], textarea[placeholder*='Criteria']").first
            if crit_box.is_visible():
                self.safe_fill(crit_box, treatment_criteria, "Treatment Criteria")

        # Remarks & Comments
        if remark:
            rem_box = self.page.locator(".ant-form-item:has-text('RAC Management') textarea").first
            if rem_box.is_visible():
                self.safe_fill(rem_box, remark, "RAC Remark")
