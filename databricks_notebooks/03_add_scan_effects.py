# Databricks notebook source
# MAGIC %md
# MAGIC # Add Scan Effects to Documents
# MAGIC 
# MAGIC This notebook adds realistic scanning artifacts to generated PDFs to simulate
# MAGIC real-world document quality variations:
# MAGIC - Light scanning: Minimal noise, slight rotation
# MAGIC - Heavy scanning: Significant degradation (fax-like quality)
# MAGIC 
# MAGIC **Prerequisites:**
# MAGIC 1. Documents already generated in Unity Catalog Volume
# MAGIC 2. Cluster with sufficient memory for image processing

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Install Dependencies

# COMMAND ----------

# DBTITLE 1,Install Image Processing Libraries
%pip install Pillow==10.2.0 numpy==1.26.3 PyMuPDF==1.23.26 PyPDF2==3.0.1 --quiet

# Note: PyMuPDF requires no system dependencies - works on all compute types!

dbutils.library.restartPython()

# COMMAND ----------

# DBTITLE 1,Configure Module Path for Shared Code
dbutils.widgets.text("module_path", "/Workspace/Users/your.email@company.com/data_gen", "08. Path to data_gen folder")

import sys
module_path = dbutils.widgets.get("module_path")

# Add module path for shared code
if module_path not in sys.path:
    sys.path.insert(0, module_path)
    print(f"✓ Added {module_path} to Python path")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Configuration

# COMMAND ----------

# DBTITLE 1,Widget Parameters
dbutils.widgets.text("catalog_name", "lending_documents", "01. Catalog Name")
dbutils.widgets.text("schema_name", "raw_data", "02. Schema Name")
dbutils.widgets.text("volume_name", "synthetic_docs", "03. Volume Name")
dbutils.widgets.dropdown("quality", "mixed", ["mixed", "light", "heavy"], "04. Scan Quality")
dbutils.widgets.text("percentage", "30", "05. Percentage to Process")
dbutils.widgets.text("dpi", "150", "06. DPI (lower = more degraded)")

# COMMAND ----------

# DBTITLE 1,Get Configuration
import random
import os
from datetime import datetime

catalog_name = dbutils.widgets.get("catalog_name")
schema_name = dbutils.widgets.get("schema_name")
volume_name = dbutils.widgets.get("volume_name")
quality = dbutils.widgets.get("quality")
percentage = int(dbutils.widgets.get("percentage"))
dpi = int(dbutils.widgets.get("dpi"))

volume_path = f"/Volumes/{catalog_name}/{schema_name}/{volume_name}"
scanned_dir = f"{volume_path}/scanned"

