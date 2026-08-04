import os
import sqlite3
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import blueprint from your routes folder
from routes.chat_routes import chat_bp

# Load secret environment variables from .env
load_dotenv()

app = Flask(__name__)

# Register routes blueprint
app.register_blueprint(chat_bp)

# Enable CORS for security checks across browsers
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Initialize the Gemini client (uses GEMINI_API_KEY from .env)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 1. EMERGENCY KEYWORD INTERCEPTOR
EMERGENCY_KEYWORDS = ["help", "danger", "following", "followed", "stalk", "attack", "police", "unsafe", "emergency", "run"]

EMERGENCY_RESPONSE = {
    "is_emergency": True,
    "message": "🚨 Safety Alert Triggered. Please stay calm. Try to move to a well-lit, public space immediately.",
    "actions": [
        "Call Emergency Services: 1091 / 100 / 112",
        "Tap the SOS button to alert your trusted contacts with your location."
    ]
}

# 2. AI PERSONALITY
SYSTEM_INSTRUCTION = """
You are a calm, deeply empathetic, and highly resourceful AI safety companion for women. 
Your tone should feel like a supportive, grounded peer—never panicked, never cold or robotic. 
Keep your text concise and scannable. Use bolding and bullet points for safety instructions so they are easy to read in stressful moments.
"""

# Database logging helpers
def log_chat_to_db(user_msg, bot_msg):
    try:
        conn = sqlite3.connect('database/women_safety.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_message, bot_response) VALUES (?, ?)",
            (user_msg, str(bot_msg))
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print("Database chat log error:", e)

def log_emergency_to_db(keyword):
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
        print("Database emergency log error:", e)

# 3. ROUTES
@app.route('/')
def home():
    """Renders the frontend HTML chatbot interface."""
    return render_template('index.html')

@app.route('/chat', methods=['POST', 'OPTIONS'])
@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    # Automatically handle browser preflight request
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
        
    raw_message = data.get("message", "").strip()
    user_message = raw_message.lower()

    if not user_message:
        return jsonify({"error": "Message content cannot be blank"}), 400

    # Safety Check: Intercept immediate physical danger keywords
    if any(keyword in user_message for keyword in EMERGENCY_KEYWORDS):
        log_emergency_to_db(raw_message)
        log_chat_to_db(raw_message, EMERGENCY_RESPONSE["message"])
        return jsonify(EMERGENCY_RESPONSE)

    # Standard Response Process: Route to AI
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=raw_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.6,
            )
        )
        
        bot_text = response.text
        log_chat_to_db(raw_message, bot_text)

        return jsonify({
            "is_emergency": False,
            "response": bot_text,
            "message": bot_text
        })

    except Exception as e:
        return jsonify({"error": f"Internal system issue: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)