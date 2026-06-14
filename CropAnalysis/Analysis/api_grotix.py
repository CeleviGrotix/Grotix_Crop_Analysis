import os
import json
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from google import genai
from PIL import Image

# 1. PEGA TU API KEY REAL AQUÍ
api_key = ""
client = genai.Client(api_key=api_key)

# 2. Inicializamos el servidor
app = FastAPI(title="Grotix AI Server")

def analyze_crop_health(image_path: str) -> dict:
    """Lógica central de Gemini 2.5 Flash"""
    try:
        img = Image.open(image_path)
    except Exception as e:
        return {"error": f"Error al abrir la imagen en el servidor: {e}"}

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
            
        return json.loads(response_text)

    except json.JSONDecodeError:
        return {"error": "El modelo no devolvió un JSON válido.", "raw_response": response.text}
    except Exception as e:
        return {"error": f"Excepción en la API de Gemini: {e}"}

# 3. Este es el Endpoint que recibirá la foto desde Flutter
@app.post("/api/analyze")
async def analyze_endpoint(file: UploadFile = File(...)):
    print(f"Recibiendo foto de Flutter: {file.filename}")
    temp_file_path = f"temp_{file.filename}"
    try:
        # Guardamos la foto temporalmente
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # La mandamos a analizar
        resultado = analyze_crop_health(temp_file_path)
        
        # Borramos la foto temporal para no llenar el disco de la PC
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            
        # Devolvemos el JSON a Flutter
        return JSONResponse(content=resultado)

    except Exception as e:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        return JSONResponse(content={"error": str(e)}, status_code=500)