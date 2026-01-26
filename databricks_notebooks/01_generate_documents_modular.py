# Databricks notebook source
# MAGIC %md
# MAGIC # Generate Synthetic Lending Documents (Modular Version)
# MAGIC 
# MAGIC This notebook uses the shared generator modules from `data_gen/generators/`.
# MAGIC **Maximum code reuse** - identical functionality to local version!
# MAGIC 
# MAGIC **Setup Required:**
# MAGIC 1. Upload `data_gen/generators/` folder to Workspace or Repos
# MAGIC 2. Upload `data_gen/config.py` to same location
# MAGIC 
# MAGIC **Alternatively:** Use `02_document_generators_inline.py` which requires no uploads.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Install Dependencies

# COMMAND ----------

# DBTITLE 1,Install Required Packages
%pip install reportlab==4.0.9 Faker==22.6.0 pandas==2.2.0 --quiet
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Configuration

# COMMAND ----------

# DBTITLE 1,Widget Parameters
dbutils.widgets.text("catalog_name", "lending_documents", "01. Catalog Name")
dbutils.widgets.text("schema_name", "raw_data", "02. Schema Name")
dbutils.widgets.text("volume_name", "synthetic_docs", "03. Volume Name")
dbutils.widgets.dropdown("doc_type", "all", ["all", "loan_agreements", "term_sheets", "financial_statements"], "04. Document Type")
dbutils.widgets.text("count_loans", "20", "05. Loan Agreements Count")
dbutils.widgets.text("count_terms", "10", "06. Term Sheets Count")
dbutils.widgets.text("count_financials", "10", "07. Financial Statements Count")
dbutils.widgets.text("module_path", "/Workspace/Users/your.email@company.com/data_gen", "08. Path to data_gen folder")

# COMMAND ----------

# DBTITLE 1,Get Configuration
import sys
import os
from datetime import datetime

catalog_name = dbutils.widgets.get("catalog_name")
schema_name = dbutils.widgets.get("schema_name")
volume_name = dbutils.widgets.get("volume_name")
doc_type = dbutils.widgets.get("doc_type")
count_loans = int(dbutils.widgets.get("count_loans"))
count_terms = int(dbutils.widgets.get("count_terms"))
count_financials = int(dbutils.widgets.get("count_financials"))
module_path = dbutils.widgets.get("module_path")

volume_path = f"/Volumes/{catalog_name}/{schema_name}/{volume_name}"

