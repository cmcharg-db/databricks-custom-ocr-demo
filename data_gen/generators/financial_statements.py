"""
Financial Statement Generator

Generates realistic UK company financial statements including:
- Balance Sheets
- Profit & Loss Statements
- Cash Flow Statements

These are typically submitted as part of lending applications and due diligence.
"""

import random
from datetime import datetime
from reportlab.platypus import Paragraph, Spacer, PageBreak
from .document_utils import (
    create_pdf_document, get_custom_styles, create_financial_table,
    format_pounds, random_name, random_job_title
)
from config import (
    UK_COMPANY_NAMES, UK_ADDRESSES, REVENUE_RANGES,
    GROSS_MARGIN_RANGE, OPERATING_MARGIN_RANGE, NET_MARGIN_RANGE,
    random_date_range, random_company_number
)


def generate_financial_statement(output_path, seed=None):
    """
    Generate a financial statement document (combination of Balance Sheet and P&L).
    
    Args:
        output_path: Path where PDF will be saved
        seed: Optional random seed for reproducibility
    
    Returns:
        dict: Metadata about the generated document
    """
    if seed is not None:
        random.seed(seed)
    
    # Generate financial parameters
    params = _generate_financial_parameters()
    
    # Create PDF
    doc, story = create_pdf_document(
        output_path,
        title=f"Financial Statements - {params['company']}",
        author=params['company']
    )
    
    styles = get_custom_styles()
    
    # Build document content
    _add_cover_page(story, styles, params)
    story.append(PageBreak())
    
    _add_profit_loss_statement(story, styles, params)
    story.append(PageBreak())
    
    _add_balance_sheet(story, styles, params)
    story.append(PageBreak())
    
    _add_notes(story, styles, params)
    
    # Build the PDF
    doc.build(story)
    
    return params


def _generate_financial_parameters():
    """Generate realistic financial statement data."""
    # Select company size and generate revenue
    revenue_range = random.choice(REVENUE_RANGES)
    revenue = random.randint(revenue_range[0], revenue_range[1])
    revenue = round(revenue / 100000) * 100000  # Round to nearest 100k
    
    # Generate margins
    gross_margin = random.uniform(*GROSS_MARGIN_RANGE)
    operating_margin = random.uniform(*OPERATING_MARGIN_RANGE)
    net_margin = random.uniform(*NET_MARGIN_RANGE)
    
    # Calculate P&L items
    cost_of_sales = revenue * (1 - gross_margin)
    gross_profit = revenue - cost_of_sales
    
    # Operating expenses
    staff_costs = gross_profit * random.uniform(0.35, 0.50)
    admin_costs = gross_profit * random.uniform(0.10, 0.20)
    depreciation = gross_profit * random.uniform(0.03, 0.08)
    other_expenses = gross_profit * random.uniform(0.05, 0.15)
    
    operating_profit = revenue * operating_margin
    
    # Interest and tax
    interest_expense = revenue * random.uniform(0.005, 0.02)
    profit_before_tax = operating_profit - interest_expense
    tax_expense = profit_before_tax * random.uniform(0.18, 0.21)  # UK corporation tax
    net_profit = revenue * net_margin
    
    # Balance sheet items (simplified but realistic ratios)
    # Assets
    cash = revenue * random.uniform(0.05, 0.15)
    receivables = revenue * random.uniform(0.10, 0.20)
    inventory = cost_of_sales * random.uniform(0.15, 0.30)
    current_assets = cash + receivables + inventory + (revenue * random.uniform(0.02, 0.05))
    
    fixed_assets_gross = revenue * random.uniform(0.40, 0.80)
    accumulated_depreciation = fixed_assets_gross * random.uniform(0.25, 0.50)
    fixed_assets_net = fixed_assets_gross - accumulated_depreciation
    
    total_assets = current_assets + fixed_assets_net
    
    # Liabilities
    payables = cost_of_sales * random.uniform(0.10, 0.20)
    short_term_debt = revenue * random.uniform(0.05, 0.15)
    accruals = revenue * random.uniform(0.03, 0.08)
    current_liabilities = payables + short_term_debt + accruals
    
    long_term_debt = revenue * random.uniform(0.15, 0.40)
    provisions = revenue * random.uniform(0.02, 0.06)
    non_current_liabilities = long_term_debt + provisions
    
    total_liabilities = current_liabilities + non_current_liabilities
    
    # Equity (balancing item)
    share_capital = round(revenue * random.uniform(0.05, 0.15), 0)
    retained_earnings = total_assets - total_liabilities - share_capital
    total_equity = share_capital + retained_earnings
    
    # Financial year
    year_end_date = random_date_range(2023, 2025)
    year_end_date = year_end_date.replace(month=12, day=31)  # Year-end
    
    params = {
        'company': random.choice(UK_COMPANY_NAMES),
        'company_number': random_company_number(),
        'address': random.choice(UK_ADDRESSES),
        'year_end': year_end_date,
        'previous_year_end': year_end_date.replace(year=year_end_date.year - 1),
        'director_name': random_name(),
        'director_title': random_job_title(),
        # P&L items
        'revenue': revenue,
        'cost_of_sales': cost_of_sales,
        'gross_profit': gross_profit,
        'staff_costs': staff_costs,
        'admin_costs': admin_costs,
        'depreciation': depreciation,
        'other_expenses': other_expenses,
        'operating_profit': operating_profit,
        'interest_expense': interest_expense,
        'profit_before_tax': profit_before_tax,
        'tax_expense': tax_expense,
        'net_profit': net_profit,
        # Balance sheet - Assets
        'cash': cash,
        'receivables': receivables,
        'inventory': inventory,
        'current_assets': current_assets,
        'fixed_assets_gross': fixed_assets_gross,
        'accumulated_depreciation': accumulated_depreciation,
        'fixed_assets_net': fixed_assets_net,
        'total_assets': total_assets,
        # Balance sheet - Liabilities
        'payables': payables,
        'short_term_debt': short_term_debt,
        'accruals': accruals,
        'current_liabilities': current_liabilities,
        'long_term_debt': long_term_debt,
        'provisions': provisions,
        'non_current_liabilities': non_current_liabilities,
        'total_liabilities': total_liabilities,
        # Balance sheet - Equity
        'share_capital': share_capital,
        'retained_earnings': retained_earnings,
        'total_equity': total_equity,
    }
    
    # Generate prior year (with growth)
    growth_rate = random.uniform(-0.05, 0.15)  # -5% to +15% YoY
    params['revenue_py'] = revenue / (1 + growth_rate)
    params['net_profit_py'] = net_profit / (1 + growth_rate * 1.2)  # Slightly different leverage
    
    return params


