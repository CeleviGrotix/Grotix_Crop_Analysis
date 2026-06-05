from pydantic import BaseModel


class AnalysisResponse(BaseModel):

    analysisId: int

    imageUrl: str

    healthScore: float

    phase: str