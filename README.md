# Rasayu Clinical Management Portal - Automation Testing Framework

Enterprise-grade, human-engineered UI test automation framework built with **Python**, **Playwright**, and **pytest** for the **Rasayu Clinical Management Portal** (`http://54.169.232.62/admin/`).

---

## Architecture & Directory Structure

The framework is organized into decoupled, modular directories ensuring strict separation of concerns, zero hardcoding, and complete portability across local machines and CI/CD servers.

```
rasayu-automation-testing/
│
├── shared-tools/                     # 100% Generic & Reusable Automation Utilities
│   ├── auth/                         # Authentication & generic login page object
│   ├── base/                         # Base page with resilient Playwright interactions
│   ├── components/                   # Universal UI components (Admin navigation, tables)
│   ├── popup/                        # Toast alerts, modals, summary dialogs, and confirmation popups
│   ├── reporter/                     # Enterprise HTML reporter with Coreco branding & KPI cards
│   ├── test_data/                    # Universal Excel test data reader & pydantic data models
│   │   ├── Rasayu_Test_Cases.xlsx
│   │   └── Rasayu_Test_Data.xlsx
│   └── utils/                        # Logging, environment configuration, & screenshot management
│
├── master-management/                # Master Data Management Modules
│   ├── RAC/                          # Rasayu Cancer Clinic Masters
│   │   ├── create/
│   │   │   └── baseline-module/      # Disease at Baseline Master Create Module
│   │   │       ├── master_pages/     # MasterBasePage and RacBaselineMasterPage
│   │   │       ├── tests/            # 52 Automated Master Test Cases (TC-01 to TC-52)
│   │   │       ├── master_baseline_data.py # Module data adapter reading 'master-rac-createbaseline'
│   │   │       └── README.md         # Master baseline module documentation
│   │   └── update/
│   └── DWC/                          # Doctor Wellness Clinic Masters
│       ├── create/
│       └── update/
│
├── transaction-management/           # Clinical Transaction & Patient Care Modules
│   ├── create/                       # New Transaction creation
│   └── update/                       # Transaction updates & clinical follow-ups
│       └── baseline-module/          # Baseline Visit Case Report Form (CRF) Module
│           ├── pages/                # Page objects (sub-tabs, patient directory, clinical forms)
│           ├── tests/                # 37 Automated pytest test suites (23 Positive + 14 Negative)
│           ├── baseline_data.py      # Module data adapter reading 'createbaseline' sheet
│           └── README.md             # Baseline module documentation
│
├── conftest.py                       # Root pytest fixtures, session hooks, screenshot hooks
├── pytest.ini                        # Pytest configuration and execution markers
├── requirements.txt                  # Python dependencies
├── .env.example                      # Template for environment variables (NO credentials in Git)
└── .gitignore                        # Git ignore rules (.env, screenshots, reports, pycache)
```

---

## Core Engineering Features

1. **Zero Hardcoded Data**:
   - Credentials strictly reside in local `.env` (never committed to version control).
   - All test payloads, patient identifiers, clinical options, and boundary values are dynamically read from Excel (`Rasayu_Test_Data.xlsx`) via generic helper models.
2. **Headless Execution by Default**:
   - `pytest` runs in headless mode by default for server and CI/CD efficiency.
   - Use `--headed` flag when visual interaction or debugging is desired.
3. **Automated Evidence & Screenshot Lifecycle**:
   - Automatically takes a full-page screenshot upon completion of every test case.
   - Named strictly by official Test Case ID (e.g. `TC-BASE-POS-01.png`, `TC-MASTER-BASE-RAC-02.png`).
   - Saved to the `screenshots/` directory and attached directly to the HTML test report.
   - **Vanish on Session Start**: The `screenshots/` directory is automatically wiped clean when starting a new automation test run.
   - **100-File FIFO Limit**: Retains at most 100 screenshots; older files are automatically purged based on modification time.
4. **Execution Summary & Report Popup**:
   - Generates an enterprise HTML report with KPIs, pie charts, and embedded screenshots.
   - Automatically shows a native UI summary popup at test completion allowing the user to view or launch the HTML report (gracefully suppresses without error on headless Linux/Docker environments without a display server).
5. **Decoupled Common Architecture**:
   - `shared-tools/` contains zero medical terms or module-specific logic, allowing seamless scaling to any future clinic or transaction module.

---

## Test Inventory & Coverage (89 Automated Test Cases)

| Module | Scope | Tests | Key Features Covered |
|---|---|:---:|---|
| **Transaction Management**<br>`update/baseline-module` | Baseline Visit CRF | **37** | Admin Authentication, Patient Directory, Demographics, Allergies, Allopathy & Ayurvedic Diagnosis, Comorbidities, Family History, Medicines & Chemo, Chief Complaints, Vitals & ECOG, TNM Staging, Surgical & Radiation History, Lab Tests, Hetu Sevan, Clinical Prognosis, RAC Protocol, Physician Opinion, Form Submission + 14 Boundary/Negative validations. |
| **Master Management**<br>`RAC/create/baseline-module` | Disease at Baseline Masters | **52** | Admin Auth & Nav, Marital Status, Consanguineous, Allergy Type/Reason, Disease Group/Type/Subtype/Stage/Grading, Ayurvedic Nidan, Avastha, Avayava/Srotas/Dosha/Dhatu/Upadhatu/Mala Drushti, Agni/Oja Vikriti, Therapy/Treatment Response, Subjective Prognosis, Comorbidities & Complications, Surgeries & Outcomes, Lineage & Family History, Obstetrics/Delivery, Medicine Forms/Generics/Brands/Units/Frequencies/Side Effects, Chemo & Radiation Regimens, ADR, Cycle Details, Symptoms Types. |
| **Total Automated Coverage** | | **89** | **100% Automated Test Case Catalog** |

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Google Chrome or Chromium browser

### 2. Environment Setup
```powershell
# Clone the repository
git clone <repository-url>
cd rasayu-automation-testing

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install required dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
playwright install chromium
```

### 3. Environment Configuration
Copy `.env.example` to `.env` and fill in your portal credentials:
```powershell
cp .env.example .env
```
Edit `.env`:
```ini
BASE_URL=http://54.169.232.62/admin/
ADMIN_USERNAME=ADMIN
ADMIN_PASSWORD=YourSecurePasswordHere
HEADLESS=true
DEFAULT_CLINIC=RAC
```

---

## Test Execution Commands

```powershell
# 1. Run all 89 tests across the entire framework (Headless by default)
pytest

# 2. Run all tests in Headed mode (opens visible browser)
pytest --headed

# 3. Run only the RAC Master Baseline Module (52 tests)
pytest master-management/RAC/create/baseline-module/

# 4. Run only the Transaction Baseline Visit Module (37 tests)
pytest transaction-management/update/baseline-module/

# 5. Run a single specific master test case by ID
pytest master-management/RAC/create/baseline-module/ -k "TC-MASTER-BASE-RAC-02"

# 6. Collect all tests across the framework without executing
pytest --collect-only
```
