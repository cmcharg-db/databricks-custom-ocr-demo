"""
Configuration file for synthetic document generation.
Contains templates, data ranges, and styling options for generating
realistic UK merchant bank lending documents.
"""

import random
from datetime import datetime, timedelta

# ==============================================================================
# COMPANY AND BORROWER DATA
# ==============================================================================

# Sample UK company names for borrowers
UK_COMPANY_NAMES = [
    "Westminster Trading Ltd",
    "Thames Capital Holdings PLC",
    "Bristol Manufacturing Group",
    "Edinburgh Properties Ltd",
    "Manchester Logistics Solutions",
    "Birmingham Industrial Partners",
    "Leeds Technology Ventures",
    "Cardiff Commercial Enterprises",
    "Glasgow Investment Holdings",
    "Southampton Retail Group Ltd",
    "Newcastle Development Corporation",
    "Liverpool Export Services",
    "Sheffield Engineering Ltd",
    "Nottingham Food Distributors",
    "Oxford Research & Development",
]

# Sample lender (merchant bank) names
UK_LENDERS = [
    "Sterling Merchant Bank PLC",
    "Cavendish Capital Limited",
    "Lombard Street Finance",
    "Threadneedle Lending Group",
    "Aldgate Commercial Bank",
    "Bishopsgate Financial Services",
]

# Sample broker names
UK_BROKERS = [
    "City Finance Brokers Ltd",
    "Canary Wharf Capital Advisors",
    "Mayfair Lending Solutions",
    "Westminster Broker Services",
    "London Bridge Financial Partners",
]

# UK addresses for borrowers
UK_ADDRESSES = [
    "25 Gresham Street, London, EC2V 7HN",
    "100 Victoria Street, Westminster, London, SW1E 5JL",
    "45 Old Broad Street, London, EC2N 1HT",
    "78 Cannon Street, London, EC4N 6HL",
    "The Pavilion, 15 Prescot Street, London, E1 8LZ",
    "50 Broadway, Westminster, London, SW1H 0BL",
    "123 High Street, Birmingham, B4 7SL",
    "88 Princess Street, Manchester, M1 6NG",
    "42 George Street, Edinburgh, EH2 2LE",
    "15 Park Place, Cardiff, CF10 3DQ",
]

# ==============================================================================
# LOAN PARAMETERS
# ==============================================================================

# Loan amount ranges (in GBP)
LOAN_AMOUNT_RANGES = [
    (500_000, 1_000_000),      # Small business loans
    (1_000_000, 5_000_000),    # Medium enterprise
    (5_000_000, 15_000_000),   # Large corporate
    (15_000_000, 50_000_000),  # Major facilities
]

# Interest rates (annual %)
INTEREST_RATE_RANGE = (4.5, 8.5)

# Loan tenors (in months)
LOAN_TENORS = [12, 18, 24, 36, 48, 60, 84, 120]

# Security types
SECURITY_TYPES = [
    "First Legal Charge over Commercial Property",
    "Debenture over all assets",
    "Personal Guarantee from Directors",
    "Fixed and Floating Charge",
    "Share Pledge Agreement",
    "Cash Collateral Account",
    "Combination of Property Charge and Debenture",
]

# Loan purposes
LOAN_PURPOSES = [
    "Working capital and general corporate purposes",
    "Acquisition financing",
    "Property development",
    "Refinancing of existing facilities",
    "Capital expenditure on equipment and machinery",
    "Business expansion and growth",
    "Trade finance and export activities",
]

# Covenants
FINANCIAL_COVENANTS = [
    "Minimum Interest Cover Ratio: 2.5x",
    "Maximum Debt to EBITDA: 3.0x",
    "Minimum Net Worth: £{} million",
    "Maximum Capital Expenditure: £{} per annum",
    "Minimum Liquidity: £{} at all times",
]

# ==============================================================================
# FINANCIAL STATEMENT PARAMETERS
# ==============================================================================

# Revenue ranges for different company sizes (in GBP)
REVENUE_RANGES = [
    (2_000_000, 5_000_000),      # Small
    (5_000_000, 25_000_000),     # Medium
    (25_000_000, 100_000_000),   # Large
]

# Typical margin ranges
GROSS_MARGIN_RANGE = (0.25, 0.45)
OPERATING_MARGIN_RANGE = (0.05, 0.20)
NET_MARGIN_RANGE = (0.02, 0.12)

# ==============================================================================
# DOCUMENT STYLING
# ==============================================================================

# PDF page settings
PAGE_WIDTH = 595.27   # A4 width in points
PAGE_HEIGHT = 841.89  # A4 height in points
MARGIN = 72           # 1 inch margins

# Font settings
FONT_TITLE = "Helvetica-Bold"
FONT_HEADING = "Helvetica-Bold"
FONT_BODY = "Helvetica"
FONT_SIZE_TITLE = 18
FONT_SIZE_HEADING = 14
FONT_SIZE_SUBHEADING = 12
FONT_SIZE_BODY = 10
FONT_SIZE_SMALL = 8

# Colors (RGB)
COLOR_HEADER = (0.2, 0.3, 0.5)
COLOR_BODY = (0, 0, 0)
COLOR_TABLE_HEADER = (0.9, 0.9, 0.9)

# ==============================================================================
# SCAN EFFECT PARAMETERS
# ==============================================================================

# Percentage of documents to apply scanning effects
SCAN_EFFECT_DISTRIBUTION = {
    "pristine": 0.70,      # 70% clean PDFs
    "light_scan": 0.20,    # 20% lightly scanned
    "heavy_scan": 0.10,    # 10% heavily scanned/degraded
}

# Scan quality parameters
SCAN_EFFECTS = {
    "pristine": {
        "noise": 0,
        "blur": 0,
        "rotation": 0,
        "brightness": 1.0,
    },
    "light_scan": {
        "noise": 5,
        "blur": 1,
        "rotation": 0.5,
        "brightness": 0.95,
    },
    "heavy_scan": {
        "noise": 15,
        "blur": 2,
        "rotation": 1.5,
        "brightness": 0.85,
    },
}

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def random_date_range(start_year=2023, end_year=2026):
    """Generate a random date within the specified year range."""
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    time_between = end_date - start_date
    days_between = time_between.days
    random_days = random.randrange(days_between)
    return start_date + timedelta(days=random_days)


def format_currency(amount, currency="GBP"):
    """Format a number as currency."""
    if currency == "GBP":
        return f"£{amount:,.2f}"
    return f"{currency} {amount:,.2f}"


def format_number(number):
    """Format a number with thousand separators."""
    return f"{number:,.0f}"


def random_company_number():
    """Generate a realistic UK Companies House number."""
    # UK company numbers are typically 8 digits, sometimes with leading zeros
    return f"{random.randint(1000000, 99999999):08d}"


def random_reference_number(prefix="LF"):
    """Generate a loan facility reference number."""
    year = random.randint(2023, 2026)
    seq = random.randint(1000, 9999)
    return f"{prefix}-{year}-{seq}"
