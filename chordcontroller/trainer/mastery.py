from __future__ import annotations

import time

from chordcontroller.trainer.domain import AttemptFeedback, ItemProgress, MasteryLevel


def _mastery_level_from_score(score: float) -> MasteryLevel:
    if score >= 0.95:
        return MasteryLevel.MASTERED
    if score >= 0.85:
        return MasteryLevel.AUTOMATIC
    if score >= 0.70:
        return MasteryLevel.RELIABLE
    if score >= 0.50:
        return MasteryLevel.RECOGNIZED
    if score >= 0.20:
        return MasteryLevel.LEARNING
    return MasteryLevel.UNKNOWN


def update_item_progress(progress: ItemProgress, feedback: AttemptFeedback) -> ItemProgress:
    progress.attempts += 1
    if feedback.correct:
        progress.correct_attempts += 1
        progress.recent_errors = max(0, progress.recent_errors - 1)
    else:
        progress.recent_errors += 1

    if progress.best_reaction_ms == 0 or feedback.reaction_ms < progress.best_reaction_ms:
        progress.best_reaction_ms = feedback.reaction_ms

    if progress.avg_reaction_ms == 0.0:
        progress.avg_reaction_ms = float(feedback.reaction_ms)
    else:
        alpha = 0.2
        progress.avg_reaction_ms = (1 - alpha) * progress.avg_reaction_ms + alpha * feedback.reaction_ms

    quality = 5 if feedback.correct and feedback.reaction_ms <= 900 else 4 if feedback.correct else 2
    progress.easiness = max(1.3, progress.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    if feedback.correct:
        if progress.repetitions == 0:
            progress.interval_days = 1
        elif progress.repetitions == 1:
            progress.interval_days = 3
        else:
            progress.interval_days = max(1, int(round(progress.interval_days * progress.easiness)))
        progress.repetitions += 1
    else:
        progress.repetitions = 0
        progress.interval_days = 1

    now = feedback.timestamp_ts if feedback.timestamp_ts > 0 else time.time()
    progress.due_ts = now + progress.interval_days * 86400
    progress.last_practiced_ts = now

    accuracy = progress.accuracy
    speed_factor = 0.0
    if progress.avg_reaction_ms > 0:
        speed_factor = max(0.0, min(1.0, (1500.0 - progress.avg_reaction_ms) / 1200.0))
    progress.mastery_score = max(0.0, min(1.0, 0.7 * accuracy + 0.3 * speed_factor))
    progress.mastery_level = _mastery_level_from_score(progress.mastery_score)
    return progress
