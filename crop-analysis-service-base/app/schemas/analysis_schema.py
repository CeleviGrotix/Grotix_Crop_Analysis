from pydantic import BaseModel


class AnalyzeRequest(
    BaseModel
):
    forceImageCapture: bool = False