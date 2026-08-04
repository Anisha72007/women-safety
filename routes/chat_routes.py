from flask import Blueprint, request, jsonify
import sqlite3

chat_bp = Blueprint('chat', __name__)

EMERGENCY_KEYWORDS = ['help', 'emergency', 'danger', 'save me', 'police']

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'response': 'Please enter a valid message.', 'is_emergency': False}), 400

    # Check for emergency keywords
    is_emergency = any(keyword in user_message.lower() for keyword in EMERGENCY_KEYWORDS)

    if is_emergency:
        bot_response = "🚨 EMERGENCY ALERT TRIGGERED! Help request logged."
        log_emergency(user_message)
    else:
        bot_response = f"AI Assistant received: '{user_message}'. Stay safe!"

    # Save to database
    log_chat(user_message, bot_response)

    return jsonify({
        'response': bot_response,
        'is_emergency': is_emergency
    })

def log_chat(user_msg, bot_msg):
    try:
        conn = sqlite3.connect('database/women_safety.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)",
            (user_msg, bot_msg)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Database error:", e)

def log_emergency(keyword):
    try:
        conn = sqlite3.connect('database/women_safety.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO emergency_alerts (keyword_triggered) VALUES (?)",
            (keyword,)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Database error:", e)