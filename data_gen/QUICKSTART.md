# Quick Start Guide - Synthetic Document Generation

This guide will help you generate realistic UK merchant bank lending documents in minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Step 1: Install Dependencies

From the `data_gen` directory, run:

```bash
pip install -r requirements.txt
```

This will install:
- `reportlab` - PDF generation
- `Pillow` - Image manipulation
- `Faker` - Fake data generation
- Other supporting libraries

**Note:** On macOS, you may also need to install poppler for PDF processing:
```bash
brew install poppler
```

On Ubuntu/Debian:
```bash
sudo apt-get install poppler-utils
```

## Step 2: Generate Documents

### Generate Everything (Recommended for First Run)

Generate the default set of documents (40 total):

```bash
python generate_all.py
```

This creates:
- 20 loan agreement PDFs (5-8 pages each)
- 10 broker term sheet PDFs (2-3 pages each)
- 10 financial statement PDFs (3-4 pages each)

**Expected time:** 2-5 minutes depending on your system

### Generate Specific Document Types

Generate only loan agreements:
```bash
python generate_all.py --type loan_agreements --count 15
```

Generate only term sheets:
```bash
python generate_all.py --type term_sheets --count 10
```

Generate only financial statements:
```bash
python generate_all.py --type financial_statements --count 10
```

### Custom Counts

Generate custom numbers of each type:
```bash
python generate_all.py --count-loans 25 --count-terms 12 --count-financials 15
```

## Step 3: Add Scan Effects (Optional but Recommended)

To simulate real-world document quality variations, add scanning effects:

```bash
python add_scan_effects.py
```

This will:
- Select 30% of your generated PDFs (configurable)
- Apply realistic scanning artifacts (noise, blur, rotation)
- Create two quality levels: "light" and "heavy" scanning
- Save results in `outputs/scanned/`

**Options:**
```bash
# Process 50% of documents
python add_scan_effects.py --percentage 50

# Only apply light scanning effects
python add_scan_effects.py --quality light --percentage 100

# Only heavy degradation
python add_scan_effects.py --quality heavy --percentage 20

# Lower DPI for more degraded quality
python add_scan_effects.py --dpi 100
```

**Expected time:** 1-3 minutes for 30% of 40 documents

## Step 4: Review Generated Documents

Your documents are organized in:

```
data_gen/outputs/
├── loan_agreements/         # Facility agreements (5-8 pages)
│   ├── loan_agreement_001.pdf
│   ├── loan_agreement_002.pdf
│   └── ...
├── term_sheets/             # Broker term sheets (2-3 pages)
│   ├── term_sheet_001.pdf
│   ├── term_sheet_002.pdf
│   └── ...
├── financial_statements/    # Balance sheets & P&L (3-4 pages)
│   ├── financial_statement_001.pdf
│   ├── financial_statement_002.pdf
│   └── ...
├── scanned/                 # Degraded quality versions
│   ├── scanned_light_loan_agreement_001.pdf
│   ├── scanned_heavy_term_sheet_003.pdf
│   └── ...
└── manifest.txt            # Catalog of all generated documents
```

Open a few PDFs to verify they look realistic!

## Step 5: Upload to Databricks

Once you're satisfied with the documents:

1. Open your Databricks workspace
2. Navigate to the Data tab or DBFS
3. Create a directory: `/FileStore/lending_documents/` or use your Volume/external storage
4. Upload the PDFs from `outputs/` folders

**CLI Upload (if you have Databricks CLI configured):**
```bash
databricks fs cp -r outputs/loan_agreements/ dbfs:/FileStore/lending_documents/loan_agreements/
databricks fs cp -r outputs/term_sheets/ dbfs:/FileStore/lending_documents/term_sheets/
databricks fs cp -r outputs/financial_statements/ dbfs:/FileStore/lending_documents/financial_statements/
databricks fs cp -r outputs/scanned/ dbfs:/FileStore/lending_documents/scanned/
```

## What Gets Generated?

### Loan Agreements (5-8 pages each)
- Full UK-style facility agreements
- Loan amounts: £500K - £50M
- Multi-section structure: Parties, Terms, Covenants, Security, Schedules
- Realistic legal language and formatting
- Signature blocks

### Term Sheets (2-3 pages each)
- Broker-style deal summaries
- Transaction overview and key terms
- Borrower profile and financials
- Pricing and fee structures
- Security package details

### Financial Statements (3-4 pages each)
- Profit & Loss statements
- Balance sheets
- Notes to accounts
- UK FRS 102 compliant formatting
- Realistic financial ratios

### Scanned Versions
- Light quality: Minimal artifacts (simulates good scanner)
- Heavy quality: Significant degradation (simulates fax or old photocopies)
- Random rotation (0-2 degrees)
- Noise and blur effects
- Brightness adjustments

## Troubleshooting

### "ModuleNotFoundError: No module named 'reportlab'"
Run: `pip install -r requirements.txt`

### "pdf2image.exceptions.PDFPageCountError"
Install poppler:
- macOS: `brew install poppler`
- Ubuntu: `sudo apt-get install poppler-utils`

### "Permission denied" when running scripts
Make scripts executable:
```bash
chmod +x generate_all.py add_scan_effects.py
```

### Documents look identical
This is by design with reproducible seeds. If you want more variation, regenerate with different seeds or modify the `start_seed` parameters in the code.

### Want different company names or parameters?
Edit `config.py` to customize:
- Company names
- Address list
- Loan amount ranges
- Interest rate ranges
- Financial covenants

## Next Steps

Once you have your synthetic documents:

1. **Test OCR locally** with DeepSeek OCR to validate quality
2. **Upload to Databricks** workspace or cloud storage
3. **Follow the main implementation plan** to build the OCR ingestion pipeline
4. **Use these documents** to demonstrate the Bronze → Silver → Gold data flow

## Tips for Demo Success

1. **Mix quality levels**: Use 70% pristine, 20% light scanned, 10% heavy scanned
2. **Realistic volumes**: 30-50 documents is perfect for a demo
3. **Show variety**: Include all three document types in your demo
4. **Highlight challenges**: The scanned versions show OCR's value proposition
5. **Explain synthetic data**: Be upfront that these are generated for demo purposes

## Support

For issues or questions:
- Check the main `IMPLEMENTATION_PLAN.md`
- Review code comments in `generators/` folder
- Modify `config.py` for customization

Happy generating! 🎉
