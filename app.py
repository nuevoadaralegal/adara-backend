from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("La variable de entorno API_KEY no está definida")

# Usamos v1beta para soporte multimodal avanzado en Gemini 3
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
        # Nuevos campos para el archivo
        archivo_b64 = data.get("archivo_base64", None) # El string largo del PDF
        mime_type = data.get("mime_type", "application/pdf")

        if not texto and not archivo_b64:
            return jsonify({"error": "Debe enviar texto o un archivo"}), 400

        # Prompt Universal (modificado ligeramente para mencionar el archivo)
        prompt_text = (
            "INSTRUCCIONES MAESTRAS PARA LA IA:\n"
            "1. TU MISIÓN: Analizar la información proporcionada (texto y/o documentos adjuntos).\n"
            "2. DETECCIÓN DE CONTEXTO: Detecta automáticamente el tema (ej: Legal/Concursal).\n"
            "3. ADOPCIÓN DE ROL: Adopta la personalidad del mayor experto mundial en la materia.\n"
            "4. ANÁLISIS DOCUMENTAL: Si se adjunta un documento (PDF/DOCX), analízalo en profundidad "
            "cruzando los datos con el resumen de texto proporcionado.\n"
            "5. FORMATO DE RESPUESTA: Informe estructurado (Diagnóstico, Puntos Fuertes, Riesgos, Conclusión).\n"
            "   Usa HTML simple (<b>, <br>, <ul>).\n\n"
            "--- COMIENZO DEL RESUMEN DE USUARIO ---\n"
            f"{texto}\n"
            "--- FIN DEL RESUMEN ---"
        )

        # Construimos las "partes" del mensaje
        parts = [{"text": prompt_text}]

        # Si hay archivo, lo añadimos al payload
        if archivo_b64:
            parts.append({
                "inline_data": {
                    "mime_type": mime_type,
                    "data": archivo_b64
                }
            })

        payload = {
            "contents": [{
                "parts": parts
            }]
        }

        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": API_KEY
        }

        response = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=120) # Aumentamos timeout a 120s por si el PDF es grande

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