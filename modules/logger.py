import datetime
import os

LOG_FILE = "logs/activity.log"

def log_event(event_text):
   
    if not os.path.exists("logs"):
        os.makedirs("logs")

    with open(LOG_FILE, "a") as f:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{current_time} - {event_text}\n")