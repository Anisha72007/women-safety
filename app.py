from flask import Flask, render_template
import sqlite3

from routes.contacts import contacts_bp
from routes.sos import sos_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(contacts_bp)
app.register_blueprint(sos_bp)


# -----------------------------
# Create Database and Tables
# -----------------------------
def create_table():
    conn = sqlite3.connect("database/women_safety.db")
    cursor = conn.cursor()

    # Emergency Contacts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emergency_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        relationship TEXT
    )
    """)

    # SOS History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sos_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        latitude REAL,
        longitude REAL,
        timestamp TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()


# -----------------------------
# Frontend Routes
# -----------------------------

# Dashboard
@app.route("/")
def home():
    return render_template("index.html")


# Emergency Contacts Page
@app.route("/contacts_page")
def contacts_page():
    return render_template("contacts.html")


# SOS Page
@app.route("/sos_page")
def sos_page():
    return render_template("sos.html")


# SOS History Page
@app.route("/history_page")
def history_page():
    return render_template("history.html")


# -----------------------------
# Run Application
# -----------------------------
if __name__ == "__main__":
    create_table()
    app.run(debug=True)