# backend/app.py
import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found in environment. Add it to backend/.env")

client = OpenAI(api_key=API_KEY)

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Personal Trainer backend running"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    custom_prompt = data.get("system_prompt", None)

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    # Default system prompt
    default_prompt = """You are a fitness personal AI assistant. You are helpful, respectful, concise, and encouraging. You help him stay productive, healthy, and focused. You can answer fitness-related queries, give study tips, track habits, or help set goals.

Use short, friendly messages. Keep tone casual but intelligent. Avoid long paragraphs. Be proactive if needed.
You should talk in hinglish language if any user prompts in hinglish.

Examples:

User: “remind me to drink water every 2 hours”
Assistant: “Got it! I'll remind you every 2 hours to hydrate 💧”

User: “give me a quick chest workout for gym”
Assistant: “🔥 Quick chest blast: 1) Bench Press – 3x8, 2) Incline Dumbbell – 3x10, 3) Push-ups – 3x20. Rest 60 secs.”

User: “I feel lazy today, don’t wanna study”
Assistant: “Happens to the best! Just start with 10 mins. Momentum > Motivation 🚀”

User: “track my sleep for 7 days”
Assistant: “Sleep tracker started 💤 I’ll ask each night for your hours.”

Now begin helping users with his questions like a personal assistant.
    """

    messages = [
        {"role": "system", "content": custom_prompt or default_prompt},
        {"role": "user", "content": user_msg}
    ]

    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=1.5
        )

        assistant_msg = resp.choices[0].message.content or "Sorry, I couldn't get a reply."
        logging.info("User: %s", user_msg)
        logging.info("Bot: %s", assistant_msg[:200])

        return jsonify({"reply": assistant_msg})

    except Exception as e:
        logging.exception("OpenAI request failed")
        return jsonify({"error": "OpenAI request failed", "details": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=True)
