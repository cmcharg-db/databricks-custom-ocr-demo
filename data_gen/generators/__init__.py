"""
Document generators package for creating synthetic UK merchant bank lending documents.
"""

from .loan_agreements import generate_loan_agreement
from .term_sheets import generate_term_sheet
from .financial_statements import generate_financial_statement

__all__ = [
    'generate_loan_agreement',
    'generate_term_sheet',
    'generate_financial_statement',
]
