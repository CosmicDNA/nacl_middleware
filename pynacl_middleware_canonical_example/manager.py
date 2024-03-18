"""The middleman between Plover and the server."""

from typing import Optional
import os

from pynacl_middleware_canonical_example.errors import (
    ERROR_SERVER_RUNNING,
    ERROR_NO_SERVER
)
from pynacl_middleware_canonical_example.server import (
    EngineServer,
    ServerStatus
)
from pynacl_middleware_canonical_example.websocket.server import WebSocketServer
from pynacl_middleware_canonical_example.config import ServerConfig
from pynacl_middleware_canonical_example.logger import log

SERVER_CONFIG_FILE = 'config.json'
CONFIG_DIR = './'

class EngineServerManager():
    """Manages a server that exposes the Plover engine."""

    _server: EngineServer
    def __init__(self) -> None:
        self._server = None
        self._config_path: str = os.path.join(CONFIG_DIR, SERVER_CONFIG_FILE)
        if self.get_server_status() != ServerStatus.Stopped:
            raise AssertionError(ERROR_SERVER_RUNNING)

        self._config = ServerConfig(self._config_path)  # reload the configuration when the server is restarted

        self._server = WebSocketServer(self._config.host, self._config.port, self._config.ssl, self._config.remotes, self._config.private_key)
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

        self._server.queue_stop()
        log.info("Joining server thread...")
        self._server.join()
        log.info("Server thread joined.")
        self._server = None

    def get_server_status(self) -> ServerStatus:
        """Gets the status of the server.

        Returns:
            The status of the server.
        """

        return self._server.status if self._server else ServerStatus.Stopped

    def join(self) -> None:
        self._server.join()

    def add_listener(self, listener: callable) -> None:
        self._server.add_listener(listener)

    def _on_message(self, data: dict):
        self._server.queue_message(data)
