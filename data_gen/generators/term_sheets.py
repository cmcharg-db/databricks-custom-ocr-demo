"""
Term Sheet Generator

Generates broker-style term sheets and deal summaries.
These are typically shorter, summary documents that brokers send to merchant banks
when proposing lending opportunities.
"""

import random
from datetime import datetime, timedelta
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .document_utils import (
    create_pdf_document, get_custom_styles, add_header_block,
    add_date_block, create_info_table, format_pounds,
    random_name, random_job_title
)
from config import (
    UK_COMPANY_NAMES, UK_LENDERS, UK_BROKERS, UK_ADDRESSES,
    LOAN_AMOUNT_RANGES, INTEREST_RATE_RANGE, LOAN_TENORS,
    SECURITY_TYPES, LOAN_PURPOSES,
    random_date_range, random_company_number, random_reference_number
)


def generate_term_sheet(output_path, seed=None):
    """
    Generate a broker term sheet PDF.
    
    Term sheets are typically 1-3 pages and provide a high-level summary
    of a proposed lending transaction.
    
    Args:
        output_path: Path where PDF will be saved
        seed: Optional random seed for reproducibility
    
    Returns:
        dict: Metadata about the generated document
    """
    if seed is not None:
        random.seed(seed)
    
    # Generate term sheet parameters
    params = _generate_term_sheet_parameters()
    
    # Create PDF
    doc, story = create_pdf_document(
        output_path,
        title=f"Term Sheet - {params['borrower']}",
        author=params['broker']
    )
    
    styles = get_custom_styles()
    
    # Build document content
    _add_header(story, styles, params)
    _add_transaction_summary(story, styles, params)
    _add_key_terms(story, styles, params)
    _add_borrower_profile(story, styles, params)
    _add_security_details(story, styles, params)
    _add_broker_recommendation(story, styles, params)
    _add_next_steps(story, styles, params)
    _add_disclaimer(story, styles, params)
    
    # Build the PDF
    doc.build(story)
    
    return params


def _generate_term_sheet_parameters():
    """Generate random but realistic term sheet parameters."""
    # Select loan size and generate amount
    amount_range = random.choice(LOAN_AMOUNT_RANGES)
    loan_amount = random.randint(amount_range[0], amount_range[1])
    loan_amount = round(loan_amount / 100000) * 100000  # Round to nearest 100k
    
    # Generate dates
    term_sheet_date = random_date_range(2023, 2026)
    proposed_close_date = term_sheet_date + timedelta(days=random.randint(30, 90))
    
    # Interest rate components
    base_rate = round(random.uniform(*INTEREST_RATE_RANGE), 2)
    margin = round(random.uniform(1.5, 4.0), 2)
    
    # Fees
    arrangement_fee = round(loan_amount * random.uniform(0.01, 0.025), 0)
    broker_fee = round(loan_amount * random.uniform(0.005, 0.015), 0)
    
    params = {
        'borrower': random.choice(UK_COMPANY_NAMES),
        'borrower_number': random_company_number(),
        'borrower_address': random.choice(UK_ADDRESSES),
        'broker': random.choice(UK_BROKERS),
        'broker_address': random.choice(UK_ADDRESSES),
        'broker_contact': random_name(),
        'broker_email': f"{random_name().replace(' ', '.').lower()}@broker.co.uk",
        'broker_phone': f"+44 20 {random.randint(7000, 7999)} {random.randint(1000, 9999)}",
        'deal_ref': random_reference_number("TS"),
        'term_sheet_date': term_sheet_date,
        'proposed_close_date': proposed_close_date,
        'loan_amount': loan_amount,
        'currency': 'GBP',
        'base_rate': base_rate,
        'margin': margin,
        'total_rate': base_rate + margin,
        'tenor_months': random.choice(LOAN_TENORS),
        'arrangement_fee': arrangement_fee,
        'broker_fee': broker_fee,
        'security_type': random.choice(SECURITY_TYPES),
        'purpose': random.choice(LOAN_PURPOSES),
        'sector': random.choice(['Manufacturing', 'Retail', 'Technology', 'Healthcare', 
                                'Property', 'Professional Services', 'Distribution', 'Hospitality']),
        'years_trading': random.randint(3, 25),
        'annual_revenue': loan_amount * random.uniform(1.5, 4.0),
        'ebitda': loan_amount * random.uniform(0.15, 0.35),
    }
    
    return params


