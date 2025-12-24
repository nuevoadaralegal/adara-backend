from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Permitir peticiones desde cualquier origen (útil para pruebas, cuidado en producción)
CORS(app, resources={r"/*": {"origins": "*"}})

# 1. Leer API KEY desde Render
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    # Esto hará que la app falle al arrancar si no pusiste la clave en Render,
    # lo cual es bueno para que te des cuenta rápido.
    raise ValueError("La variable de entorno API_KEY no está definida")

# 2. URL Corregida: Usamos 'v1beta' para asegurar compatibilidad con Gemini 3 Preview
# Y quitamos la key de la URL para mayor seguridad
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3-flash-preview:generateContent"
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

        # Estructura del payload
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        # 3. Headers: Aquí es donde enviamos la API Key de forma segura
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        }

        # Hacemos la petición POST
        response = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=60)

        if response.status_code != 200:
            # Si falla, devolvemos el error exacto que nos da Google para poder depurar
            return jsonify({
                "error": "Error al llamar a Gemini",
                "status_code": response.status_code,
                "detalle": response.text
            }), 500

        return jsonify(response.json()), 200

    except Exception as e:
        return jsonify({"error": "Error interno del servidor", "detalle": str(e)}), 500


# Endpoint para que Render no "duerma" la app si usas el plan gratuito
@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200


if __name__ == "__main__":
    # La configuración host="0.0.0.0" y port=10000 es perfecta para Render
    app.run(host="0.0.0.0", port=10000)