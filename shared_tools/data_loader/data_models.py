from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class TestDataRecord:
    test_case_id: str
    test_type: str
    clinical_module: str
    test_scenario: str
    raw_payload: str
    expected_outcome: str
    parsed_payload: Dict[str, str] = field(default_factory=dict)
    active_record_input: Optional[str] = ""
    inactive_record_input: Optional[str] = ""


@dataclass
class TestCaseRecord:
    test_case_id: str
    scenario: str
    precondition: str
    test_steps: str
    expected_result: str
    automation_status: str
    test_status: Optional[str] = None
    remarks: Optional[str] = None
