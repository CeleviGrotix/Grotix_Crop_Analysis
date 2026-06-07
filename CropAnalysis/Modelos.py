from google import genai

# 1. PEGA TU API KEY REAL AQUÍ
api_key = ""

def check_models():
    print("Conectando con Google AI Studio...\n")
    try:
        client = genai.Client(api_key=api_key)
        
        print("Modelos disponibles:")
        print("-" * 30)
        
        # Pedimos a la API la lista de todos los modelos
        modelos = client.models.list()
        
        modelos_encontrados = 0
        for m in modelos:
            # Filtramos un poco para que no te salga demasiada basura, 
            # solo nos interesan los modelos 'gemini'
            if "gemini" in m.name.lower():
                print(f"🔸 Nombre del modelo: {m.name}")
                modelos_encontrados += 1
                
        if modelos_encontrados == 0:
            print("No se encontraron modelos Gemini asociados a esta API Key.")
            
    except Exception as e:
        print(f"Error al conectar con la API: {e}")

if __name__ == "__main__":
    check_models()