from typing import Dict, List
from math import isfinite

DEFAULT_TARGETS = {"calories": 1800, "protein": 110, "carbs": 200, "fat": 60, "fiber": 25}
FIELDS = ["calories","protein","carbs","fat","fiber"]

def scale_macros(macros_per_100g: Dict[str, float], grams: int) -> Dict[str, float]:
    return {k: round((macros_per_100g.get(k, 0.0) * grams) / 100.0, 1) for k in FIELDS}

def sum_macros(items: List[Dict[str, float]]) -> Dict[str, float]:
    out = {k: 0.0 for k in FIELDS}
    for m in items:
        for k in FIELDS:
            v = m.get(k, 0.0)
            if isfinite(v):
                out[k] += v
    return {k: round(v, 1) for k, v in out.items()}

def remaining(totals: Dict[str, float], targets: Dict[str, float] = None) -> Dict[str, float]:
    targets = targets or DEFAULT_TARGETS
    return {k: round(max(targets.get(k, 0.0) - totals.get(k, 0.0), 0.0), 1) for k in FIELDS}

def simple_coach_reply(totals: Dict[str, float]) -> str:
    if totals["protein"] >= 25:
        return "Great protein hit!"
    if totals["fat"] >= 20:
        return "Go easy on the fats!"
    return "Nice balanced meal!"