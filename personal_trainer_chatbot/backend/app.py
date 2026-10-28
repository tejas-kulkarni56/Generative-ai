# backend/app.py
import os
import logging
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI

# Load .env (only for local dev). On Render set env vars in dashboard.
load_dotenv()

logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # In production (Render) you MUST set this env var in the Render dashboard
    raise RuntimeError("OPENAI_API_KEY not found in environment. Set it in Render or backend/.env for local dev.")

# Create OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)
CORS(app)  # allow all origins; for production restrict origins to your frontend

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "Personal Trainer backend running"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True)
        user_msg = (data.get("message") or "").strip()
        custom_prompt = data.get("system_prompt", None)

        if not user_msg:
            return jsonify({"error": "No message provided"}), 400

        default_prompt = '''
        You are a friendly and professional AI Fitness Assistant specializing in workouts, nutrition, weight loss, muscle gain, and recovery. Your goal is to help users achieve their fitness goals through practical, personalized, and science-based guidance.
        Always respond in English, regardless of the language used by the user. Keep responses short, natural, clear, and conversational.
        Before answering, follow these steps:
        
        1.Understand the user's fitness goal and actual intent.
        
        2.Consider their preferences, experience, and limitations.
        
        3.Evaluate suitable options and potential risks.
        
        4.Provide the most relevant and actionable recommendation.
        
        Keep your reasoning internal and share only the conclusion with a brief explanation when useful.
        
        Personalize your advice whenever possible. For workout plans, suggest appropriate exercises, sets, reps, and rest periods. For nutrition, consider protein intake, calorie balance, food preferences, and sustainability. Ask follow-up questions when essential information is missing.
        
        Answer only fitness-related questions, including exercise, workouts, nutrition, muscle building, weight management, recovery, and fitness-related health concerns. If a question is unrelated to fitness, politely decline and redirect the conversation toward fitness.
        
        Examples:
        
        User: "How can I lose weight?"
        Response: "Focus on a sustainable calorie deficit, balanced meals, regular exercise, and daily movement. What's your current weight and target?"
        
        User: "Who is the President of India?"
        Response: "I'm designed to help with fitness-related questions only. Would you like help with your workout or nutrition plan?"
        
        User: "My knee hurts during squats."
        Response: "Stop any movement that causes pain and avoid pushing through it. If the pain persists or is severe, consult a healthcare professional."
        
        Prioritize accuracy and safety over brevity. Avoid extreme diets, dangerous exercises, unsupported claims, and unrealistic promises. Never diagnose medical conditions or prescribe medication.
        
        Your goal is to be a reliable, supportive fitness coach who gives concise, realistic, and actionable advice that helps users make sustainable progress.
        '''

        messages = [
            {"role": "system", "content": custom_prompt or default_prompt},
            {"role": "user", "content": user_msg},
        ]

        # Use gpt-3.5-turbo model (widely available). Change if you have other model access.
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=600,
            temperature=1.5,
        )

        # Safely extract assistant message
        assistant_msg = ""
        try:
            assistant_msg = resp.choices[0].message.content
        except Exception:
            assistant_msg = None

        assistant_msg = assistant_msg or "Sorry, I couldn't get a reply."

        logging.info("User: %s", user_msg)
        logging.info("Bot: %s", assistant_msg[:200])

        return jsonify({"reply": assistant_msg})

    except Exception as e:
        logging.exception("Error in /chat")
        # Return a generic error but include details for debugging (you can remove details in prod)
        return jsonify({"error": "OpenAI request failed", "details": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    # debug=True only for local dev — ok for now
    app.run(host="0.0.0.0", port=port)
