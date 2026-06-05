from sqlalchemy import desc

from app.infrastructure.persistence.models.analysis_report_model import AnalysisReportModel


class MySQLAnalysisRepository:

    def __init__(self, db):

        self.db = db

    def save(self, report_data):

        report = AnalysisReportModel(
            **report_data
        )

        self.db.add(report)

        self.db.commit()

        self.db.refresh(report)

        return report

    def find_latest_by_zone(
        self,
        zone_id
    ):

        return (
            self.db.query(
                AnalysisReportModel
            )
            .filter(
                AnalysisReportModel.zone_id == zone_id
            )
            .order_by(
                desc(
                    AnalysisReportModel.created_at
                )
            )
            .first()
        )

    def find_by_id(
        self,
        report_id
    ):

        return (
            self.db.query(
                AnalysisReportModel
            )
            .filter(
                AnalysisReportModel.report_id == report_id
            )
            .first()
        )

    def get_history(
            self,
            zone_id,
            limit=50,
            offset=0
    ):
        return (
            self.db.query(
                AnalysisReportModel
            )
            .filter(
                AnalysisReportModel.zone_id == zone_id
            )
            .order_by(
                AnalysisReportModel.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )