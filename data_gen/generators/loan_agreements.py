"""
Loan Agreement Generator

Generates realistic UK merchant bank loan facility agreements with:
- Multi-page structure with schedules
- Standard loan clauses and covenants
- Security and guarantee details
- Varying complexity levels
"""

import random
from datetime import datetime, timedelta
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .document_utils import (
    create_pdf_document, get_custom_styles, add_header_block,
    add_date_block, create_info_table, add_signature_block,
    add_footer_disclaimer, format_pounds, random_name, random_job_title
)
from config import (
    UK_COMPANY_NAMES, UK_LENDERS, UK_ADDRESSES,
    LOAN_AMOUNT_RANGES, INTEREST_RATE_RANGE, LOAN_TENORS,
    SECURITY_TYPES, LOAN_PURPOSES, FINANCIAL_COVENANTS,
    random_date_range, random_company_number, random_reference_number
)


def generate_loan_agreement(output_path, seed=None):
    """
    Generate a single loan facility agreement PDF.
    
    Args:
        output_path: Path where PDF will be saved
        seed: Optional random seed for reproducibility
    
    Returns:
        dict: Metadata about the generated document
    """
    if seed is not None:
        random.seed(seed)
    
    # Generate loan parameters
    params = _generate_loan_parameters()
    
    # Create PDF
    doc, story = create_pdf_document(
        output_path,
        title=f"Loan Facility Agreement - {params['borrower']}",
        author=params['lender']
    )
    
    styles = get_custom_styles()
    
    # Build document content
    _add_title_page(story, styles, params)
    story.append(PageBreak())
    
    _add_parties_section(story, styles, params)
    _add_facility_terms(story, styles, params)
    _add_conditions_precedent(story, styles, params)
    _add_covenants_section(story, styles, params)
    _add_security_section(story, styles, params)
    _add_representations(story, styles, params)
    
    story.append(PageBreak())
    _add_schedules(story, styles, params)
    
    story.append(PageBreak())
    add_signature_block(story, styles, [params['borrower'], params['lender']])
    add_footer_disclaimer(story, styles)
    
    # Build the PDF
    doc.build(story)
    
    return params


def _generate_loan_parameters():
    """Generate random but realistic loan agreement parameters."""
    # Select loan size category and generate amount
    amount_range = random.choice(LOAN_AMOUNT_RANGES)
    loan_amount = random.randint(amount_range[0], amount_range[1])
    
    # Calculate related amounts
    loan_amount = round(loan_amount / 100000) * 100000  # Round to nearest 100k
    
    # Generate dates
    agreement_date = random_date_range(2023, 2026)
    drawdown_date = agreement_date + timedelta(days=random.randint(7, 45))
    tenor_months = random.choice(LOAN_TENORS)
    maturity_date = drawdown_date + timedelta(days=tenor_months * 30)
    
    # Interest rate
    base_rate = round(random.uniform(*INTEREST_RATE_RANGE), 2)
    margin = round(random.uniform(1.5, 3.5), 2)
    total_rate = base_rate + margin
    
    params = {
        'borrower': random.choice(UK_COMPANY_NAMES),
        'borrower_number': random_company_number(),
        'borrower_address': random.choice(UK_ADDRESSES),
        'lender': random.choice(UK_LENDERS),
        'lender_address': random.choice(UK_ADDRESSES),
        'facility_ref': random_reference_number("LF"),
        'agreement_date': agreement_date,
        'drawdown_date': drawdown_date,
        'maturity_date': maturity_date,
        'loan_amount': loan_amount,
        'currency': 'GBP',
        'base_rate': base_rate,
        'margin': margin,
        'interest_rate': total_rate,
        'tenor_months': tenor_months,
        'security_type': random.choice(SECURITY_TYPES),
        'purpose': random.choice(LOAN_PURPOSES),
        'covenants': random.sample(FINANCIAL_COVENANTS, k=3),
    }
    
    return params


