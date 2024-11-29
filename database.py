import sqlite3
from datetime import datetime

# Connect to SQLite Database
def connect_db():
    conn = sqlite3.connect("patient_app.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create BP Record
def create_bp_record(systolic, diastolic, pulse, risk_score, measurement_time):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bp_records (systolic, diastolic, pulse, risk_score, measurement_time)
        VALUES (?, ?, ?, ?, ?)
        """,
        (systolic, diastolic, pulse, risk_score, measurement_time),
    )
    conn.commit()
    conn.close()

# Read BP Records
def read_bp_records():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bp_records")
    records = cur.fetchall()
    conn.close()
    return records

# Create Reminder
def create_reminder(time):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO reminders (time) VALUES (?)", (time,))
    conn.commit()
    conn.close()

# Read Reminders
def read_reminders():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM reminders")
    reminders = cur.fetchall()
    conn.close()
    return reminders

# Delete Reminder
def delete_reminder(reminder_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
    conn.commit()
    conn.close()

# List Clinicians
def list_clinicians():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clinicians")
    clinicians = cur.fetchall()
    conn.close()
    return clinicians
