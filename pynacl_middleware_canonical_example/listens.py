from asyncio import gather, create_task, Task, Future
from typing import Callable
# from pynacl_middleware_canonical_example.logger import log

# Listens interface
class Listens:
    _notify_listeners_task: Task
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
    _listeners: list[Callable] = []
    _notify_listeners_task: Task
    status = RawListens()

    async def _notify_listeners(self, new_status) -> Future:
        # Create a list of coroutines to execute concurrently
        coroutines = [listener(new_status) for listener in self._listeners]
        return gather(*coroutines)

    def add_listener(self, callback: Callable) -> None:
        self._listeners.append(callback)