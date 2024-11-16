import sqlite3
import schedule
import time
from datetime import datetime
from twilio.rest import Client
import os

DB_FILE = os.path.join(os.path.dirname(__file__), '../app/birthdays.db')

def send_birthday_reminders():
    """Check today's birthdays and send reminders."""
    today = datetime.utcnow().strftime("%m-%d")  # Get today's date in MM-DD format
    print(f"DEBUG: Checking birthdays for today: {today}")

    try:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM birthdays WHERE strftime('%m-%d', birthday) = ?", (today,))
            today_birthdays = [row[0] for row in cursor.fetchall()]
        
        if today_birthdays:
            send_whatsapp_message(f"🎉 Today's Birthdays: {', '.join(today_birthdays)}! 🎂 Don't forget to celebrate!")
        else:
            print("DEBUG: No birthdays to notify at this moment.")
    except Exception as e:
        print(f"ERROR: Failed to check birthdays: {e}")

def send_whatsapp_message(body):
    """Send WhatsApp message via Twilio."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
    whatsapp_to = os.getenv("WHATSAPP_GROUP_TO")

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=body, from_=whatsapp_from, to=whatsapp_to)
        print(f"DEBUG: Message sent, SID: {message.sid}")
    except Exception as e:
        print(f"ERROR: Failed to send message: {e}")

def schedule_reminders():
    """Schedule the reminder function to run every day at 9:00 AM UTC."""
    print("DEBUG: Scheduler started to send reminders every 3 minutes.")
    schedule.every(3).minutes.do(send_birthday_reminders)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    send_birthday_reminders()  # Test sending reminders
    schedule_reminders()
