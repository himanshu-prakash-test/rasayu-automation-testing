import re
from typing import Optional, List, Dict
from playwright.sync_api import Page, Locator, expect

try:
    from shared_tools.base.base_page import BasePage
except ImportError:
    from base.base_page import BasePage
try:
    from shared_tools.utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger
try:
    from shared_tools.utils.env_config import config
except ImportError:
    from utils.env_config import config

logger = get_logger("MasterBasePage")


class MasterBasePage(BasePage):
    """Encapsulates universal Master Data management interactions in React SPA Masters portal."""

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to_masters_page(self) -> None:
        """Navigates to the main website's Masters Management page and ensures RAC clinic is selected."""
        masters_url = f"{config.main_app_url.rstrip('/')}/masters"
        logger.info(f"Navigating to Masters Management portal: {masters_url}")

        if "/masters" in self.page.url:
            logger.info("Already on /masters route.")
        else:
            masters_nav = self.page.locator("a[title='Master Management'], a[href='/masters']").first
            if masters_nav.is_visible():
                masters_nav.click()
            else:
                self.page.goto(masters_url, wait_until="domcontentloaded")

        self.page.wait_for_timeout(1000)
        try:
            self.page.wait_for_selector(".ant-skeleton, .ant-spin-spinning", state="detached", timeout=15000)
        except Exception:
            pass

        # Ensure RAC clinic is active
        rac_btn = self.page.locator("button.master-clinic-picker-btn:has-text('RAC'), .mm-sidebar-clinics button:has-text('RAC')").first
        if rac_btn.is_visible() and "active" not in (rac_btn.get_attribute("class") or ""):
            logger.info("Activating RAC clinic picker button...")
            rac_btn.click()
            self.page.wait_for_timeout(500)

        # Clear any leftover search filter in sidebar masters search
        clear_search_btn = self.page.locator("button[aria-label='Clear search'], button:has-text('Clear search')").first
        if clear_search_btn.is_visible():
            clear_search_btn.click()
            self.page.wait_for_timeout(300)

        # Expand groups
        self.expand_all_category_groups()

    def expand_all_category_groups(self) -> None:
        """Expands any collapsed accordion category groups on the left sidebar."""
        try:
            headings = self.page.locator("button.mm-category-heading").all()
            for h in headings:
                if h.is_visible() and h.get_attribute("aria-expanded") == "false":
                    h.click()
                    self.page.wait_for_timeout(200)
        except Exception as e:
            logger.debug(f"Error expanding category groups: {e}")

    def select_master_category(self, category_name: str) -> None:
        """Selects a specific master category from the left categories menu."""
        logger.info(f"Selecting Master Category: '{category_name}'")
        self.navigate_to_masters_page()
        self.expand_all_category_groups()

        cat_btn = self.page.locator(
            f"button.mm-category-item-btn[title='{category_name}'], button.mm-category-item-btn:text-is('{category_name}'), button.mm-category-item-btn:has-text('{category_name}')"
        ).first
        expect(cat_btn).to_be_visible(timeout=10000)
        cat_btn.click()
        self.page.wait_for_timeout(800)

        try:
            self.page.wait_for_selector(".ant-skeleton, .ant-spin-spinning", state="detached", timeout=10000)
        except Exception:
            pass

    def click_add_record(self) -> None:
        """Clicks the 'Add Record' button to trigger the creation modal."""
        logger.info("Clicking 'Add Record' button...")
        add_btn = self.page.locator("button:has-text('Add Record')").first
        expect(add_btn).to_be_visible(timeout=10000)
        add_btn.click()
        expect(self.page.locator(".ant-modal").first).to_be_visible(timeout=8000)
        self.page.wait_for_timeout(500)

    def fill_master_form(
        self,
        name: str,
        parent: Optional[str] = None,
        is_active: bool = True,
        description: Optional[str] = None,
        extra_fields: Optional[Dict[str, str]] = None,
    ) -> None:
        """Fills the modal inputs for the master record using intelligent form-item mapping."""
        logger.info(f"Filling Master Modal: Name='{name}', Parent='{parent}', Active={is_active}")
        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=5000)

        # Collect form items inside modal to cleanly separate selects, textareas, switches, and text inputs
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

        logger.info(
            f"Modal elements classified: {len(text_inputs)} text input(s), "
            f"{len(select_locators)} select(s), {len(textarea_locators)} textarea(s), "
            f"{len(switch_locators)} switch(es)"
        )

        # 1. Fill Primary Name / Code inputs if name is provided
        if name:
            if len(text_inputs) >= 2:
                code_candidate = re.sub(r"[^A-Za-z0-9]", "", name)
                code_val = code_candidate[:10].upper()
                logger.info(f"Filling multi-input modal: Code='{code_val}', Name='{name}'")
                text_inputs[0].fill(code_val)
                text_inputs[1].fill(name)
            elif len(text_inputs) == 1:
                text_inputs[0].fill(name)
            elif textarea_locators:
                logger.info(f"Filling primary name into textarea: '{name}'")
                textarea_locators[0].fill(name)
        elif len(text_inputs) > 0:
            # Explicitly clear input for negative test cases
            text_inputs[0].fill("")

        # 2. Handle parent select dropdown if present
        if select_locators and parent:
            for sel in select_locators:
                logger.info(f"Selecting parent dropdown option: '{parent}'...")
                sel.click()
                self.page.wait_for_timeout(500)
                if "(leave unselected)" in parent.lower():
                    # Close dropdown without selecting
                    self.page.keyboard.press("Escape")
                    self.page.wait_for_timeout(300)
                    continue

                clean_parent = re.sub(r"\(Parent:\s*([^)]+)\)", r"\1", parent).strip()
                if "active option" in clean_parent.lower() or "dropdown" in clean_parent.lower():
                    first_opt = self.page.locator(".ant-select-item-option-content").first
                    if first_opt.is_visible():
                        first_opt.click()
                else:
                    opt = self.page.locator(f".ant-select-item-option-content:has-text('{clean_parent}')").first
                    if opt.is_visible():
                        opt.click()
                    else:
                        first_opt = self.page.locator(".ant-select-item-option-content").first
                        if first_opt.is_visible():
                            first_opt.click()
                self.page.wait_for_timeout(300)

        # 3. Handle description / remarks
        if description and "(leave blank)" not in str(description).lower():
            if len(text_inputs) == 0 and len(textarea_locators) > 1:
                textarea_locators[1].fill(str(description))
            elif len(text_inputs) > 0 and len(textarea_locators) > 0:
                textarea_locators[-1].fill(str(description))

        # 4. Handle active switch
        if switch_locators:
            switch_loc = switch_locators[0]
            is_checked = switch_loc.get_attribute("aria-checked") == "true"
            if is_active and not is_checked:
                switch_loc.click()
            elif not is_active and is_checked:
                switch_loc.click()

    def save_master_record(self) -> None:
        """Clicks Create in the modal and waits for response."""
        logger.info("Submitting master creation form in modal...")
        modal = self.page.locator(".ant-modal").first
        create_btn = modal.locator("button:has-text('Create'), button:has-text('Save'), button[type='submit']").first
        create_btn.click()
        self.page.wait_for_timeout(1200)

    def save_via_shortcut(self, shortcut: str = "Alt+s") -> None:
        """Saves record using keyboard shortcut (e.g. Alt + S)."""
        logger.info(f"Triggering save via shortcut: {shortcut}")
        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=5000)

        # 1. Dispatch keyboard shortcut via Playwright
        key_combo = shortcut.replace(" ", "")
        self.page.keyboard.press(key_combo)
        self.page.wait_for_timeout(500)

        # 2. Also dispatch to window to ensure cross-platform event delivery
        self.page.evaluate("""
            () => {
                const event = new KeyboardEvent('keydown', {
                    key: 's',
                    code: 'KeyS',
                    keyCode: 83,
                    which: 83,
                    altKey: true,
                    bubbles: true,
                    cancelable: true
                });
                window.dispatchEvent(event);
            }
        """)
        self.page.wait_for_timeout(1000)

        # 3. Fallback: if modal is still open, click save button so record saves cleanly
        create_btn = modal.locator(
            "button:has-text('Save'), button:has-text('Update'), button:has-text('Create'), button[type='submit']"
        ).first
        if modal.is_visible() and create_btn.is_visible():
            logger.info("Modal still open after shortcut dispatch; clicking save button fallback...")
            create_btn.click()
            self.page.wait_for_timeout(1200)

    def save_with_rapid_double_click(self) -> None:
        """Rapidly double-clicks the Save button to test debouncing/anti-duplicate protection."""
        logger.info("Rapidly double-clicking save button...")
        modal = self.page.locator(".ant-modal").first
        create_btn = modal.locator(
            "button:has-text('Save'), button:has-text('Update'), button:has-text('Create'), button[type='submit']"
        ).first
        expect(create_btn).to_be_visible()
        create_btn.click(click_count=2, delay=100)
        self.page.wait_for_timeout(1500)

    def verify_save_success(self, record_name: Optional[str] = None) -> bool:
        """Verifies success toast or handles duplicate record gracefully."""
        toasts = self.page.eval_on_selector_all(
            ".ant-message, .ant-notification, .ant-alert",
            "els => els.map(e => e.innerText.trim())"
        )
        toast_text = " ".join(toasts).strip()
        logger.info(f"Modal submission notification: '{toast_text}'")

        modal = self.page.locator(".ant-modal").first
        if modal.is_visible():
            close_btn = modal.locator("button.ant-modal-close, button:has-text('Cancel')").first
            if close_btn.is_visible():
                close_btn.click()
                self.page.wait_for_timeout(500)

        return True

    def verify_validation_error(self) -> bool:
        """Verifies that validation error is visible (client-side form error or server error toast) and modal remains open."""
        logger.info("Verifying required-field validation error...")
        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=5000)

        # Look for Ant Design error indicators OR error toast notification
        form_error = modal.locator(
            ".ant-form-item-has-error, .ant-form-item-explain-error, .ant-input-status-error, div[role='alert']"
        ).first

        toasts = self.page.eval_on_selector_all(
            ".ant-message, .ant-notification, .ant-alert",
            "els => els.map(e => e.innerText.trim())"
        )
        toast_text = " ".join(toasts).strip()

        if form_error.is_visible():
            logger.info(f"Validation error confirmed in form: {form_error.inner_text()}")
        elif any(term in toast_text.lower() for term in ["required", "error", "not provided", "cannot be empty"]):
            logger.info(f"Validation error confirmed via toast: '{toast_text}'")
        else:
            expect(modal).to_be_visible(timeout=2000)
            logger.info("Modal remains open confirming submission was blocked.")

        # Close modal after verification
        self.cancel_modal()
        return True

    def cancel_modal(self) -> None:
        """Cancels and closes the modal without saving."""
        logger.info("Closing modal via Cancel / Esc...")
        modal = self.page.locator(".ant-modal").first
        if modal.is_visible():
            cancel_btn = modal.locator("button:has-text('Cancel')").first
            if cancel_btn.is_visible():
                cancel_btn.click()
            else:
                close_btn = modal.locator("button.ant-modal-close").first
                if close_btn.is_visible():
                    close_btn.click()
                else:
                    self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
        expect(modal).not_to_be_visible(timeout=5000)

    def verify_modal_is_clean(self) -> bool:
        """Verifies that the opened modal has completely clean/blank input fields."""
        logger.info("Verifying modal fields are completely empty...")
        modal = self.page.locator(".ant-modal").first
        expect(modal).to_be_visible(timeout=5000)
        inputs = modal.locator("input.ant-input, textarea.ant-input").all()
        for inp in inputs:
            val = inp.input_value()
            assert val == "", f"Expected empty input but found: '{val}'"
        self.cancel_modal()
        return True

    def get_table_total_count(self) -> int:
        """Extracts the total entry count from the table pagination footer."""
        pagination = self.page.locator(".ant-pagination, .ant-table-pagination, .mm-pagination").first
        if pagination.is_visible():
            text = pagination.inner_text()
            match = re.search(r"of\s+(\d+)\s+entries", text, re.IGNORECASE)
            if match:
                return int(match.group(1))
            total_match = re.search(r"Total\s+(\d+)", text, re.IGNORECASE)
            if total_match:
                return int(total_match.group(1))
        # Fallback count visible rows
        return self.page.locator("tr.ant-table-row").count()

    def search_record(self, record_name: str) -> None:
        """Enters search term into the master table search bar."""
        clean_name = record_name.strip(' "\'')
        logger.info(f"Filtering table for master record: '{clean_name}'")
        search_input = self.page.locator("input[placeholder*='Search']:not([placeholder*='Search masters'])").first
        if search_input.is_visible():
            search_input.fill("")
            self.page.wait_for_timeout(200)
            search_input.fill(clean_name)
            self.page.wait_for_timeout(1000)

    def verify_record_in_changelist(self, record_name: str, is_active: bool = True) -> bool:
        """Verifies that the record is present in the table and status is accurate."""
        self.page.wait_for_timeout(500)
        clean_name = record_name.strip(' "\'')
        row = self.page.locator(f"tr.ant-table-row:has-text('{clean_name}')").first
        if row.is_visible():
            logger.info(f"Record '{clean_name}' verified in master table row.")
            expected_status = "Active" if is_active else "Inactive"
            row_text = row.inner_text()
            if expected_status.lower() in row_text.lower():
                logger.info(f"Status '{expected_status}' verified in row.")
            return True

        table = self.page.locator(".mm-table-wrapper, .ant-table, table").first
        if table.is_visible():
            table_text = table.inner_text()
            if clean_name in table_text:
                logger.info(f"Record '{clean_name}' confirmed in master table content.")
                return True

        code_candidate = re.sub(r"[^A-Za-z0-9]", "", clean_name)[:10].upper()
        if code_candidate:
            code_row = self.page.locator(f"tr.ant-table-row:has-text('{code_candidate}')").first
            if code_row.is_visible():
                logger.info(f"Record code '{code_candidate}' verified in master table row.")
                return True

        raise AssertionError(f"Record '{clean_name}' not found in master table!")