print(f"📁 Configuration:")
print(f"  Volume Path: {volume_path}")
print(f"  Scanned Output: {scanned_dir}")
print(f"  Quality: {quality}")
print(f"  Percentage: {percentage}%")
print(f"  DPI: {dpi}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Import Libraries and Define Functions

# COMMAND ----------

# DBTITLE 1,Import Shared Scan Effects Module
# Import the SHARED scan_effects module - same code as local version!
try:
    from scan_effects import (
        process_pdf,
        apply_scan_effects,
        add_noise,
        add_blur,
        adjust_brightness,
        add_rotation,
        SCAN_EFFECT_DISTRIBUTION,
        SCAN_EFFECTS
    )
    print("✓ Scan effects module imported successfully")
    print("  Using SHARED code with local version!")
    print(f"  Available quality levels: {list(SCAN_EFFECTS.keys())}")
except ImportError as e:
    print(f"✗ Error importing scan_effects module: {e}")
    print(f"  Make sure scan_effects.py is in: {module_path}")
    dbutils.notebook.exit(f"Failed to import scan_effects: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Find and Process Documents

# COMMAND ----------

# DBTITLE 1,Find All PDFs in Volume
def find_pdfs(base_path):
    """Find all PDF files in the volume subdirectories."""
    pdfs = []
    subdirs = ['loan_agreements', 'term_sheets', 'financial_statements']
    
    for subdir in subdirs:
        subdir_path = f"{base_path}/{subdir}"
        try:
            files = dbutils.fs.ls(subdir_path)
            pdf_files = [f for f in files if f.name.endswith('.pdf')]
            for pdf_file in pdf_files:
                # Convert dbfs:/Volumes/... to /Volumes/... for PyMuPDF
                posix_path = pdf_file.path.replace('dbfs:', '')
                pdfs.append({
                    'name': pdf_file.name,
                    'path': posix_path,
                    'size': pdf_file.size,
                    'subdir': subdir
                })
        except Exception as e:
            print(f"⚠ Could not list {subdir}: {e}")
    
    return pdfs

# Find all PDFs
print("🔍 Finding PDFs in volume...")
all_pdfs = find_pdfs(volume_path)

print(f"\n✓ Found {len(all_pdfs)} PDF documents")
print(f"  Will process {int(len(all_pdfs) * percentage / 100)} documents ({percentage}%)")

# COMMAND ----------

# DBTITLE 1,Create Scanned Output Directory
# Ensure scanned directory exists
try:
    dbutils.fs.ls(scanned_dir)
    print(f"✓ Scanned directory exists: {scanned_dir}")
except:
    dbutils.fs.mkdirs(scanned_dir)
    print(f"✓ Created scanned directory: {scanned_dir}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Process Documents

# COMMAND ----------

# DBTITLE 1,Apply Scan Effects to Selected Documents
print("\n" + "="*70)
print(" "*20 + "SCAN EFFECTS PROCESSOR")
print(" "*15 + "Simulate Scanned Document Quality")
print("="*70)
print(f"\nQuality mode: {quality}")
print(f"DPI: {dpi}")
print(f"Processing {percentage}% of documents\n")

# Randomly select documents to process
num_to_process = int(len(all_pdfs) * percentage / 100)
selected_pdfs = random.sample(all_pdfs, min(num_to_process, len(all_pdfs)))

processed_count = 0
failed_count = 0

for i, pdf_info in enumerate(selected_pdfs, 1):
    # Determine quality
    if quality == 'mixed':
        doc_quality = random.choice(['light', 'heavy'])
    else:
        doc_quality = quality
    
    # Create output filename
    output_filename = f"scanned_{doc_quality}_{pdf_info['name']}"
    output_path = f"{scanned_dir}/{output_filename}"
    
    # Use direct Volume path (already converted from dbfs: format)
    input_path = pdf_info['path']
    
    print(f"\n[{i}/{len(selected_pdfs)}] Processing: {pdf_info['name']}")
    print(f"  Source: {pdf_info['subdir']}")
    print(f"  Quality: {doc_quality}")
    print(f"  Output: {output_filename}")
    
    try:
        # Process PDF directly using Volume paths
        success = process_pdf(input_path, output_path, quality=doc_quality, dpi=dpi)
        
        if success:
            processed_count += 1
            # Get output file size
            try:
                output_files = dbutils.fs.ls(scanned_dir)
                output_file = next((f for f in output_files if f.name == output_filename), None)
                if output_file:
                    size_mb = output_file.size / (1024 * 1024)
                    print(f"  ✓ Success! Size: {size_mb:.2f} MB")
            except:
                print(f"  ✓ Success!")
        else:
            failed_count += 1
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        failed_count += 1

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Summary

# COMMAND ----------

# DBTITLE 1,Display Processing Summary
print("\n" + "="*70)
print(" "*25 + "PROCESSING COMPLETE")
print("="*70)
print(f"\n✅ Successfully processed: {processed_count}/{len(selected_pdfs)}")
if failed_count > 0:
    print(f"❌ Failed: {failed_count}")

print(f"\n📁 Output location: {scanned_dir}")

# Count files by quality
try:
    scanned_files = dbutils.fs.ls(scanned_dir)
    light_count = len([f for f in scanned_files if 'light' in f.name])
    heavy_count = len([f for f in scanned_files if 'heavy' in f.name])
    
    print(f"\n📊 Quality Distribution:")
    print(f"  • Light scanned: {light_count} documents")
    print(f"  • Heavy scanned: {heavy_count} documents")
    print(f"  • Total scanned: {len(scanned_files)} documents")
    
    total_size = sum(f.size for f in scanned_files) / (1024 * 1024)
    print(f"  • Total size: {total_size:.2f} MB")
except Exception as e:
    print(f"⚠ Could not calculate statistics: {e}")

print("\n✅ Scanned documents ready for OCR testing!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Verification

# COMMAND ----------

# DBTITLE 1,List Generated Scanned Files
print("🔍 Verifying scanned files...\n")

try:
    scanned_files = dbutils.fs.ls(scanned_dir)
    
    if not scanned_files:
        print("⚠ No scanned files found")
    else:
        print(f"Scanned Files ({len(scanned_files)} total):")
        print("-" * 70)
        
        # Show first 10 as samples
        for f in scanned_files[:10]:
            size_mb = f.size / (1024 * 1024)
            quality_type = "light" if "light" in f.name else "heavy"
            print(f"  • {f.name}")
            print(f"    Size: {size_mb:.2f} MB | Quality: {quality_type}")
        
        if len(scanned_files) > 10:
            print(f"  ... and {len(scanned_files) - 10} more files")
        
        print("\n" + "-" * 70)
        print(f"All files saved in: {scanned_dir}")
        
except Exception as e:
    print(f"✗ Error listing files: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Next Steps
# MAGIC 
# MAGIC You now have documents with varying quality levels:
# MAGIC - **Original (pristine)**: In source directories
# MAGIC - **Light scanned**: Minimal artifacts
# MAGIC - **Heavy scanned**: Significant degradation
# MAGIC 
# MAGIC **Use these for:**
# MAGIC 1. Testing OCR robustness across quality levels
# MAGIC 2. Demonstrating DeepSeek OCR's accuracy on degraded documents
# MAGIC 3. Creating realistic demo scenarios
# MAGIC 
# MAGIC **Next**: Proceed with OCR pipeline (Bronze → Silver → Gold)
