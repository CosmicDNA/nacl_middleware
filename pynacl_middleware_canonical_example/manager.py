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

    def __init__(self):
        self._server: Optional[EngineServer] = None
        self._config_path: str = os.path.join(CONFIG_DIR, SERVER_CONFIG_FILE)

    def start(self):
        """Starts the server.

        Raises:
            AssertionError: The server failed to start.
            IOError: The server failed to start.
        """

        if self.get_server_status() != ServerStatus.Stopped:
            raise AssertionError(ERROR_SERVER_RUNNING)

        self._config = ServerConfig(self._config_path)  # reload the configuration when the server is restarted

        self._server = WebSocketServer(self._config.host, self._config.port, self._config.ssl, self._config.remotes, self._config.private_key)
        self._server.register_message_callback(self._on_message)
        self._server.start()

    def stop(self):
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

    def _on_message(self, data: dict):
        self._server.queue_message(data)
