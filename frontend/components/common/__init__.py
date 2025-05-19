"""
Common Components for Humanyzer
This module contains common components that can be used across the application.
"""

from .keyboard_nav import add_keyboard_nav_to_page
from .transitions import add_transitions_to_page
from .mobile_enhancements import add_mobile_enhancements_to_page

def initialize_ui_enhancements():
    """
    Initialize all UI enhancements at once.
    This function should be called at the beginning of each page.
    """
    add_keyboard_nav_to_page()
    add_transitions_to_page()
    add_mobile_enhancements_to_page()
