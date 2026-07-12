from __future__ import annotations

from chordcontroller.trainer.domain import Curriculum, DrillPrompt, DrillType, Lesson, LessonStage
from chordcontroller.trainer.drills import generate_drill


def lesson_stage_prompts(lesson: Lesson, curriculum: Curriculum) -> dict[LessonStage, list[DrillPrompt]]:
    new_ids = lesson.new_item_ids
    mixed_ids = lesson.review_item_ids + lesson.new_item_ids

    introduce = generate_drill(DrillType.CHARACTER, curriculum, new_ids, size=min(8, len(new_ids)))
    recognition = generate_drill(DrillType.RECOGNITION, curriculum, new_ids, size=max(8, len(new_ids) * 2))
    recall = generate_drill(DrillType.CHORD, curriculum, new_ids, size=max(8, len(new_ids) * 2))
    mixed = generate_drill(DrillType.CHARACTER, curriculum, mixed_ids, size=24)
    mini_words = generate_drill(DrillType.WORD, curriculum, mixed_ids, size=12)
    timed = generate_drill(DrillType.CHARACTER, curriculum, mixed_ids, size=40)
    review = generate_drill(DrillType.CHARACTER, curriculum, mixed_ids, size=20)

    return {
        LessonStage.INTRODUCE: introduce,
        LessonStage.RECOGNITION: recognition,
        LessonStage.RECALL: recall,
        LessonStage.MIXED_PRACTICE: mixed,
        LessonStage.MINI_WORDS: mini_words,
        LessonStage.TIMED_ROUND: timed,
        LessonStage.REVIEW: review,
    }
