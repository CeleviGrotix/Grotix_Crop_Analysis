import pytest
import httpx
from unittest.mock import MagicMock
from app.domain.services.diagnosis_engine import DiagnosisEngine
from app.application.handlers.generate_crop_analysis_handler import GenerateCropAnalysisHandler
from app.infrastructure.external.ai_adapter import AIAdapter

# ==========================================
# TDD: DiagnosisEngine (4 Tests)
# ==========================================
def test_diagnosis_engine_formats_report_correctly(mocker):
    engine = DiagnosisEngine()
    # Simulamos la respuesta del AIAdapter
    mock_response = {
        "healthScore": 85.5, "detectedPhase": "Germinación", "recommendations": "Mantener riego",
        "disease": "Ninguna", "stressLevel": "Bajo", "leafColorScore": 9.0,
        "greenPercentage": 90, "yellowPercentage": 10, "brownPercentage": 0,
        "findings": "Crecimiento óptimo", "confidence": 0.98, "analysisTimestamp": "2026-06-06T10:00:00Z"
    }
    mocker.patch.object(engine.ai_adapter, 'analyze_image', return_value=mock_response)
    
    report = engine.generate_diagnostic_report("fake/path.jpg")
    
    assert report["health_score"] == 85.5
    assert report["detected_phase"] == "Germinación"
    assert report["analysis_details"]["disease"] == "Ninguna"

def test_diagnosis_engine_is_critical_returns_true():
    engine = DiagnosisEngine()
    assert engine.is_critical(69.9) is True

def test_diagnosis_engine_is_critical_returns_false():
    engine = DiagnosisEngine()
    assert engine.is_critical(85.0) is False

def test_diagnosis_engine_is_critical_edge_case():
    engine = DiagnosisEngine()
    assert engine.is_critical(70.0) is False

# ==========================================
# TDD: GenerateCropAnalysisHandler (3 Tests)
# ==========================================
def test_handler_executes_and_saves_correctly(mocker):
    mock_repo = MagicMock()
    # Simulamos el reporte que devuelve el DiagnosisEngine
    mock_diagnosis = {
        "detected_phase": "Floración", "health_score": 92.0,
        "recommendations": "Añadir fertilizante", "analysis_details": {}
    }
    
    handler = GenerateCropAnalysisHandler(mock_repo)
    mocker.patch.object(handler.diagnosis_engine, 'generate_diagnostic_report', return_value=mock_diagnosis)
    
    handler.execute(10, "/images/test_crop.jpg")
    
    # Verificamos que el repositorio guardó el archivo con el nombre correcto (sin la ruta completa)
    mock_repo.save.assert_called_once()
    saved_data = mock_repo.save.call_args[0][0]
    assert saved_data["zone_id"] == 10
    assert saved_data["image_path"] == "test_crop.jpg"

def test_handler_extracts_filename_from_complex_path(mocker):
    mock_repo = MagicMock()
    handler = GenerateCropAnalysisHandler(mock_repo)
    mocker.patch.object(handler.diagnosis_engine, 'generate_diagnostic_report', return_value={"detected_phase": "A", "health_score": 90, "recommendations": "B", "analysis_details": {}})
    
    handler.execute(1, "C:/users/admin/images/2026/plant.png")
    
    saved_data = mock_repo.save.call_args[0][0]
    assert saved_data["image_path"] == "plant.png"

def test_handler_propagates_engine_exception(mocker):
    mock_repo = MagicMock()
    handler = GenerateCropAnalysisHandler(mock_repo)
    mocker.patch.object(handler.diagnosis_engine, 'generate_diagnostic_report', side_effect=Exception("AI Error"))
    
    with pytest.raises(Exception, match="AI Error"):
        handler.execute(1, "path.jpg")

# ==========================================
# TDD: AIAdapter (3 Tests)
# ==========================================
def test_ai_adapter_successful_post(mocker):
    adapter = AIAdapter()
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"fake_image_data"))
    
    # Simulamos la respuesta de httpx
    mock_response = MagicMock()
    mock_response.json.return_value = {"healthScore": 99}
    mock_response.raise_for_status.return_value = None
    mocker.patch("httpx.post", return_value=mock_response)
    
    result = adapter.analyze_image("fake.jpg")
    assert result["healthScore"] == 99

def test_ai_adapter_http_error_raises_exception(mocker):
    adapter = AIAdapter()
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))
    
    # Simulamos un error 500 del servidor de IA
    mocker.patch("httpx.post", side_effect=httpx.HTTPStatusError("Error", request=MagicMock(), response=MagicMock()))
    
    with pytest.raises(Exception, match="AI Prediction Service unavailable"):
        adapter.analyze_image("fake.jpg")

def test_ai_adapter_connection_timeout_raises_exception(mocker):
    adapter = AIAdapter()
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))
    
    # Simulamos timeout de red
    mocker.patch("httpx.post", side_effect=httpx.TimeoutException("Timeout"))
    
    with pytest.raises(Exception, match="AI Prediction Service unavailable"):
        adapter.analyze_image("fake.jpg")