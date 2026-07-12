from __future__ import annotations

from chordcontroller.trainer.domain import Curriculum, Lesson, LessonProgress, TrainerProgress


class LessonStatus:
    RECOMMENDED = "recommended"
    NOT_RECOMMENDED = "not_recommended"
    MASTERED = "mastered"


def _lesson_accuracy(lesson: Lesson, progress: TrainerProgress) -> float:
    item_ids = lesson.new_item_ids + lesson.review_item_ids
    if not item_ids:
        return 0.0
    accuracies = []
    for item_id in item_ids:
        item = progress.item_progress.get(item_id)
        if item and item.attempts > 0:
            accuracies.append(item.accuracy)
    return sum(accuracies) / len(accuracies) if accuracies else 0.0


def _lesson_avg_reaction(lesson: Lesson, progress: TrainerProgress) -> float:
    reaction_times = []
    for item_id in lesson.new_item_ids + lesson.review_item_ids:
        item = progress.item_progress.get(item_id)
        if item and item.avg_reaction_ms > 0:
            reaction_times.append(item.avg_reaction_ms)
    return sum(reaction_times) / len(reaction_times) if reaction_times else 0.0


def _prior_mastery_ratio(lesson_index: int, curriculum: Curriculum, progress: TrainerProgress) -> float:
    if lesson_index <= 0:
        return 1.0
    prior_items = []
    for prior in curriculum.lessons[:lesson_index]:
        prior_items.extend(prior.new_item_ids)
    if not prior_items:
        return 1.0
    mastered = 0
    total = 0
    for item_id in prior_items:
        item = progress.item_progress.get(item_id)
        if not item:
            continue
        total += 1
        if item.mastery_score >= 0.8:
            mastered += 1
    return mastered / total if total else 0.0


def evaluate_statuses(curriculum: Curriculum, progress: TrainerProgress) -> dict[str, str]:
    statuses: dict[str, str] = {}
    recommended_assigned = False
    for index, lesson in enumerate(curriculum.lessons):
        lesson_state = progress.lesson_progress.setdefault(lesson.lesson_id, LessonProgress())
        lesson_state.unlocked = True
        if lesson_state.completed:
            statuses[lesson.lesson_id] = LessonStatus.MASTERED
            continue

        if not recommended_assigned:
            statuses[lesson.lesson_id] = LessonStatus.RECOMMENDED
            recommended_assigned = True
        else:
            statuses[lesson.lesson_id] = LessonStatus.NOT_RECOMMENDED

    return statuses
