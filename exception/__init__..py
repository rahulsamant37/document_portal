"""
Exception Module

This module provides custom exception classes and exception handling utilities
for the document portal application.

Features:
- DocumentPortalException: Enhanced exception with detailed context
- Exception logging integration
- Structured error reporting

Usage:
    from exception import DocumentPortalException
    from exception.custom_exception import DocumentPortalException
"""

from .custom_exception import DocumentPortalException

__all__ = ["DocumentPortalException"]