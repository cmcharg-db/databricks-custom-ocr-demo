#!/usr/bin/env python3
"""
Main script to generate all synthetic UK merchant bank lending documents.

This script orchestrates the generation of loan agreements, term sheets,
and financial statements, saving them in organized output directories.

Usage:
    python generate_all.py                              # Generate default set
    python generate_all.py --count-loans 15             # Custom loan count
    python generate_all.py --type term_sheets           # Only term sheets
    python generate_all.py --add-scans                  # Add scan effects
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime

# Add generators to path
sys.path.insert(0, os.path.dirname(__file__))

from generators import generate_loan_agreement, generate_term_sheet, generate_financial_statement


def create_output_directories():
    """
    Create organized output directory structure for generated documents.
    
    Returns:
        dict: Dictionary of Path objects for each output directory
    """
    base_dir = Path(__file__).parent / "outputs"
    
    dirs = {
        'base': base_dir,
        'loan_agreements': base_dir / "loan_agreements",
        'term_sheets': base_dir / "term_sheets",
        'financial_statements': base_dir / "financial_statements",
        'scanned': base_dir / "scanned",
    }
    
    # Create all directories
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def generate_loan_agreements(output_dir, count=20, start_seed=1000):
    """
    Generate multiple loan agreement PDFs.
    
    Args:
        output_dir: Directory to save PDFs
        count: Number of documents to generate
        start_seed: Starting seed for random generation
    
    Returns:
        list: List of generated file metadata
    """
    print(f"\n{'='*70}")
    print(f"Generating {count} Loan Agreements...")
    print(f"{'='*70}")
    
    generated = []
    
    for i in range(count):
        seed = start_seed + i
        filename = f"loan_agreement_{i+1:03d}.pdf"
        filepath = output_dir / filename
        
        try:
            params = generate_loan_agreement(str(filepath), seed=seed)
            generated.append({
                'type': 'loan_agreement',
                'filename': filename,
                'path': str(filepath),
                'borrower': params['borrower'],
                'amount': params['loan_amount'],
                'seed': seed
            })
            print(f"  ✓ Generated: {filename} - {params['borrower']} - £{params['loan_amount']:,.0f}")
        except Exception as e:
            print(f"  ✗ Error generating {filename}: {e}")
    
    print(f"\nSuccessfully generated {len(generated)}/{count} loan agreements")
    return generated


def generate_term_sheets(output_dir, count=10, start_seed=2000):
    """
    Generate multiple term sheet PDFs.
    
    Args:
        output_dir: Directory to save PDFs
        count: Number of documents to generate
        start_seed: Starting seed for random generation
    
    Returns:
        list: List of generated file metadata
    """
    print(f"\n{'='*70}")
    print(f"Generating {count} Term Sheets...")
    print(f"{'='*70}")
    
    generated = []
    
    for i in range(count):
        seed = start_seed + i
        filename = f"term_sheet_{i+1:03d}.pdf"
        filepath = output_dir / filename
        
        try:
            params = generate_term_sheet(str(filepath), seed=seed)
            generated.append({
                'type': 'term_sheet',
                'filename': filename,
                'path': str(filepath),
                'borrower': params['borrower'],
                'amount': params['loan_amount'],
                'broker': params['broker'],
                'seed': seed
            })
            print(f"  ✓ Generated: {filename} - {params['borrower']} - £{params['loan_amount']:,.0f}")
        except Exception as e:
            print(f"  ✗ Error generating {filename}: {e}")
    
    print(f"\nSuccessfully generated {len(generated)}/{count} term sheets")
    return generated


def generate_financial_statements(output_dir, count=10, start_seed=3000):
    """
    Generate multiple financial statement PDFs.
    
    Args:
        output_dir: Directory to save PDFs
        count: Number of documents to generate
        start_seed: Starting seed for random generation
    
    Returns:
        list: List of generated file metadata
    """
    print(f"\n{'='*70}")
    print(f"Generating {count} Financial Statements...")
    print(f"{'='*70}")
    
    generated = []
    
    for i in range(count):
        seed = start_seed + i
        filename = f"financial_statement_{i+1:03d}.pdf"
        filepath = output_dir / filename
        
        try:
            params = generate_financial_statement(str(filepath), seed=seed)
            generated.append({
                'type': 'financial_statement',
                'filename': filename,
                'path': str(filepath),
                'company': params['company'],
                'revenue': params['revenue'],
                'year_end': params['year_end'].strftime('%Y-%m-%d'),
                'seed': seed
            })
            print(f"  ✓ Generated: {filename} - {params['company']} - £{params['revenue']:,.0f} revenue")
        except Exception as e:
            print(f"  ✗ Error generating {filename}: {e}")
    
    print(f"\nSuccessfully generated {len(generated)}/{count} financial statements")
    return generated


def save_manifest(output_dir, all_generated):
    """
    Save a manifest file with metadata about all generated documents.
    
    Args:
        output_dir: Base output directory
        all_generated: List of all generated document metadata
    """
    manifest_path = output_dir / "manifest.txt"
    
    with open(manifest_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("SYNTHETIC DOCUMENT GENERATION MANIFEST\n")
        f.write("="*70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Documents: {len(all_generated)}\n")
        f.write("="*70 + "\n\n")
        
        # Group by type
        by_type = {}
        for doc in all_generated:
            doc_type = doc['type']
            if doc_type not in by_type:
                by_type[doc_type] = []
            by_type[doc_type].append(doc)
        
        # Write each type
        for doc_type, docs in by_type.items():
            f.write(f"\n{doc_type.upper().replace('_', ' ')} ({len(docs)} documents)\n")
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
                f.write("\n")
    
    print(f"\n✓ Manifest saved to: {manifest_path}")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Generate synthetic UK merchant bank lending documents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate default document set (20 loans, 10 term sheets, 10 statements)
  python generate_all.py
  
  # Generate only loan agreements
  python generate_all.py --type loan_agreements --count 15
  
  # Generate only term sheets
  python generate_all.py --type term_sheets --count 5
  
  # Generate all with custom counts
  python generate_all.py --count-loans 25 --count-terms 12 --count-financials 15
        """
    )
    
    parser.add_argument(
        '--type',
        choices=['loan_agreements', 'term_sheets', 'financial_statements', 'all'],
        default='all',
        help='Type of documents to generate (default: all)'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        help='Number of documents to generate (applies when --type is specified)'
    )
    
    parser.add_argument(
        '--count-loans',
        type=int,
        default=20,
        help='Number of loan agreements to generate (default: 20)'
    )
    
    parser.add_argument(
        '--count-terms',
        type=int,
        default=10,
        help='Number of term sheets to generate (default: 10)'
    )
    
    parser.add_argument(
        '--count-financials',
        type=int,
        default=10,
        help='Number of financial statements to generate (default: 10)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Custom output directory (default: ./outputs)'
    )
    
    args = parser.parse_args()
    
    # Print header
    print("\n" + "="*70)
    print(" "*15 + "SYNTHETIC DOCUMENT GENERATOR")
    print(" "*10 + "UK Merchant Bank Lending Documents")
    print("="*70)
    
    # Create output directories
    if args.output_dir:
        base_dir = Path(args.output_dir)
        base_dir.mkdir(parents=True, exist_ok=True)
        dirs = {
            'base': base_dir,
            'loan_agreements': base_dir / "loan_agreements",
            'term_sheets': base_dir / "term_sheets",
            'financial_statements': base_dir / "financial_statements",
            'scanned': base_dir / "scanned",
        }
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
    else:
        dirs = create_output_directories()
    
    print(f"\nOutput directory: {dirs['base']}")
    
    # Generate documents based on arguments
    all_generated = []
    
    if args.type == 'all':
        # Generate all types
        all_generated.extend(generate_loan_agreements(
            dirs['loan_agreements'],
            count=args.count_loans
        ))
        all_generated.extend(generate_term_sheets(
            dirs['term_sheets'],
            count=args.count_terms
        ))
        all_generated.extend(generate_financial_statements(
            dirs['financial_statements'],
            count=args.count_financials
        ))
    elif args.type == 'loan_agreements':
        count = args.count if args.count else args.count_loans
        all_generated.extend(generate_loan_agreements(
            dirs['loan_agreements'],
            count=count
        ))
    elif args.type == 'term_sheets':
        count = args.count if args.count else args.count_terms
        all_generated.extend(generate_term_sheets(
            dirs['term_sheets'],
            count=count
        ))
    elif args.type == 'financial_statements':
        count = args.count if args.count else args.count_financials
        all_generated.extend(generate_financial_statements(
            dirs['financial_statements'],
            count=count
        ))
    
    # Save manifest
    save_manifest(dirs['base'], all_generated)
    
    # Print summary
    print("\n" + "="*70)
    print(" "*25 + "GENERATION COMPLETE")
    print("="*70)
    print(f"\nTotal documents generated: {len(all_generated)}")
    print(f"Output location: {dirs['base']}")
    print("\nNext steps:")
    print("  1. Review generated PDFs in the outputs/ directory")
    print("  2. Run 'python add_scan_effects.py' to create scanned versions")
    print("  3. Upload documents to your Databricks workspace for OCR processing")
    print("\n")


if __name__ == "__main__":
    main()
