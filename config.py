# config.py
"""
Personal configuration for Tesla Preconditioning Controller.
Replace the placeholders with your own credentials and settings.
"""

# Tesla API credentials
TESLA_CLIENT_ID = "ownerapi"
TESLA_REFRESH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjI5Skh4dlVBVVFfbDlBVXFhcHBrV2dLRDhRRSJ9.eyJpc3MiOiJodHRwczovL2F1dGgudGVzbGEuY29tL29hdXRoMi92MyIsImF1ZCI6Imh0dHBzOi8vYXV0aC50ZXNsYS5jb20vb2F1dGgyL3YzL3Rva2VuIiwiaWF0IjoxNzU3ODI5NTIxLCJzY3AiOlsib3BlbmlkIiwib2ZmbGluZV9hY2Nlc3MiXSwib3VfY29kZSI6IkVVIiwiZGF0YSI6eyJ2IjoiMSIsImF1ZCI6Imh0dHBzOi8vb3duZXItYXBpLnRlc2xhbW90b3JzLmNvbS8iLCJzdWIiOiI0YTg2M2FiOS05ZjVjLTRiMTQtOGMwNy04ZmQ3M2MzNmQ1Y2MiLCJzY3AiOlsib3BlbmlkIiwiZW1haWwiLCJvZmZsaW5lX2FjY2VzcyJdLCJhenAiOiJvd25lcmFwaSIsImFtciI6WyJwd2QiLCJtZmEiLCJvdHAiXSwiYXV0aF90aW1lIjoxNzU3ODI5NTE3fX0.N2ckwPlHCMgWlPtRM9Ty8xZNqwivcZJW4YVilgfJfED4YaLFzIgO8V-wRBaOd3S46iHUowvRLV8DVJLA8_wSakvfTH0WE-wvF7loxPKJVTYccsaL9EB4QnE5xb5Xg-jJxA3h59LsxUoSVWAPOqTGPGehSWzg2bLUCzPztMUf0nX1xiQDSq-58sUz198EDXyK2Dv7uTItqmy4wEBzhcP0YeIaQan-L6CJFeFeWfnlvvSHt4EMthRHyvtyTm8cZWyHhL9N-dLfaqEJ5Ytp8lVY_NpaE0ZKdw4WQhzVi_XmX63Eur7Xdb-ry974BW8bNQsfWU_c9caQW6TljowjR38NqA"
VEHICLE_ID = "929770148073832"

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
