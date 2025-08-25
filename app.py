from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("La variable de entorno API_KEY no está definida")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent?key={API_KEY}"

@app.route("/api/conclusiones", methods=["POST"])
def conclusiones():
    data = request.json
    texto = data.get("texto", "")
  
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    response = requests.post(GEMINI_URL, json=payload)
    return jsonify(response.json())

@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
