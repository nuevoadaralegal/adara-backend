from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

API_KEY = os.getenv("API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={API_KEY}"

@app.route("/api/conclusiones", methods=["POST"])
def conclusiones():
    data = request.json
    texto = data.get("texto", "")
    prompt = (
        "Actúa como analista legal. Analiza el siguiente conjunto de datos generado por una herramienta informática. "
        "Elabora unas conclusiones razonadas y profesionales, pero indica claramente que el análisis ha sido realizado por medios automáticos "
        "y que para un asesoramiento completo debe contactarse con Adara Legal:\n\n" + texto
    )
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    response = requests.post(GEMINI_URL, json=payload)
    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
