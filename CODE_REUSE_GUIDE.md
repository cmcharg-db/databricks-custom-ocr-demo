# Code Reuse Architecture

## Overview

This project uses **shared modules** to ensure identical functionality between local Python scripts and Databricks notebooks.

## Structure

```
data_gen/
├── config.py                    # Shared configuration
├── scan_effects.py              # Shared scan effects
└── generators/                  # Shared document generators
    ├── document_utils.py
    ├── loan_agreements.py
    ├── term_sheets.py
    └── financial_statements.py
```

## Local Usage

```bash
cd data_gen
python generate_all.py          # Uses generators/
python add_scan_effects.py      # Uses scan_effects.py
```

## Databricks Usage

**Setup:**
1. Upload `data_gen/` folder to Workspace or Repos
2. Set `module_path` widget in notebooks to point to uploaded folder
3. Notebooks import shared modules automatically

**Notebooks:**
- `01_generate_documents_modular.py` - Imports shared generators
- `03_add_scan_effects.py` - Imports shared scan_effects

## Code Reuse Benefits

| Component | Shared? | Result |
|-----------|---------|--------|
| Document generation | ✅ 100% | Identical output |
| Scan effects | ✅ 100% | Same quality parameters |
| Configuration | ✅ 100% | Same settings |

**Edit once, applies everywhere.**

## Customization

**Change scan quality:**
```python
# Edit data_gen/scan_effects.py
SCAN_EFFECTS = {
    "light": {
        "noise": 3,      # Adjust intensity
        "blur": 0.3,
        "rotation": 0.2,
        "brightness": 0.98,
    }
}
```

**Change document parameters:**
```python
# Edit data_gen/config.py
LOAN_AMOUNT_RANGES = [
    (1_000_000, 10_000_000),  # Adjust ranges
]
```

Both local and Databricks use updated values immediately.

## Verification

Test identical output with same seed:

```python
# Local
from generators.loan_agreements import generate_loan_agreement
generate_loan_agreement('test.pdf', seed=1234)

# Databricks (after importing)
from generators.loan_agreements import generate_loan_agreement
generate_loan_agreement('/dbfs/test.pdf', seed=1234)
```

Same seed produces byte-for-byte identical PDFs.

## Architecture

```
┌─────────────────────────┐
│   SHARED MODULES        │
│   (Core Logic)          │
└────────┬────────────────┘
         │ Import
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────────┐
│LOCAL │  │DATABRICKS │
│Files │  │Volumes    │
└──────┘  └───────────┘
```

~95% code reuse, 100% functional parity.
