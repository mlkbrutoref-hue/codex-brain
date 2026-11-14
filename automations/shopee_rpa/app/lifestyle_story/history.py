"""Persistent variation history for Nina lifestyle Stories."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


class LifestyleHistoryStore:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)

    def load(self) -> List[Dict[str, Any]]:
        if not self.path.is_file():
            return []
        data = json.loads(self.path.read_text(encoding="utf-8-sig"))
        if not isinstance(data, list):
            raise ValueError("Lifestyle history must be a JSON array")
        return [item for item in data if isinstance(item, dict)]

    def record(self, plan: Dict[str, Any], final_path: str = "") -> None:
        items = self.load()
        items.append({
            "created_at": datetime.now(timezone.utc).isoformat(),
            "time_of_day": plan.get("time_of_day"),
            "category": plan.get("category"),
            "story_type": plan.get("story_type"),
            "text_mode": plan.get("text_mode"),
            "location": plan.get("location"),
            "pose": plan.get("pose"),
            "camera_angle": plan.get("camera_angle"),
            "wardrobe": plan.get("wardrobe"),
            "mood": plan.get("mood"),
            "optional_text": plan.get("optional_text"),
            "scene_signature": plan.get("scene_signature"),
            "final_path": final_path,
        })
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    @staticmethod
    def usage_count(history: Iterable[Dict[str, Any]], signature: str) -> int:
        return sum(1 for item in history if item.get("scene_signature") == signature)
