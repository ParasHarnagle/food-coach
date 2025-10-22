import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, Dict, Any, List
from app.models import CoachPayload, CoachItem
from app.utils.taxonomy import Taxonomy
from app.utils.image_io import validate_image_or_raise, make_upload_path, hashed_filename
from app.utils.nutrition import scale_macros, sum_macros, remaining, simple_coach_reply
from app.storage import save_json

router = APIRouter(prefix="/api/coach", tags=["coach"])
TAX = Taxonomy("data/taxonomy.json")

def _map_to_taxonomy(name: str) -> Optional[Dict[str, Any]]:
    return TAX.match(name) or TAX.match(name.strip().lower())

def _vision_stub(raw: bytes) -> List[Dict[str, Any]]:
    """Call in-process stub instead of HTTP: re-use the same logic as /vision (simplified)."""
    # Minimal deterministic stub to help tests be stable:
    # Always return Greek Salad 200g 0.94 unless we want randomness.
    return [{"name": "Greek Salad", "grams": 200, "confidence": 0.94, "tags": ["salad","vegetarian"]}]

@router.post("/photo", response_model=CoachPayload)
async def coach_photo(file: UploadFile = File(...), text: Optional[str] = None):
    raw = await file.read()
    try:
        _ = validate_image_or_raise(raw)
    except ValueError as e:
        raise HTTPException(status_code=415, detail=str(e))

    # persist upload
    folder = make_upload_path()
    fname = hashed_filename(raw, file.filename or "upload.jpg")
    img_path = folder / fname
    img_path.write_bytes(raw)

    # get detections (could call /api/vision/upload via HTTP; we stub in-process here)
    detections = _vision_stub(raw)

    items: List[CoachItem] = []
    macro_list = []

    for det in detections:
        match = _map_to_taxonomy(det["name"])
        if not match:
            continue
        macros = scale_macros(match["macros_per_100g"], det["grams"])
        macro_list.append(macros)
        items.append(CoachItem(
            name=match["name"],
            grams=det["grams"],
            confidence=det["confidence"],
            tags=det.get("tags", []),
            ingredients=match.get("ingredients", []),
            macros=macros
        ))

    if not items:
        raise HTTPException(status_code=422, detail="No recognizable foods for nutrition mapping.")

    totals = sum_macros(macro_list)
    rem = remaining(totals)
    reply = simple_coach_reply(totals)

    payload = CoachPayload(
        mealId=str(uuid.uuid4()),
        items=items,
        totals=totals,
        remainingDaily=rem,
        coachReply=reply
    )

    # persist meal json next to image
    json_path = Path(str(img_path) + ".json")
    save_json(json_path, payload.model_dump())
    return payload