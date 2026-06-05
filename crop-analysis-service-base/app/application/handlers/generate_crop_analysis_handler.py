import os

from app.domain.services.diagnosis_engine import DiagnosisEngine


class GenerateCropAnalysisHandler:

    def __init__(
        self,
        repository
    ):

        self.repository = repository

        self.diagnosis_engine = (
            DiagnosisEngine()
        )

    def execute(
        self,
        zone_id,
        image_path
    ):

        diagnosis = (
            self.diagnosis_engine
            .generate_diagnostic_report(
                image_path
            )
        )

        image_filename = os.path.basename(
            image_path
        )

        report = self.repository.save({

            "zone_id": zone_id,

            "detected_phase":
                diagnosis[
                    "detected_phase"
                ],

            "health_score":
                diagnosis[
                    "health_score"
                ],

            "recommendations":
                diagnosis[
                    "recommendations"
                ],

            "analysis_details":
                diagnosis[
                    "analysis_details"
                ],

            # Solo el nombre del archivo
            "image_path":
                image_filename
        })

        return report