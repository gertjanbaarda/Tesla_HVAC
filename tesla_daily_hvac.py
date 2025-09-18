#!/usr/bin/env python3
"""
Tesla Daily HVAC Automation Script

Description:
- Automates daily HVAC control for a Tesla vehicle based on configurable
  days, start time, and temperature thresholds.
- Fetches vehicle data via Tesla API, handles token refresh and retries.
- Starts HVAC if outside temperature is below OUTDOOR_TEMP_THRESHOLD
  or inside temperature is above INDOOR_TEMP_THRESHOLD.
- Stops HVAC after CHECK_DELAY seconds if the car hasn’t moved.
- Logs all actions, successes, warnings, and errors to 'tesla_hvac.log'.

Features:
- Robust API handling: retries, token refresh, timeouts.
- Scheduled execution using 'schedule' module.
- Wake-up logic to handle sleeping vehicles.
- Adjustable parameters in 'config.py' for client ID, refresh token,
  vehicle ID, target temperature, days of operation, start time,
  and thresholds.
- Safety checks to avoid unnecessary HVAC usage.

Usage:
- Configure parameters in 'config.py'.
- Run script continuously (e.g., via systemd or cron) to execute
  HVAC job automatically at the scheduled time.
"""


import requests
import schedule
import time
import logging
import datetime
from config import (
    TESLA_CLIENT_ID,
    TESLA_REFRESH_TOKEN,
    VEHICLE_ID,
    START_TIME,
    CHECK_DELAY,
    TARGET_TEMP,
    DAYS,
    OUTDOOR_TEMP_THRESHOLD,
    INDOOR_TEMP_THRESHOLD
)

# ------------------- Logging -------------------
logging.basicConfig(
    filename="tesla_hvac.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

ACCESS_TOKEN = None

# ------------------- Tesla API Helpers -------------------
def get_access_token(retries=3):
    """Fetch or refresh Tesla access token with retries."""
    global ACCESS_TOKEN
    url = "https://auth.tesla.com/oauth2/v3/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": TESLA_CLIENT_ID,
        "refresh_token": TESLA_REFRESH_TOKEN,
    }
    for attempt in range(retries):
        try:
            r = requests.post(url, json=data, timeout=10)
            r.raise_for_status()
            ACCESS_TOKEN = r.json().get("access_token")
            logging.info("Obtained new Tesla access token.")
            return True
        except requests.RequestException as e:
            logging.warning(f"Token fetch attempt {attempt+1} failed: {e}")
            time.sleep(2)
    logging.error("Failed to obtain access token after multiple attempts.")
    return False

