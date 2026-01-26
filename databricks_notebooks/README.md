# Databricks Notebooks

## Overview

These notebooks use **shared modules** from `data_gen/` for maximum code reuse with local scripts.

## Notebooks

| Notebook | Purpose | Imports |
|----------|---------|---------|
| `01_generate_documents_modular.py` | Generate synthetic documents | `generators/`, `config.py` |
| `03_add_scan_effects.py` | Add scan effects to PDFs | `scan_effects.py` |

## Setup

### 1. Upload Shared Modules

Upload `data_gen/` folder to Databricks:

**Option A: Workspace Files**
```
/Workspace/Users/your.email@company.com/data_gen/
├── config.py
├── scan_effects.py
└── generators/
    ├── __init__.py
    ├── document_utils.py
    ├── loan_agreements.py
    ├── term_sheets.py
    └── financial_statements.py
```

**Option B: Repos (Recommended)**
- Clone this repo to Databricks Repos
- Modules automatically available at `/Repos/<repo-name>/custom_ocr_demo/data_gen`

### 2. Create Unity Catalog Objects

```sql
CREATE CATALOG IF NOT EXISTS lending_documents;
CREATE SCHEMA IF NOT EXISTS lending_documents.raw_data;
CREATE VOLUME IF NOT EXISTS lending_documents.raw_data.synthetic_docs;
```

### 3. Install Dependencies

In cluster or notebook:
```python
%pip install reportlab==4.0.9 Faker==22.6.0 pandas==2.2.0 Pillow==10.2.0 numpy==1.26.3 pdf2image==1.17.0
```

For scan effects, also install poppler:
```bash
%sh apt-get update && apt-get install -y poppler-utils
```

### 4. Configure Notebooks

Set `module_path` widget to your uploaded folder location:
- Workspace: `/Workspace/Users/your.email@company.com/data_gen`
- Repos: `/Repos/your-repo/custom_ocr_demo/data_gen`

## Usage

### Generate Documents

1. Import `01_generate_documents_modular.py`
2. Configure widgets:
   - `catalog_name`, `schema_name`, `volume_name`
   - `module_path` (path to data_gen folder)
   - Document counts
3. Run all cells

**Output:** PDFs in `/Volumes/lending_documents/raw_data/synthetic_docs/`

### Add Scan Effects

1. Import `03_add_scan_effects.py`
2. Configure widgets:
   - Volume paths
   - `module_path`
   - Quality settings
3. Run all cells

**Output:** Scanned PDFs in `scanned/` subdirectory

## Benefits

- ✅ Uses same code as local scripts
- ✅ Edit shared modules → changes apply everywhere
- ✅ Same seed produces identical documents
- ✅ Consistent scan quality parameters

## Troubleshooting

**"Module not found" error:**
- Check `module_path` widget points to correct location
- Verify files uploaded: `dbutils.fs.ls("/Workspace/...")`

**Different output than local:**
- Ensure same package versions
- Use identical seeds for comparison
- Verify using same shared modules

## Next Steps

After generating documents:
1. Proceed with DeepSeek OCR deployment
2. Build Bronze → Silver → Gold pipeline
3. Test OCR on various quality levels
