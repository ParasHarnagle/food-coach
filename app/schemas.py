from typing import List, Literal, Optional
from pydantic import BaseModel, Field, conlist, confloat, PositiveInt

PortionSource = Literal["heuristic", "device", "mono"]

class VisionItem(BaseModel):
    name: str
    grams: PositiveInt
    confidence: confloat(ge=0.0, le=1.0)
    tags: List[str] = Field(default_factory=list)
    suggestions: Optional[List[str]] = None  # used when name="unknown"

class VisionTelemetry(BaseModel):
    time_ms: confloat(ge=0.0)
    portion_source: PortionSource
    depth_coverage_pct: confloat(ge=0.0, le=100.0)

class VisionResponse(BaseModel):
    foodList: conlist(VisionItem, min_items=0)
    telemetry: VisionTelemetry

class Macros(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float

class CoachItem(VisionItem):
    ingredients: List[str]
    macros: Macros

class Totals(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float

class RemainingDaily(Totals):
    pass

class CoachResponse(BaseModel):
    mealId: str
    mealSlot: Literal["breakfast", "lunch", "dinner", "snack"] = "lunch"
    items: conlist(CoachItem, min_items=1)
    totals: Totals
    remainingDaily: RemainingDaily
    coachReply: str
    imagePath: str
