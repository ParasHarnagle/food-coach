import random, time
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Optional
from app.models import VisionItem, VisionTelemetry, VisionResponse
from app.utils.image_io import validate_image_or_raise, read_depth_and_coverage

router = APIRouter(prefix="/api/vision", tags=["vision"])

# tiny internal list for stubbed detection
_FAKE_MENU = [
    ("Greek Salad", ["salad","vegetarian"]),
    ("Fried Rice", ["rice","stirfry"]),
    ("Tonkotsu Ramen", ["noodles","pork"]),
    ("Chicken Adobo", ["chicken","filipino"]),
    ("Caesar Salad", ["salad","chicken"]),
]

@router.post("/upload", response_model=VisionResponse)
async def upload(
    file: UploadFile = File(...),
    depth_png: Optional[UploadFile] = File(None),
    depth_unit: Optional[str] = None,  # mm|cm|m (not used beyond presence)
):
    start = time.perf_counter()

    raw = await file.read()
    try:
        _ = validate_image_or_raise(raw)
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    depth_cov = 0.0
    portion_source = "heuristic"
    if depth_png is not None:
        depth_bytes = await depth_png.read()
        depth_cov = read_depth_and_coverage(depth_bytes)
        portion_source = "device"

    # Simulate detection: 1–2 items
    k = random.choice([1, 2])
    picks = random.sample(_FAKE_MENU, k=k)

    food_list = []
    for name, tags in picks:
        grams = random.randint(120, 400)
        confidence = round(random.uniform(0.48, 0.98), 2)
        # optional low-confidence "unknown" branch
        if confidence < 0.5:
            food_list.append(VisionItem(name="unknown", grams=grams, confidence=confidence, tags=[]))
        else:
            food_list.append(VisionItem(name=name, grams=grams, confidence=confidence, tags=tags))

    elapsed = (time.perf_counter() - start) * 1000.0
    return VisionResponse(
        foodList=food_list,
        telemetry=VisionTelemetry(
            time_ms=round(elapsed, 1),
            portion_source=portion_source,  # heuristic or device
            depth_coverage_pct=depth_cov,
        )
    )
