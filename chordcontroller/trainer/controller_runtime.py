from __future__ import annotations

import queue
import threading
import time
from typing import Literal

import pygame

from chordcontroller.config import Config, ControllerButtonName
from chordcontroller.controller_inputs import Controller

NavDirection = Literal["up", "down"]


class ControllerRuntime:
    """Owns a controller polling loop used by the trainer UI."""

    def __init__(self) -> None:
        self.controller = Controller(Config.load_config())
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._click_queue: queue.SimpleQueue[tuple[frozenset[ControllerButtonName], float]] = queue.SimpleQueue()
        self._button_click_queue: queue.SimpleQueue[tuple[ControllerButtonName, float]] = queue.SimpleQueue()
        self._nav_queue: queue.SimpleQueue[tuple[NavDirection, float]] = queue.SimpleQueue()
        self._connection_queue: queue.SimpleQueue[tuple[bool, float]] = queue.SimpleQueue()
        self._capture_tag = "trainer_chord_capture"
        self._button_capture_tag = "trainer_button_capture"
        self._stick_capture_tag = "trainer_stick_capture"
        self._controller_state_tag = "trainer_connection_capture"
        self._last_nav_ts = 0.0

        self.controller.add_event_listener("controller_connected", self._on_controller_connected, self._controller_state_tag)
        self.controller.add_event_listener("controller_disconnected", self._on_controller_disconnected, self._controller_state_tag)

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        self.controller.multi_button_events.remove_all_event_listeners(self._capture_tag)
        for button_name in ["face_right", "face_up", "face_down", "home"]:
            self.controller.buttons[button_name].remove_all_event_listeners(self._button_capture_tag)
        self.controller.sticks["stick_left"].remove_all_event_listeners(self._stick_capture_tag)
        self.controller.remove_all_event_listeners(self._controller_state_tag)
        pygame.quit()

    def configure_chord_capture(self, allowed_buttons: set[ControllerButtonName]) -> None:
        """Enable controller multi-button click capture for the provided button set."""
        self.controller.multi_button_events.remove_all_event_listeners(self._capture_tag)
        self.controller.multi_button_events.registered_buttons = sorted(allowed_buttons)
        self.controller.multi_button_events.add_event_listener(
            "click",
            None,
            self._on_multi_button_click,
            self._capture_tag,
        )

    def configure_navigation_capture(self) -> None:
        """Enable face_right/home button clicks and left-stick navigation events."""
        for button_name in ["face_right", "face_up", "face_down", "home"]:
            self.controller.buttons[button_name].remove_all_event_listeners(self._button_capture_tag)
            self.controller.buttons[button_name].add_event_listener(
                "click",
                lambda button, button_name=button_name: self._on_button_click(button_name),
                self._button_capture_tag,
            )
        self.controller.sticks["stick_left"].remove_all_event_listeners(self._stick_capture_tag)
        self.controller.sticks["stick_left"].add_event_listener(
            "move",
            self._on_stick_move,
            self._stick_capture_tag,
        )

    def drain_clicks(self) -> list[tuple[frozenset[ControllerButtonName], float]]:
        clicks: list[tuple[frozenset[ControllerButtonName], float]] = []
        while not self._click_queue.empty():
            clicks.append(self._click_queue.get())
        return clicks

    def drain_button_clicks(self) -> list[tuple[ControllerButtonName, float]]:
        events: list[tuple[ControllerButtonName, float]] = []
        while not self._button_click_queue.empty():
            events.append(self._button_click_queue.get())
        return events

    def drain_nav_events(self) -> list[tuple[NavDirection, float]]:
        events: list[tuple[NavDirection, float]] = []
        while not self._nav_queue.empty():
            events.append(self._nav_queue.get())
        return events

    def drain_connection_events(self) -> list[tuple[bool, float]]:
        events: list[tuple[bool, float]] = []
        while not self._connection_queue.empty():
            events.append(self._connection_queue.get())
        return events

    def _on_multi_button_click(self, buttons: list[Controller.Button]) -> None:
        self._click_queue.put((frozenset(button.name for button in buttons), time.time()))

    def _on_button_click(self, button_name: ControllerButtonName) -> None:
        self._button_click_queue.put((button_name, time.time()))

    def _on_stick_move(self, stick: Controller.Stick) -> None:
        now = time.time()
        if now - self._last_nav_ts < 0.22:
            return
        if stick.y <= -0.75:
            self._nav_queue.put(("up", now))
            self._last_nav_ts = now
        elif stick.y >= 0.75:
            self._nav_queue.put(("down", now))
            self._last_nav_ts = now

    def _on_controller_connected(self, _=None):
        self._connection_queue.put((True, time.time()))

    def _on_controller_disconnected(self, _=None):
        self._connection_queue.put((False, time.time()))

    def _run(self) -> None:
        while not self._stop_event.is_set():
            for event in pygame.event.get():
                self.controller.handle_pygame_event(event)
            self.controller.update_check_controller_connection()
            time.sleep(0.01)
