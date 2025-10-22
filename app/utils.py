import hashlib
import os
import time
from datetime import datetime
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MAX_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))  # 10 MB

def read_file_limited(file: UploadFile) -> bytes:
    data = file.file.read(MAX_BYTES + 1)
    if len(data) == 0:
        raise HTTPException(status_code=400, detail="Empty file.")
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail=f"File too large (>{MAX_BYTES} bytes).")
    return data

def ensure_image(img_bytes: bytes) -> Image.Image:
    try:
        im = Image.open(io := __import__("io").BytesIO(img_bytes))
        im.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=415, detail="Unsupported media type: not an image.")
    if im.format not in ALLOWED_FORMATS:
        raise HTTPException(status_code=415, detail=f"Unsupported format: {im.format}. Allowed: {', '.join(ALLOWED_FORMATS)}")
    return im

def parse_depth_png(depth_bytes: bytes):
    from PIL import Image
    im = Image.open(io := __import__("io").BytesIO(depth_bytes))
    if im.format != "PNG":
        raise HTTPException(status_code=415, detail="depth_png must be a PNG.")
    if im.mode not in ("I;16", "I", "L"):
        im = im.convert("L")
    pixels = im.getdata()
    total = len(pixels)
    nonzero = sum(1 for p in pixels if int(p) != 0)
    coverage = (nonzero / total * 100.0) if total else 0.0
    return round(coverage, 2), (nonzero / total if total else 0.0)

def hashed_name(img_bytes: bytes, ext: str) -> str:
    h = hashlib.sha256(img_bytes + str(time.time_ns()).encode()).hexdigest()[:16]
    return f"{h}{ext}"

def persist_upload(img_bytes: bytes, suffix: str) -> str:
    now = datetime.utcnow()
    folder = Path("storage/uploads") / f"{now.year:04d}" / f"{now.month:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / hashed_name(img_bytes, suffix)
    path.write_bytes(img_bytes)
    return str(path)

def persist_meal(meal_id: str, payload: dict) -> str:
    folder = Path("storage/meals")
    folder.mkdir(parents=True, exist_ok=True)
    p = folder / f"{meal_id}.json"
    p.write_text(__import__("json").dumps(payload, ensure_ascii=False, indent=2))
    return str(p)
