# Synthetic Document Generation for UK Merchant Bank Demo

This folder contains scripts to generate realistic synthetic lending documents for OCR testing and demo purposes.

## Folder Structure

```
data_gen/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── config.py                          # Configuration and templates
├── generators/                        # Document generation modules
│   ├── __init__.py
│   ├── loan_agreements.py            # Loan agreement generator
│   ├── term_sheets.py                # Term sheet generator
│   ├── financial_statements.py       # Financial statement generator
│   └── document_utils.py             # Shared utilities
├── outputs/                          # Generated documents (gitignored)
│   ├── loan_agreements/              # Loan agreement PDFs
│   ├── term_sheets/                  # Term sheet PDFs
│   ├── financial_statements/         # Financial statement PDFs
│   └── scanned/                      # Degraded quality versions
├── generate_all.py                   # Main script to generate all documents
└── add_scan_effects.py               # Script to create scanned versions

```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate all documents:
```bash
python generate_all.py
```

This will create:
- 20 loan agreement PDFs
- 10 broker term sheet PDFs
- 10 financial statement PDFs
- Scanned/degraded versions of a subset

3. Generate specific document types:
```bash
# Generate only loan agreements
python generate_all.py --type loan_agreements --count 15

# Generate only term sheets
python generate_all.py --type term_sheets --count 10

# Generate with specific quality degradation
python generate_all.py --add-scans --scan-percentage 30
```

## Document Types Generated

### Loan Agreements
- UK-style facility agreements
- Varying loan amounts (£500K - £50M)
- Different security structures
- Multi-page with schedules and covenants

### Term Sheets
- Broker-style term sheets
- Deal summaries and proposals
- Various formatting styles

### Financial Statements
- Balance sheets
- Profit & Loss statements
- Cash flow statements
- Multi-column layouts with tables

## Quality Variations

The generator creates documents with:
- Clean, pristine PDFs (70%)
- Slightly degraded/photocopied (20%)
- Heavily scanned with noise (10%)

## Customization

Edit `config.py` to customize:
- Company names and addresses
- Loan amount ranges
- Interest rate ranges
- Document templates and styles
