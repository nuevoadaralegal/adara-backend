from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Leer API KEY desde variable de entorno
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("La variable de entorno API_KEY no está definida")

# Endpoint de Gemini 3 Flash Preview
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1/"
    "models/gemini-3-flash-preview:generateContent"
    f"?key={API_KEY}"
)

@app.route("/api/conclusiones", methods=["POST"])
def conclusiones():
    try:
        data = request.json

        if not data:
            return jsonify({"error": "No se recibió JSON"}), 400

        texto = data.get("texto", "").strip()

        if not texto:
            return jsonify({"error": "Campo 'texto' vacío o no enviado"}), 400

        prompt = (
            "Eres un experto jurista español especializado en reestructuraciones, "
            "concursos de acreedores y derecho financiero. Analiza el siguiente contenido "
            "y devuelve conclusiones claras, estructuradas y prácticas. "
            "Si hay riesgos, destácalos. Si hay oportunidades estratégicas, explícalas.\n\n"
            f"Contenido:\n{texto}"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(GEMINI_URL, json=payload, timeout=60)

        if response.status_code != 200:
            return jsonify({
                "error": "Error al llamar a Gemini",
                "status_code": response.status_code,
                "detalle": response.text
            }), 500

        return jsonify(response.json()), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500


@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
