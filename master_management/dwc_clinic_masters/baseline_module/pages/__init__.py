"""
DWC Clinic Masters - Baseline Module Page Objects.
"""
from .dwc_master_base_page import DwcMasterBasePage
from .dwc_create_page import DwcBaselineMasterCreatePage
from .dwc_update_page import DwcBaselineMasterUpdatePage
from .dwc_delete_page import DwcBaselineMasterDeletePage

__all__ = [
    "DwcMasterBasePage",
    "DwcBaselineMasterCreatePage",
    "DwcBaselineMasterUpdatePage",
    "DwcBaselineMasterDeletePage",
]
