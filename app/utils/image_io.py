import io, hashlib, time
from datetime import datetime
from pathlib import Path
from typing import Tuple
from PIL import Image

MAX_BYTES = 8 * 1024 * 1024  # 8MB

def validate_image_or_raise(raw_bytes: bytes) -> Image.Image:
    if len(raw_bytes) > MAX_BYTES:
        raise ValueError("File too large (max 8MB).")
    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img.verify()  # quick check
        img = Image.open(io.BytesIO(raw_bytes))  # re-open to use it
        img.load()
        if img.format not in {"JPEG","PNG","WEBP"}:
            raise ValueError("Unsupported image format (use JPEG/PNG/WebP).")
        return img
    except Exception:
        raise ValueError("Invalid or corrupted image.")

def read_depth_and_coverage(depth_bytes: bytes) -> float:
    """Count non-zero pixels / total * 100. Accepts 8/16-bit PNG."""
    if not depth_bytes:
        return 0.0
    try:
        img = Image.open(io.BytesIO(depth_bytes))
        img.load()
        # Convert to grayscale to count non-zero
        g = img.convert("I") if img.mode not in ("I","I;16") else img
        pixels = g.getdata()
        total = len(pixels)
        nonzero = sum(1 for p in pixels if p and int(p) > 0)
        return round((nonzero / total) * 100, 1) if total else 0.0
    except Exception:
        return 0.0

def make_upload_path() -> Path:
    now = datetime.utcnow()
    folder = Path("uploads") / f"{now.year:04d}" / f"{now.month:02d}"
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def hashed_filename(raw_bytes: bytes, orig_name: str) -> str:
    h = hashlib.sha256(raw_bytes + str(time.time()).encode()).hexdigest()[:16]
    ext = orig_name.split(".")[-1].lower()
    if ext not in ("jpg","jpeg","png","webp"):
        ext = "jpg"
    return f"{h}.{ext}"