def _add_header(story, styles, params):
    """Add the term sheet header with broker branding."""
    # Broker letterhead
    story.append(Paragraph(f"<b>{params['broker']}</b>", styles['heading']))
    story.append(Paragraph(params['broker_address'], styles['small']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"Tel: {params['broker_phone']} | Email: {params['broker_email']}", styles['small']))
    story.append(Spacer(1, 20))
    
    # Document title
    story.append(Paragraph("CONFIDENTIAL TERM SHEET", styles['title']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Deal Reference: {params['deal_ref']}", styles['body_bold']))
    story.append(Spacer(1, 6))
    add_date_block(story, styles, params['term_sheet_date'], "Date")
    story.append(Spacer(1, 20))
    
    # Confidentiality notice
    confidentiality = """
    <b>CONFIDENTIAL:</b> This term sheet is provided on a confidential basis for discussion purposes only. 
    It does not constitute an offer or commitment to lend and is subject to credit approval, 
    due diligence, and satisfactory documentation.
    """
    story.append(Paragraph(confidentiality.strip(), styles['small']))
    story.append(Spacer(1, 20))


def _add_transaction_summary(story, styles, params):
    """Add high-level transaction summary box."""
    story.append(Paragraph("TRANSACTION SUMMARY", styles['heading']))
    story.append(Spacer(1, 12))
    
    # Create summary table
    table_data = [
        ['Transaction Element', 'Details'],
        ['Borrower', f"{params['borrower']}\n(Co. No. {params['borrower_number']})"],
        ['Facility Type', 'Senior Term Loan'],
        ['Facility Amount', f"<b>{format_pounds(params['loan_amount'])}</b>"],
        ['Currency', params['currency']],
        ['Tenor', f"{params['tenor_months']} months"],
        ['Proposed Closing', params['proposed_close_date'].strftime('%d %B %Y')],
        ['Purpose', params['purpose']],
        ['Security', params['security_type']],
    ]
    
    table = create_info_table(table_data, col_widths=[2*72, 4.5*72])
    story.append(table)
    story.append(Spacer(1, 20))


def _add_key_terms(story, styles, params):
    """Add detailed facility terms."""
    story.append(Paragraph("KEY COMMERCIAL TERMS", styles['heading']))
    story.append(Spacer(1, 12))
    
    # Pricing section
    story.append(Paragraph("<b>Pricing:</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    pricing_data = [
        ['Component', 'Rate/Amount'],
        ['Base Rate', f'SONIA + {params["margin"]}%'],
        ['Current SONIA', f'{params["base_rate"]}%'],
        ['All-in Rate (indicative)', f'<b>{params["total_rate"]}% p.a.</b>'],
        ['Arrangement Fee', f'{format_pounds(params["arrangement_fee"])} ({(params["arrangement_fee"]/params["loan_amount"]*100):.2f}%)'],
        ['Commitment Fee', 'N/A (single drawdown)'],
    ]
    
    pricing_table = create_info_table(pricing_data, col_widths=[2.5*72, 3.5*72])
    story.append(pricing_table)
    story.append(Spacer(1, 15))
    
    # Repayment section
    story.append(Paragraph("<b>Repayment Structure:</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    repayment_type = random.choice(['Bullet repayment at maturity', 
                                    'Quarterly amortisation with balloon at maturity',
                                    'Monthly interest, bullet principal at maturity'])
    
    story.append(Paragraph(f"• <b>Principal:</b> {repayment_type}", styles['body']))
    story.append(Paragraph(f"• <b>Interest:</b> Payable quarterly in arrears", styles['body']))
    story.append(Paragraph(f"• <b>Prepayment:</b> Permitted with 30 days notice, subject to break costs", styles['body']))
    story.append(Spacer(1, 15))
    
    # Fees section
    story.append(Paragraph("<b>Fees:</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph(f"• <b>Arrangement Fee:</b> {format_pounds(params['arrangement_fee'])} payable on drawdown", styles['body']))
    story.append(Paragraph(f"• <b>Broker Fee:</b> {format_pounds(params['broker_fee'])} payable by Borrower on completion", styles['body']))
    story.append(Paragraph(f"• <b>Legal Fees:</b> Borrower to cover Lender's reasonable legal costs (capped at £15,000)", styles['body']))
    story.append(Spacer(1, 20))


def _add_borrower_profile(story, styles, params):
    """Add borrower profile and financial highlights."""
    story.append(Paragraph("BORROWER PROFILE", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>Company Name:</b> {params['borrower']}", styles['body']))
    story.append(Paragraph(f"<b>Registration:</b> {params['borrower_number']}", styles['body']))
    story.append(Paragraph(f"<b>Registered Office:</b> {params['borrower_address']}", styles['body']))
    story.append(Paragraph(f"<b>Sector:</b> {params['sector']}", styles['body']))
    story.append(Paragraph(f"<b>Years Trading:</b> {params['years_trading']} years", styles['body']))
    story.append(Spacer(1, 12))
    
    # Financial highlights
    story.append(Paragraph("<b>Financial Highlights (Latest FY):</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    financial_data = [
        ['Metric', 'Amount (£000s)'],
        ['Annual Revenue', f"{format_pounds(params['annual_revenue'])[1:-3]}"],  # Remove .00
        ['EBITDA', f"{format_pounds(params['ebitda'])[1:-3]}"],
        ['EBITDA Margin', f"{(params['ebitda']/params['annual_revenue']*100):.1f}%"],
        ['Proposed Debt', f"{format_pounds(params['loan_amount'])[1:-3]}"],
        ['Debt / EBITDA', f"{(params['loan_amount']/params['ebitda']):.1f}x"],
    ]
    
    financial_table = create_info_table(financial_data, col_widths=[2.5*72, 3.5*72])
    story.append(financial_table)
    story.append(Spacer(1, 20))


def _add_security_details(story, styles, params):
    """Add security package details."""
    story.append(Paragraph("SECURITY PACKAGE", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"The facility will be secured by the following:", styles['body']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph(f"• {params['security_type']}", styles['body']))
    
    # Add additional security items based on loan size
    if params['loan_amount'] > 5_000_000:
        story.append(Paragraph(f"• Personal guarantees from all directors", styles['body']))
        story.append(Paragraph(f"• Fixed and floating charge over all assets", styles['body']))
    
    if params['loan_amount'] > 10_000_000:
        story.append(Paragraph(f"• Assignment of material contracts", styles['body']))
        story.append(Paragraph(f"• Share pledge over subsidiaries (if applicable)", styles['body']))
    
    story.append(Spacer(1, 12))
    
    # Financial covenants
    story.append(Paragraph("<b>Financial Covenants (Indicative):</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph(f"• <b>Interest Cover:</b> Minimum 2.5x (tested quarterly)", styles['body']))
    story.append(Paragraph(f"• <b>Leverage:</b> Maximum Debt/EBITDA of 3.0x", styles['body']))
    story.append(Paragraph(f"• <b>Net Worth:</b> Maintain minimum tangible net worth of {format_pounds(params['loan_amount'] * 0.4)}", styles['body']))
    story.append(Spacer(1, 20))


def _add_broker_recommendation(story, styles, params):
    """Add broker's recommendation and deal rationale."""
    story.append(Paragraph("BROKER ASSESSMENT", styles['heading']))
    story.append(Spacer(1, 12))
    
    # Generate semi-randomized recommendation
    strengths = [
        f"Established business with {params['years_trading']} years operating history",
        f"Strong EBITDA margin of {(params['ebitda']/params['annual_revenue']*100):.1f}%",
        f"Conservative leverage at {(params['loan_amount']/params['ebitda']):.1f}x Debt/EBITDA",
        "Experienced management team",
        "Diversified customer base",
        f"Quality security package including {params['security_type'].lower()}",
    ]
    
    story.append(Paragraph("<b>Key Strengths:</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    for strength in random.sample(strengths, k=min(4, len(strengths))):
        story.append(Paragraph(f"• {strength}", styles['body']))
        story.append(Spacer(1, 4))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Broker Recommendation:</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    recommendation = f"""
    We recommend this transaction as a suitable senior debt opportunity. The borrower demonstrates 
    strong financial performance with sustainable cash generation. The proposed leverage of 
    {(params['loan_amount']/params['ebitda']):.1f}x EBITDA is conservative for the sector, and the 
    comprehensive security package provides strong downside protection. Management has been receptive 
    to covenant requirements and structural protections.
    """
    
    story.append(Paragraph(recommendation.strip(), styles['body']))
    story.append(Spacer(1, 20))


def _add_next_steps(story, styles, params):
    """Add next steps and timeline."""
    story.append(Paragraph("NEXT STEPS & TIMELINE", styles['heading']))
    story.append(Spacer(1, 12))
    
    # Calculate timeline milestones
    base_date = params['term_sheet_date']
    
    timeline_items = [
        ('Indicative term sheet issued', base_date),
        ('Initial credit assessment', base_date + timedelta(days=7)),
        ('Site visit and management meeting', base_date + timedelta(days=14)),
        ('Credit committee approval', base_date + timedelta(days=21)),
        ('Full due diligence', base_date + timedelta(days=35)),
        ('Legal documentation', base_date + timedelta(days=50)),
        ('Financial close', params['proposed_close_date']),
    ]
    
    table_data = [['Milestone', 'Target Date']]
    for item, date in timeline_items:
        table_data.append([item, date.strftime('%d %B %Y')])
    
    timeline_table = create_info_table(table_data, col_widths=[3.5*72, 2.5*72])
    story.append(timeline_table)
    story.append(Spacer(1, 20))


def _add_disclaimer(story, styles, params):
    """Add legal disclaimer and contact information."""
    story.append(Spacer(1, 30))
    
    disclaimer = """
    <b>IMPORTANT DISCLAIMER:</b> This term sheet is indicative only and does not constitute an offer, 
    commitment, or obligation to provide financing. All terms are subject to credit approval, 
    satisfactory due diligence, and execution of definitive documentation. The lender reserves the 
    right to modify or withdraw this proposal at any time. This term sheet is confidential and 
    may not be disclosed to third parties without the broker's prior written consent.
    """
    
    story.append(Paragraph(disclaimer.strip(), styles['small']))
    story.append(Spacer(1, 20))
    
    # Broker contact details
    story.append(Paragraph("<b>For further information, please contact:</b>", styles['body_bold']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>{params['broker_contact']}</b>", styles['body']))
    story.append(Paragraph(params['broker'], styles['body']))
    story.append(Paragraph(f"Tel: {params['broker_phone']}", styles['body']))
    story.append(Paragraph(f"Email: {params['broker_email']}", styles['body']))
