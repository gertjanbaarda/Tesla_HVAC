# config.py
"""
Personal configuration for Tesla Preconditioning Controller.
Replace the placeholders with your own credentials and settings.
"""

# Tesla API credentials
TESLA_CLIENT_ID = "ownerapi"
TESLA_REFRESH_TOKEN = "MY_REFRESH_TOKEN"
VEHICLE_ID = "MY_VEHICLE_ID"

# ------------------- HVAC Scheduling -------------------
START_TIME = "07:55"  # 24h format, e.g., "07:50"
CHECK_DELAY = 1800       # seconds to wait before checking if car moved

# ------------------- Target Temperature -------------------
TARGET_TEMP = 18       # Temperature to set in Celsius

# ------------------- Temperature Thresholds -------------------
# HVAC will start if one of these conditions is met
OUTDOOR_TEMP_THRESHOLD = 4    # start if outside temp is below this
INDOOR_TEMP_THRESHOLD = 25    # start if inside temp is above this

# ------------------- Active Days -------------------
# 0=Monday, 6=Sunday
DAYS = [0, 1, 2, 3, 4, 5, 6]  # default: all days

# ------------------- Optional Logging -------------------
# LOG_FILE = "tesla_hvac.log"  # filename controlled in main script
