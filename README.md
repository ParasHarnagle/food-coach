# 🥗 Food Coach — Nutrition AI (FastAPI Stub)

A lightweight FastAPI backend that simulates a **photo-based nutrition coach**.  
It has two key endpoints:

1. **`/api/vision/upload`** – Pretends to detect foods in an image (Vision API).  
2. **`/api/coach/photo`** – Saves the photo, maps the detected foods to a nutrition taxonomy, calculates macros, and returns a “coach” response (Coach API).

---

## 🚀 Features

✅ Upload food photos (JPEG/PNG/WebP)  
✅ Stubbed AI food detection with random grams & confidence  
✅ Nutrition lookup via `data/taxonomy.json`  
✅ Automatic macro scaling (`per 100g × grams / 100`)  
✅ Saves uploaded meals to `uploads/YYYY/MM/`  
✅ Simple rule-based coach feedback  
✅ Proper validation & error handling (415 / 422)  
✅ Minimal tests (pass + fail cases)

---

## 🧠 How It Works

### 1. Vision Upload API
- **Endpoint:** `POST /api/vision/upload`
- **Input:** multipart image (`file`) and optional `depth_png`
- **Output:** list of detected foods + telemetry (simulated)

**Example**
```bash
curl -sS \
  -F "file=@data/greeksalad.jpeg;type=image/jpeg" \
  http://localhost:8000/api/vision/upload | jq
```
  ### Sample Response
  ```json
  {
  "foodList": [
    { "name": "Greek Salad", "grams": 220, "confidence": 0.91, "tags": ["salad","vegetarian"] }
  ],
  "telemetry": { "time_ms": 134.2, "portion_source": "heuristic", "depth_coverage_pct": 0.0 }
}

**###2. Coach Photo API**

- **Endpoint:**: POST /api/coach/photo
- **Input:**: multipart image (file)
- **Process:** internally calls Vision stub, maps detected foods to taxonomy, scales macros, and stores the result.
- **Output:** : full meal analysis and remaining daily macros.

###Example
```bash
curl -sS \
  -F "file=@data/greeksalad.jpeg;type=image/jpeg" \
  http://localhost:8000/api/coach/photo | jq

###Sample Response
```json
{
  "mealId": "uuid-1234",
  "mealSlot": "lunch",
  "items": [
    {
      "name": "Greek Salad",
      "grams": 200,
      "confidence": 0.94,
      "tags": ["salad","vegetarian"],
      "ingredients": ["Tomatoes","Cucumbers","Olives","Feta"],
      "macros": { "calories": 150, "protein": 6, "carbs": 10, "fat": 9, "fiber": 3 }
    }
  ],
  "totals": { "calories": 150, "protein": 6, "carbs": 10, "fat": 9, "fiber": 3 },
  "remainingDaily": { "calories": 1650, "protein": 104, "carbs": 190, "fat": 51, "fiber": 22 },
  "coachReply": "Nice balanced meal!"
}

###Bad file (should 415)
curl -sS \
  -F "file=@README.md;type=text/plain" \
  http://localhost:8000/api/coach/photo | jq

  ###Sample Response
  ```json
  {
  "detail": [
    {
      "type": "value_error",
      "loc": [
        "body",
        "file"
      ],
      "msg": "Value error, Expected UploadFile, received: <class 'str'>",
      "input": "/Users/parasharnagle/Documents/LLMsprojs/Food_Coach/data/greeksalad.jpeg",
      "ctx": {
        "error": {}
      }
    }
  ]
}
**##Setup & Run**

**###1. Clone and enter**
```bash
git clone https://github.com/<your-username>/food-coach.git
cd food-coach

**###2. Environment setup**
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt


**###3. Launch API**
```bash
python -m uvicorn app.main:app --reload

Then visit Swagger UI **👉 http://127.0.0.1:8000/docs**


