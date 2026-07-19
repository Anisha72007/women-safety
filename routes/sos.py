from flask import Blueprint, request
import sqlite3
from datetime import datetime

sos_bp = Blueprint("sos", __name__)

# -------------------------
# Trigger SOS
# -------------------------
@sos_bp.route("/trigger_sos", methods=["POST"])
def trigger_sos():

    data = request.get_json()

    latitude = data["latitude"]
    longitude = data["longitude"]

    conn = sqlite3.connect("database/women_safety.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO sos_history(latitude, longitude, timestamp, status)
        VALUES (?, ?, ?, ?)
    """, (
        latitude,
        longitude,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "ACTIVE"
    ))

    conn.commit()
    conn.close()

    return {"message": "SOS Triggered Successfully!"}


# -------------------------
# SOS History
# -------------------------
@sos_bp.route("/sos_history", methods=["GET"])
def get_sos_history():

    conn = sqlite3.connect("database/women_safety.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM sos_history ORDER BY id DESC")

    history = cursor.fetchall()

    conn.close()

    return [dict(row) for row in history]