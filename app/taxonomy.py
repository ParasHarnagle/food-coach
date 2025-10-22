import json
from pathlib import Path
from typing import Dict, List, Optional

class Taxonomy:
    def __init__(self, path: Path):
        self.data = json.loads(path.read_text(encoding="utf-8"))
        self._index = {}
        for dish in self.data["dishes"]:
            self._index[dish["name"].lower()] = dish
            for a in dish.get("aliases", []):
                self._index[a.lower()] = dish

    def match(self, raw_name: str) -> Optional[Dict]:
        if not raw_name:
            return None
        return self._index.get(raw_name.strip().lower())

    def suggestions(self, top_k: int = 3) -> List[str]:
        return [d["name"] for d in self.data["dishes"]][:top_k]

    @staticmethod
    def scale_macros(macros_per_100g: Dict[str, float], grams: int) -> Dict[str, float]:
        factor = grams / 100.0
        return {k: round(v * factor, 1) for k, v in macros_per_100g.items()}
