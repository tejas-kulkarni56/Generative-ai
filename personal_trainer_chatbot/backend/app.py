from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Create Flask app
app = Flask(__name__)
CORS(app)  # Allow requests from any frontend origin

# Get API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is missing in environment variables!")

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


@app.route("/chat", methods=["POST"])
def chat():
    try:
        # Parse JSON request
        data = request.get_json()
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' field"}), 400

        user_message = data["message"]

        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Use your desired model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200
        )

        # Extract reply
        ai_reply = response.choices[0].message.content.strip()

        return jsonify({"reply": ai_reply})

    except Exception as e:
        # Log error for debugging
        print("❌ Error in /chat:", str(e))
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
