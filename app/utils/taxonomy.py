import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class Taxonomy:
    def __init__(self, path: str = "data/taxonomy.json"):
        self.path = Path(path)
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.version = data.get("version", "test-1")
        self.dishes: List[Dict[str, Any]] = data.get("dishes", [])
        # Build fast lookup (case-insensitive)
        self._by_name = {}
        for d in self.dishes:
            self._by_name[d["name"].lower()] = d
            for a in d.get("aliases", []):
                self._by_name[a.lower()] = d

    def match(self, raw: str) -> Optional[Dict[str, Any]]:
        return self._by_name.get(raw.lower())

    def list_names(self) -> List[str]:
        return [d["name"] for d in self.dishes]