from __future__ import annotations

import random

from chordcontroller.trainer.domain import Curriculum, DrillPrompt, DrillType, ItemCategory


_WORDS = [
    "at",
    "eat",
    "tea",
    "ten",
    "net",
    "stone",
    "tone",
    "read",
    "learn",
    "chord",
    "input",
    "practice",
]

_SENTENCES = [
    "the trainer grows skill one step at a time.",
    "short sessions build reliable muscle memory.",
    "focus on ideas, not on button recall.",
    "mistakes guide the next best review.",
]


def _item_prompts(item_ids: list[str], curriculum: Curriculum) -> list[DrillPrompt]:
    prompts: list[DrillPrompt] = []
    for item_id in item_ids:
        item = curriculum.items[item_id]
        prompts.append(
            DrillPrompt(
                prompt=item.output,
                expected=item.output,
                item_id=item_id,
                chord=item.chord,
            )
        )
    return prompts


def _known_characters(item_ids: list[str], curriculum: Curriculum) -> set[str]:
    chars: set[str] = set()
    for item_id in item_ids:
        out = curriculum.items[item_id].output
        if len(out) == 1 and out.isalpha():
            chars.add(out.lower())
    return chars


def _words_from_known_chars(known_chars: set[str]) -> list[str]:
    usable = []
    for word in _WORDS:
        if set(word.lower()).issubset(known_chars):
            usable.append(word)
    return usable


def generate_drill(drill_type: DrillType, curriculum: Curriculum, item_ids: list[str], size: int = 20) -> list[DrillPrompt]:
    if not item_ids:
        return []

    if drill_type in {DrillType.CHARACTER, DrillType.RECOGNITION, DrillType.CHORD}:
        prompts = _item_prompts(item_ids, curriculum)
        random.shuffle(prompts)
        return prompts[:size]

    if drill_type == DrillType.WORD:
        known = _known_characters(item_ids, curriculum)
        words = _words_from_known_chars(known)
        if not words:
            words = ["at", "tea", "net"]
        random.shuffle(words)
        return [DrillPrompt(prompt=w, expected=w) for w in words[:size]]

    if drill_type == DrillType.SENTENCE:
        return [DrillPrompt(prompt=s, expected=s) for s in _SENTENCES[: min(size, len(_SENTENCES))]]

    if drill_type == DrillType.MODIFIER:
        modifiers = [item for item in item_ids if curriculum.items[item].category == ItemCategory.MODIFIER]
        return _item_prompts(modifiers[:size], curriculum)

    if drill_type == DrillType.EDITING:
        editing = [
            item for item in item_ids if curriculum.items[item].category in {ItemCategory.EDITING, ItemCategory.NAVIGATION}
        ]
        return _item_prompts(editing[:size], curriculum)

    if drill_type == DrillType.WORD_CHORD:
        words = [item for item in item_ids if curriculum.items[item].category == ItemCategory.WORD_CHORD]
        return _item_prompts(words[:size], curriculum)

    if drill_type == DrillType.NUMBER:
        numbers = [item for item in item_ids if curriculum.items[item].category == ItemCategory.NUMBER]
        return _item_prompts(numbers[:size], curriculum)

    if drill_type == DrillType.SYMBOL:
        symbols = [item for item in item_ids if curriculum.items[item].category == ItemCategory.PUNCTUATION]
        return _item_prompts(symbols[:size], curriculum)

    if drill_type == DrillType.FREE_TYPING:
        return [DrillPrompt(prompt="Type any text. Adaptive hints can reveal non-mastered chords.", expected="")]

    return _item_prompts(item_ids, curriculum)[:size]
