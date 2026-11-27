import pytest
from playwright.sync_api import Page

try:
    from transaction_management.baseline_module.pages.baseline_common_page import BaselinePage
except ImportError:
    from pages.baseline_common_page import BaselinePage


@pytest.fixture
def baseline_page(authenticated_page: Page) -> BaselinePage:
    return BaselinePage(authenticated_page)
