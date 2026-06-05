from app.infrastructure.external.ai_adapter import AIAdapter


class DiagnosisEngine:

    def __init__(self):

        self.ai_adapter = AIAdapter()

    def generate_diagnostic_report(
        self,
        image_path: str
    ):

        ai_result = (
            self.ai_adapter
            .analyze_image(
                image_path
            )
        )

        return {

            "health_score":
                ai_result["healthScore"],

            "detected_phase":
                ai_result["detectedPhase"],

            "recommendations":
                ai_result["recommendations"],

            "analysis_details": {

                "disease":
                    ai_result["disease"],

                "stressLevel":
                    ai_result["stressLevel"],

                "leafColorScore":
                    ai_result["leafColorScore"],

                "greenPercentage":
                    ai_result["greenPercentage"],

                "yellowPercentage":
                    ai_result["yellowPercentage"],

                "brownPercentage":
                    ai_result["brownPercentage"],

                "findings":
                    ai_result["findings"],

                "confidence":
                    ai_result["confidence"],

                "analysisTimestamp":
                    ai_result["analysisTimestamp"]
            }
        }

    def is_critical(
        self,
        health_score: float
    ):

        return health_score < 70