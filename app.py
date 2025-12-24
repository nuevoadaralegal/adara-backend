from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Permitimos CORS para que tu web de WordPress pueda hablar con este servidor
CORS(app, resources={r"/*": {"origins": "*"}})

API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("Falta la API_KEY")

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"

# --- CONTEXTO DE ADARA LEGAL (Extraído de tu Landing) ---
CONTEXTO_ADARA = """
ERES: El Asistente Virtual IA de 'Adara Legal', un despacho boutique en Madrid experto en Ley de Segunda Oportunidad.
TU TONO: Profesional, empático, jurídico pero accesible, y tranquilizador.
EQUIPO: Miguel Ángel Marchena (Socio Director), David Alonso (Procesal), Tatiana García (Proyectos).
UBICACIÓN: Calle del General Díaz Porlier, 80 1º AB, 28006 Madrid.
CONTACTO: 91 547 59 19 | 666 33 86 04 | administracion@adaralegal.es.

REGLA DE ORO (AVISO LEGAL):
JAMÁS des asesoramiento jurídico vinculante. Siempre debes decir que tu respuesta es informativa.
AL FINAL DE CADA RESPUESTA IMPORTANTE: Invita al usuario a pedir el "Estudio de Viabilidad Gratuito" contactando con el despacho.

CONOCIMIENTOS CLAVE:
- Objetivo: Exoneración del Pasivo Insatisfecho (EPI).
- Requisitos: Deudor de buena fe, no delitos económicos en 10 años.
- Deuda Pública: Se puede exonerar hasta 10.000€ Hacienda y 10.000€ Seg. Social.
- Vivienda: Adara prioriza estrategias para conservarla mediante planes de pago.
- Duración: 6-12 meses aprox.
"""

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        mensaje_usuario = data.get("mensaje", "")
        historial = data.get("historial", []) # Para mantener el hilo de la charla (opcional)

        if not mensaje_usuario:
            return jsonify({"error": "Mensaje vacío"}), 400

        # Construimos el prompt
        prompt = (
            f"{CONTEXTO_ADARA}\n\n"
            "PREGUNTA DEL USUARIO:\n"
            f"{mensaje_usuario}\n\n"
            "TU RESPUESTA (Breve, max 100 palabras, formato HTML simple si es necesario):"
        )

        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        headers = {"Content-Type": "application/json", "x-goog-api-key": API_KEY}
        
        response = requests.post(GEMINI_URL, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return jsonify({"respuesta": "Lo siento, estoy saturado. Por favor llama al 666 33 86 04."}), 200

        respuesta_ia = response.json()['candidates'][0]['content']['parts'][0]['text']
        return jsonify({"respuesta": respuesta_ia})

    except Exception as e:
        print(e)
        return jsonify({"respuesta": "Error técnico. Contacta con nosotros directamente."})

@app.route("/wake", methods=["GET"])
def wake():
    return jsonify({"status": "awake"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)