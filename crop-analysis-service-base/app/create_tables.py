from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.database import engine

from app.infrastructure.persistence.models.analysis_report_model import AnalysisReportModel

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Done.")