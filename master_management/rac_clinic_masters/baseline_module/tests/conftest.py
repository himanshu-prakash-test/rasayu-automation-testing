import pytest
from playwright.sync_api import Page

from ..pages.master_create_page import MasterCreatePage, RacBaselineMasterPage
from ..pages.master_read_page import MasterReadPage
from ..pages.master_update_page import MasterUpdatePage
from ..pages.master_delete_page import MasterDeletePage


@pytest.fixture
def master_create_page(authenticated_page: Page) -> MasterCreatePage:
    mp = MasterCreatePage(authenticated_page)
    mp.navigate_to_baseline_master_home()
    return mp


@pytest.fixture
def master_page(master_create_page: MasterCreatePage) -> MasterCreatePage:
    return master_create_page


@pytest.fixture
def read_page(authenticated_page: Page) -> MasterReadPage:
    rp = MasterReadPage(authenticated_page)
    rp.navigate_to_masters_page()
    return rp


@pytest.fixture
def update_page(authenticated_page: Page) -> MasterUpdatePage:
    up = MasterUpdatePage(authenticated_page)
    up.navigate_to_masters_page()
    return up


@pytest.fixture
def delete_page(authenticated_page: Page) -> MasterDeletePage:
    dp = MasterDeletePage(authenticated_page)
    dp.navigate_to_masters_page()
    return dp
