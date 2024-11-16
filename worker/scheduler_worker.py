import sqlite3
from datetime import datetime, timedelta
import time
from twilio.rest import Client
import schedule
import os

DB_FILE = 'app/birthdays.db'

def send_birthday_reminders():
    """Send birthday reminders."""
    today = datetime.utcnow().strftime("%m-%d")
    print(f"DEBUG: Checking birthdays for today: {today}")

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM birthdays WHERE strftime('%m-%d', birthday) = ?", (today,))
            birthdays = [row[0] for row in cursor.fetchall()]

        if birthdays:
            send_whatsapp_message(f"🎉 Today's Birthdays: {', '.join(birthdays)}!")
        else:
            print("DEBUG: No birthdays today.")
    except Exception as e:
        print(f"ERROR: Failed to fetch birthdays: {e}")

def send_whatsapp_message(body):
    """Send a WhatsApp message."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
    whatsapp_to = os.getenv("WHATSAPP_GROUP_TO")

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=body, from_=whatsapp_from, to=whatsapp_to)
        print(f"DEBUG: Message sent, SID: {message.sid}")
    except Exception as e:
        print(f"ERROR: Failed to send WhatsApp message: {e}")

def schedule_reminders():
    """Schedule reminders to run every day."""
    print("DEBUG: Scheduler started.")
    schedule.every().day.at("17:13").do(send_birthday_reminders)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    schedule_reminders()
