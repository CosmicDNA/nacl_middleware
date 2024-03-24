from asyncio import gather, create_task, Task
from asyncio.futures import Future

# Listens interface
class Listens:
    _listeners: list[callable]
    _notify_listeners_task: Task
    _status: any
    async def _notify_listeners(self, new_status) -> Future:
        pass
    def add_listener(self, callback: callable) -> None:
        pass
    def stop_listening(self) -> None:
        pass

class RawListens:
    def __get__(self, obj: Listens, objtype=None):
        value = obj._status
        # log.debug(f'Accessing status giving {value}')
        return value

    def __set__(self, obj: Listens, value):
        # log.debug(f'Updating status to {value}')
        obj._status = value
        if(len(obj._listeners)):
            obj._notify_listeners_task = create_task(obj._notify_listeners(value))

class Listens:
    _listeners: list[callable]
    _notify_listeners_task: Task
    status: RawListens = RawListens()

    def __init__(self) -> None:
        self._listeners = []
        self._notify_listeners_task = None

    async def _notify_listeners(self, new_status) -> Future:
        # Create a list of coroutines to execute concurrently
        coroutines = [listener(new_status) for listener in self._listeners]
        return gather(*coroutines)

    def add_listener(self, callback: callable) -> None:
        self._listeners.append(callback)

    def stop_listening(self) -> None:
        self._listeners = []