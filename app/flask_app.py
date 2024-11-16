from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database setup
DB_FILE = os.path.join(os.path.dirname(__file__), 'birthdays.db')

def init_db():
    """Initialize the database and create the birthdays table if it doesn't exist."""
    try:
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)  # Delete existing corrupted database
            print("DEBUG: Existing database file deleted.")

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
            print("DEBUG: Database initialized successfully.")
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")


init_db()

@app.route("/")
def home():
    """Home route for the Flask app."""
    return "🎉 Welcome to La Famiglia Birthday Bot! Use WhatsApp to interact with the bot."

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming WhatsApp messages."""
    incoming_msg = request.values.get('Body', '').lower()
    response = MessagingResponse()
    msg = response.message()

    try:
        if incoming_msg.startswith("add"):
            _, name, birthday = incoming_msg.split(",")
            birthday = datetime.strptime(birthday.strip(), "%Y/%m/%d").strftime("%Y-%m-%d")
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO birthdays (name, birthday) VALUES (?, ?)", (name.strip(), birthday))
                conn.commit()
            msg.body(f"🎉 {name}'s birthday has been added for {birthday}!")
        
        elif incoming_msg.startswith("list"):
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, birthday FROM birthdays")
                birthdays = cursor.fetchall()
                if birthdays:
                    msg.body("\n".join([f"🎂 {name}: {birthday}" for name, birthday in birthdays]))
                else:
                    msg.body("No birthdays added yet! Use `add, Name, YYYY/MM/DD` to add one.")
        
        elif incoming_msg.startswith("remove"):
            _, name = incoming_msg.split(",")
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM birthdays WHERE name = ?", (name.strip(),))
                conn.commit()
            msg.body(f"{name} has been removed from the birthday list.")
        
        else:
            msg.body("🎉 Hello! I'm your Family Birthday Bot! Use these commands:\n"
                     "- `add, Name, YYYY/MM/DD` to add a birthday\n"
                     "- `list` to see all birthdays\n"
                     "- `remove, Name` to delete a birthday")
    except Exception as e:
        msg.body(f"ERROR: Unable to process your request. Please try again.\nDetails: {e}")
        print(f"ERROR: {e}")
    
    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
