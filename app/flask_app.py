from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_FILE = 'birthdays.db'

def init_db():
    """Initialize the database."""
    try:
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

@app.route("/")
def home():
    return "🎉 Welcome to the Birthday Bot! Use WhatsApp to interact with me."

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get('Body', '').lower()
    response = MessagingResponse()
    msg = response.message()

    if incoming_msg.startswith("add"):
        try:
            _, name, birthday = incoming_msg.split(",")
            birthday = datetime.strptime(birthday.strip(), "%Y/%m/%d").strftime("%Y-%m-%d")
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO birthdays (name, birthday) VALUES (?, ?)", (name.strip(), birthday))
                conn.commit()
            msg.body(f"🎉 {name}'s birthday added for {birthday}!")
        except ValueError:
            msg.body("ERROR: Use the format `add, Name, YYYY/MM/DD`")

    elif incoming_msg.startswith("list"):
        with sqlite3.connect(DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name, birthday FROM birthdays")
            rows = cursor.fetchall()
            if rows:
                msg.body("\n".join([f"🎂 {name}: {birthday}" for name, birthday in rows]))
            else:
                msg.body("No birthdays found. Add one with `add, Name, YYYY/MM/DD`")

    elif incoming_msg.startswith("remove"):
        try:
            _, name = incoming_msg.split(",")
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM birthdays WHERE name = ?", (name.strip(),))
                conn.commit()
            msg.body(f"Removed {name} from the birthday list.")
        except ValueError:
            msg.body("ERROR: Use the format `remove, Name`")

    else:
        msg.body("Commands:\n- `add, Name, YYYY/MM/DD`\n- `list`\n- `remove, Name`")
    return str(response)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
