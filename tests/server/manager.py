"""The middleman between Plover and the server."""

import os
from operator import itemgetter

from aiohttp.web import WebSocketResponse

from tests.server.config import ServerConfig
from tests.server.errors import ERROR_NO_SERVER, ERROR_SERVER_RUNNING
from tests.server.logger import log
from tests.server.server import EngineServer, ServerStatus
from tests.server.websocket.server import WebSocketServer

SERVER_CONFIG_FILE = "config.json"
CONFIG_DIR = "./"


class EngineServerManager:
    """Manages a server that exposes the Plover engine."""

    _server: EngineServer

    def __init__(self) -> None:
        self._server = None
        self._config_path: str = os.path.join(CONFIG_DIR, SERVER_CONFIG_FILE)
        if self.get_server_status() != ServerStatus.Stopped:
            raise AssertionError(ERROR_SERVER_RUNNING)

        self._config = ServerConfig(
            self._config_path
        )  # reload the configuration when the server is restarted

        self._server = WebSocketServer(
            self._config.host,
            self._config.port,
            self._config.ssl,
            self._config.remotes,
            self._config.private_key,
        )
        self._server.register_message_callback(self._on_message)

    def start(self) -> None:
        """Starts the server.

        Raises:
            AssertionError: The server failed to start.
            IOError: The server failed to start.
        """
        self._server.start()

    def stop(self) -> None:
        """Stops the server.

        Raises:
            AssertionError: The server failed to stop.
        """

        if self.get_server_status() != ServerStatus.Running:
            raise AssertionError(ERROR_NO_SERVER)

        self._server.data.stop_listening()
        self.stop_listening()
        self._server.queue_stop()

    def get_server_status(self) -> ServerStatus:
        """Gets the status of the server.

        Returns:
            The status of the server.
        """

        return self._server.listened.status if self._server else ServerStatus.Stopped

    def join(self) -> None:
        """Waits for the server to finish processing all requests and stops the server."""
        self._server.join()

    def add_listener(self, listener: callable) -> None:
        """Adds a listener to the server.

        Args:
            listener (callable): The listener function to be added.
        """
        self._server.listened.add_listener(listener)

    def stop_listening(self) -> None:
        """Stops the server from listening for status changes."""
        self._server.listened.stop_listening()

    async def _on_message(self, data: dict) -> None:
        """
        Process the received message.

        Args:
            data (dict): The received message data.

        Returns:
            None
        """
        decrypted: dict = itemgetter("decrypted")(data)
        log.info(f"Received data {decrypted}")
        socket: WebSocketResponse = itemgetter("socket")(data)
        await socket.send_json(decrypted)
