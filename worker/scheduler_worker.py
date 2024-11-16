import sqlite3
from datetime import datetime
import time
import schedule
import os
from twilio.rest import Client

DB_FILE = 'app/birthdays.db'

def init_db():
    """Initialize the database if it doesn't exist."""
    if not os.path.exists(DB_FILE):
        print(f"DEBUG: Initializing new database at {DB_FILE}")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS birthdays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    birthday DATE NOT NULL
                )
            """)
            conn.commit()
    else:
        print(f"DEBUG: Database already exists at {DB_FILE}")

def send_birthday_reminders():
    """Check today's birthdays and send reminders."""
    today = datetime.utcnow().strftime("%m-%d")  # Get today's date in MM-DD format
    print(f"DEBUG: Checking birthdays for today: {today}")

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM birthdays WHERE strftime('%m-%d', birthday) = ?", (today,))
        today_birthdays = [row[0] for row in cursor.fetchall()]

    if today_birthdays:
        print(f"DEBUG: Found birthdays for today: {', '.join(today_birthdays)}")
        send_whatsapp_message(f"🎉 Today's Birthdays: {', '.join(today_birthdays)}! 🎂 Don't forget to celebrate!")
    else:
        print("DEBUG: No birthdays found for today.")
        send_whatsapp_message("DEBUG: No birthdays found for today.")

def send_whatsapp_message(body):
    """Send a WhatsApp message."""
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")
    whatsapp_to = os.getenv("TWILIO_WHATSAPP_GROUP_TO")  # Use the group or individual number here

    print(f"DEBUG: Sending message: {body}")
    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(body=body, from_=whatsapp_from, to=whatsapp_to)
        print(f"DEBUG: Message sent successfully, SID: {message.sid}")
    except Exception as e:
        print(f"ERROR: Failed to send WhatsApp message: {e}")

def schedule_reminders():
    """Schedule the birthday reminder function to run every 3 minutes."""
    print("DEBUG: Scheduler started to send reminders every 3 minutes")
    schedule.every(3).minutes.do(send_birthday_reminders)

    while True:
        print("DEBUG: Running scheduled jobs...")
        schedule.run_pending()
        time.sleep(1)

def handle_test_commands(incoming_msg):
    """Respond to test commands received via WhatsApp."""
    incoming_msg = incoming_msg.lower()
    if "test date" in incoming_msg:
        today = datetime.utcnow().strftime("%Y-%m-%d")
        send_whatsapp_message(f"DEBUG: Today's UTC date is {today}.")
    elif "test hour" in incoming_msg:
        current_hour = datetime.utcnow().strftime("%H:%M:%S")
        send_whatsapp_message(f"DEBUG: Current UTC time is {current_hour}.")
    elif "check today" in incoming_msg:
        today = datetime.utcnow().strftime("%m-%d")
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM birthdays WHERE strftime('%m-%d', birthday) = ?", (today,))
            today_birthdays = [row[0] for row in cursor.fetchall()]
        if today_birthdays:
            send_whatsapp_message(f"DEBUG: Today's birthdays: {', '.join(today_birthdays)}")
        else:
            send_whatsapp_message("DEBUG: No birthdays found for today.")
    elif "add test" in incoming_msg:
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO birthdays (name, birthday) VALUES (?, ?)", ("TestUser", "2024-11-16"))
            conn.commit()
        send_whatsapp_message("DEBUG: Test birthday added for TestUser on 2024-11-16.")
    else:
        send_whatsapp_message("DEBUG: Unknown command. Try 'test date', 'test hour', 'check today', or 'add test'.")

if __name__ == "__main__":
    print("DEBUG: Scheduler worker starting...")
    init_db()

    # Add a mechanism to process test commands sent via WhatsApp
    try:
        print("DEBUG: Listening for test commands...")
        incoming_test_msg = os.getenv("TEST_COMMAND")  # Simulate receiving a test command
        if incoming_test_msg:
            handle_test_commands(incoming_test_msg)
    except Exception as e:
        print(f"ERROR: Failed to process test command: {e}")

    # Start the scheduler
    print("DEBUG: Starting scheduler thread...")
    schedule_reminders()
