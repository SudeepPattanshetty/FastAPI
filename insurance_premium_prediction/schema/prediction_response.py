from pydantic import BaseModel, Field
from typing import Dict

class PredictionResponse(BaseModel):
    predicted_category: str = Field(..., description="Predicted insurance premium category", example="High")
    confidence: float = Field(..., description="Confidence score of the prediction range(0 to 1)", example=0.8432)
    class_probabilities: Dict[str, float] = Field(..., description="Probabilities for each insurance premium category", example={"High": 0.8432, "Medium": 0.1234, "Low": 0.0334})