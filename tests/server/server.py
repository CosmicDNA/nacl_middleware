"""Core engine server definitions."""

import asyncio
from asyncio import Future
from enum import Enum, auto
from threading import Thread

from tests.server.listens import Listens


class ServerStatus(Enum):
    """Represents the status of the server.

    Attributes:
        Stopped: The server is stopped.
        Running: The server is running.
    """

    Stopped = auto()
    Running = auto()


class EngineServer:
    """A server example.

    This class represents a server that can be started and stopped. It provides methods to queue messages for broadcasting
    and register callbacks to handle received messages.

    Attributes:
        listened: An instance of the Listens class representing the listeners for the server.
        data: An instance of the Listens class representing the data received by the server.
    """

    listened: Listens = Listens()
    data: Listens = Listens()

    def __init__(self, host: str, port: str) -> None:
        """Initialize the server.

        Args:
            host: The host address for the server to run on.
            port: The port for the server to run on.
        """
        self._thread = Thread(target=self._start, name="ServerThread")
        # it's not recommended to subclass Thread because some of its methods
        # might be accidentally overloaded, for example _stop.
        # Documented in Python documentation: https://docs.python.org/3/library/threading.html#thread-objects

        self._host = host
        self._port = port

        self._loop = None
        self._callbacks = []
        self.listened.status = ServerStatus.Stopped

    def start(self) -> None:
        """Function to start the server (external thread)."""
        self._thread.start()

    def join(self) -> None:
        """Function to stop the underlying thread."""
        self._thread.join()

    def queue_message(self, data: dict) -> Future:
        """Queues a message for the server to broadcast.

        Assumes it is called from a thread different from the event loop.

        Args:
            data: The data in JSON format to broadcast.
        """

        if not self._loop:
            return

        return asyncio.run_coroutine_threadsafe(
            self._broadcast_message(data), self._loop
        )

    def queue_stop(self) -> None:
        """Queues the server to stop.

        Assumes it is called from a thread different from the event loop.
        """

        if not self._loop:
            return

        asyncio.run_coroutine_threadsafe(self._stop(), self._loop)

    def _start(self) -> None:
        """Starts the server.

        Will create a blocking event loop.
        """

        raise NotImplementedError()

    async def _stop(self) -> None:
        """Stops the server.

        Performs any clean up operations as needed.
        """

        raise NotImplementedError()

    async def _broadcast_message(self, data: dict) -> None:
        """Broadcasts a message to connected clients.

        Args:
            data: The data in JSON format to broadcast.
        """

        raise NotImplementedError()

    def register_message_callback(self, callback) -> None:
        """Registers a callback function to handle received messages.

        Args:
            callback: The callback function to register.
        """
        self.data.add_listener(callback)
