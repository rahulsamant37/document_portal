"""
Global Logger Module

This module provides a centralized GLOBAL_LOGGER instance that can be imported
and used across the entire document portal application.

Usage:
    from logger import GLOBAL_LOGGER as log
    
    log.info("Operation successful", user_id=123, filename="doc.pdf")
    log.error("Operation failed", error=str(e), traceback=traceback_str)
"""

from .custom_logger import CustomLogger

# Create a global logger instance that can be imported throughout the application
_custom_logger = CustomLogger()
GLOBAL_LOGGER = _custom_logger.get_logger("document_portal")

# For convenience, also expose the logger class
__all__ = ["GLOBAL_LOGGER", "CustomLogger"]