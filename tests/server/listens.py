from asyncio import Task, create_task, gather
from asyncio.futures import Future

from tests.server.logger import log


# Listens interface
class Listens:
    _listeners: list[callable]
    _status: any
    _count: int

    async def _notify_listeners(self, new_status) -> Future:
        pass

    def add_listener(self, callback: callable) -> None:
        pass

    def stop_listening(self) -> None:
        pass


class RawListens:
    """
    A descriptor class for accessing and updating the status of a Listens object.

    This class provides the __get__ and __set__ methods to get and set the status
    of a Listens object. When the status is updated, it notifies the listeners
    asynchronously.

    Attributes:
        None

    Methods:
        __get__(self, obj: Listens, objtype=None) -> Any:
            Get the status of the Listens object.

        __set__(self, obj: Listens, value) -> None:
            Set the status of the Listens object and notify the listeners.
    """

    def __get__(self, obj: Listens, objtype=None):
        value = obj._status
        # log.debug(f'Accessing status giving {value}')
        return value

    def __set__(self, obj: Listens, value):
        # log.debug(f'Updating status to {value}')
        obj._status = value
        if len(obj._listeners):
            name = f"NL-{obj._count}"
            log.debug(f"Creating {name} with value {value}...")
            create_task(obj._notify_listeners(value), name=name)
            obj._count = obj._count + 1


class Listens:
    """
    A class that manages listeners and notifies them of changes in status.

    Attributes:
        _listeners (list[callable]): A list of callback functions to be executed when a change in status occurs.
        _notify_listeners_task (Task): An asyncio task that executes the coroutines of the listeners concurrently.
        status (RawListens): An instance of the RawListens class representing the current status.
        _count (int): A counter to keep track of the number of listeners.

    Methods:
        __init__(): Initializes the Listens object.
        _notify_listeners(new_status): Notifies all listeners of a change in status.
        add_listener(callback): Adds a new listener to the list of listeners.
        stop_listening(): Removes all listeners from the list.
    """

    _listeners: list[callable]
    _notify_listeners_task: Task
    status: RawListens = RawListens()
    _count: int = 0

    def __init__(self) -> None:
        """
        Initializes a new instance of the Listens class.
        """
        self._listeners = []
        self._notify_listeners_task = None

    async def _notify_listeners(self, new_status) -> Future:
        """
        Notifies all listeners of a change in status.

        Args:
            new_status: The new status to be passed to the listeners.

        Returns:
            A Future object representing the completion of the notification process.
        """
        # Create a list of coroutines to execute concurrently
        coroutines = [listener(new_status) for listener in self._listeners]
        return gather(*coroutines)

    def add_listener(self, callback: callable) -> None:
        """
        Adds a new listener to the list of listeners.

        Args:
            callback: The callback function to be added as a listener.
        """
        self._listeners.append(callback)

    def stop_listening(self) -> None:
        """
        Removes all listeners from the list.
        """
        self._listeners = []
