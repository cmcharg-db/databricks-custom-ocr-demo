#!/usr/bin/env python3
"""
Add Scan Effects to PDFs

This script takes pristine PDF documents and creates degraded versions
that simulate scanned documents with varying quality levels:
- Light scanning: Minimal noise, slight rotation, minor quality loss
- Heavy scanning: Significant noise, rotation, compression artifacts

This is useful for testing OCR robustness across different document qualities.

Usage:
    python add_scan_effects.py                          # Process all PDFs
    python add_scan_effects.py --quality light          # Only light effects
    python add_scan_effects.py --percentage 30          # Process 30% of docs

Note: This script uses the shared scan_effects module for maximum code reuse
      with the Databricks notebooks version.
"""

import argparse
import os
import random
from pathlib import Path

# Import shared scan effects module - same code used by Databricks notebooks!
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


def find_pdfs(base_dir):
    """
    Find all PDF files in the outputs directory.
    
    Args:
        base_dir: Base directory to search
    
    Returns:
        list: List of Path objects for PDF files
    """
    pdfs = []
    for subdir in ['loan_agreements', 'term_sheets', 'financial_statements']:
        subdir_path = base_dir / subdir
        if subdir_path.exists():
            pdfs.extend(list(subdir_path.glob('*.pdf')))
    return pdfs


def process_pdf_with_progress(input_path, output_path, quality, dpi):
    """
    Wrapper around shared process_pdf function with progress messages.
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save processed PDF
        quality: Effect quality ('light' or 'heavy')
        dpi: DPI for image conversion
    
    Returns:
        bool: True if successful
    """
    print(f"    Converting and processing pages...")
    return process_pdf(str(input_path), str(output_path), quality=quality, dpi=dpi)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Add scanning effects to PDF documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process 30% of documents with mixed quality
  python add_scan_effects.py --percentage 30
  
  # Process all documents with light quality
  python add_scan_effects.py --quality light --percentage 100
  
  # Process only heavy quality scans
  python add_scan_effects.py --quality heavy --percentage 20
        """
    )
    
    parser.add_argument(
        '--quality',
        choices=['light', 'heavy', 'mixed'],
        default='mixed',
        help='Scan quality to apply (default: mixed)'
    )
    
    parser.add_argument(
        '--percentage',
        type=int,
        default=30,
        help='Percentage of documents to process (default: 30)'
    )
    
    parser.add_argument(
        '--dpi',
        type=int,
        default=150,
        help='DPI for image conversion (default: 150, lower = more degraded)'
    )
    
    parser.add_argument(
        '--input-dir',
        type=str,
        help='Input directory containing outputs/ folder'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*70)
    print(" "*20 + "SCAN EFFECTS PROCESSOR")
    print(" "*15 + "Simulate Scanned Document Quality")
    print("="*70)
    
    # Determine directories
    if args.input_dir:
        base_dir = Path(args.input_dir) / "outputs"
    else:
        base_dir = Path(__file__).parent / "outputs"
    
    scanned_dir = base_dir / "scanned"
    scanned_dir.mkdir(exist_ok=True)
    
    # Find all PDFs
    pdfs = find_pdfs(base_dir)
    
    if not pdfs:
        print("\n✗ No PDF files found in outputs directory")
        print("  Please run generate_all.py first to create documents")
        return
    
    print(f"\nFound {len(pdfs)} PDF documents")
    print(f"Will process {args.percentage}% = {int(len(pdfs) * args.percentage / 100)} documents")
    print(f"Quality mode: {args.quality}")
    print(f"DPI: {args.dpi}")
    print(f"Output directory: {scanned_dir}\n")
    
    # Randomly select documents to process
    num_to_process = int(len(pdfs) * args.percentage / 100)
    selected_pdfs = random.sample(pdfs, min(num_to_process, len(pdfs)))
    
    # Process each selected PDF
    processed_count = 0
    failed_count = 0
    
    for i, pdf_path in enumerate(selected_pdfs, 1):
        # Determine quality
        if args.quality == 'mixed':
            quality = random.choice(['light', 'heavy'])
        else:
            quality = args.quality
        
        # Create output filename
        output_filename = f"scanned_{quality}_{pdf_path.name}"
        output_path = scanned_dir / output_filename
        
        print(f"\n[{i}/{len(selected_pdfs)}] Processing: {pdf_path.name}")
        print(f"  Quality: {quality}")
        print(f"  Output: {output_filename}")
        
        # Process the PDF using shared module
        success = process_pdf_with_progress(pdf_path, output_path, quality, args.dpi)
        
        if success:
            processed_count += 1
            file_size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"  ✓ Success! Size: {file_size_mb:.2f} MB")
        else:
            failed_count += 1
    
    # Print summary
    print("\n" + "="*70)
    print(" "*25 + "PROCESSING COMPLETE")
    print("="*70)
    print(f"\nSuccessfully processed: {processed_count}/{len(selected_pdfs)}")
    if failed_count > 0:
        print(f"Failed: {failed_count}")
    print(f"Output location: {scanned_dir}")
    print("\nScanned documents are ready for OCR testing!")
    print("These simulate real-world document quality variations.\n")


if __name__ == "__main__":
    main()
