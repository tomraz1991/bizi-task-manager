"""
Application-wide constants.
"""
# Default number of days to look ahead for notifications
DEFAULT_NOTIFICATION_DAYS = 7

# Far future days constant (used when date is missing)
FAR_FUTURE_DAYS = 999

# Task type display labels
TASK_TYPE_LABELS = {
    "recording": "Recording",
    "editing": "Editing",
    "reels": "Reels",
    "publishing": "Publishing",
    "studio_preparation": "Studio Preparation"
}

# File upload limits
MAX_CSV_FILE_SIZE = 10 * 1024 * 1024  # 10MB
