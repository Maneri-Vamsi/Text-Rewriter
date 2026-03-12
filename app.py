from flask import Flask, request, render_template, jsonify
import os
import requests
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable not found. Please set it in your environment or .env file.")

app = Flask(__name__)

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "mistralai/mixtral-8x7b-instruct"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        tone = data.get("tone", "").strip().lower()

        if not text:
            return jsonify({"error": "Please enter text to rewrite."}), 400
        if not tone:
            return jsonify({"error": "Please select a tone."}), 400

        prompt = f"Rewrite the following in a {tone} tone:\n\n{text}"

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://127.0.0.1:5000", # Optional
            "X-OpenRouter-Title": "AI Text Generator" # Optional
        }

        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": f"You are an assistant that rewrites text in a {tone} tone."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({"error": f"OpenRouter API error: {response.text}"}), 500

        result = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Bind correctly for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
