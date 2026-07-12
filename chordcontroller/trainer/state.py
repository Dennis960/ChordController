from __future__ import annotations

import time

from chordcontroller.config import Config

from chordcontroller.trainer.curriculum import generate_curriculum
from chordcontroller.trainer.domain import AttemptFeedback, ItemProgress, LessonProgress, TrainerProgress
from chordcontroller.trainer.mastery import update_item_progress
from chordcontroller.trainer.progress_store import ProgressStore
from chordcontroller.trainer.unlocks import LessonStatus, evaluate_statuses


class TrainerState:
    def __init__(self) -> None:
        self.config = Config.load_config()
        self.curriculum = generate_curriculum(self.config, mode_name="typing")
        self.store = ProgressStore()
        self.progress = self.store.load()
        self.store.update_streak(self.progress)
        self.statuses = evaluate_statuses(self.curriculum, self.progress)

    def refresh_statuses(self) -> None:
        self.statuses = evaluate_statuses(self.curriculum, self.progress)

    def save(self) -> None:
        self.store.save(self.progress)

    def recommended_lesson_id(self) -> str | None:
        for lesson in self.curriculum.lessons:
            status = self.statuses.get(lesson.lesson_id)
            if status == LessonStatus.RECOMMENDED:
                lp = self.progress.lesson_progress.setdefault(lesson.lesson_id, LessonProgress())
                if not lp.completed:
                    return lesson.lesson_id
        return self.curriculum.lessons[0].lesson_id if self.curriculum.lessons else None

    def register_attempt(self, item_id: str, correct: bool, reaction_ms: int) -> None:
        item_progress = self.progress.item_progress.setdefault(item_id, ItemProgress())
        feedback = AttemptFeedback(correct=correct, reaction_ms=reaction_ms, timestamp_ts=time.time())
        self.progress.item_progress[item_id] = update_item_progress(item_progress, feedback)
        self.refresh_statuses()
        self.save()

    def mark_lesson_completed(self, lesson_id: str, accuracy: float, avg_reaction_ms: float) -> None:
        lesson_state = self.progress.lesson_progress.setdefault(lesson_id, LessonProgress())
        lesson_state.completed = True
        lesson_state.unlocked = True
        lesson_state.best_accuracy = max(lesson_state.best_accuracy, accuracy)
        if lesson_state.best_avg_reaction_ms == 0.0:
            lesson_state.best_avg_reaction_ms = avg_reaction_ms
        else:
            lesson_state.best_avg_reaction_ms = min(lesson_state.best_avg_reaction_ms, avg_reaction_ms)
        self.refresh_statuses()
        self.save()
