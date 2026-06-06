import os
from unittest.mock import MagicMock

# Vars de entorno ANTES de cualquier import de app
os.environ["MYSQL_USER"] = "user"
os.environ["MYSQL_PASSWORD"] = "pass"
os.environ["MYSQL_HOST"] = "localhost"
os.environ["MYSQL_PORT"] = "3306"
os.environ["MYSQL_DATABASE"] = "testdb"
os.environ["STORAGE_PATH"] = "./tests/storage"

from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.analysis_controller import router
from app.infrastructure.persistence.database import get_db

# ✅ dependency_overrides — única forma correcta de mockear Depends()
app = FastAPI()
app.include_router(router)

def override_get_db():
    yield MagicMock()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_analyze_zone_endpoint(mocker):
    mock_storage = mocker.patch("app.api.analysis_controller.ImageStorageService")
    mock_storage.return_value.save.return_value = "fake_path/image.jpg"

    mock_handler = mocker.patch("app.api.analysis_controller.GenerateCropAnalysisHandler")

    class FakeReport:
        report_id = 123
        image_path = "image.jpg"
        health_score = 88.5
        detected_phase = "Crecimiento"

    mock_handler.return_value.execute.return_value = FakeReport()

    response = client.post(
        "/zones/1/analyze",
        files={"image": ("test.jpg", b"fake_bytes", "image/jpeg")}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["analysisId"] == 123
    assert data["healthScore"] == 88.5
    assert data["phase"] == "Crecimiento"