from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

PortionSource = Literal["heuristic", "device", "mono"]

class VisionItem(BaseModel):
    name: str
    grams: int
    confidence: float = Field(ge=0.0, le=1.0)
    tags: List[str] = []

class VisionTelemetry(BaseModel):
    time_ms: float
    portion_source: PortionSource
    depth_coverage_pct: float

class VisionResponse(BaseModel):
    foodList: List[VisionItem]
    telemetry: VisionTelemetry

class CoachItem(BaseModel):
    name: str
    grams: int
    confidence: float
    tags: List[str]
    ingredients: List[str]
    macros: Dict[str, float]

class CoachPayload(BaseModel):
    mealId: str
    mealSlot: Literal["breakfast","lunch","dinner","snack"] = "lunch"
    items: List[CoachItem]
    totals: Dict[str, float]
    remainingDaily: Dict[str, float]
    coachReply: str

# request schemas (multipart files handled by FastAPI directly)
