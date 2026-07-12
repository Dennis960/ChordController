from __future__ import annotations

import time
from dataclasses import dataclass, field

from chordcontroller.config import ControllerButtonName

from chordcontroller.trainer.domain import Curriculum, DrillPrompt, Lesson, LessonStage, button_label
from chordcontroller.trainer.lesson_flow import lesson_stage_prompts


@dataclass(slots=True)
class ActivePrompt:
    stage: LessonStage
    prompt_text: str
    expected_text: str | None = None
    expected_chord: tuple[ControllerButtonName, ...] | None = None
    item_id: str | None = None
    input_mode: str = "controller"


@dataclass(slots=True)
class SessionMetrics:
    attempts: int = 0
    correct: int = 0
    reaction_times_ms: list[int] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        if self.attempts == 0:
            return 0.0
        return self.correct / self.attempts

    @property
    def avg_reaction_ms(self) -> float:
        if not self.reaction_times_ms:
            return 0.0
        return sum(self.reaction_times_ms) / len(self.reaction_times_ms)


class LessonSession:
    _STAGE_ORDER = [
        LessonStage.INTRODUCE,
        LessonStage.MIXED_PRACTICE,
        LessonStage.RECOGNITION,
        LessonStage.RECALL,
        LessonStage.MINI_WORDS,
        LessonStage.TIMED_ROUND,
        LessonStage.REVIEW,
    ]

    def __init__(self, lesson: Lesson, curriculum: Curriculum) -> None:
        self.lesson = lesson
        self.curriculum = curriculum
        self.metrics = SessionMetrics()
        self.started_at_ts = time.time()
        self._stage_index = 0
        self._prompt_index = 0
        self._await_started_ts = time.time()
        self._timed_round_started_ts: float | None = None
        self._timed_round_limit_s = 60
        self._prompts = self._build_prompts()

    @property
    def stage(self) -> LessonStage:
        return self._STAGE_ORDER[self._stage_index]

    @property
    def stage_name(self) -> str:
        return self.stage.value.replace("_", " ").title()

    @property
    def stage_progress(self) -> str:
        current = self._prompt_index + 1
        total = max(1, len(self._prompts[self.stage]))
        return f"{current}/{total}"

    @property
    def is_finished(self) -> bool:
        return self._stage_index >= len(self._STAGE_ORDER)

    def current_prompt(self) -> ActivePrompt | None:
        if self.is_finished:
            return None

        prompts = self._prompts[self.stage]
        if not prompts:
            self._advance_stage()
            return self.current_prompt()

        if self.stage == LessonStage.TIMED_ROUND and self._timed_round_started_ts is None:
            self._timed_round_started_ts = time.time()

        if self.stage == LessonStage.TIMED_ROUND and self._timed_round_started_ts is not None:
            if time.time() - self._timed_round_started_ts >= self._timed_round_limit_s:
                self._advance_stage()
                return self.current_prompt()

        if self._prompt_index >= len(prompts):
            self._advance_stage()
            return self.current_prompt()

        return prompts[self._prompt_index]

    def accept_attempt(self, *, correct: bool, reaction_ms: int) -> None:
        prompt = self.current_prompt()
        if prompt is None:
            return

        self.metrics.attempts += 1
        self.metrics.reaction_times_ms.append(reaction_ms)
        if correct:
            self.metrics.correct += 1
            self._prompt_index += 1
        else:
            # Keep the same prompt active until answered correctly.
            pass

        self._await_started_ts = time.time()

    def await_reaction_ms(self) -> int:
        return max(1, int((time.time() - self._await_started_ts) * 1000.0))

    def restart_wait_timer(self) -> None:
        self._await_started_ts = time.time()

    def timed_round_remaining_s(self) -> int:
        if self.stage != LessonStage.TIMED_ROUND or self._timed_round_started_ts is None:
            return 0
        return max(0, int(self._timed_round_limit_s - (time.time() - self._timed_round_started_ts)))

    def _advance_stage(self) -> None:
        self._stage_index += 1
        self._prompt_index = 0
        self._await_started_ts = time.time()

    def _build_prompts(self) -> dict[LessonStage, list[ActivePrompt]]:
        stage_drills = lesson_stage_prompts(self.lesson, self.curriculum)
        result: dict[LessonStage, list[ActivePrompt]] = {stage: [] for stage in self._STAGE_ORDER}

        # Introduce stage: each new chord practiced once without timer pressure.
        for item_id in self.lesson.new_item_ids:
            item = self.curriculum.items[item_id]
            result[LessonStage.INTRODUCE].append(
                ActivePrompt(
                    stage=LessonStage.INTRODUCE,
                    prompt_text=f"Press chord for '{item.output}' ({button_label(item.chord)})",
                    expected_text=item.output,
                    expected_chord=tuple(item.chord),
                    item_id=item_id,
                    input_mode="controller",
                )
            )

        for prompt in stage_drills[LessonStage.RECOGNITION]:
            result[LessonStage.RECOGNITION].append(
                ActivePrompt(
                    stage=LessonStage.RECOGNITION,
                    prompt_text=f"Character: {prompt.expected}",
                    expected_text=prompt.expected,
                    expected_chord=tuple(prompt.chord) if prompt.chord else None,
                    item_id=prompt.item_id,
                    input_mode="controller",
                )
            )

        for prompt in stage_drills[LessonStage.RECALL]:
            if not prompt.item_id or not prompt.chord:
                continue
            result[LessonStage.RECALL].append(
                ActivePrompt(
                    stage=LessonStage.RECALL,
                    prompt_text=f"Chord: {button_label(prompt.chord)}",
                    expected_text=self.curriculum.items[prompt.item_id].output,
                    expected_chord=tuple(prompt.chord),
                    item_id=prompt.item_id,
                    input_mode="controller",
                )
            )

        for stage in [LessonStage.MIXED_PRACTICE, LessonStage.TIMED_ROUND, LessonStage.REVIEW]:
            for prompt in stage_drills[stage]:
                if not prompt.chord:
                    continue
                result[stage].append(
                    ActivePrompt(
                        stage=stage,
                        prompt_text=f"Character: {prompt.expected}",
                        expected_text=prompt.expected,
                        expected_chord=tuple(prompt.chord),
                        item_id=prompt.item_id,
                        input_mode="controller",
                    )
                )

        # Mini-words are intentionally skipped in controller-only mode.

        return result


class PracticeSession:
    def __init__(self, prompts: list[DrillPrompt]) -> None:
        self.prompts = prompts
        self.index = 0
        self.metrics = SessionMetrics()
        self._await_started = time.time()

    def current(self) -> DrillPrompt | None:
        if self.index >= len(self.prompts):
            return None
        return self.prompts[self.index]

    def submit(self, correct: bool) -> int:
        reaction_ms = max(1, int((time.time() - self._await_started) * 1000.0))
        self.metrics.attempts += 1
        self.metrics.reaction_times_ms.append(reaction_ms)
        if correct:
            self.metrics.correct += 1
            self.index += 1
        else:
            self.prompts.insert(min(self.index + 1, len(self.prompts)), self.prompts[self.index])
        self._await_started = time.time()
        return reaction_ms

    @property
    def finished(self) -> bool:
        return self.index >= len(self.prompts)
