from __future__ import annotations

import json
from dataclasses import asdict
from datetime import date
from pathlib import Path

from chordcontroller.paths import get_user_config_dir

from chordcontroller.trainer.domain import ItemProgress, LessonProgress, TrainerProgress


class ProgressStore:
    def __init__(self) -> None:
        base = get_user_config_dir() / "trainer"
        base.mkdir(parents=True, exist_ok=True)
        self.path = base / "progress.json"

    def load(self) -> TrainerProgress:
        if not self.path.exists():
            return TrainerProgress()

        data = json.loads(self.path.read_text(encoding="utf-8"))
        item_progress = {
            item_id: ItemProgress(**payload)
            for item_id, payload in data.get("item_progress", {}).items()
        }
        lesson_progress = {
            lesson_id: LessonProgress(**payload)
            for lesson_id, payload in data.get("lesson_progress", {}).items()
        }
        return TrainerProgress(
            item_progress=item_progress,
            lesson_progress=lesson_progress,
            streak_days=data.get("streak_days", 0),
            last_active_date=data.get("last_active_date", ""),
        )

    def save(self, progress: TrainerProgress) -> None:
        payload = {
            "item_progress": {item_id: asdict(p) for item_id, p in progress.item_progress.items()},
            "lesson_progress": {lesson_id: asdict(p) for lesson_id, p in progress.lesson_progress.items()},
            "streak_days": progress.streak_days,
            "last_active_date": progress.last_active_date,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def update_streak(self, progress: TrainerProgress) -> None:
        today = date.today()
        today_str = today.isoformat()
        if not progress.last_active_date:
            progress.streak_days = 1
            progress.last_active_date = today_str
            return

        if progress.last_active_date == today_str:
            return

        last = date.fromisoformat(progress.last_active_date)
        delta = (today - last).days
        if delta == 1:
            progress.streak_days += 1
        else:
            progress.streak_days = 1
        progress.last_active_date = today_str
