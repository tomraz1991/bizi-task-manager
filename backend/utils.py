"""
Utility functions for the podcast task manager.
"""
from typing import Optional
from datetime import datetime
from dateutil import parser

from constants import DEFAULT_NOTIFICATION_DAYS, FAR_FUTURE_DAYS, TASK_TYPE_LABELS


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string in various formats.
    
    Args:
        date_str: Date string in formats like DD.MM.YY, DD/MM/YY, or ISO format
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str or date_str.strip() == "":
        return None
    
    try:
        # Try parsing common formats: DD.MM.YY, DD/MM/YY, DD.MM.YYYY, etc.
        date_str = date_str.strip()
        if "." in date_str:
            parts = date_str.split(".")
            if len(parts) == 3:
                day, month, year = parts
                # Handle 2-digit year: assume 20XX for years 00-99
                if len(year) == 2:
                    year_int = int(year)
                    # For years 00-25, assume 2000-2025
                    # For years 26-99, check if it's a typo (should be 2025)
                    # Current date context: we're in 2026, but most dates should be 2025
                    # If year is 26 and month > 1, it's likely a typo (should be 25)
                    if year_int == 26 and int(month) > 1:
                        # Likely typo: "10.08.26" should be "10.08.25"
                        year = "2025"
                        print(f"Warning: Corrected likely typo '{date_str}' -> year 2025 (was 2026)")
                    elif year_int <= 25:
                        year = "20" + year
                    elif year_int == 26:
                        # January 2026 is legitimate
                        year = "2026"
                    else:
                        year = "19" + year
                parsed_date = datetime(int(year), int(month), int(day))
                # Debug: log if year seems wrong
                if parsed_date.year > 2026:
                    print(f"Warning: Parsed date '{date_str}' as year {parsed_date.year}")
                return parsed_date
        elif "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 3:
                day, month, year = parts
                if len(year) == 2:
                    year_int = int(year)
                    # Same logic for slash format
                    if year_int == 26 and int(month) > 1:
                        year = "2025"
                        print(f"Warning: Corrected likely typo '{date_str}' -> year 2025 (was 2026)")
                    elif year_int <= 25:
                        year = "20" + year
                    elif year_int == 26:
                        year = "2026"
                    else:
                        year = "19" + year
                parsed_date = datetime(int(year), int(month), int(day))
                if parsed_date.year > 2026:
                    print(f"Warning: Parsed date '{date_str}' as year {parsed_date.year}")
                return parsed_date
        
        # Fallback to dateutil parser
        parsed_date = parser.parse(date_str)
        if parsed_date.year > 2026:
            print(f"Warning: dateutil parsed '{date_str}' as year {parsed_date.year}")
        return parsed_date
    except Exception as e:
        # Log error in production
        print(f"Error parsing date '{date_str}': {e}")
        return None
