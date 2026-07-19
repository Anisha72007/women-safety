import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load secret environment variables from .env
load_dotenv()

app = Flask(__name__)

# This setup handles the CORS security checks robustly so Chrome won't drop the connection
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})

# Initialize the Gemini client (looks for GEMINI_API_KEY in your .env)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

# 1. EMERGENCY KEYWORD INTERCEPTOR
EMERGENCY_KEYWORDS = ["help", "danger","following","followed", "stalk", "attack", "police", "unsafe", "emergency", "run"]

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

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat_endpoint():
    # Automatically handle the browser preflight request without crashing
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"}), 200

    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
        
    user_message = data.get("message", "").strip().lower()

    if not user_message:
        return jsonify({"error": "Message content cannot be blank"}), 400

    # Safety Check: Intercept immediate physical danger keywords
    if any(keyword in user_message for keyword in EMERGENCY_KEYWORDS):
        return jsonify(EMERGENCY_RESPONSE)

    # Standard Response Process: Route to AI
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.6,
            )
        )
        
        return jsonify({
            "is_emergency": False,
            "message": response.text
        })

    except Exception as e:
        return jsonify({"error": f"Internal system issue: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)