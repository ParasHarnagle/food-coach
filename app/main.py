from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import vision, coach

app = FastAPI(title="Nutrition AI (Stub)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

app.include_router(vision.router)
app.include_router(coach.router)

@app.get("/")
def root():
    return {"ok": True, "service": "nutrition-ai"}