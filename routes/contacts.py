from flask import Blueprint, request
import sqlite3

contacts_bp = Blueprint("contacts", __name__)

# -------------------------
# Add Contact
# -------------------------
@contacts_bp.route("/add_contact", methods=["POST"])
def add_contact():
    data = request.get_json()

    name = data["name"]
    phone = data["phone"]
    relationship = data["relationship"]

    conn = sqlite3.connect("database/women_safety.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO emergency_contacts (name, phone, relationship) VALUES (?, ?, ?)",
        (name, phone, relationship)
    )

    conn.commit()
    conn.close()

    return {"message": "Contact added successfully!"}


# -------------------------
# View Contacts
# -------------------------
@contacts_bp.route("/contacts", methods=["GET"])
def get_contacts():

    conn = sqlite3.connect("database/women_safety.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM emergency_contacts")

    contacts = cursor.fetchall()

    conn.close()

    return [dict(contact) for contact in contacts]


# -------------------------
# Edit Contact
# -------------------------
@contacts_bp.route("/edit_contact/<int:id>", methods=["PUT"])
def edit_contact(id):

    data = request.get_json()

    conn = sqlite3.connect("database/women_safety.db")
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE emergency_contacts
        SET name = ?, phone = ?, relationship = ?
        WHERE id = ?
    """, (
        data["name"],
        data["phone"],
        data["relationship"],
        id
    ))

    conn.commit()
    conn.close()

    return {"message": "Contact updated successfully!"}


# -------------------------
# Delete Contact
# -------------------------
@contacts_bp.route("/delete_contact/<int:id>", methods=["DELETE"])
def delete_contact(id):

    conn = sqlite3.connect("database/women_safety.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM emergency_contacts WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return {"message": "Contact deleted successfully!"}

print("contacts_bp =", contacts_bp)