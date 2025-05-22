from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = "AIzaSyCk99OoL2D6XnmuXQDqLyq8EirQ1nuQ9-c"  # Clave insertada directamente
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash-preview-05-20:generateContent?key={API_KEY}"

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

@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
