"""
Baseline Module Test Data Helper.
Encapsulates module-specific sheet names and default patient lookups.
Keeps `shared-tools` 100% common, generic, and decoupled from any specific module.
"""
from typing import Optional
from test_data.excel_reader import get_test_data, get_test_data_by_id
from test_data.data_models import TestDataRecord

BASELINE_SHEET = "createbaseline"


def get_baseline_test_data(test_case_id: str) -> TestDataRecord:
    """Retrieves a test data record specifically from the baseline visit test suite."""
    return get_test_data_by_id(test_case_id, sheet_name=BASELINE_SHEET)


def get_default_patient_id() -> str:
    """
    Dynamically extracts the default baseline patient ID from TC-BASE-POS-02 in Excel.
    """
    try:
        rec = get_baseline_test_data("TC-BASE-POS-02")
        pid = rec.parsed_payload.get("Patient ID")
        if pid:
            return pid
    except Exception:
        pass
    return "220261119"


def get_default_patient_name() -> str:
    """
    Dynamically extracts the default baseline patient name from TC-BASE-POS-02 in Excel.
    """
    try:
        rec = get_baseline_test_data("TC-BASE-POS-02")
        name = rec.parsed_payload.get("Patient Name")
        if name:
            return name
    except Exception:
        pass
    return "Rita D varma"
