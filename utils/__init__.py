"""
Utility functions shared across modules.
"""

from .config import get_config
from .logging import setup_logging

__all__ = ['get_config', 'setup_logging'] 