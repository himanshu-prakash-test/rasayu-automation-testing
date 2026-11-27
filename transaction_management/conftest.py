"""
Shared patient directory & clinical tab nav fixtures.
"""
import pytest
from playwright.sync_api import Page

try:
    from shared_tools.utils.env_config import config
except ImportError:
    from utils.env_config import config


@pytest.fixture(scope="function")
def patient_directory(authenticated_page: Page):
    """Ensures navigation to the Patient Directory."""
    if "/patients" not in authenticated_page.url:
        authenticated_page.goto(f"{config.main_app_url.rstrip('/')}/patients", wait_until="domcontentloaded")
    return authenticated_page
