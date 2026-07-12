from __future__ import annotations

from collections import defaultdict

from chordcontroller.config import Config, ControllerButtonName

from chordcontroller.trainer.domain import Curriculum, ItemCategory, Lesson, LessonRequirement, TrainingItem

_LEFT = {"shoulder_l", "trigger_l", "dpad_up", "dpad_down", "dpad_left", "dpad_right"}
_RIGHT = {"shoulder_r", "trigger_r", "face_up", "face_down", "face_left", "face_right"}


def _movement_score(chord: tuple[ControllerButtonName, ...]) -> float:
    size_score = len(chord) * 0.7
    left = sum(1 for b in chord if b in _LEFT)
    right = sum(1 for b in chord if b in _RIGHT)
    hand_switch_penalty = 0.4 if left and right else 0.0
    return size_score + hand_switch_penalty


def _extract_down_keys(actions: dict) -> list[str]:
    down_actions = actions.get("down")
    if down_actions is None:
        return []
    action_list = down_actions if isinstance(down_actions, list) else [down_actions]
    keys: list[str] = []
    for action in action_list:
        if getattr(action, "action", "") == "key_down":
            keys.append(action.key)
    return keys


def _classify_output(output: str) -> ItemCategory:
    if len(output) == 1 and output.isalpha():
        return ItemCategory.LETTER
    if len(output) == 1 and output.isdigit():
        return ItemCategory.NUMBER
    if output in {"space"}:
        return ItemCategory.SPACE
    if output in {"enter"}:
        return ItemCategory.ENTER
    if output in {"ctrl", "alt", "shift", "cmd"}:
        return ItemCategory.MODIFIER
    if output in {"backspace", "delete"}:
        return ItemCategory.EDITING
    if output in {"left", "right", "up", "down", "pos1", "end", "tab", "menu"}:
        return ItemCategory.NAVIGATION
    if output.startswith("f") and output[1:].isdigit():
        return ItemCategory.FUNCTION
    if len(output) >= 2 and output.isalpha():
        return ItemCategory.WORD_CHORD
    if len(output) == 1 and not output.isalnum():
        return ItemCategory.PUNCTUATION
    return ItemCategory.OTHER


def generate_curriculum(config: Config, mode_name: str = "typing") -> Curriculum:
    mode = config.modes.get(mode_name)
    if mode is None or not mode.multi_button_actions:
        return Curriculum(items={}, lessons=[])

    items: dict[str, TrainingItem] = {}
    for index, mba in enumerate(mode.multi_button_actions):
        keys = _extract_down_keys(mba.actions)
        if not keys:
            continue
        output = "".join(" " if k == "space" else "\n" if k == "enter" else k for k in keys)
        item_id = f"{mode_name}:{index}"
        chord = tuple(sorted(mba.buttons))
        items[item_id] = TrainingItem(
            item_id=item_id,
            output=output,
            chord=chord,
            category=_classify_output(output),
            mode_name=mode_name,
            movement_score=_movement_score(chord),
        )

    by_phase: dict[str, list[TrainingItem]] = defaultdict(list)
    for item in items.values():
        if item.category == ItemCategory.LETTER:
            phase = "letters"
        elif item.category == ItemCategory.NUMBER:
            phase = "numbers"
        elif item.category == ItemCategory.PUNCTUATION:
            phase = "punctuation"
        elif item.category in {ItemCategory.EDITING, ItemCategory.NAVIGATION}:
            phase = "editing-navigation"
        elif item.category == ItemCategory.MODIFIER:
            phase = "modifiers"
        elif item.category == ItemCategory.WORD_CHORD:
            phase = "word-chords"
        elif item.category == ItemCategory.FUNCTION:
            phase = "advanced"
        else:
            phase = "other"
        by_phase[phase].append(item)

    lessons: list[Lesson] = []
    learned: list[str] = []
    lesson_index = 1

    def add_lessons(phase_name: str, phase_items: list[TrainingItem], chunk_size: int) -> None:
        nonlocal lesson_index
        if not phase_items:
            return
        for chunk_start in range(0, len(phase_items), chunk_size):
            chunk = phase_items[chunk_start : chunk_start + chunk_size]
            new_ids = [item.item_id for item in chunk]
            review_ids = learned[-30:]
            lesson = Lesson(
                lesson_id=f"lesson-{lesson_index:02d}",
                title=f"Lesson {lesson_index}: {phase_name}",
                phase=phase_name,
                new_item_ids=new_ids,
                review_item_ids=review_ids,
                requirements=LessonRequirement(),
            )
            lessons.append(lesson)
            learned.extend(new_ids)
            lesson_index += 1

    letter_items = sorted(by_phase.get("letters", []), key=lambda x: (x.movement_score, x.output))
    lowercase_letters = [item for item in letter_items if len(item.output) == 1 and item.output.islower()]
    uppercase_letters = [item for item in letter_items if len(item.output) == 1 and item.output.isupper()]
    remaining_letters = [item for item in letter_items if item not in lowercase_letters and item not in uppercase_letters]

    add_lessons("lowercase letters", lowercase_letters, chunk_size=2)
    add_lessons("uppercase letters", uppercase_letters, chunk_size=10)
    add_lessons("letters mixed", remaining_letters, chunk_size=5)

    for phase in [
        "numbers",
        "punctuation",
        "editing-navigation",
        "modifiers",
        "word-chords",
        "advanced",
        "other",
    ]:
        phase_items = sorted(by_phase.get(phase, []), key=lambda x: (x.movement_score, x.output))
        add_lessons(phase, phase_items, chunk_size=5)

    return Curriculum(items=items, lessons=lessons)
