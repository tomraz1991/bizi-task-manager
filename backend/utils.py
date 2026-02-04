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
        date_str: Date string in formats like DD.MM.YY, DD.MM, DD/MM/YY, or ISO format.
                  European/Israeli style: day first, then month (e.g. 30.12 = 30 Dec).
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if not date_str or date_str.strip() == "":
        return None

    date_str = date_str.strip()
    # Reject obvious non-dates
    if date_str in ("?", "-", "–", "—", "n/a", "N/A", "TBD"):
        return None
    if not any(c.isdigit() for c in date_str):
        return None
    
    try:
        # Try parsing common formats: DD.MM.YY, DD.MM, DD/MM/YY, etc. (day first)
        if "." in date_str:
            parts = date_str.split(".")
            if len(parts) == 2:
                # DD.MM (no year) — assume current year
                day, month = parts
                year = str(datetime.now().year)
                parsed_date = datetime(int(year), int(month), int(day))
                return parsed_date
            if len(parts) == 3:
                day, month, year = parts
                # Handle 2-digit year: assume 20XX for years 00-99
                if len(year) == 2:
                    year_int = int(year)
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
        elif "/" in date_str:
            parts = date_str.split("/")
            if len(parts) == 2:
                day, month = parts
                year = str(datetime.now().year)
                parsed_date = datetime(int(year), int(month), int(day))
                return parsed_date
            if len(parts) == 3:
                day, month, year = parts
                if len(year) == 2:
                    year_int = int(year)
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

        # Fallback to dateutil (handles ISO etc.). DD.MM already handled above.
        parsed_date = parser.parse(date_str)
        if parsed_date.year > 2026:
            print(f"Warning: dateutil parsed '{date_str}' as year {parsed_date.year}")
        return parsed_date
    except Exception as e:
        # Log error in production
        print(f"Error parsing date '{date_str}': {e}")
        return None
