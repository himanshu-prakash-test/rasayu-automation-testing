# Doctor Wellness Clinic (DWC) Masters Module

Automated CRUD test suites and page objects for **Doctor Wellness Clinic (DWC)** Master Management on the Rasayu Clinical Portal.

## Architecture & Submodules
- **`baseline_module/`**: Covers Disease at Baseline Master CRUD operations dynamically loaded from `master_dwc_createbaseline`, `master_dwc_updatebaseline`, and `master_dwc_deletebaseline`.
- **`visit_module/`**: Covers Visit Masters CRUD operations dynamically loaded from `CRUDmaster-dwc-visit`.
- **`OnExam_module/`**: On Examination Masters (scaffolded for future additions).

## Running Tests
Run all DWC master tests:
```bash
pytest master_management/dwc_clinic_masters --headless
```

Run only DWC Create tests:
```bash
pytest -m "dwc and create" --headless
```

Run only DWC Visit tests:
```bash
pytest -m "dwc and visit" --headless
```
