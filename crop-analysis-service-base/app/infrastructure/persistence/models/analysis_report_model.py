from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    DateTime,
    JSON
)

from datetime import datetime

from app.infrastructure.persistence.database import Base


class AnalysisReportModel(Base):

    __tablename__ = "analysis_report"

    report_id = Column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    zone_id = Column(
        Integer,
        nullable=False
    )

    detected_phase = Column(
        String(100),
        nullable=False
    )

    health_score = Column(
        Float,
        nullable=False
    )

    recommendations = Column(
        JSON
    )

    analysis_details = Column(
        JSON
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    image_path = Column(
        String(500),
        nullable=True
    )