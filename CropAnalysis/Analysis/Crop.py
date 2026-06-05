import os
import json
from google import genai
from PIL import Image

api_key = "" 

def analyze_crop_health(image_path: str) -> dict:
    """
    Ejecuta el análisis de la imagen del cultivo utilizando la nueva SDK de Gemini.
    """
    try:
        img = Image.open(image_path)
    except Exception as e:
        return {"error": f"Error al abrir la imagen local: {e}"}

    client = genai.Client(api_key=api_key)

    prompt = """
    You are an expert agricultural engineer and computer vision specialist. 
    Analyze the provided image of a crop and perform a strict diagnostic evaluation.
    
    You must extract exactly three data points based on visual observation and return them in a pure JSON format.
    
    Constraints:
    1. "estado_germinacion": You must classify the current developmental stage using ONLY one of the following exact string values: 
       ["seed", "germination", "vegetative", "flowering", "fruiting", "harvest", "unknown"]. 
       If no crop is clearly visible, the image is too blurry, or the camera is obstructed, you MUST choose "unknown".
    
    2. "health_score": An integer from 0 to 100 representing the overall vitality of the plant based on leaf color, structural integrity, and visible pests. 100 represents optimal health.
       CRITICAL RULE: If the "estado_germinacion" is "unknown", the "health_score" MUST be exactly 0.
       
    3. "observaciones": A concise technical note (maximum 2 sentences) justifying the health score, noting any visible deficiencies (e.g., water stress, discoloration), or explaining why it was marked as "unknown".

    Output ONLY a valid JSON object with the keys "estado_germinacion", "health_score", and "observaciones". Do not include markdown formatting, code blocks, or any conversational text.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        analysis_result = json.loads(response_text)
        return analysis_result

    except json.JSONDecodeError:
        return {"error": "El modelo no devolvió un JSON válido.", "raw_response": response.text}
    except Exception as e:
        return {"error": f"Excepción en la API de Gemini: {e}"}

# --- Ejecución ---
if __name__ == "__main__":
    ruta_imagen_local = "ce.jpg" 
    
    if os.path.exists(ruta_imagen_local):
        print(f"Procesando imagen local: {ruta_imagen_local}...")
        resultado = analyze_crop_health(ruta_imagen_local)
        
        print("\n--- Diagnóstico Agrícola ---")
        print(json.dumps(resultado, indent=4, ensure_ascii=False))
    else:
        print(f"Error: No se encontró la imagen '{ruta_imagen_local}'.")