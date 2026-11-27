"""
Hetu Sevan Page Object:
Handles Tab 2 - Habits / Addictions, Aahar (Dietary Habits),
Vihar (Physical Activity & Lifestyle), Veg Dharan (Suppression of Natural Urges),
and Manas (Psychological Factors).
"""
from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, Locator, expect

try:
    from shared_tools.base.base_page import BasePage
    from shared_tools.utils.logger import get_logger
except ImportError:
    from base.base_page import BasePage
    from utils.logger import get_logger

logger = get_logger("HetuSevanPage")


class HetuSevanPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page, context_name="HetuSevanPage")

    # ---------- Habits / Addictions ----------
    def fill_habit(self, habit: str, status: str, qty: str = "3", since: str = "10", unit: str = "Years", stopped_since: Optional[str] = None, peg_size: Optional[str] = None) -> None:
        logger.info(f"Filling Habit: {habit}, Status={status}, Qty={qty}, Since={since} {unit}")
        # Habit selection
        habit_box = self.page.locator(".ant-form-item:has-text('Habit') .ant-select, select[name*='habit']").first
        if habit_box.is_visible():
            habit_box.click()
            self.page.wait_for_timeout(300)
            opt = self.page.locator(f".ant-select-item-option:has-text('{habit}')").first
            if opt.is_visible():
                opt.click()

        # Status
        if status:
            status_box = self.page.locator(".ant-form-item:has-text('Status') .ant-select, select[name*='status']").first
            if status_box.is_visible():
                status_box.click()
                self.page.wait_for_timeout(300)
                opt = self.page.locator(f".ant-select-item-option:has-text('{status}')").first
                if opt.is_visible():
                    opt.click()

        # Qty
        if qty:
            qty_input = self.page.locator("input[placeholder*='Quantity'], input[name*='qty'], input[placeholder*='Qty']").first
            if qty_input.is_visible():
                self.safe_fill(qty_input, str(qty), "Habit Quantity")

        # Since
        if since:
            since_input = self.page.locator("input[placeholder*='Since'], input[name*='since']").first
            if since_input.is_visible():
                self.safe_fill(since_input, str(since), "Habit Since")

        # Stopped Since
        if stopped_since:
            stop_input = self.page.locator("input[placeholder*='Stopped Since']").first
            if stop_input.is_visible():
                self.safe_fill(stop_input, str(stopped_since), "Stopped Since")

        # Peg Size
        if peg_size:
            peg_input = self.page.locator("input[placeholder*='Peg Size']").first
            if peg_input.is_visible():
                self.safe_fill(peg_input, str(peg_size), "Peg Size")

    # ---------- Aahar (Dietary Habits) ----------
    def fill_aahar(self, meal: str, timing: str, food_habits: List[str], remark: Optional[str] = None, row_index: int = 0) -> None:
        logger.info(f"Filling Aahar (row {row_index}): Meal={meal}, Timing={timing}, FoodHabits={food_habits}")
        # Meal
        meal_box = self.page.locator(".ant-form-item:has-text('Meal') .ant-select, select[name*='meal']").nth(row_index)
        if meal_box.is_visible():
            meal_box.click()
            self.page.wait_for_timeout(300)
            opt = self.page.locator(f".ant-select-item-option:has-text('{meal}')").first
            if opt.is_visible():
                opt.click()

        # Timing
        if timing:
            time_input = self.page.locator("input[placeholder*='Timing'], input[placeholder*='Select time']").nth(row_index)
            if time_input.is_visible():
                self.safe_fill(time_input, timing, "Meal Timing")

        # Food Habits chips
        if food_habits:
            for habit in food_habits:
                chip = self.page.locator(f".ant-tag:has-text('{habit}'), button:has-text('{habit}')").first
                if chip.is_visible():
                    chip.click()

        # Remark
        if remark:
            rem_input = self.page.locator(".ant-form-item:has-text('Aahar') textarea, textarea[placeholder*='Remark']").nth(row_index)
            if rem_input.is_visible():
                self.safe_fill(rem_input, remark, "Aahar Remark")

    # ---------- Vihar (Exercise / Physical Activity) ----------
    def fill_vihar(self, exercise: str, etype: Optional[str] = None, freq: Optional[str] = None, duration: Optional[str] = None, since: Optional[str] = None, unit: Optional[str] = None) -> None:
        logger.info(f"Filling Vihar: Exercise={exercise}, Type={etype}")
        # Exercise toggle Yes / No
        ex_btn = self.page.locator(f".ant-radio-button-wrapper:has-text('{exercise}'), button:has-text('{exercise}')").first
        if ex_btn.is_visible():
            ex_btn.click()
            self.page.wait_for_timeout(300)

        if exercise.lower() == "yes" and etype:
            t_box = self.page.locator("input[placeholder*='Exercise Type'], select[name*='exercise_type']").first
            if t_box.is_visible():
                self.safe_fill(t_box, etype, "Exercise Type")

    # ---------- Veg Dharan (Suppression of Urges) ----------
    def fill_veg_dharan(self, veg: str, lakshan: List[str]) -> None:
        logger.info(f"Filling Veg Dharan: Veg={veg}, Lakshan={lakshan}")
        v_box = self.page.locator(".ant-form-item:has-text('Veg') .ant-select, select[name*='veg']").first
        if v_box.is_visible():
            v_box.click()
            self.page.wait_for_timeout(300)
            opt = self.page.locator(f".ant-select-item-option:has-text('{veg}')").first
            if opt.is_visible():
                opt.click()

        if lakshan:
            for l_item in lakshan:
                chip = self.page.locator(f".ant-tag:has-text('{l_item}'), button:has-text('{l_item}')").first
                if chip.is_visible():
                    chip.click()

    # ---------- Manas (Psychological Factors) ----------
    def fill_manas(self, activities: List[str], remark: Optional[str] = None) -> None:
        logger.info(f"Filling Manas: Activities={activities}, Remark={remark}")
        if activities:
            for act in activities:
                chip = self.page.locator(f".ant-tag:has-text('{act}'), button:has-text('{act}')").first
                if chip.is_visible():
                    chip.click()

        if remark:
            rem_input = self.page.locator(".ant-form-item:has-text('Manas') textarea").first
            if rem_input.is_visible():
                self.safe_fill(rem_input, remark, "Manas Remark")
