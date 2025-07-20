from flask import Flask, request, render_template, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not TOGETHER_API_KEY:
    raise ValueError("TOGETHER_API_KEY not found in .env file")

app = Flask(__name__)

TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"
MODEL = "mistralai/Mixtral-8x7B-Instruct-v0.1"

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
            "Authorization": f"Bearer {TOGETHER_API_KEY}",
            "Content-Type": "application/json"
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

        response = requests.post(TOGETHER_API_URL, headers=headers, json=payload)

        if response.status_code != 200:
            return jsonify({"error": f"Together AI API error: {response.text}"}), 500

        result = response.json()["choices"][0]["message"]["content"].strip()
        return jsonify({"result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
