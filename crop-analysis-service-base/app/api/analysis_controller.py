import os

from fastapi import APIRouter
from fastapi import Depends
from fastapi import UploadFile
from fastapi import File

from sqlalchemy.orm import Session

from app.infrastructure.persistence.database import get_db
from app.infrastructure.persistence.repositories.mysql_analysis_repository import (
    MySQLAnalysisRepository
)
from app.application.handlers.generate_crop_analysis_handler import (
    GenerateCropAnalysisHandler
)
from app.infrastructure.storage.image_storage_service import (
    ImageStorageService
)

from app.schemas.analysis_response import (
    AnalysisResponse
)

router = APIRouter()


@router.post(
    "/zones/{id}/analyze",
    response_model=AnalysisResponse
)
def analyze_zone(
    id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    storage = ImageStorageService()

    # Ruta física completa
    image_path = storage.save(image)

    repository = MySQLAnalysisRepository(db)

    handler = GenerateCropAnalysisHandler(
        repository
    )

    report = handler.execute(
        zone_id=id,
        image_path=image_path
    )

    return {

        "analysisId":
            report.report_id,

        "imageUrl":
            f"http://localhost:5106/images/{report.image_path}",

        "healthScore":
            report.health_score,

        "phase":
            report.detected_phase
    }

@router.get(
    "/zones/{id}/health"
)
def get_zone_health(
    id: int,
    db: Session = Depends(
        get_db
    )
):

    repository = (
        MySQLAnalysisRepository(
            db
        )
    )

    report = (
        repository.find_latest_by_zone(
            id
        )
    )

    if not report:

        return {
            "message":
                "No reports found"
        }

    return {
        "zoneId":
            report.zone_id,

        "timestamp":
            report.created_at,

        "healthScore":
            report.health_score,

        "detectedPhase":
            report.detected_phase,

        "recommendations":
            report.recommendations
    }

@router.get(
    "/zones/{id}/reports"
)
def get_zone_reports(
    id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(
        get_db
    )
):

    repository = (
        MySQLAnalysisRepository(
            db
        )
    )

    reports = (
        repository.get_history(
            zone_id=id,
            limit=limit,
            offset=offset
        )
    )

    return [
        {
            "reportId":
                report.report_id,

            "zoneId":
                report.zone_id,

            "detectedPhase":
                report.detected_phase,

            "healthScore":
                report.health_score,

            "createdAt":
                report.created_at
        }
        for report in reports
    ]

@router.get(
    "/reports/{id}"
)
def get_report_detail(
    id: int,
    db: Session = Depends(
        get_db
    )
):

    repository = (
        MySQLAnalysisRepository(
            db
        )
    )

    report = (
        repository.find_by_id(
            id
        )
    )

    if not report:

        return {
            "message":
                "Report not found"
        }

    return {

        "reportId":
            report.report_id,

        "zoneId":
            report.zone_id,

        "imageUrl":
            f"http://localhost:5106/images/{report.image_path}",

        "healthScore":
            report.health_score,

        "detectedPhase":
            report.detected_phase,

        "createdAt":
            report.created_at,

        "analysisDetails":
            report.analysis_details,

        "recommendations":
            report.recommendations,
    }