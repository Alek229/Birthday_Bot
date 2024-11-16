# Birthday Reminder Bot

This project is a birthday reminder bot built with Flask and a background scheduler. It consists of two components:
1. A **Flask App** for WhatsApp interaction via Twilio.
2. A **Scheduler Worker** for sending birthday reminders.

---

## **Project Structure**

```plaintext
birthday-bot/
├── app/
│   ├── flask_app.py               # Flask app for WhatsApp interaction
│   ├── birthdays.db               # SQLite database
│   └── requirements.txt           # Python dependencies
├── worker/
│   ├── scheduler_worker.py        # Scheduler worker for birthday reminders
│   └── requirements.txt           # Python dependencies for worker
├── README.md                      # Repository documentation
└── .gitignore                     # Files to exclude from version control
