from asyncio import gather, create_task

class Listens:
    _listeners: list[callable]
    _status: any

    def __init__(self) -> None:
        self._status = None
        self._listeners = []

    def add_listener(self, callback) -> None:
        self._listeners.append(callback)

    @property
    def status(self) -> any:
        return self._status

    @status.setter
    def status(self, new_status) -> None:
        self._status = new_status
        create_task(self._notify_listeners(new_status))

    async def _notify_listeners(self, new_status) -> None:
        # Create a list of coroutines to execute concurrently
        coroutines = [listener(new_status) for listener in self._listeners]
        await gather(*coroutines)