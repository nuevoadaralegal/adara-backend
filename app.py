from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Permitir peticiones desde cualquier origen
CORS(app, resources={r"/*": {"origins": "*"}})

# 1. Leer API KEY
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("La variable de entorno API_KEY no está definida")

# 2. URL segura (v1beta)
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

        # --- AQUÍ ESTÁ EL CAMBIO: EL PROMPT UNIVERSAL ---
        prompt = (
            "INSTRUCCIONES MAESTRAS PARA LA IA:\n"
            "1. TU MISIÓN: Analizar el texto proporcionado a continuación.\n"
            "2. DETECCIÓN DE CONTEXTO: Detecta automáticamente el tema, la industria y la naturaleza del texto "
            "(ej: Legal/Concursal, Cinematográfico, Médico, Ingeniería, etc.).\n"
            "3. ADOPCIÓN DE ROL: Adopta inmediatamente la personalidad del mayor experto mundial en esa materia detectada.\n"
            "   - Si es legal: Sé preciso, cita leyes aplicables (como TRLC en España) y sé formal.\n"
            "   - Si es cine: Sé creativo, crítico y analítico con la narrativa.\n"
            "   - Si es técnico: Sé riguroso con los datos.\n"
            "4. FORMATO DE RESPUESTA: Genera un informe estructurado que sirva para tomar decisiones.\n"
            "   Usa esta estructura:\n"
            "   - 🎯 **Diagnóstico del Experto:** De qué trata esto y cuál es la situación actual.\n"
            "   - ✅ **Puntos Fuertes:** Qué está bien planteado.\n"
            "   - ⚠️ **Riesgos o Debilidades:** Qué falla o qué podría salir mal (sé crítico).\n"
            "   - 💡 **Conclusión Final:** Tu veredicto profesional.\n\n"
            "5. ESTILO: Usa formato HTML simple (negritas <b>, saltos de línea <br>) para que sea fácil de leer.\n\n"
            "--- COMIENZO DEL TEXTO A ANALIZAR ---\n"
            f"{texto}\n"
            "--- FIN DEL TEXTO ---"
        )

        # Preparar la petición a Google
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        }

        response = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=60)

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