def _add_title_page(story, styles, params):
    """Add the title page with key facility details."""
    story.append(Spacer(1, 100))
    
    # Main title
    title = f"LOAN FACILITY AGREEMENT"
    story.append(Paragraph(title, styles['title']))
    story.append(Spacer(1, 40))
    
    # Facility amount (prominent display)
    amount_text = f"<b>Facility Amount: {format_pounds(params['loan_amount'])}</b>"
    story.append(Paragraph(amount_text, styles['heading']))
    story.append(Spacer(1, 60))
    
    # Parties
    story.append(Paragraph(f"<b>Between:</b>", styles['body_bold']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(f"<b>{params['lender']}</b>", styles['body']))
    story.append(Paragraph("(the <b>\"Lender\"</b>)", styles['body']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("<b>and</b>", styles['body_bold']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(f"<b>{params['borrower']}</b>", styles['body']))
    story.append(Paragraph(f"Company Number: {params['borrower_number']}", styles['body']))
    story.append(Paragraph("(the <b>\"Borrower\"</b>)", styles['body']))
    story.append(Spacer(1, 60))
    
    # Date and reference
    add_date_block(story, styles, params['agreement_date'], "Dated")
    story.append(Paragraph(f"<b>Facility Reference:</b> {params['facility_ref']}", styles['body']))


def _add_parties_section(story, styles, params):
    """Add parties and definitions section."""
    story.append(Paragraph("1. PARTIES AND DEFINITIONS", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.1 <b>The Lender:</b>", styles['subheading']))
    story.append(Paragraph(f"{params['lender']}, a company incorporated in England and Wales, having its registered office at {params['lender_address']}.", styles['body']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.2 <b>The Borrower:</b>", styles['subheading']))
    story.append(Paragraph(f"{params['borrower']}, a company incorporated in England and Wales (Company Number: {params['borrower_number']}), having its registered office at {params['borrower_address']}.", styles['body']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("1.3 <b>Definitions:</b>", styles['subheading']))
    definitions = [
        '<b>"Facility"</b> means the term loan facility made available by the Lender to the Borrower on the terms of this Agreement.',
        f'<b>"Facility Amount"</b> means {format_pounds(params["loan_amount"])}.',
        '<b>"Business Day"</b> means a day (other than a Saturday or Sunday) on which banks are open for general business in London.',
        f'<b>"Maturity Date"</b> means {params["maturity_date"].strftime("%d %B %Y")}.',
        '<b>"Security Documents"</b> means the documents creating or evidencing the Security.',
    ]
    for definition in definitions:
        story.append(Paragraph(f"• {definition}", styles['body']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))


def _add_facility_terms(story, styles, params):
    """Add the facility terms and conditions section."""
    story.append(Paragraph("2. THE FACILITY", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.1 <b>Facility Amount:</b>", styles['subheading']))
    story.append(Paragraph(
        f"The Lender makes available to the Borrower a term loan facility in an aggregate amount of {format_pounds(params['loan_amount'])} (the \"Facility\").",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.2 <b>Purpose:</b>", styles['subheading']))
    story.append(Paragraph(
        f"The Borrower shall apply all amounts borrowed under the Facility towards {params['purpose']}.",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.3 <b>Interest Rate:</b>", styles['subheading']))
    story.append(Paragraph(
        f"Interest shall accrue on the Facility at a rate per annum equal to {params['base_rate']}% (SONIA) plus a margin of {params['margin']}%, being a total rate of {params['interest_rate']}% per annum.",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("2.4 <b>Repayment:</b>", styles['subheading']))
    story.append(Paragraph(
        f"The Borrower shall repay the Facility in full on the Maturity Date, being {params['maturity_date'].strftime('%d %B %Y')}, together with all accrued interest and other amounts due under this Agreement.",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    # Create facility summary table
    story.append(Paragraph("2.5 <b>Facility Summary:</b>", styles['subheading']))
    story.append(Spacer(1, 6))
    
    table_data = [
        ['Facility Details', 'Terms'],
        ['Facility Type', 'Term Loan'],
        ['Facility Amount', format_pounds(params['loan_amount'])],
        ['Currency', params['currency']],
        ['Drawdown Date', params['drawdown_date'].strftime('%d %B %Y')],
        ['Maturity Date', params['maturity_date'].strftime('%d %B %Y')],
        ['Tenor', f"{params['tenor_months']} months"],
        ['Interest Rate', f"{params['interest_rate']}% p.a."],
        ['Interest Payment', 'Quarterly in arrears'],
        ['Security', params['security_type']],
    ]
    
    table = create_info_table(table_data)
    story.append(table)
    story.append(Spacer(1, 20))


def _add_conditions_precedent(story, styles, params):
    """Add conditions precedent section."""
    story.append(Paragraph("3. CONDITIONS PRECEDENT", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "3.1 The Lender shall not be obliged to make the Facility available until it has received all of the following documents and evidence, in form and substance satisfactory to the Lender:",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    conditions = [
        "A copy of the constitutional documents of the Borrower",
        "A copy of a resolution of the board of directors of the Borrower approving the terms of this Agreement",
        "A certificate of the Borrower certifying that borrowing is within the Borrower's corporate powers",
        "Evidence of the identity of each person who is an authorised signatory",
        "The Security Documents, duly executed",
        "Evidence of insurance as required by the Lender",
        "Legal opinions from the Borrower's solicitors",
        "Three years of audited financial statements",
        "Current management accounts not more than one month old",
        "A certificate of solvency from the Borrower's directors"
    ]
    
    for i, condition in enumerate(conditions, 1):
        story.append(Paragraph(f"({chr(96+i)}) {condition};", styles['body']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))


def _add_covenants_section(story, styles, params):
    """Add financial and other covenants."""
    story.append(Paragraph("4. COVENANTS", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.1 <b>Financial Covenants:</b>", styles['subheading']))
    story.append(Paragraph(
        "The Borrower undertakes that it shall ensure that the following financial covenants are complied with at all times:",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    for i, covenant in enumerate(params['covenants'], 1):
        # Format covenant with placeholder values
        if '{}' in covenant:
            value = random.randint(1, 10)
            covenant = covenant.format(value)
        story.append(Paragraph(f"({chr(96+i)}) {covenant};", styles['body']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("4.2 <b>Information Covenants:</b>", styles['subheading']))
    story.append(Paragraph(
        "The Borrower shall supply to the Lender:",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    info_covenants = [
        "Annual audited financial statements within 120 days of financial year end",
        "Quarterly management accounts within 30 days of quarter end",
        "A compliance certificate with each set of financial statements",
        "Notice of any default or potential default immediately upon becoming aware",
        "Details of any litigation exceeding £100,000 within 5 Business Days"
    ]
    
    for i, covenant in enumerate(info_covenants, 1):
        story.append(Paragraph(f"({chr(96+i)}) {covenant};", styles['body']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))


def _add_security_section(story, styles, params):
    """Add security and guarantees section."""
    story.append(Paragraph("5. SECURITY", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("5.1 <b>Security Documents:</b>", styles['subheading']))
    story.append(Paragraph(
        f"The obligations of the Borrower under this Agreement are secured by way of {params['security_type']} created by the Security Documents.",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("5.2 <b>Priority:</b>", styles['subheading']))
    story.append(Paragraph(
        "The Security shall rank in priority to all other security interests over the assets of the Borrower.",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("5.3 <b>Further Assurance:</b>", styles['subheading']))
    story.append(Paragraph(
        "The Borrower shall promptly do all such acts and execute all such documents as the Lender may reasonably specify to perfect the Security.",
        styles['body']
    ))
    story.append(Spacer(1, 20))


def _add_representations(story, styles, params):
    """Add representations and warranties section."""
    story.append(Paragraph("6. REPRESENTATIONS AND WARRANTIES", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "6.1 The Borrower represents and warrants to the Lender that:",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    reps = [
        "<b>Status:</b> It is a company duly incorporated and validly existing under the law of England and Wales.",
        "<b>Power and authority:</b> It has the power to enter into and perform this Agreement and the transactions contemplated by this Agreement.",
        "<b>Legal validity:</b> This Agreement constitutes legal, valid and binding obligations.",
        "<b>Non-conflict:</b> The entry into and performance of this Agreement does not conflict with any law or regulation or any document binding on it.",
        "<b>No default:</b> No event of default is outstanding or might result from the making or performance of the Agreement.",
        "<b>Financial statements:</b> Its most recent financial statements fairly represent its financial condition.",
        "<b>Pari passu ranking:</b> Its payment obligations under this Agreement rank at least pari passu with all its other present and future unsecured and unsubordinated obligations.",
        "<b>No misleading information:</b> All information provided to the Lender is true, complete and accurate."
    ]
    
    for i, rep in enumerate(reps, 1):
        story.append(Paragraph(f"({chr(96+i)}) {rep}", styles['body']))
        story.append(Spacer(1, 6))
    
    story.append(Spacer(1, 20))


def _add_schedules(story, styles, params):
    """Add schedules and appendices."""
    story.append(Paragraph("SCHEDULE 1 - REPAYMENT SCHEDULE", styles['heading']))
    story.append(Spacer(1, 12))
    
    # Generate a simple repayment schedule
    story.append(Paragraph(
        f"The Facility shall be repaid in accordance with the following schedule:",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    # For simplicity, bullet repayment at maturity
    story.append(Paragraph(
        f"<b>Bullet Repayment:</b> The entire principal amount of {format_pounds(params['loan_amount'])} shall be repaid on the Maturity Date ({params['maturity_date'].strftime('%d %B %Y')}).",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        "<b>Interest Payments:</b> Interest shall be paid quarterly in arrears on the last Business Day of each calendar quarter.",
        styles['body']
    ))
    story.append(Spacer(1, 30))
    
    # Add Schedule 2
    story.append(Paragraph("SCHEDULE 2 - FORM OF DRAWDOWN NOTICE", styles['heading']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("To: " + params['lender'], styles['body']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        f"We refer to the Loan Facility Agreement dated {params['agreement_date'].strftime('%d %B %Y')} (the \"Agreement\"). Terms defined in the Agreement have the same meaning in this notice.",
        styles['body']
    ))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph(
        f"We hereby give you notice that we wish to borrow £[amount] under the Facility on [date].",
        styles['body']
    ))
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("For and on behalf of", styles['body']))
    story.append(Paragraph(params['borrower'], styles['body_bold']))
