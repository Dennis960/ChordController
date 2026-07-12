from __future__ import annotations

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from chordcontroller.trainer.controller_runtime import ControllerRuntime
from chordcontroller.trainer.guided_focus import GuidedCoursePane
from chordcontroller.trainer.models import TrainerSection
from chordcontroller.trainer.practice_focus import PracticeFocusPane
from chordcontroller.trainer.state import TrainerState
from chordcontroller.trainer.widgets.controller_buttons import SingleButton


def _build_panel(title: str, subtitle: str) -> tuple[QFrame, QVBoxLayout]:
    page = QFrame()
    page.setObjectName("panel")

    layout = QVBoxLayout(page)
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setSpacing(10)

    title_label = QLabel(title)
    title_label.setObjectName("title")

    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("subtitle")
    subtitle_label.setWordWrap(True)

    layout.addWidget(title_label)
    layout.addWidget(subtitle_label)
    return page, layout


class TrainerMainWindow(QMainWindow):
    def __init__(self, controller_runtime: ControllerRuntime) -> None:
        super().__init__()
        self.controller_runtime = controller_runtime
        self.state = TrainerState()
        self.controller_focus_mode = "sidebar"

        self._configure_controller_capture()

        self.setWindowTitle("Chord Trainer")
        self.resize(1240, 800)

        root = QWidget(self)
        root.setObjectName("root")
        self.setCentralWidget(root)

        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(10)

        self.global_header = self._create_global_header()
        root_layout.addLayout(self.global_header)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(16)

        self.nav_list = QListWidget()
        self.nav_list.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.nav_list.setFixedWidth(280)

        self.stack = QStackedWidget()
        body.addWidget(self.nav_list)
        body.addWidget(self.stack, 1)

        root_layout.addLayout(body, 1)

        self._setup_sections()
        self.nav_list.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav_list.currentRowChanged.connect(lambda _i: self._update_flow_hint())
        self.nav_list.setCurrentRow(0)

        self._set_sidebar_focus(True)

        self.input_timer = QTimer(self)
        self.input_timer.timeout.connect(self._poll_runtime)
        self.input_timer.start(30)

        self.refresh_views()

    def closeEvent(self, event) -> None:
        self.state.save()
        super().closeEvent(event)

    def _create_global_header(self):
        row = QHBoxLayout()
        row.setSpacing(12)

        self.connection_state_label = QLabel("Controller: disconnected")
        self.connection_state_label.setObjectName("topBarPrimary")

        flow_hint_widget = QWidget()
        flow_hint_layout = QHBoxLayout(flow_hint_widget)
        flow_hint_layout.setContentsMargins(0, 0, 0, 0)
        flow_hint_layout.setSpacing(16)

        self.joystick_hint_text = QLabel("navigate")
        self.joystick_hint_text.setObjectName("topBarSecondary")
        self.action_hint_text = QLabel("select")
        self.action_hint_text.setObjectName("topBarSecondary")
        self.home_hint_text = QLabel("back")
        self.home_hint_text.setObjectName("topBarSecondary")

        flow_hint_layout.addWidget(SingleButton("stick_left", scale=0.30))
        flow_hint_layout.addWidget(self.joystick_hint_text)
        flow_hint_layout.addWidget(SingleButton("face_right", scale=0.30))
        flow_hint_layout.addWidget(self.action_hint_text)
        flow_hint_layout.addWidget(SingleButton("home", scale=0.30))
        flow_hint_layout.addWidget(self.home_hint_text)

        self.focus_area_label = QLabel("Focus: sidebar")
        self.focus_area_label.setObjectName("topBarSecondary")
        self.focus_area_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        row.addWidget(self.connection_state_label, 3)
        row.addWidget(flow_hint_widget, 4)
        row.addWidget(self.focus_area_label, 2)
        return row

    def _configure_controller_capture(self) -> None:
        allowed_buttons = {
            button
            for item in self.state.curriculum.items.values()
            for button in item.chord
        }
        if allowed_buttons:
            self.controller_runtime.configure_chord_capture(allowed_buttons)
        self.controller_runtime.configure_navigation_capture()

    def _setup_sections(self) -> None:
        sections = [
            TrainerSection.GUIDED_COURSE,
            TrainerSection.PRACTICE,
        ]
        for section in sections:
            item = QListWidgetItem(section.value)
            item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.nav_list.addItem(item)

        self.guided_page = self._create_guided_page()
        self.practice_page = self._create_practice_page()

        self.stack.addWidget(self.guided_page)
        self.stack.addWidget(self.practice_page)

    def _create_guided_page(self) -> QWidget:
        page = QFrame()
        page.setObjectName("panel")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(10)
        self.guided_pane = GuidedCoursePane(self.state)
        layout.addWidget(self.guided_pane, 1)
        return page

    def _create_practice_page(self) -> QWidget:
        page, layout = _build_panel(
            "Practice",
            "Calm, flashcard-style flow: one prompt, one controller target, immediate feedback.",
        )
        self.practice_pane = PracticeFocusPane(self.state, on_progress=self.refresh_views)
        layout.addWidget(self.practice_pane, 1)
        return page

    def _poll_runtime(self) -> None:
        for connected, _ in self.controller_runtime.drain_connection_events():
            self._set_connection_state(connected)

        nav_events = self.controller_runtime.drain_nav_events()
        for direction, _ in nav_events:
            self._handle_nav(direction)

        button_events = self.controller_runtime.drain_button_clicks()
        for button_name, _ in button_events:
            if self.controller_focus_mode == "content" and self.stack.currentWidget() is self.guided_page:
                if self.guided_pane.handle_face_button(button_name):
                    continue
            if self.controller_focus_mode == "content" and self.stack.currentWidget() is self.practice_page:
                if self.practice_pane.handle_face_button(button_name):
                    continue
            if button_name == "face_right":
                self._handle_activate()
            elif button_name == "home":
                self._handle_back()

        clicks = self.controller_runtime.drain_clicks()
        for clicked_chord, _ in clicks:
            self.guided_pane.handle_controller_click(clicked_chord)
            self.practice_pane.handle_controller_click(clicked_chord)

        self.guided_pane.tick()
        self.practice_pane.tick()

    def _set_connection_state(self, connected: bool) -> None:
        text = "Controller: connected" if connected else "Controller: disconnected"
        self.connection_state_label.setText(text)
        self.guided_pane.set_connection_state(connected)
        self.practice_pane.set_connection_state(connected)

    def _handle_nav(self, direction: str) -> None:
        if self.controller_focus_mode == "sidebar":
            row = self.nav_list.currentRow()
            if direction == "up":
                self.nav_list.setCurrentRow(max(0, row - 1))
            else:
                self.nav_list.setCurrentRow(min(self.nav_list.count() - 1, row + 1))
            return

        if self.stack.currentWidget() is self.guided_page:
            self.guided_pane.controller_move(direction)
        elif self.stack.currentWidget() is self.practice_page:
            self.practice_pane.controller_move(direction)

    def _handle_activate(self) -> None:
        if self.controller_focus_mode == "sidebar":
            self._set_sidebar_focus(False)
            return

        if self.stack.currentWidget() is self.guided_page:
            if self.guided_pane.lesson_uses_face_right_for_text_submit():
                self.guided_pane.controller_activate()
            elif self.guided_pane.accepts_activation_navigation():
                self.guided_pane.controller_activate()
            return

        if self.stack.currentWidget() is self.practice_page:
            if self.practice_pane.requires_face_right_for_text_submit():
                self.practice_pane.controller_activate()
            elif self.practice_pane.accepts_activation_navigation():
                self.practice_pane.controller_activate()
            return

        return

    def _handle_back(self) -> None:
        if self.controller_focus_mode == "sidebar":
            if self.stack.currentWidget() is self.guided_page and self.guided_pane.is_on_selection_view():
                self.close()
            return

        if self.stack.currentWidget() is self.guided_page:
            handled = self.guided_pane.controller_back()
            if not handled:
                self._set_sidebar_focus(True)
            return
        if self.stack.currentWidget() is self.practice_page:
            handled = self.practice_pane.controller_back()
            if not handled:
                self._set_sidebar_focus(True)
            return

        self._set_sidebar_focus(True)

    def _set_sidebar_focus(self, focused: bool) -> None:
        self.controller_focus_mode = "sidebar" if focused else "content"
        self.nav_list.setProperty("controllerFocus", focused)
        self.nav_list.style().unpolish(self.nav_list)
        self.nav_list.style().polish(self.nav_list)
        if self.stack.currentWidget() is self.guided_page:
            self.guided_pane.set_selection_navigation_enabled(not focused)
        if self.stack.currentWidget() is self.practice_page:
            self.practice_pane.set_selection_navigation_enabled(not focused)
        self.focus_area_label.setText(f"Focus: {self.controller_focus_mode}")
        self._update_flow_hint()

    def _update_flow_hint(self) -> None:
        section = TrainerSection(self.nav_list.currentItem().text()) if self.nav_list.currentItem() else TrainerSection.GUIDED_COURSE
        if self.controller_focus_mode == "sidebar":
            self.joystick_hint_text.setText("select section")
            self.action_hint_text.setText("enter")
            self.home_hint_text.setText("stay")
            return
        if section == TrainerSection.GUIDED_COURSE:
            self.joystick_hint_text.setText("navigate")
            self.action_hint_text.setText("select/submit")
            self.home_hint_text.setText("back")
        elif section == TrainerSection.PRACTICE:
            self.joystick_hint_text.setText("navigate setup")
            self.action_hint_text.setText("select/submit")
            self.home_hint_text.setText("back")
        else:
            self.joystick_hint_text.setText("scroll")
            self.action_hint_text.setText("context action")
            self.home_hint_text.setText("sidebar")

    def refresh_views(self) -> None:
        self.state.refresh_statuses()
        self.guided_pane.refresh_view()
