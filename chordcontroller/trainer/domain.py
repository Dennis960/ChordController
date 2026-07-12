from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable

from chordcontroller.config import ControllerButtonName


class MasteryLevel(str, Enum):
    UNKNOWN = "unknown"
    LEARNING = "learning"
    RECOGNIZED = "recognized"
    RELIABLE = "reliable"
    AUTOMATIC = "automatic"
    MASTERED = "mastered"


class ItemCategory(str, Enum):
    LETTER = "letter"
    NUMBER = "number"
    PUNCTUATION = "punctuation"
    SPACE = "space"
    ENTER = "enter"
    EDITING = "editing"
    NAVIGATION = "navigation"
    MODIFIER = "modifier"
    SHORTCUT = "shortcut"
    WORD_CHORD = "word_chord"
    FUNCTION = "function"
    OTHER = "other"


class DrillType(str, Enum):
    CHARACTER = "character"
    RECOGNITION = "recognition"
    CHORD = "chord"
    WORD = "word"
    SENTENCE = "sentence"
    MODIFIER = "modifier"
    EDITING = "editing"
    WORD_CHORD = "word_chord"
    NUMBER = "number"
    SYMBOL = "symbol"
    FREE_TYPING = "free_typing"


class LessonStage(str, Enum):
    INTRODUCE = "introduce"
    RECOGNITION = "recognition"
    RECALL = "recall"
    MIXED_PRACTICE = "mixed_practice"
    MINI_WORDS = "mini_words"
    TIMED_ROUND = "timed_round"
    REVIEW = "review"


@dataclass(slots=True)
class TrainingItem:
    item_id: str
    output: str
    chord: tuple[ControllerButtonName, ...]
    category: ItemCategory
    mode_name: str
    movement_score: float


@dataclass(slots=True)
class LessonRequirement:
    min_accuracy: float = 0.90
    max_avg_reaction_ms: int = 1000
    min_prior_mastery_ratio: float = 0.80


@dataclass(slots=True)
class Lesson:
    lesson_id: str
    title: str
    phase: str
    new_item_ids: list[str]
    review_item_ids: list[str]
    requirements: LessonRequirement = field(default_factory=LessonRequirement)


@dataclass(slots=True)
class Curriculum:
    items: dict[str, TrainingItem]
    lessons: list[Lesson]


@dataclass(slots=True)
class ItemProgress:
    attempts: int = 0
    correct_attempts: int = 0
    avg_reaction_ms: float = 0.0
    best_reaction_ms: int = 0
    last_practiced_ts: float = 0.0
    mastery_score: float = 0.0
    mastery_level: MasteryLevel = MasteryLevel.UNKNOWN
    interval_days: int = 0
    due_ts: float = 0.0
    easiness: float = 2.5
    repetitions: int = 0
    recent_errors: int = 0

    @property
    def accuracy(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.correct_attempts / self.attempts


@dataclass(slots=True)
class LessonProgress:
    unlocked: bool = False
    completed: bool = False
    best_accuracy: float = 0.0
    best_avg_reaction_ms: float = 0.0


@dataclass(slots=True)
class TrainerProgress:
    item_progress: dict[str, ItemProgress] = field(default_factory=dict)
    lesson_progress: dict[str, LessonProgress] = field(default_factory=dict)
    streak_days: int = 0
    last_active_date: str = ""


@dataclass(slots=True)
class AttemptFeedback:
    correct: bool
    reaction_ms: int
    timestamp_ts: float


@dataclass(slots=True)
class DrillPrompt:
    prompt: str
    expected: str
    item_id: str | None = None
    chord: tuple[ControllerButtonName, ...] | None = None


def button_label(chord: Iterable[ControllerButtonName]) -> str:
    return " + ".join(sorted(chord))
