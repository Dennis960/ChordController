from __future__ import annotations

import random
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Callable

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QComboBox,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QProgressBar,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from chordcontroller.trainer.common.sequence_markup import render_sequence_markup
from chordcontroller.trainer.domain import DrillType, Lesson, button_label
from chordcontroller.trainer.domain import DrillPrompt, ItemCategory
from chordcontroller.trainer.drills import generate_drill
from chordcontroller.trainer.session import PracticeSession
from chordcontroller.trainer.state import TrainerState
from chordcontroller.trainer.widgets.controller_overlay import ControllerOverlay


_DEFAULT_SENTENCES = [
    "the quick brown fox jumps over the lazy dog",
    "practice makes progress every single day",
    "small steps become reliable skills",
    "focus and rhythm build confidence",
]


@dataclass
class PracticeConfig:
    item_ids: list[str]
    mode: str
    selected_categories: list[str]
    lesson: Lesson | None


class PracticeFocusPane(QFrame):
    def __init__(self, state: TrainerState, on_progress: Callable[[], None], parent=None):
        super().__init__(parent)
        self.state = state
        self.on_progress = on_progress

        self.active_session: PracticeSession | None = None
        self.active_config: PracticeConfig | None = None
        self.prompt_shown_ts = time.time()
        self.session_streak = 0
        self.last_wrong = False
        self.best_accuracy = 0.0
        self.connection_connected = False
        self._nav_index = 0
        self._selection_controls: list[QWidget] = []
        self._selection_navigation_enabled = False
        self._category_checkboxes: list[QCheckBox] = []
        self._sentences_file = Path(__file__).parent / "data" / "practice_sentences.txt"

        self._build_ui()
        self._wire()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(12, 12, 12, 12)

        self.stacked = QStackedWidget()
        root.addWidget(self.stacked, 1)

        self.selection_view = self._build_selection_view()
        self.focus_view = self._build_focus_view()
        self.completion_view = self._build_completion_view()

        self.stacked.addWidget(self.selection_view)
        self.stacked.addWidget(self.focus_view)
        self.stacked.addWidget(self.completion_view)

        self.bottom_bar = self._build_bottom_bar()
        root.addLayout(self.bottom_bar)

        self._set_hint_message("Choose symbols and mode, then start.")
        self._set_selection_focus(0)

    def _build_selection_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lesson_label = QLabel("Practice Setup")
        self.lesson_label.setObjectName("topBarPrimary")

        self.connection_label = QLabel("Controller: disconnected")
        self.connection_label.setObjectName("topBarSecondary")

        mode_row = QHBoxLayout()
        mode_row.setSpacing(10)
        mode_label = QLabel("Practice Mode")
        mode_label.setObjectName("topBarSecondary")
        self.practice_mode_combo = QComboBox()
        self.practice_mode_combo.addItem("Random Order", "random")
        self.practice_mode_combo.addItem("Real Sentences", "sentences")
        self.practice_mode_combo.setObjectName("secondaryButton")
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.practice_mode_combo, 1)

        hint_row = QHBoxLayout()
        hint_row.setSpacing(10)
        hint_label = QLabel("Hint Visibility")
        hint_label.setObjectName("topBarSecondary")
        self.hint_mode_combo = QComboBox()
        self.hint_mode_combo.addItems(["Hint: Always", "Hint: Delayed", "Hint: After Wrong", "Hint: Hidden"])
        self.hint_mode_combo.setObjectName("secondaryButton")
        hint_row.addWidget(hint_label)
        hint_row.addWidget(self.hint_mode_combo, 1)

        categories_label = QLabel("Allowed Symbol Types")
        categories_label.setObjectName("topBarSecondary")

        categories_container = QWidget()
        categories_layout = QVBoxLayout(categories_container)
        categories_layout.setContentsMargins(8, 8, 8, 8)
        categories_layout.setSpacing(8)
        self._populate_category_checkboxes(categories_layout)

        action_row = QHBoxLayout()
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.setObjectName("secondaryButton")
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.setObjectName("secondaryButton")
        self.start_button = QPushButton("Start Practice")
        self.start_button.setObjectName("secondaryButton")
        action_row.addWidget(self.select_all_button)
        action_row.addWidget(self.clear_all_button)
        action_row.addWidget(self.start_button)

        layout.addWidget(self.lesson_label)
        layout.addWidget(self.connection_label)
        layout.addLayout(mode_row)
        layout.addLayout(hint_row)
        layout.addWidget(categories_label)
        layout.addWidget(categories_container, 1)
        layout.addLayout(action_row)

        self._selection_controls = [
            self.practice_mode_combo,
            self.hint_mode_combo,
            *self._category_checkboxes,
            self.select_all_button,
            self.clear_all_button,
            self.start_button,
        ]
        return view

    def _build_focus_view(self) -> QWidget:
        view = QWidget()
        layout = QVBoxLayout(view)
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        top = QHBoxLayout()
        top.setSpacing(12)

        left_col = QVBoxLayout()
        left_col.setSpacing(4)
        self.active_mode_label = QLabel("Mode")
        self.active_mode_label.setObjectName("topBarPrimary")
        self.active_filter_label = QLabel("Symbols")
        self.active_filter_label.setObjectName("topBarSecondary")
        left_col.addWidget(self.active_mode_label)
        left_col.addWidget(self.active_filter_label)

        center_col = QVBoxLayout()
        center_col.setSpacing(4)
        self.progress_label = QLabel("Progress")
        self.progress_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_label.setObjectName("topBarSecondary")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setFixedWidth(320)
        center_col.addWidget(self.progress_label)
        center_col.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignHCenter)

        right_col = QVBoxLayout()
        right_col.setSpacing(4)
        self.accuracy_label = QLabel("Accuracy: 0%")
        self.streak_label = QLabel("Streak: 0")
        self.remaining_label = QLabel("Remaining: 0")
        for lbl in [self.accuracy_label, self.streak_label, self.remaining_label]:
            lbl.setObjectName("topBarSecondary")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            right_col.addWidget(lbl)

        top.addLayout(left_col, 4)
        top.addLayout(center_col, 3)
        top.addLayout(right_col, 4)

        self.prompt_type_label = QLabel("Type")
        self.prompt_type_label.setObjectName("promptType")
        self.prompt_type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prompt_label = QLabel("Start")
        self.prompt_label.setObjectName("promptMain")
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt_label.setTextFormat(Qt.TextFormat.RichText)
        self.prompt_label.setWordWrap(False)
        self.prompt_label.setMinimumHeight(76)
        self.prompt_label.setMaximumHeight(76)

        self.overlay = ControllerOverlay()
        self.overlay.set_highlight_color(QColor("#3b82f6"))

        layout.addLayout(top)
        layout.addWidget(self.prompt_type_label)
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.overlay, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        return view

    def _build_completion_view(self) -> QWidget:
        completion = QWidget()
        done_layout = QVBoxLayout(completion)
        done_layout.setSpacing(10)
        done_layout.setContentsMargins(0, 0, 0, 0)

        self.done_icon = QLabel("✓")
        self.done_icon.setObjectName("completionIcon")
        self.done_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.done_summary = QLabel("")
        self.done_summary.setObjectName("completionSummary")
        self.done_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.continue_button = QPushButton("Practice Again")
        self.back_button = QPushButton("Back to Practice Setup")
        self.back_button.setObjectName("secondaryButton")

        done_layout.addStretch(1)
        done_layout.addWidget(self.done_icon)
        done_layout.addWidget(self.done_summary)
        done_layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignCenter)
        done_layout.addWidget(self.back_button, alignment=Qt.AlignmentFlag.AlignCenter)
        done_layout.addStretch(1)
        return completion

    def _build_bottom_bar(self):
        row = QHBoxLayout()
        self.bottom_message = QLabel("")
        self.bottom_message.setObjectName("bottomMessage")
        self.bottom_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(self.bottom_message)
        return row

    def _wire(self) -> None:
        self.start_button.clicked.connect(self.start_from_selection)
        self.continue_button.clicked.connect(self.practice_again)
        self.back_button.clicked.connect(self.back_to_selection)
        self.select_all_button.clicked.connect(self._select_all_symbols)
        self.clear_all_button.clicked.connect(self._clear_all_symbols)

    def _populate_category_checkboxes(self, parent_layout: QVBoxLayout) -> None:
        category_rows = [
            ("Lowercase letters", {ItemCategory.LETTER}, lambda t: len(t) == 1 and t.islower()),
            ("Uppercase letters", {ItemCategory.LETTER}, lambda t: len(t) == 1 and t.isupper()),
            ("Numbers", {ItemCategory.NUMBER}, lambda _t: True),
            ("Punctuation", {ItemCategory.PUNCTUATION}, lambda _t: True),
            ("Space / Enter", {ItemCategory.SPACE, ItemCategory.ENTER}, lambda _t: True),
            ("Editing / Navigation", {ItemCategory.EDITING, ItemCategory.NAVIGATION}, lambda _t: True),
        ]

        for label, categories, text_filter in category_rows:
            checkbox = QCheckBox(label)
            checkbox.setChecked(True)
            checkbox.setObjectName("secondaryButton")
            checkbox.setProperty("categoryKinds", categories)
            checkbox.setProperty("textFilter", text_filter)
            parent_layout.addWidget(checkbox)
            self._category_checkboxes.append(checkbox)

    def _selected_categories(self) -> list[str]:
        return [cb.text() for cb in self._category_checkboxes if cb.isChecked()]

    def _select_all_symbols(self) -> None:
        for checkbox in self._category_checkboxes:
            checkbox.setChecked(True)

    def _clear_all_symbols(self) -> None:
        for checkbox in self._category_checkboxes:
            checkbox.setChecked(False)

    def start_from_selection(self) -> None:
        lesson = self._recommended_lesson()
        selected_categories = self._selected_categories()
        if not selected_categories:
            self._set_hint_message("Select at least one symbol type to start practice.")
            return

        item_ids = self._filtered_item_ids_for_selected_categories()
        selected_item_id_set = set(item_ids)
        if not item_ids and lesson is not None:
            item_ids = [
                item_id
                for item_id in (lesson.new_item_ids + lesson.review_item_ids)
                if self.state.curriculum.items.get(item_id) is not None
                and item_id in selected_item_id_set
            ]
        if not item_ids:
            item_ids = [
                item.item_id for item in self.state.curriculum.items.values() if len(item.output) == 1 and item.chord
            ][:40]

        self.start_session(
            PracticeConfig(
                item_ids=item_ids,
                mode=str(self.practice_mode_combo.currentData()),
                selected_categories=selected_categories,
                lesson=lesson,
            )
        )

    def _filtered_item_ids_for_selected_categories(self) -> list[str]:
        selected_checkboxes = [cb for cb in self._category_checkboxes if cb.isChecked()]
        if not selected_checkboxes:
            return []

        result: list[str] = []
        for item in self.state.curriculum.items.values():
            if item.chord is None:
                continue
            for checkbox in selected_checkboxes:
                categories = checkbox.property("categoryKinds")
                text_filter = checkbox.property("textFilter")
                if item.category in categories and callable(text_filter) and text_filter(item.output):
                    result.append(item.item_id)
                    break
        return result

    def start_session(self, config: PracticeConfig) -> None:
        if config.mode == "sentences":
            prompts = self._generate_sentence_prompts(config.item_ids, size=25)
        else:
            prompts = generate_drill(DrillType.CHARACTER, self.state.curriculum, config.item_ids, size=25)
            prompts = [prompt for prompt in prompts if prompt.chord is not None]

        if not prompts:
            fallback_item_ids = [item_id for item_id in config.item_ids if item_id in self.state.curriculum.items]
            if not fallback_item_ids:
                fallback_item_ids = [item.item_id for item in self.state.curriculum.items.values() if item.chord]

            prompts = generate_drill(DrillType.CHARACTER, self.state.curriculum, fallback_item_ids, size=25)
            prompts = [prompt for prompt in prompts if prompt.chord is not None]

            if prompts:
                self._set_hint_message("This drill had no controller prompts. Switched to controller-friendly prompts.")
            else:
                self._set_hint_message("No controller-only prompts available for this drill.")
                self.active_session = None
                return
        self.active_config = config
        self.active_session = PracticeSession(prompts)
        self.session_streak = 0
        self.last_wrong = False
        self.prompt_shown_ts = time.time()
        self.stacked.setCurrentWidget(self.focus_view)

        mode_label = "Real Sentences" if config.mode == "sentences" else "Random Order"
        self.active_mode_label.setText(f"Practice: {mode_label}")
        self.active_filter_label.setText(f"Types: {', '.join(config.selected_categories[:4])}")
        self.overlay.setVisible(True)

        self._update_prompt()

    def handle_controller_click(self, clicked_chord: frozenset[str]) -> None:
        session = self.active_session
        if session is None:
            return
        prompt = session.current()
        if prompt is None or prompt.chord is None:
            return

        expected = frozenset(prompt.chord)
        correct = clicked_chord == expected
        reaction_ms = session.submit(correct=correct)

        if prompt.item_id:
            self.state.register_attempt(prompt.item_id, correct=correct, reaction_ms=reaction_ms)

        self._after_submission(
            correct=correct,
            reaction_ms=reaction_ms,
            expected=button_label(expected),
            got=" + ".join(sorted(clicked_chord)),
        )

    def tick(self) -> None:
        session = self.active_session
        if session is None:
            return
        prompt = session.current()
        if prompt is None:
            self._finish_session()
            return

        self._refresh_hint_visibility(prompt)

    def continue_next(self) -> None:
        self.practice_again()

    def practice_again(self) -> None:
        if self.active_config is None:
            self.start_from_selection()
            return
        self.start_session(self.active_config)

    def back_to_selection(self) -> None:
        self.stacked.setCurrentWidget(self.selection_view)
        self.active_session = None
        self._set_hint_message("Returned to practice setup.")

    def set_connection_state(self, connected: bool) -> None:
        self.connection_connected = connected
        self.connection_label.setText("Controller: connected" if connected else "Controller: disconnected")

    def controller_move(self, direction: str) -> None:
        if self.stacked.currentWidget() is not self.selection_view:
            return
        if not self._selection_navigation_enabled:
            return
        delta = -1 if direction == "up" else 1
        self._set_selection_focus((self._nav_index + delta) % len(self._selection_controls))

    def controller_activate(self) -> None:
        if self.stacked.currentWidget() is self.completion_view:
            self.continue_button.click()
            return

        if self.stacked.currentWidget() is self.selection_view and self._selection_navigation_enabled:
            widget = self._selection_controls[self._nav_index]
            if isinstance(widget, QComboBox):
                idx = (widget.currentIndex() + 1) % max(1, widget.count())
                widget.setCurrentIndex(idx)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(not widget.isChecked())
            elif isinstance(widget, QPushButton):
                widget.click()
            return

    def controller_back(self) -> bool:
        if self.stacked.currentWidget() is self.completion_view:
            self.back_to_selection()
            return True
        if self.stacked.currentWidget() is self.focus_view and self.active_session is not None:
            self.active_session = None
            self.stacked.setCurrentWidget(self.selection_view)
            self._set_hint_message("Practice canceled. Select a new setup.")
            return True
        return False

    def accepts_activation_navigation(self) -> bool:
        return self.stacked.currentWidget() in {self.selection_view, self.completion_view}

    def requires_face_right_for_text_submit(self) -> bool:
        return False

    def handle_face_button(self, button_name: str) -> bool:
        if self.stacked.currentWidget() is self.completion_view:
            if button_name == "face_right":
                self.practice_again()
                return True
            if button_name in {"face_down", "home", "face_up"}:
                self.back_to_selection()
                return True
        if self.stacked.currentWidget() is self.focus_view and button_name == "home":
            self.controller_back()
            return True
        return False

    def _after_submission(self, *, correct: bool, reaction_ms: int, expected: str, got: str) -> None:
        if correct:
            self.session_streak += 1
            self.last_wrong = False
            self.overlay.set_pulse_color(QColor("#16a34a"))
            self.overlay.pulse()
            if self.session_streak > 1:
                self._set_hint_message(f"Nice! {self.session_streak} correct in a row")
            else:
                self._set_hint_message("Good rhythm. Keep going.")
        else:
            self.session_streak = 0
            self.last_wrong = True
            self.overlay.set_pulse_color(QColor("#ef4444"))
            self.overlay.pulse()
            self._set_hint_message(f"Expected: {expected} | Got: {got}")

        self.prompt_shown_ts = time.time()
        self._update_prompt()
        self.on_progress()

    def _update_prompt(self) -> None:
        session = self.active_session
        if session is None:
            return
        prompt = session.current()
        if prompt is None:
            self._finish_session()
            return

        self.prompt_type_label.setText("Sentence" if self.active_config and self.active_config.mode == "sentences" else "Character")
        self.prompt_label.setText(self._sequence_markup(session))

        if prompt.chord is not None:
            self.overlay.highlight_buttons(list(prompt.chord))
        else:
            self.overlay.hide()
        self._refresh_hint_visibility(prompt)

        self._refresh_top_stats()

    def _refresh_hint_visibility(self, prompt) -> None:
        if prompt.chord is None:
            self.overlay.hide()
            return

        mode = self.hint_mode_combo.currentText()
        elapsed = time.time() - self.prompt_shown_ts

        visible = True
        if mode == "Hint: Delayed":
            visible = elapsed >= 1.0
        elif mode == "Hint: After Wrong":
            visible = self.last_wrong
        elif mode == "Hint: Hidden":
            visible = False

        self.overlay.setVisible(visible)

    def _refresh_top_stats(self) -> None:
        session = self.active_session
        if session is None:
            return

        total = len(session.prompts)
        current = min(session.index, total)
        percent = int((current / max(1, total)) * 100)
        self._animate_progress(percent)

        self.accuracy_label.setText(f"Accuracy: {session.metrics.accuracy:.0%}")
        self.streak_label.setText(f"Streak: {self.session_streak}")
        self.remaining_label.setText(f"Remaining: {max(0, total - current)}")

    def _animate_progress(self, value: int) -> None:
        anim = QPropertyAnimation(self.progress_bar, b"value", self)
        anim.setDuration(180)
        anim.setStartValue(self.progress_bar.value())
        anim.setEndValue(value)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()
        self._progress_anim = anim

    def _finish_session(self) -> None:
        session = self.active_session
        if session is None:
            return

        accuracy = session.metrics.accuracy
        avg_rt = session.metrics.avg_reaction_ms
        total_attempts = session.metrics.attempts
        personal_best = accuracy > self.best_accuracy
        if personal_best:
            self.best_accuracy = accuracy

        self.done_summary.setText(
            "\n".join(
                [
                    "Session completed",
                    f"Accuracy: {accuracy:.1%}",
                    f"Average response: {avg_rt:.0f} ms",
                    f"Exercises: {total_attempts}",
                    f"Personal best: {'yes' if personal_best else 'no'}",
                ]
            )
        )

        self.state.save()
        self.on_progress()

        self.stacked.setCurrentWidget(self.completion_view)

    def _recommended_lesson(self) -> Lesson | None:
        lesson_id = self.state.recommended_lesson_id()
        if not lesson_id:
            return None
        return next((l for l in self.state.curriculum.lessons if l.lesson_id == lesson_id), None)

    def _next_unlocked_lesson_after_current(self) -> Lesson | None:
        if self.active_config is None or self.active_config.lesson is None:
            return self._recommended_lesson()

        current_id = self.active_config.lesson.lesson_id
        lessons = self.state.curriculum.lessons
        current_index = next((i for i, l in enumerate(lessons) if l.lesson_id == current_id), -1)
        if current_index < 0:
            return self._recommended_lesson()

        for lesson in lessons[current_index + 1 :]:
            if self.state.statuses.get(lesson.lesson_id) != "mastered":
                return lesson
        return self._recommended_lesson()

    def _set_hint_message(self, message: str) -> None:
        self.bottom_message.setText(message)

    def _sequence_markup(self, session: PracticeSession) -> str:
        tokens = [prompt.expected or "?" for prompt in session.prompts]
        return render_sequence_markup(tokens, session.index, self.last_wrong)

    def _set_selection_focus(self, index: int) -> None:
        self._nav_index = index
        for i, widget in enumerate(self._selection_controls):
            focused = self._selection_navigation_enabled and i == index and self.stacked.currentWidget() is self.selection_view
            widget.setProperty("controllerFocus", focused)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def set_selection_navigation_enabled(self, enabled: bool) -> None:
        self._selection_navigation_enabled = enabled
        self._set_selection_focus(self._nav_index)

    def is_on_selection_view(self) -> bool:
        return self.stacked.currentWidget() is self.selection_view

    def _load_sentences(self) -> list[str]:
        if self._sentences_file.exists():
            lines = [line.strip() for line in self._sentences_file.read_text(encoding="utf-8").splitlines() if line.strip()]
            if lines:
                return lines
        return _DEFAULT_SENTENCES

    def _generate_sentence_prompts(self, selected_item_ids: list[str], size: int = 25) -> list[DrillPrompt]:
        selected_set = {
            self.state.curriculum.items[item_id].output
            for item_id in selected_item_ids
            if item_id in self.state.curriculum.items
        }
        item_by_output = {
            item.output: item
            for item in self.state.curriculum.items.values()
            if len(item.output) == 1 and item.chord is not None
        }
        allowed_chars = selected_set.intersection(set(item_by_output.keys()))
        if not allowed_chars:
            return []

        sentences = self._load_sentences()
        filtered = []
        for sentence in sentences:
            normalized = sentence.strip()
            if not normalized:
                continue
            chars = [ch for ch in normalized if not ch.isspace()]
            if chars and all(ch in allowed_chars for ch in chars):
                filtered.append(normalized)

        if not filtered:
            return []

        random.shuffle(filtered)
        chosen = filtered[: min(8, len(filtered))]
        prompts: list[DrillPrompt] = []
        for sentence in chosen:
            for ch in sentence:
                if ch.isspace():
                    continue
                item = item_by_output.get(ch)
                if item is None:
                    prompts = []
                    break
                prompts.append(DrillPrompt(prompt=ch, expected=ch, item_id=item.item_id, chord=item.chord))
            if len(prompts) >= size:
                break

        return prompts[:size]
