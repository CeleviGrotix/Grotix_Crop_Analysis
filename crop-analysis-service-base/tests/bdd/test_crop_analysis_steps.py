from pytest_bdd import scenarios, given, when, then
from unittest.mock import MagicMock
from app.domain.services.diagnosis_engine import DiagnosisEngine
from app.application.handlers.generate_crop_analysis_handler import GenerateCropAnalysisHandler

# Carga los escenarios del archivo feature
scenarios('features/crop_analysis.feature')

# ==========================================
# US24 - Escenario 1: Categorización exitosa
# ==========================================
@given('la Inteligencia Artificial ha recibido una imagen pre-procesada', target_fixture='ctx_s1')
def step_given_imagen_recibida():
    return {"engine": DiagnosisEngine(), "image_path": "imagen_lista.jpg"}

@when('se ejecute el algoritmo de inferencia')
def step_when_ejecuta_inferencia(ctx_s1, mocker):
    mock_response = {
        "healthScore": 95, "detectedPhase": "Germinación", "recommendations": "Óptimo",
        "disease": "Ninguna", "stressLevel": "Bajo", "leafColorScore": 9,
        "greenPercentage": 90, "yellowPercentage": 10, "brownPercentage": 0,
        "findings": "Saludable", "confidence": 0.96, "analysisTimestamp": "2026-06-06"
    }
    mocker.patch.object(ctx_s1["engine"].ai_adapter, 'analyze_image', return_value=mock_response)
    ctx_s1["report"] = ctx_s1["engine"].generate_diagnostic_report(ctx_s1["image_path"])

@then('el sistema debe clasificar la planta en una de las categorías definidas con base en el dataset de entrenamiento')
def step_then_clasifica_planta(ctx_s1):
    assert ctx_s1["report"]["detected_phase"] == "Germinación"
    assert ctx_s1["report"]["health_score"] == 95

# ==========================================
# US24 - Escenario 2: Umbral de confianza
# ==========================================
@given('el modelo genera un resultado de clasificación', target_fixture='ctx_s2')
def step_given_resultado_generado():
    return {"engine": DiagnosisEngine()}

@when('el nivel de confianza sea inferior al 75%')
def step_when_confianza_inferior(ctx_s2, mocker):
    # Simulamos que la IA devuelve baja confianza y la lógica falla en determinar la fase
    mock_response = {
        "healthScore": 50, "detectedPhase": "Indeterminado", "recommendations": "Volver a capturar imagen",
        "disease": "Desconocida", "stressLevel": "Alto", "leafColorScore": 5,
        "greenPercentage": 50, "yellowPercentage": 50, "brownPercentage": 0,
        "findings": "Imagen borrosa", "confidence": 0.60, "analysisTimestamp": "2026-06-06"
    }
    mocker.patch.object(ctx_s2["engine"].ai_adapter, 'analyze_image', return_value=mock_response)
    ctx_s2["report"] = ctx_s2["engine"].generate_diagnostic_report("foto_borrosa.jpg")

@then('el sistema debe marcar el estado como "Indeterminado"')
def step_then_marcar_indeterminado(ctx_s2):
    assert ctx_s2["report"]["detected_phase"] == "Indeterminado"

# ==========================================
# US24 - Escenario 3: Actualización automática
# ==========================================
@given('el modelo ha identificado un cambio de etapa', target_fixture='ctx_s3')
def step_given_cambio_etapa():
    mock_repo = MagicMock()
    handler = GenerateCropAnalysisHandler(mock_repo)
    return {"handler": handler, "repo": mock_repo}

@when('se valide el resultado')
def step_when_valide_resultado(ctx_s3, mocker):
    mock_diagnosis = {
        "detected_phase": "Floración", "health_score": 92.0,
        "recommendations": "Añadir fertilizante", "analysis_details": {}
    }
    # Forzamos al engine a devolver el nuevo estado (Floración)
    mocker.patch.object(ctx_s3["handler"].diagnosis_engine, 'generate_diagnostic_report', return_value=mock_diagnosis)
    
    # Ejecutamos el handler que se encarga de guardar en BD
    ctx_s3["handler"].execute(zone_id=1, image_path="nueva_etapa.jpg")

@then('el sistema debe actualizar automáticamente el estado actual en la base de datos')
def step_then_actualiza_bd(ctx_s3):
    # Verificamos que el repositorio intentó guardar los datos (Actualización de la BD)
    ctx_s3["repo"].save.assert_called_once()
    
    # Extraemos qué fue lo que se guardó en la base de datos
    saved_data = ctx_s3["repo"].save.call_args[0][0]
    
    # Confirmamos que se guardó el cambio de etapa correcto
    assert saved_data["detected_phase"] == "Floración"
    assert saved_data["zone_id"] == 1