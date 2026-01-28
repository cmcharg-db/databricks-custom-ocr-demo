#!/usr/bin/env python3
"""
Test Setup Script

Quick script to verify all dependencies are installed correctly
and generate a single test document of each type.

Run this before generating the full document set to catch any issues early.
"""

import sys
import os
from pathlib import Path

def test_imports():
    """Test that all required packages can be imported."""
    print("Testing package imports...")
    packages = {
        'reportlab': 'reportlab',
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'faker': 'Faker',
        'fitz': 'PyMuPDF',
        'PyPDF2': 'PyPDF2',
    }
    
    failed = []
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT FOUND")
            failed.append(name)
    
    if failed:
        print(f"\n✗ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✓ All packages installed correctly!\n")
    return True


def test_generators():
    """Test that document generators work."""
    print("Testing document generators...")
    
    # Add current directory to path
    sys.path.insert(0, os.path.dirname(__file__))
    
    try:
        from generators import generate_loan_agreement, generate_term_sheet, generate_financial_statement
        print("  ✓ Generator modules loaded")
    except ImportError as e:
        print(f"  ✗ Failed to load generators: {e}")
        return False
    
    # Create test output directory
    test_dir = Path(__file__).parent / "outputs" / "test"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Test each generator
    tests = [
        ("Loan Agreement", generate_loan_agreement, test_dir / "test_loan.pdf"),
        ("Term Sheet", generate_term_sheet, test_dir / "test_term.pdf"),
        ("Financial Statement", generate_financial_statement, test_dir / "test_financial.pdf"),
    ]
    
    for doc_type, generator, output_path in tests:
        try:
            print(f"\n  Generating test {doc_type}...")
            params = generator(str(output_path), seed=9999)
            
            if output_path.exists():
                size_kb = output_path.stat().st_size / 1024
                print(f"  ✓ {doc_type} generated successfully ({size_kb:.1f} KB)")
                print(f"    Location: {output_path}")
                
                # Print some params
                if 'borrower' in params:
                    print(f"    Borrower: {params['borrower']}")
                    print(f"    Amount: £{params.get('loan_amount', params.get('revenue', 0)):,.0f}")
                elif 'company' in params:
                    print(f"    Company: {params['company']}")
            else:
                print(f"  ✗ {doc_type} - File not created")
                return False
                
        except Exception as e:
            print(f"  ✗ {doc_type} generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print(f"\n✓ All generators working correctly!")
    print(f"Test PDFs saved in: {test_dir}")
    return True


def test_pymupdf():
    """Test PyMuPDF installation."""
    print("\nTesting PDF to image conversion with PyMuPDF...")
    
    try:
        import fitz
        
        test_pdf = Path(__file__).parent / "outputs" / "test" / "test_loan.pdf"
        
        if not test_pdf.exists():
            print("  ⚠ Skipping (no test PDF found - run generator tests first)")
            return True
        
        try:
            # Try to open and render just the first page
            doc = fitz.open(str(test_pdf))
            page = doc[0]
            pix = page.get_pixmap()
            print(f"  ✓ PDF to image conversion working")
            print(f"    Converted page size: {pix.width}x{pix.height}")
            doc.close()
            return True
        except Exception as e:
            print(f"  ✗ Error converting PDF: {e}")
            return False
            
    except Exception as e:
        print(f"  ✗ PDF conversion test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print(" "*25 + "SETUP TEST")
    print(" "*15 + "Synthetic Document Generator")
    print("="*70 + "\n")
    
    results = []
    
    # Test imports
    results.append(("Package Imports", test_imports()))
    
    # Test generators
    results.append(("Document Generators", test_generators()))
    
    # Test PDF conversion
    results.append(("PDF to Image (PyMuPDF)", test_pymupdf()))
    
    # Summary
    print("\n" + "="*70)
    print(" "*27 + "TEST SUMMARY")
    print("="*70 + "\n")
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:.<50} {status}")
    
    all_critical_passed = results[0][1] and results[1][1]
    
    print("\n" + "="*70)
    
    if all_critical_passed:
        print("\n✓ Setup is working correctly!")
        print("\nNext steps:")
        print("  1. Review test PDFs in outputs/test/")
        print("  2. Run: python generate_all.py")
        print("  3. Optionally run: python add_scan_effects.py")
        print("\n")
        return 0
    else:
        print("\n✗ Setup has issues - please fix errors above")
        print("\nCommon fixes:")
        print("  • Install missing packages: pip install -r requirements.txt")
        print("\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