print(f"📁 Configuration:")
print(f"  Volume Path: {volume_path}")
print(f"  Module Path: {module_path}")
print(f"  Document Type: {doc_type}")
if doc_type == "all":
    print(f"  Total Documents: {count_loans + count_terms + count_financials}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Import Shared Modules
# MAGIC 
# MAGIC These are the SAME modules used by the local version!

# COMMAND ----------

# DBTITLE 1,Add Module Path to Python Path
# Add the data_gen folder to Python path
if module_path not in sys.path:
    sys.path.insert(0, module_path)

print(f"✓ Added {module_path} to Python path")

# COMMAND ----------

# DBTITLE 1,Import Shared Configuration
# Import configuration from shared config.py
try:
    from config import (
        UK_COMPANY_NAMES, UK_LENDERS, UK_BROKERS, UK_ADDRESSES,
        LOAN_AMOUNT_RANGES, INTEREST_RATE_RANGE, LOAN_TENORS,
        SECURITY_TYPES, LOAN_PURPOSES, FINANCIAL_COVENANTS,
        REVENUE_RANGES, GROSS_MARGIN_RANGE, OPERATING_MARGIN_RANGE, NET_MARGIN_RANGE,
        random_date_range, random_company_number, random_reference_number, format_currency
    )
    print("✓ Configuration imported from shared config.py")
    print(f"  • {len(UK_COMPANY_NAMES)} company names loaded")
    print(f"  • {len(LOAN_AMOUNT_RANGES)} loan amount tiers")
except ImportError as e:
    print(f"✗ Error importing config: {e}")
    print(f"  Make sure config.py is in: {module_path}")
    dbutils.notebook.exit(f"Failed to import configuration: {e}")

# COMMAND ----------

# DBTITLE 1,Import Shared Generator Functions
# Import generator functions from shared modules
try:
    from generators.loan_agreements import generate_loan_agreement
    from generators.term_sheets import generate_term_sheet
    from generators.financial_statements import generate_financial_statement
    
    print("✓ Generator modules imported successfully")
    print("  • loan_agreements.generate_loan_agreement")
    print("  • term_sheets.generate_term_sheet")
    print("  • financial_statements.generate_financial_statement")
    print("\n✅ Using SHARED code with local version!")
except ImportError as e:
    print(f"✗ Error importing generators: {e}")
    print(f"  Make sure generators/ folder is in: {module_path}")
    dbutils.notebook.exit(f"Failed to import generators: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Volume Setup

# COMMAND ----------

# DBTITLE 1,Create Volume Directories
def create_volume_directories(base_path):
    """Create directory structure in Databricks Volume."""
    dirs = {
        'base': base_path,
        'loan_agreements': f"{base_path}/loan_agreements",
        'term_sheets': f"{base_path}/term_sheets",
        'financial_statements': f"{base_path}/financial_statements",
        'scanned': f"{base_path}/scanned",
    }
    
    print(f"📁 Creating directory structure...")
    
    for dir_name, dir_path in dirs.items():
        try:
            try:
                dbutils.fs.ls(dir_path)
                print(f"  ✓ {dir_name}: {dir_path} (exists)")
            except:
                dbutils.fs.mkdirs(dir_path)
                print(f"  ✓ {dir_name}: {dir_path} (created)")
        except Exception as e:
            print(f"  ✗ Error with {dir_name}: {e}")
    
    return dirs

output_dirs = create_volume_directories(volume_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Generate Documents
# MAGIC 
# MAGIC Using the SAME generation functions as local version!

# COMMAND ----------

# DBTITLE 1,Generation Functions
def generate_documents_batch(generator_func, output_dir, count, start_seed, doc_type_name):
    """
    Generic batch generation function - works with any generator.
    
    Args:
        generator_func: The generator function to call
        output_dir: Directory to save PDFs
        count: Number of documents to generate
        start_seed: Starting seed value
        doc_type_name: Name for display
    
    Returns:
        list: Generated document metadata
    """
    print(f"\n{'='*70}")
    print(f"Generating {count} {doc_type_name}...")
    print(f"{'='*70}")
    
    generated = []
    
    for i in range(count):
        seed = start_seed + i
        filename = f"{doc_type_name.lower().replace(' ', '_')}_{i+1:03d}.pdf"
        filepath = f"{output_dir}/{filename}"
        local_filepath = filepath.replace("/Volumes/", "/dbfs/Volumes/")
        
        try:
            # Call the SHARED generator function
            params = generator_func(local_filepath, seed=seed)
            
            # Extract relevant metadata
            metadata = {
                'type': doc_type_name.lower().replace(' ', '_'),
                'filename': filename,
                'path': filepath,
                'seed': seed
            }
            
            # Add type-specific fields
            if 'borrower' in params:
                metadata['borrower'] = params['borrower']
                metadata['amount'] = params['loan_amount']
                print(f"  ✓ {filename} - {params['borrower']} - £{params['loan_amount']:,.0f}")
            elif 'company' in params:
                metadata['company'] = params['company']
                metadata['revenue'] = params['revenue']
                print(f"  ✓ {filename} - {params['company']} - £{params['revenue']:,.0f}")
            else:
                print(f"  ✓ {filename}")
            
            generated.append(metadata)
            
        except Exception as e:
            print(f"  ✗ Error: {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n✓ Successfully generated {len(generated)}/{count} {doc_type_name}")
    return generated

# COMMAND ----------

# DBTITLE 1,Main Generation Logic
print("\n" + "="*70)
print(" "*15 + "SYNTHETIC DOCUMENT GENERATOR")
print(" "*10 + "UK Merchant Bank Lending Documents")
print(" "*12 + "(Using Shared Generator Modules)")
print("="*70)
print(f"\nOutput location: {volume_path}\n")

all_generated = []

# Generate based on doc_type using SHARED functions
if doc_type == 'all' or doc_type == 'loan_agreements':
    all_generated.extend(generate_documents_batch(
        generate_loan_agreement,
        output_dirs['loan_agreements'],
        count_loans,
        1000,
        "Loan Agreement"
    ))

if doc_type == 'all' or doc_type == 'term_sheets':
    all_generated.extend(generate_documents_batch(
        generate_term_sheet,
        output_dirs['term_sheets'],
        count_terms,
        2000,
        "Term Sheet"
    ))

if doc_type == 'all' or doc_type == 'financial_statements':
    all_generated.extend(generate_documents_batch(
        generate_financial_statement,
        output_dirs['financial_statements'],
        count_financials,
        3000,
        "Financial Statement"
    ))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Save Manifest

# COMMAND ----------

# DBTITLE 1,Create Manifest File
manifest_path = f"{output_dirs['base']}/manifest.txt"
local_manifest = manifest_path.replace("/Volumes/", "/dbfs/Volumes/")

with open(local_manifest, 'w') as f:
    f.write("="*70 + "\n")
    f.write("SYNTHETIC DOCUMENT GENERATION MANIFEST\n")
    f.write("="*70 + "\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Total Documents: {len(all_generated)}\n")
    f.write(f"Volume Path: {volume_path}\n")
    f.write(f"Generator: Shared modules (identical to local version)\n")
    f.write("="*70 + "\n\n")
    
    by_type = {}
    for doc in all_generated:
        dt = doc['type']
        if dt not in by_type:
            by_type[dt] = []
        by_type[dt].append(doc)
    
    for dt, docs in by_type.items():
        f.write(f"\n{dt.upper().replace('_', ' ')} ({len(docs)} documents)\n")
        f.write("-"*70 + "\n")
        for doc in docs:
            f.write(f"  {doc['filename']}\n")
            if 'borrower' in doc:
                f.write(f"    Borrower: {doc['borrower']}\n")
                f.write(f"    Amount: £{doc['amount']:,.0f}\n")
            elif 'company' in doc:
                f.write(f"    Company: {doc['company']}\n")
                f.write(f"    Revenue: £{doc['revenue']:,.0f}\n")
            f.write(f"    Seed: {doc['seed']}\n")
            f.write(f"    Path: {doc['path']}\n\n")

print(f"✓ Manifest saved: {manifest_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Summary and Verification

# COMMAND ----------

# DBTITLE 1,Display Summary
print("\n" + "="*70)
print(" "*25 + "GENERATION COMPLETE")
print("="*70)
print(f"\n✅ Total documents generated: {len(all_generated)}")
print(f"📁 Output location: {volume_path}")
print(f"🔄 Using SHARED code with local version")

by_type = {}
for doc in all_generated:
    dt = doc['type']
    if dt not in by_type:
        by_type[dt] = []
    by_type[dt].append(doc)

print(f"\n📊 Document Breakdown:")
for dt, docs in by_type.items():
    print(f"  • {dt.replace('_', ' ').title()}: {len(docs)} documents")

print(f"\n📄 Manifest: {manifest_path}")
print("\n✅ Documents ready for OCR processing!")
print("\n💡 These documents are IDENTICAL to locally generated ones!")

# COMMAND ----------

# DBTITLE 1,Verify Files
print("\n🔍 Verifying generated files...\n")

for dir_name, dir_path in output_dirs.items():
    if dir_name in ['base', 'scanned']:
        continue
    
    try:
        files = dbutils.fs.ls(dir_path)
        pdfs = [f for f in files if f.name.endswith('.pdf')]
        
        print(f"{dir_name.replace('_', ' ').title()}:")
        print(f"  Location: {dir_path}")
        print(f"  Files: {len(pdfs)} PDFs")
        
        if pdfs:
            total_size = sum(f.size for f in pdfs) / (1024 * 1024)
            print(f"  Total Size: {total_size:.2f} MB")
            print(f"  Samples:")
            for pdf in pdfs[:3]:
                print(f"    • {pdf.name} ({pdf.size / (1024 * 1024):.2f} MB)")
        print()
    except Exception as e:
        print(f"  ✗ Error listing {dir_name}: {e}\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Complete!
# MAGIC 
# MAGIC **Key Points:**
# MAGIC - ✅ Used SHARED generator modules (same as local version)
# MAGIC - ✅ Used SHARED configuration (same as local version)
# MAGIC - ✅ **Identical functionality** between local and Databricks
# MAGIC - ✅ Documents saved in Unity Catalog Volume
# MAGIC 
# MAGIC **Next Steps:**
# MAGIC 1. Optional: Run `03_add_scan_effects` to add quality variations
# MAGIC 2. Proceed with DeepSeek OCR deployment (Phase 2)
# MAGIC 3. Build Bronze → Silver → Gold pipeline (Phase 4)