def api_get(endpoint, retries=3, delay=2, timeout=30):
    """GET request with retry and token refresh."""
    global ACCESS_TOKEN
    for attempt in range(retries):
        if not ACCESS_TOKEN:
            if not get_access_token():
                return None
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        url = f"https://owner-api.teslamotors.com/api/1{endpoint}"
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            if r.status_code == 401:
                logging.info("Access token expired, refreshing...")
                get_access_token()
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logging.warning(f"GET {endpoint} attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    logging.error(f"GET {endpoint} failed after {retries} attempts.")
    return None

def api_post(endpoint, data=None, retries=3, delay=2):
    """POST request with retry and token refresh."""
    global ACCESS_TOKEN
    for attempt in range(retries):
        if not ACCESS_TOKEN:
            if not get_access_token():
                return None
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        url = f"https://owner-api.teslamotors.com/api/1{endpoint}"
        try:
            r = requests.post(url, headers=headers, json=data or {}, timeout=30)
            if r.status_code == 401:
                logging.info("Access token expired, refreshing...")
                get_access_token()
                continue
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logging.warning(f"POST {endpoint} attempt {attempt+1} failed: {e}")
            time.sleep(delay)
    logging.error(f"POST {endpoint} failed after {retries} attempts.")
    return None

# ------------------- Vehicle Helpers -------------------
def wake_vehicle():
    resp = api_post(f"/vehicles/{VEHICLE_ID}/wake_up")
    if resp:
        logging.info("Sent wake_up command to Tesla.")
    else:
        logging.warning("Wake_up command failed or no response.")

def get_vehicle_data(retries=5, delay=10):
    """Fetch vehicle data with retries and wake attempts."""
    for attempt in range(retries):
        data = api_get(f"/vehicles/{VEHICLE_ID}/vehicle_data", timeout=30)
        if data:
            logging.info(f"Vehicle data fetched successfully on attempt {attempt+1}.")
            return data
        logging.warning(f"Vehicle data not ready, retry {attempt+1}/{retries}. Waiting {delay}s...")
        wake_vehicle()
        time.sleep(delay)
    logging.error("Failed to fetch vehicle data after multiple retries.")
    return None

def start_hvac():
    resp_start = api_post(f"/vehicles/{VEHICLE_ID}/command/auto_conditioning_start")
    resp_set_temp = api_post(f"/vehicles/{VEHICLE_ID}/command/set_temps",
                             {"driver_temp": TARGET_TEMP, "passenger_temp": TARGET_TEMP})
    logging.info(f"HVAC started. Start response: {resp_start}, Set Temp response: {resp_set_temp}")

def stop_hvac():
    resp_stop = api_post(f"/vehicles/{VEHICLE_ID}/command/auto_conditioning_stop")
    logging.info(f"HVAC stopped. Stop response: {resp_stop}")

# ------------------- Core Logic -------------------
def hvac_job():
    """Main daily HVAC job with OR temperature check and detailed debug logging."""
    logging.info(f"=== HVAC Job Triggered at {datetime.datetime.now()} ===")
    
    data = get_vehicle_data()
    if not data:
        logging.error("Skipping HVAC job: vehicle data unavailable.")
        return

    try:
        response = data.get("response", {})
        climate = response.get("climate_state", {})
        drive = response.get("drive_state", {})

        state = response.get("state")
        outside_temp = climate.get("outside_temp")
        inside_temp = climate.get("inside_temp")
        speed = drive.get("speed")

        logging.info(f"Vehicle state: {state}, Speed: {speed}")
        logging.info(f"Outside Temp={outside_temp}°C, Inside Temp={inside_temp}°C")

        trigger_reasons = []
        if outside_temp is not None and outside_temp < OUTDOOR_TEMP_THRESHOLD:
            trigger_reasons.append(f"Outside temp {outside_temp}°C < {OUTDOOR_TEMP_THRESHOLD}°C")
        if inside_temp is not None and inside_temp > INDOOR_TEMP_THRESHOLD:
            trigger_reasons.append(f"Inside temp {inside_temp}°C > {INDOOR_TEMP_THRESHOLD}°C")

        if trigger_reasons:
            logging.info(f"Temperature condition met → starting HVAC due to: {', '.join(trigger_reasons)}")
            start_hvac()
            schedule.every(CHECK_DELAY).seconds.do(check_shutdown).tag("shutdown_check")
        else:
            logging.info("Temperature conditions NOT met → skipping HVAC.")

    except Exception as e:
        logging.error(f"Error in hvac_job: {e}")


def check_shutdown():
    """Check if car moved after CHECK_DELAY seconds; stop HVAC if idle."""
    schedule.clear("shutdown_check")
    data = get_vehicle_data()
    if not data:
        logging.error("Shutdown check skipped: vehicle data unavailable.")
        return

    try:
        drive = data.get("response", {}).get("drive_state", {})
        speed = drive.get("speed")
        state = data.get("response", {}).get("state")

        logging.info(f"Shutdown check → Vehicle state: {state}, Speed={speed}")

        if speed is None or speed == 0:
            stop_hvac()
            logging.info(f"HVAC stopped after {CHECK_DELAY}s because car idle.")
        else:
            logging.info("Car is moving → HVAC remains active.")

    except Exception as e:
        logging.error(f"Error in shutdown check: {e}")

# ------------------- Scheduler -------------------
def schedule_hvac_job():
    today_weekday = datetime.datetime.now().weekday()  # 0=Monday, 6=Sunday
    if today_weekday in DAYS:
        schedule.every().day.at(START_TIME).do(hvac_job)
        logging.info(f"Tesla HVAC job scheduled for today ({today_weekday}) at {START_TIME}.")
    else:
        logging.info(f"Today ({today_weekday}) not in configured DAYS → skipping HVAC schedule.")

schedule_hvac_job()
logging.info("Tesla HVAC script started.")

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except Exception as e:
        logging.error(f"Unexpected error in main loop: {e}")
        time.sleep(5)
