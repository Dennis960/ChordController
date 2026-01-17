import uuid
from typing import Callable, TypeVar, Generic
from dataclasses import dataclass


CallbackParameter = TypeVar("CallbackParameter")
EventTrigger = TypeVar("EventTrigger")


@dataclass(frozen=True)
class EventListenerConfig(Generic[EventTrigger, CallbackParameter]):
    id: uuid.UUID
    event_trigger: EventTrigger | None
    listener: Callable[[CallbackParameter], None]
    tag: str | None = None
    single_shot: bool = False


class Events(Generic[EventTrigger, CallbackParameter]):
    """
    A class to manage event listeners and their configurations.

    :param EventTrigger: The type of event trigger.
    :param CallbackParameter: The type of parameter passed to the listener callbacks.
    """

    def __init__(self):
        self._event_listener_configs: dict[uuid.UUID, EventListenerConfig] = {}

    def add_event_listener(
        self,
        event_trigger: EventTrigger | None,
        listener: Callable[[CallbackParameter], None],
        tag: str | None = None,
        single_shot: bool = False,
    ) -> uuid.UUID:
        """
        Add a listener for the given event.
        Returns the listener_id which can be used to remove the listener.
        If the event_trigger is None, the listener will be called for all events.
        @param event_trigger: The event trigger for which the listener is added.
        @param listener: The listener function to be called when the event is triggered.
        @param tag: An optional tag to identify the listener.
        @param single_shot: If True, the listener will be removed after being called once.
        """
        listener_id = uuid.uuid4()
        while listener_id in self._event_listener_configs:
            listener_id = uuid.uuid4()
        self._event_listener_configs[listener_id] = EventListenerConfig(
            id=listener_id,
            event_trigger=event_trigger,
            listener=listener,
            tag=tag,
            single_shot=single_shot,
        )
        return listener_id

    def remove_event_listener(self, listener_id: uuid.UUID) -> None:
        """Remove a listener using the listener_id."""
        if listener_id in self._event_listener_configs:
            del self._event_listener_configs[listener_id]

    def get_event_listeners(
        self, event_trigger: EventTrigger
    ) -> list[EventListenerConfig]:
        """Get all listeners for the given event."""
        return [
            listener_config
            for listener_config in self._event_listener_configs.values()
            if listener_config.event_trigger == event_trigger
            or listener_config.event_trigger is None
        ]

    def call_event_listeners(
        self,
        event_trigger: EventTrigger,
        callback_parameter: CallbackParameter | None = None,
    ) -> None:
        """Call all listeners for the given event."""
        if callback_parameter is None:
            callback_parameter = self
        for listener in self.get_event_listeners(event_trigger):
            listener.listener(callback_parameter)
            if listener.single_shot:
                self.remove_event_listener(listener.id)

    def remove_all_event_listeners(self, tag: str | None = None) -> None:
        """
        Remove all event listeners.
        In case a tag is provided, only listeners with that tag will be removed.
        """
        if tag is None:
            self._event_listener_configs.clear()
        else:
            self._event_listener_configs = {
                listener_id: listener
                for listener_id, listener in self._event_listener_configs.items()
                if listener.tag != tag
            }
