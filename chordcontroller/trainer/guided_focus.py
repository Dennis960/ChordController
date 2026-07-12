from __future__ import annotations

import time
from dataclasses import dataclass

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PySide6.QtGui import QColor, QBrush, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QProgressBar,
    QStackedWidget,
    QVBoxLayout,
)
from chordcontroller.config import ControllerButtonName

from chordcontroller.trainer.common.sequence_markup import render_sequence_markup
from chordcontroller.trainer.domain import Lesson, LessonStage, button_label
from chordcontroller.trainer.session import LessonSession
from chordcontroller.trainer.state import TrainerState
from chordcontroller.trainer.widgets.controller_buttons import SingleButton
from chordcontroller.trainer.widgets.controller_overlay import ControllerOverlay


@dataclass
class GuidedSummary:
    lesson_id: str
    passed: bool
    accuracy: float
    avg_reaction_ms: float


class GuidedCoursePane(QFrame):
    def __init__(self, state: TrainerState, parent=None):
        super().__init__(parent)
        self.state = state
        self.active_session: LessonSession | None = None
        self.prompt_shown_ts = time.time()
        self.current_streak = 0
        self.last_wrong = False
        self._nav_index = 0
        self._selection_controls: list = []
        self.connection_connected = False
        self._blind_wrong_count = 0
        self._ignore_click_until_ts = 0.0
        self._active_lesson_index: int | None = None
        self._last_finished_lesson_index: int | None = None
        self._last_lesson_passed = True
        self._mastered_arrow_icon = self._build_mastered_arrow_icon()
        self._selection_navigation_enabled = False

        root = QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(12, 12, 12, 12)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.selection_view = self._build_selection_view()
        self.lesson_view = self._build_lesson_view()
        self.completion_view = self._build_completion_view()

        self.stack.addWidget(self.selection_view)
        self.stack.addWidget(self.lesson_view)
        self.stack.addWidget(self.completion_view)

        self._refresh_selection_list()
        self._set_selection_focus(0)

    def _build_selection_view(self):
        view = QFrame()
        layout = QVBoxLayout(view)
        layout.setSpacing(10)

        self.connection_label = QLabel("Controller: disconnected")
        self.connection_label.setObjectName("topBarSecondary")

        self.lesson_list = QListWidget()
        self.lesson_list.currentRowChanged.connect(self._on_selection_changed)

        self.lesson_detail = QLabel("")
        self.lesson_detail.setWordWrap(True)

        row = QHBoxLayout()
        self.start_button = QPushButton("Start Lesson")
        self.start_button.clicked.connect(self.start_selected_lesson)
        self.start_button.setObjectName("secondaryButton")
        row.addWidget(self.start_button)

        layout.addWidget(self.connection_label)
        layout.addWidget(self.lesson_list)
        layout.addWidget(self.lesson_detail)
        layout.addLayout(row)

        self._selection_controls = [self.lesson_list, self.start_button]
        return view

    def _build_lesson_view(self):
        view = QFrame()
        layout = QVBoxLayout(view)
        layout.setSpacing(10)

        top = QHBoxLayout()
        left = QVBoxLayout()
        self.lesson_title = QLabel("Lesson")
        self.lesson_title.setObjectName("topBarPrimary")
        left.addWidget(self.lesson_title)

        center = QVBoxLayout()
        self.lesson_progress_text = QLabel("Progress")
        self.lesson_progress_text.setObjectName("topBarSecondary")
        self.lesson_progress_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lesson_progress_bar = QProgressBar()
        self.lesson_progress_bar.setRange(0, 100)
        self.lesson_progress_bar.setTextVisible(False)
        self.lesson_progress_bar.setFixedHeight(8)
        center.addWidget(self.lesson_progress_text)
        center.addWidget(self.lesson_progress_bar)

        right = QVBoxLayout()
        self.lesson_accuracy = QLabel("Accuracy: 0%")
        self.lesson_streak = QLabel("Streak: 0")
        self.lesson_remaining = QLabel("Remaining: 0")
        for lbl in [self.lesson_accuracy, self.lesson_streak, self.lesson_remaining]:
            lbl.setObjectName("topBarSecondary")
            lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            right.addWidget(lbl)

        top.addLayout(left, 4)
        top.addLayout(center, 3)
        top.addLayout(right, 2)

        self.prompt_type = QLabel("Type")
        self.prompt_type.setObjectName("promptType")
        self.prompt_type.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prompt_label = QLabel("Start")
        self.prompt_label.setObjectName("promptMain")
        self.prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.prompt_label.setWordWrap(False)
        self.prompt_label.setTextFormat(Qt.TextFormat.RichText)
        self.prompt_label.setMinimumHeight(76)
        self.prompt_label.setMaximumHeight(76)

        self.overlay = ControllerOverlay()
        self.overlay.set_highlight_color(QColor("#3b82f6"))

        self.bottom_message = QLabel("")
        self.bottom_message.setObjectName("bottomMessage")
        self.bottom_message.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(top)
        layout.addWidget(self.prompt_type)
        layout.addWidget(self.prompt_label)
        layout.addWidget(self.overlay, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.bottom_message)
        return view

    def _build_completion_view(self):
        view = QFrame()
        layout = QVBoxLayout(view)
        layout.setSpacing(10)

        icon = QLabel("✓")
        icon.setObjectName("completionIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.completion_summary = QLabel("")
        self.completion_summary.setObjectName("completionSummary")
        self.completion_summary.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.continue_button = QPushButton("Continue")
        self.continue_button.clicked.connect(self.continue_next_lesson)
        self.practice_again_button = QPushButton("Practice Again")
        self.practice_again_button.setObjectName("secondaryButton")
        self.practice_again_button.clicked.connect(self.practice_again)
        self.overview_button = QPushButton("Back to Lesson Overview")
        self.overview_button.setObjectName("secondaryButton")
        self.overview_button.clicked.connect(self.back_to_overview)

        self.continue_row = self._build_completion_action_row(self.continue_button, "face_right")
        self.practice_row = self._build_completion_action_row(self.practice_again_button, "face_up")
        self.overview_row = self._build_completion_action_row(self.overview_button, "face_down")

        layout.addStretch(1)
        layout.addWidget(icon)
        layout.addWidget(self.completion_summary)
        layout.addWidget(self.continue_row, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.practice_row, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.overview_row, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)

        return view

    def _build_mastered_arrow_icon(self) -> QIcon:
        pixmap = QPixmap(14, 14)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen = QPen(QColor("#22c55e"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(2, 11, 11, 2)
        painter.drawLine(7, 2, 11, 2)
        painter.drawLine(11, 2, 11, 6)
        painter.end()
        return QIcon(pixmap)

    def _build_completion_action_row(self, button: QPushButton, button_name: ControllerButtonName) -> QFrame:
        row = QFrame()
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        layout.addWidget(button)
        layout.addWidget(SingleButton(button_name, scale=0.42))
        return row

    def set_connection_state(self, connected: bool) -> None:
        self.connection_connected = connected
        text = "Controller: connected" if connected else "Controller: disconnected"
        self.connection_label.setText(text)

    def _refresh_selection_list(self) -> None:
        self.state.refresh_statuses()
        self.lesson_list.clear()
        for lesson in self.state.curriculum.lessons:
            status = self.state.statuses.get(lesson.lesson_id, "not_recommended")
            row = QListWidgetItem(lesson.title)
            if status == "mastered":
                row.setForeground(QBrush(QColor("#f3c24f")))
                row.setBackground(QBrush(QColor("#2f2411")))
                row.setIcon(self._mastered_arrow_icon)
            elif status == "recommended":
                row.setForeground(QBrush(QColor("#ffe680")))
                row.setBackground(QBrush(QColor("#423819")))
            else:
                row.setForeground(QBrush(QColor("#a2afba")))
                row.setBackground(QBrush(QColor("#24303a")))
            self.lesson_list.addItem(row)
        if self.lesson_list.count() > 0 and self.lesson_list.currentRow() < 0:
            self.lesson_list.setCurrentRow(0)

    def refresh_view(self) -> None:
        self._refresh_selection_list()

    def _on_selection_changed(self, index: int) -> None:
        lesson = self._selected_lesson(index)
        if lesson is None:
            self.lesson_detail.setText("No lesson selected.")
            return
        status = self.state.statuses.get(lesson.lesson_id, "not_recommended")
        self.lesson_detail.setText(
            "\n".join(
                [
                    lesson.title,
                    f"Status: {status}",
                    f"New chords: {len(lesson.new_item_ids)}",
                ]
            )
        )

    def _selected_lesson(self, index: int | None = None) -> Lesson | None:
        row = self.lesson_list.currentRow() if index is None else index
        if row < 0 or row >= len(self.state.curriculum.lessons):
            return None
        return self.state.curriculum.lessons[row]

    def start_selected_lesson(self) -> None:
        lesson = self._selected_lesson()
        if lesson is None:
            return

        self._start_lesson(lesson, self.lesson_list.currentRow(), triggered_by_controller=False)

    def _start_lesson(self, lesson: Lesson, lesson_index: int, *, triggered_by_controller: bool) -> None:
        self._active_lesson_index = lesson_index

        self.active_session = LessonSession(lesson, self.state.curriculum)
        self.current_streak = 0
        self.last_wrong = False
        self._blind_wrong_count = 0
        if triggered_by_controller:
            # Prevent the same face button press that starts the lesson from counting as a wrong chord.
            self._ignore_click_until_ts = time.time() + 0.18
        else:
            self._ignore_click_until_ts = 0.0
        self.prompt_shown_ts = time.time()
        self.lesson_title.setText(lesson.title)
        self.stack.setCurrentWidget(self.lesson_view)
        self._update_lesson_prompt()

    def tick(self) -> None:
        if self.active_session is None:
            return
        self._update_lesson_prompt()

    def handle_controller_click(self, clicked_chord: frozenset[str]) -> None:
        session = self.active_session
        if session is None:
            return
        if time.time() < self._ignore_click_until_ts:
            session.restart_wait_timer()
            return

        prompt = session.current_prompt()
        if prompt is None or prompt.input_mode != "controller" or prompt.expected_chord is None:
            return

        expected = frozenset(prompt.expected_chord)
        correct = clicked_chord == expected
        reaction_ms = session.await_reaction_ms()
        session.accept_attempt(correct=correct, reaction_ms=reaction_ms)
        if prompt.item_id:
            self.state.register_attempt(prompt.item_id, correct=correct, reaction_ms=reaction_ms)

        self._after_submit(correct, reaction_ms, button_label(expected), " + ".join(sorted(clicked_chord)))

    def _after_submit(self, correct: bool, reaction_ms: int, expected: str, got: str) -> None:
        session = self.active_session
        blind_mode = session is not None and session.stage in {
            LessonStage.RECALL,
            LessonStage.TIMED_ROUND,
            LessonStage.REVIEW,
        }
        if correct:
            self.current_streak += 1
            self.last_wrong = False
            self._blind_wrong_count = 0
            self.overlay.set_pulse_color(QColor("#16a34a"))
            self.overlay.pulse()
            self._set_bottom_message(
                f"Nice! {self.current_streak} correct in a row" if self.current_streak > 1 else "Good rhythm."
            )
        else:
            self.current_streak = 0
            self.last_wrong = True
            if blind_mode:
                self._blind_wrong_count += 1
            self.overlay.set_pulse_color(QColor("#ef4444"))
            self.overlay.pulse()
            self._set_bottom_message(f"Expected: {expected} | Got: {got}")
        self.prompt_shown_ts = time.time()
        self._update_lesson_prompt()

    def _update_lesson_prompt(self) -> None:
        session = self.active_session
        if session is None:
            return

        prompt = session.current_prompt()
        if prompt is None:
            self._finalize_lesson()
            return

        self.prompt_label.setText(self._sequence_markup(session))

        if prompt.expected_chord is not None:
            blind_stage = session.stage in {
                LessonStage.RECALL,
                LessonStage.TIMED_ROUND,
                LessonStage.REVIEW,
            }
            if blind_stage:
                # Blind mode: show chord only after 3 consecutive wrong attempts.
                if self._blind_wrong_count >= 3:
                    self.overlay.highlight_buttons(list(prompt.expected_chord))
                else:
                    self.overlay.highlight_buttons([])
            else:
                self.overlay.highlight_buttons(list(prompt.expected_chord))
            self.overlay.setVisible(True)
        else:
            self.overlay.hide()

        self._refresh_top_stats()

    def _sequence_markup(self, session: LessonSession) -> str:
        prompts = session._prompts[session.stage]
        tokens = [prompt.expected_text or "?" for prompt in prompts]
        return render_sequence_markup(tokens, session._prompt_index, self.last_wrong)

    def _refresh_top_stats(self) -> None:
        session = self.active_session
        if session is None:
            return

        prompt = session.current_prompt()
        stage = session.stage_name
        progress_text = f"{stage} • {session.stage_progress}"
        self.lesson_progress_text.setText(progress_text)

        total_approx = max(1, len(session._prompts[session.stage]))
        current = min(session._prompt_index, total_approx)
        percent = int((current / max(1, total_approx)) * 100)

        anim = QPropertyAnimation(self.lesson_progress_bar, b"value", self)
        anim.setDuration(160)
        anim.setStartValue(self.lesson_progress_bar.value())
        anim.setEndValue(percent)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        anim.start()
        self._progress_anim = anim

        self.lesson_accuracy.setText(f"Accuracy: {session.metrics.accuracy:.0%}")
        self.lesson_streak.setText(f"Streak: {self.current_streak}")

        if prompt is None:
            remaining = 0
        else:
            remaining = max(0, total_approx - session._prompt_index)
        self.lesson_remaining.setText(f"Remaining: {remaining}")

    def _finalize_lesson(self) -> None:
        session = self.active_session
        if session is None:
            return

        lesson = session.lesson
        accuracy = session.metrics.accuracy
        avg_rt = session.metrics.avg_reaction_ms
        req = lesson.requirements

        passed = accuracy >= req.min_accuracy and (avg_rt <= req.max_avg_reaction_ms if avg_rt > 0 else False)
        self._last_lesson_passed = passed
        if passed:
            self.state.mark_lesson_completed(lesson.lesson_id, accuracy, avg_rt)
        else:
            self.state.save()

        self.completion_summary.setText(
            "\n".join(
                [
                    f"{lesson.title} {'completed' if passed else 'attempt finished'}",
                    f"Accuracy: {accuracy:.1%}",
                    f"Average response: {avg_rt:.0f} ms",
                    f"New chords: {len(lesson.new_item_ids)}",
                ]
            )
        )

        self.active_session = None
        self._last_finished_lesson_index = self._active_lesson_index
        self.continue_button.setEnabled(passed)
        self.continue_row.setVisible(passed)
        self.stack.setCurrentWidget(self.completion_view)
        self._refresh_selection_list()

    def continue_next_lesson(self, *, triggered_by_controller: bool = False) -> None:
        lessons = self.state.curriculum.lessons
        if self._last_finished_lesson_index is None:
            self.stack.setCurrentWidget(self.selection_view)
            return
        next_index = self._last_finished_lesson_index + 1
        if next_index >= len(lessons):
            self.stack.setCurrentWidget(self.selection_view)
            return
        lesson = lessons[next_index]
        self.lesson_list.setCurrentRow(next_index)
        self._start_lesson(lesson, next_index, triggered_by_controller=triggered_by_controller)

    def practice_again(self, *, triggered_by_controller: bool = False) -> None:
        if self._last_finished_lesson_index is None:
            self.start_selected_lesson()
            return
        lessons = self.state.curriculum.lessons
        if 0 <= self._last_finished_lesson_index < len(lessons):
            self.lesson_list.setCurrentRow(self._last_finished_lesson_index)
            self._start_lesson(
                lessons[self._last_finished_lesson_index],
                self._last_finished_lesson_index,
                triggered_by_controller=triggered_by_controller,
            )

    def back_to_overview(self) -> None:
        self.stack.setCurrentWidget(self.selection_view)
        self._set_selection_focus(self._nav_index)

    def controller_move(self, direction: str) -> None:
        if self.stack.currentWidget() is self.selection_view:
            self._set_active_selection_widget(None)
            if self._selection_controls[self._nav_index] is self.lesson_list:
                row = self.lesson_list.currentRow()
                if direction == "up":
                    if row > 0:
                        self.lesson_list.setCurrentRow(row - 1)
                    else:
                        self._set_selection_focus(len(self._selection_controls) - 1)
                else:
                    if row < self.lesson_list.count() - 1:
                        self.lesson_list.setCurrentRow(row + 1)
                    else:
                        self._set_selection_focus(1)
            else:
                delta = -1 if direction == "up" else 1
                self._set_selection_focus((self._nav_index + delta) % len(self._selection_controls))

    def controller_activate(self) -> None:
        if self.stack.currentWidget() is self.selection_view:
            widget = self._selection_controls[self._nav_index]
            self._set_active_selection_widget(widget)
            if widget is self.lesson_list:
                lesson = self._selected_lesson()
                if lesson is not None:
                    self._start_lesson(lesson, self.lesson_list.currentRow(), triggered_by_controller=True)
            elif isinstance(widget, QPushButton):
                widget.click()
            return

        if self.stack.currentWidget() is self.lesson_view:
            # Guided lessons are controller-only; activation is handled by chord input.
            return

        if self.stack.currentWidget() is self.completion_view:
            if self._last_lesson_passed:
                self.continue_next_lesson(triggered_by_controller=True)

    def handle_face_button(self, button_name: ControllerButtonName) -> bool:
        if self.stack.currentWidget() is self.completion_view:
            if button_name == "face_right":
                if self._last_lesson_passed:
                    self.continue_next_lesson(triggered_by_controller=True)
                return True
            if button_name == "face_up":
                self.practice_again(triggered_by_controller=True)
                return True
            if button_name in {"face_down", "home"}:
                self.back_to_overview()
                return True
        return False

    def controller_back(self) -> bool:
        if self.stack.currentWidget() is self.lesson_view:
            self.active_session = None
            self.stack.setCurrentWidget(self.selection_view)
            self._set_bottom_message("Returned to lesson selection")
            return True
        if self.stack.currentWidget() is self.completion_view:
            self.stack.setCurrentWidget(self.selection_view)
            return True
        return False

    def accepts_activation_navigation(self) -> bool:
        return self.stack.currentWidget() in {self.selection_view, self.completion_view}

    def lesson_uses_face_right_for_text_submit(self) -> bool:
        return False

    def is_on_selection_view(self) -> bool:
        return self.stack.currentWidget() is self.selection_view

    def _set_selection_focus(self, index: int) -> None:
        self._nav_index = index
        for i, widget in enumerate(self._selection_controls):
            focused = self._selection_navigation_enabled and i == index and self.stack.currentWidget() is self.selection_view
            widget.setProperty("controllerFocus", focused)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _set_active_selection_widget(self, active_widget: object | None) -> None:
        for widget in self._selection_controls:
            is_active = active_widget is widget
            widget.setProperty("controllerActive", is_active)
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def set_selection_navigation_enabled(self, enabled: bool) -> None:
        self._selection_navigation_enabled = enabled
        if not enabled:
            self._set_active_selection_widget(None)
        self._set_selection_focus(self._nav_index)

    def _set_bottom_message(self, message: str) -> None:
        self.bottom_message.setText(message)
