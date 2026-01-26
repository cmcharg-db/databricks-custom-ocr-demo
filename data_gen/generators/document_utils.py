"""
Utility functions for document generation.
Shared helper functions for creating PDFs, formatting text, and styling documents.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import random


def create_pdf_document(filename, title="Document", author="System Generated"):
    """
    Create a basic PDF document template with standard UK A4 page size.
    
    Args:
        filename: Output PDF file path
        title: Document title for metadata
        author: Document author for metadata
    
    Returns:
        tuple: (doc, story) where doc is SimpleDocTemplate and story is content list
    """
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72,
        title=title,
        author=author
    )
    
    story = []
    return doc, story


def get_custom_styles():
    """
    Create custom paragraph styles for UK business documents.
    
    Returns:
        dict: Dictionary of ParagraphStyle objects
    """
    styles = getSampleStyleSheet()
    
    # Title style - for main document headings
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1a365d'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Heading style - for section headings
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2d3748'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    # Subheading style
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#4a5568'),
        spaceAfter=6,
        spaceBefore=6,
        fontName='Helvetica-Bold'
    )
    
    # Body text - justified for formal documents
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
        fontName='Helvetica'
    )
    
    # Small print style - for footnotes and disclaimers
    small_style = ParagraphStyle(
        'CustomSmall',
        parent=styles['BodyText'],
        fontSize=8,
        textColor=colors.HexColor('#718096'),
        spaceAfter=6,
        fontName='Helvetica'
    )
    
    # Bold body text
    body_bold_style = ParagraphStyle(
        'CustomBodyBold',
        parent=styles['BodyText'],
        fontSize=10,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    return {
        'title': title_style,
        'heading': heading_style,
        'subheading': subheading_style,
        'body': body_style,
        'small': small_style,
        'body_bold': body_bold_style,
        'normal': styles['Normal'],
    }


def add_header_block(story, styles, lender_name, lender_address, doc_ref=None):
    """
    Add a standard letterhead/header block to the document.
    
    Args:
        story: Document story list to append to
        styles: Dictionary of paragraph styles
        lender_name: Name of the lending institution
        lender_address: Address of the lender
        doc_ref: Optional document reference number
    """
    # Lender name (acts as letterhead)
    story.append(Paragraph(f"<b>{lender_name}</b>", styles['heading']))
    story.append(Paragraph(lender_address, styles['small']))
    
    if doc_ref:
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"Reference: {doc_ref}", styles['small']))
    
    story.append(Spacer(1, 20))


def add_date_block(story, styles, date_obj, label="Date"):
    """
    Add a formatted date block.
    
    Args:
        story: Document story list to append to
        styles: Dictionary of paragraph styles
        date_obj: datetime object
        label: Label for the date (e.g., "Date", "Dated")
    """
    formatted_date = date_obj.strftime("%d %B %Y")
    story.append(Paragraph(f"<b>{label}:</b> {formatted_date}", styles['body']))
    story.append(Spacer(1, 12))


def create_info_table(data, col_widths=None):
    """
    Create a styled table for key information display.
    Commonly used for loan details, financial summary, etc.
    
    Args:
        data: List of lists containing table data
        col_widths: Optional list of column widths
    
    Returns:
        Table: Styled reportlab Table object
    """
    if col_widths is None:
        col_widths = [2.5*inch, 4*inch]
    
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        # Header row styling
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1a365d')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body styling
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        
        # Alternate row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f7fafc')]),
    ]))
    
    return table


def create_financial_table(data, col_widths=None, has_header=True):
    """
    Create a financial table with currency formatting and totals styling.
    
    Args:
        data: List of lists containing table data
        col_widths: Optional list of column widths
        has_header: Boolean indicating if first row is a header
    
    Returns:
        Table: Styled reportlab Table object
    """
    if col_widths is None:
        # Default to label column + 2-3 data columns
        num_cols = len(data[0]) if data else 3
        col_widths = [2*inch] + [1.5*inch] * (num_cols - 1)
    
    table = Table(data, colWidths=col_widths)
    
    style_commands = [
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        
        # Right-align numeric columns (all except first)
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
    ]
    
    if has_header:
        # Header row styling
        style_commands.extend([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2d3748')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
        ])
        
        # Body rows
        style_commands.extend([
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ])
    
    # Total/subtotal rows (typically last row) in bold
    if len(data) > 1:
        style_commands.extend([
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ])
    
    table.setStyle(TableStyle(style_commands))
    return table


def add_signature_block(story, styles, parties):
    """
    Add signature blocks for multiple parties.
    
    Args:
        story: Document story list to append to
        styles: Dictionary of paragraph styles
        parties: List of party names requiring signatures
    """
    story.append(Spacer(1, 30))
    story.append(Paragraph("<b>EXECUTED as a DEED:</b>", styles['body_bold']))
    story.append(Spacer(1, 20))
    
    for party in parties:
        story.append(Paragraph(f"<b>{party}</b>", styles['body']))
        story.append(Spacer(1, 30))
        story.append(Paragraph("_" * 40, styles['body']))
        story.append(Paragraph("Authorised Signatory", styles['small']))
        story.append(Spacer(1, 10))
        story.append(Paragraph("Name: _______________________", styles['small']))
        story.append(Paragraph("Title: _______________________", styles['small']))
        story.append(Paragraph("Date: _______________________", styles['small']))
        story.append(Spacer(1, 20))


def add_footer_disclaimer(story, styles):
    """
    Add a standard legal disclaimer footer.
    
    Args:
        story: Document story list to append to
        styles: Dictionary of paragraph styles
    """
    disclaimer_text = """
    This document is private and confidential. It is intended solely for the use of the individual 
    or entity to whom it is addressed. If you are not the intended recipient, please notify the 
    sender immediately and destroy this document. This document contains legally privileged and 
    confidential information.
    """
    story.append(Spacer(1, 30))
    story.append(Paragraph(disclaimer_text.strip(), styles['small']))


def format_pounds(amount):
    """Format amount as British pounds with proper formatting."""
    return f"£{amount:,.2f}"


def format_percentage(value):
    """Format decimal as percentage."""
    return f"{value:.2%}"


def random_name():
    """Generate a random person name for signatories."""
    first_names = ["James", "Oliver", "Emma", "Sophie", "William", "Charlotte", "Thomas", "Emily", 
                   "Henry", "Amelia", "George", "Isabella", "Alexander", "Olivia", "Edward"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Taylor", "Davies", "Wilson",
                  "Evans", "Thomas", "Roberts", "Walker", "Wright", "Thompson", "White"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def random_job_title():
    """Generate a random executive job title."""
    titles = [
        "Managing Director",
        "Chief Financial Officer",
        "Chief Executive Officer",
        "Director",
        "Financial Controller",
        "Company Secretary",
        "Operations Director",
        "Commercial Director"
    ]
    return random.choice(titles)