def _add_cover_page(story, styles, params):
    """Add cover page with company details."""
    story.append(Spacer(1, 100))
    
    story.append(Paragraph(params['company'], styles['title']))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Company Number: {params['company_number']}", styles['body']))
    story.append(Spacer(1, 60))
    
    story.append(Paragraph("FINANCIAL STATEMENTS", styles['heading']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(f"For the year ended {params['year_end'].strftime('%d %B %Y')}", styles['body_bold']))
    story.append(Spacer(1, 80))
    
    story.append(Paragraph("Contents:", styles['subheading']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("• Profit and Loss Statement", styles['body']))
    story.append(Paragraph("• Balance Sheet", styles['body']))
    story.append(Paragraph("• Notes to the Financial Statements", styles['body']))
    story.append(Spacer(1, 60))
    
    story.append(Paragraph(f"Registered Office:", styles['body_bold']))
    story.append(Paragraph(params['address'], styles['body']))


def _add_profit_loss_statement(story, styles, params):
    """Add profit and loss statement."""
    story.append(Paragraph(params['company'], styles['heading']))
    story.append(Paragraph(f"Company Number: {params['company_number']}", styles['small']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("PROFIT AND LOSS STATEMENT", styles['heading']))
    story.append(Paragraph(
        f"For the year ended {params['year_end'].strftime('%d %B %Y')}",
        styles['subheading']
    ))
    story.append(Spacer(1, 20))
    
    # Create P&L table
    cy = params['year_end'].year
    py = cy - 1
    
    pl_data = [
        ['', f'{cy}\n£', f'{py}\n£'],
        ['Revenue', _format_financial(params['revenue']), _format_financial(params['revenue_py'])],
        ['Cost of sales', f"({_format_financial(params['cost_of_sales'])})", f"({_format_financial(params['revenue_py'] * 0.65)})"],
        ['', '', ''],
        ['Gross profit', _format_financial(params['gross_profit']), _format_financial(params['revenue_py'] * 0.35)],
        ['', '', ''],
        ['Operating expenses:', '', ''],
        ['  Staff costs', f"({_format_financial(params['staff_costs'])})", f"({_format_financial(params['revenue_py'] * 0.15)})"],
        ['  Administrative expenses', f"({_format_financial(params['admin_costs'])})", f"({_format_financial(params['revenue_py'] * 0.08)})"],
        ['  Depreciation', f"({_format_financial(params['depreciation'])})", f"({_format_financial(params['revenue_py'] * 0.03)})"],
        ['  Other operating expenses', f"({_format_financial(params['other_expenses'])})", f"({_format_financial(params['revenue_py'] * 0.05)})"],
        ['', '', ''],
        ['Operating profit', _format_financial(params['operating_profit']), _format_financial(params['revenue_py'] * 0.08)],
        ['', '', ''],
        ['Finance costs', f"({_format_financial(params['interest_expense'])})", f"({_format_financial(params['revenue_py'] * 0.01)})"],
        ['', '', ''],
        ['Profit before taxation', _format_financial(params['profit_before_tax']), _format_financial(params['revenue_py'] * 0.07)],
        ['', '', ''],
        ['Taxation', f"({_format_financial(params['tax_expense'])})", f"({_format_financial(params['revenue_py'] * 0.014)})"],
        ['', '', ''],
        ['Profit for the year', _format_financial(params['net_profit']), _format_financial(params['net_profit_py'])],
    ]
    
    pl_table = create_financial_table(pl_data, col_widths=[3.5*72, 1.5*72, 1.5*72], has_header=True)
    story.append(pl_table)
    story.append(Spacer(1, 30))
    
    # Add key ratios
    story.append(Paragraph("Key Financial Ratios:", styles['subheading']))
    story.append(Spacer(1, 6))
    
    gross_margin_pct = (params['gross_profit'] / params['revenue'] * 100)
    operating_margin_pct = (params['operating_profit'] / params['revenue'] * 100)
    net_margin_pct = (params['net_profit'] / params['revenue'] * 100)
    
    story.append(Paragraph(f"• Gross Margin: {gross_margin_pct:.1f}%", styles['body']))
    story.append(Paragraph(f"• Operating Margin: {operating_margin_pct:.1f}%", styles['body']))
    story.append(Paragraph(f"• Net Profit Margin: {net_margin_pct:.1f}%", styles['body']))


def _add_balance_sheet(story, styles, params):
    """Add balance sheet."""
    story.append(Paragraph(params['company'], styles['heading']))
    story.append(Paragraph(f"Company Number: {params['company_number']}", styles['small']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("BALANCE SHEET", styles['heading']))
    story.append(Paragraph(
        f"As at {params['year_end'].strftime('%d %B %Y')}",
        styles['subheading']
    ))
    story.append(Spacer(1, 20))
    
    cy = params['year_end'].year
    py = cy - 1
    
    # Assets section
    bs_data = [
        ['', f'{cy}\n£', f'{py}\n£'],
        ['ASSETS', '', ''],
        ['', '', ''],
        ['Fixed Assets', '', ''],
        ['  Property, plant and equipment', _format_financial(params['fixed_assets_net']), _format_financial(params['fixed_assets_net'] * 0.95)],
        ['', '', ''],
        ['Current Assets', '', ''],
        ['  Inventory', _format_financial(params['inventory']), _format_financial(params['inventory'] * 0.92)],
        ['  Trade receivables', _format_financial(params['receivables']), _format_financial(params['receivables'] * 0.88)],
        ['  Cash and cash equivalents', _format_financial(params['cash']), _format_financial(params['cash'] * 1.15)],
        ['', '', ''],
        ['Total Current Assets', _format_financial(params['current_assets']), _format_financial(params['current_assets'] * 0.93)],
        ['', '', ''],
        ['TOTAL ASSETS', _format_financial(params['total_assets']), _format_financial(params['total_assets'] * 0.94)],
        ['', '', ''],
        ['', '', ''],
        ['LIABILITIES', '', ''],
        ['', '', ''],
        ['Current Liabilities', '', ''],
        ['  Trade payables', f"({_format_financial(params['payables'])})", f"({_format_financial(params['payables'] * 0.90)})"],
        ['  Short-term borrowings', f"({_format_financial(params['short_term_debt'])})", f"({_format_financial(params['short_term_debt'] * 0.85)})"],
        ['  Accruals', f"({_format_financial(params['accruals'])})", f"({_format_financial(params['accruals'] * 0.92)})"],
        ['', '', ''],
        ['Total Current Liabilities', f"({_format_financial(params['current_liabilities'])})", f"({_format_financial(params['current_liabilities'] * 0.89)})"],
        ['', '', ''],
        ['Non-Current Liabilities', '', ''],
        ['  Long-term borrowings', f"({_format_financial(params['long_term_debt'])})", f"({_format_financial(params['long_term_debt'] * 1.05)})"],
        ['  Provisions', f"({_format_financial(params['provisions'])})", f"({_format_financial(params['provisions'] * 0.88)})"],
        ['', '', ''],
        ['Total Non-Current Liabilities', f"({_format_financial(params['non_current_liabilities'])})", f"({_format_financial(params['non_current_liabilities'] * 1.02)})"],
        ['', '', ''],
        ['TOTAL LIABILITIES', f"({_format_financial(params['total_liabilities'])})", f"({_format_financial(params['total_liabilities'] * 0.96)})"],
        ['', '', ''],
        ['', '', ''],
        ['EQUITY', '', ''],
        ['  Share capital', _format_financial(params['share_capital']), _format_financial(params['share_capital'])],
        ['  Retained earnings', _format_financial(params['retained_earnings']), _format_financial(params['retained_earnings'] * 0.85)],
        ['', '', ''],
        ['TOTAL EQUITY', _format_financial(params['total_equity']), _format_financial(params['total_equity'] * 0.92)],
        ['', '', ''],
        ['TOTAL LIABILITIES AND EQUITY', _format_financial(params['total_assets']), _format_financial(params['total_assets'] * 0.94)],
    ]
    
    bs_table = create_financial_table(bs_data, col_widths=[3.5*72, 1.5*72, 1.5*72], has_header=True)
    story.append(bs_table)
    story.append(Spacer(1, 30))
    
    # Add key balance sheet ratios
    story.append(Paragraph("Key Balance Sheet Ratios:", styles['subheading']))
    story.append(Spacer(1, 6))
    
    current_ratio = params['current_assets'] / params['current_liabilities']
    debt_to_equity = params['total_liabilities'] / params['total_equity']
    
    story.append(Paragraph(f"• Current Ratio: {current_ratio:.2f}", styles['body']))
    story.append(Paragraph(f"• Debt to Equity: {debt_to_equity:.2f}", styles['body']))
    story.append(Paragraph(f"• Net Working Capital: {format_pounds(params['current_assets'] - params['current_liabilities'])}", styles['body']))


def _add_notes(story, styles, params):
    """Add notes to the financial statements."""
    story.append(Paragraph(params['company'], styles['heading']))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("NOTES TO THE FINANCIAL STATEMENTS", styles['heading']))
    story.append(Paragraph(
        f"For the year ended {params['year_end'].strftime('%d %B %Y')}",
        styles['subheading']
    ))
    story.append(Spacer(1, 20))
    
    # Note 1
    story.append(Paragraph("1. Accounting Policies", styles['subheading']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "These financial statements have been prepared in accordance with Financial Reporting Standard 102 "
        "\"The Financial Reporting Standard applicable in the UK and Republic of Ireland\" (FRS 102) and the "
        "Companies Act 2006. The financial statements have been prepared under the historical cost convention.",
        styles['body']
    ))
    story.append(Spacer(1, 15))
    
    # Note 2
    story.append(Paragraph("2. Revenue", styles['subheading']))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Revenue for the year was {format_pounds(params['revenue'])} (previous year: {format_pounds(params['revenue_py'])}). "
        "Revenue represents amounts receivable for goods and services provided in the normal course of business, "
        "net of trade discounts, VAT and other sales related taxes.",
        styles['body']
    ))
    story.append(Spacer(1, 15))
    
    # Note 3
    story.append(Paragraph("3. Employees", styles['subheading']))
    story.append(Spacer(1, 6))
    num_employees = int(params['revenue'] / random.uniform(150000, 250000))
    story.append(Paragraph(
        f"The average number of employees during the year was {num_employees} (previous year: {int(num_employees * 0.95)}). "
        f"Staff costs for the year amounted to {format_pounds(params['staff_costs'])}.",
        styles['body']
    ))
    story.append(Spacer(1, 15))
    
    # Note 4
    story.append(Paragraph("4. Taxation", styles['subheading']))
    story.append(Spacer(1, 6))
    effective_tax_rate = (params['tax_expense'] / params['profit_before_tax'] * 100)
    story.append(Paragraph(
        f"The tax charge for the year was {format_pounds(params['tax_expense'])} representing an effective "
        f"tax rate of {effective_tax_rate:.1f}%. The charge is based on the standard UK corporation tax rate "
        "of 19%, adjusted for permanent differences.",
        styles['body']
    ))
    story.append(Spacer(1, 30))
    
    # Directors' signature
    story.append(Paragraph("Approved by the Board of Directors and authorised for issue on:", styles['body']))
    story.append(Spacer(1, 6))
    
    approval_date = params['year_end'] + random.randint(60, 120) * 24 * 60 * 60  # 2-4 months after year end
    story.append(Paragraph(f"{approval_date.strftime('%d %B %Y')}", styles['body_bold']))
    story.append(Spacer(1, 30))
    
    story.append(Paragraph("_" * 40, styles['body']))
    story.append(Paragraph(params['director_name'], styles['body_bold']))
    story.append(Paragraph(params['director_title'], styles['body']))


def _format_financial(amount):
    """Format financial amounts for tables (no currency symbol, comma separated)."""
    return f"{int(amount):,}"
