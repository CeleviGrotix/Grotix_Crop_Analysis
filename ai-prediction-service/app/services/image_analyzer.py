import cv2
import numpy as np
from datetime import datetime


class ImageAnalyzer:

    def analyze(self, image_path: str):

        image = cv2.imread(image_path)

        if image is None:
            raise Exception(
                f"Unable to read image: {image_path}"
            )

        hsv = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2HSV
        )

        # Verde
        green_lower = np.array([35, 40, 40])
        green_upper = np.array([90, 255, 255])

        # Amarillo
        yellow_lower = np.array([15, 40, 40])
        yellow_upper = np.array([35, 255, 255])

        # Marrón
        brown_lower = np.array([5, 40, 20])
        brown_upper = np.array([20, 255, 150])

        green_mask = cv2.inRange(
            hsv,
            green_lower,
            green_upper
        )

        yellow_mask = cv2.inRange(
            hsv,
            yellow_lower,
            yellow_upper
        )

        brown_mask = cv2.inRange(
            hsv,
            brown_lower,
            brown_upper
        )

        total_pixels = (
            image.shape[0]
            * image.shape[1]
        )

        green_percentage = (
            cv2.countNonZero(green_mask)
            / total_pixels
        )

        yellow_percentage = (
            cv2.countNonZero(yellow_mask)
            / total_pixels
        )

        brown_percentage = (
            cv2.countNonZero(brown_mask)
            / total_pixels
        )

        # Health Score
        health_score = (
            100
            - (yellow_percentage * 60)
            - (brown_percentage * 100)
        )

        health_score = round(
            max(
                0,
                min(100, health_score)
            ),
            2
        )

        # Fase detectada

        if green_percentage < 0.05:

            detected_phase = "UNKNOWN"

        elif brown_percentage > 0.30:

            detected_phase = "HARVEST"

        elif yellow_percentage > 0.20:

            detected_phase = "FRUITING"

        elif green_percentage > 0.70:

            detected_phase = "VEGETATIVE"

        else:

            detected_phase = "FLOWERING"

        # Nivel de estrés
        if health_score < 60:
            stress_level = "HIGH"

        elif health_score < 80:
            stress_level = "MEDIUM"

        else:
            stress_level = "LOW"

        # Enfermedad simulada
        disease = None

        if (
                green_percentage > 0.10
                and yellow_percentage > 0.20
        ):
            disease = "Leaf Stress"

        # Recomendaciones
        recommendations = []

        if stress_level == "HIGH":

            recommendations.append(
                "Increase irrigation immediately"
            )

            recommendations.append(
                "Inspect crop for disease symptoms"
            )

        elif stress_level == "MEDIUM":

            recommendations.append(
                "Monitor soil moisture"
            )

            recommendations.append(
                "Inspect leaf coloration"
            )

        else:

            recommendations.append(
                "Maintain irrigation schedule"
            )

            recommendations.append(
                "Continue monitoring growth"
            )

        findings = []

        if green_percentage > 0.70:
            findings.append(
                "Healthy green coloration detected"
            )

        if (
                green_percentage > 0.10
                and yellow_percentage > 0.20
        ):
            findings.append(
                "Signs of leaf stress detected"
            )

        if green_percentage < 0.05:
            findings.append(
                "No significant foliage detected"
            )

        if brown_percentage > 0.05:
            findings.append(
                "Possible pest or disease damage"
            )

        return {

            "healthScore": health_score,

            "detectedPhase": detected_phase,

            "disease": disease,

            "stressLevel": stress_level,

            "leafColorScore": round(
                green_percentage * 10,
                2
            ),

            "greenPercentage": round(
                green_percentage * 100,
                2
            ),

            "yellowPercentage": round(
                yellow_percentage * 100,
                2
            ),

            "brownPercentage": round(
                brown_percentage * 100,
                2
            ),

            "findings": findings,

            "recommendations": recommendations,

            "confidence": round(
                min(
                    0.99,
                    0.80 + green_percentage * 0.15
                ),
                2
            ),

            "analysisTimestamp": (
                datetime.utcnow()
                .isoformat()
            )
        }