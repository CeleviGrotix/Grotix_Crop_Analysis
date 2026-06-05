import httpx


class AIAdapter:

    BASE_URL = "http://localhost:8002"

    def analyze_image(
        self,
        image_path: str
    ):

        try:

            with open(
                image_path,
                "rb"
            ) as image:

                files = {
                    "image": image
                }

                response = httpx.post(
                    f"{self.BASE_URL}/predict",
                    files=files,
                    timeout=30
                )

            response.raise_for_status()

            return response.json()

        except Exception:

            raise Exception(
                "AI Prediction Service unavailable"
            )