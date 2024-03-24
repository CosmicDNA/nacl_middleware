"""The middleman between Plover and the server."""

import os
from operator import itemgetter
from sorcery import dict_of

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

    def get_server_status(self) -> ServerStatus:
        """Gets the status of the server.

        Returns:
            The status of the server.
        """

        return self._server.listened.status if self._server else ServerStatus.Stopped

    def join(self) -> None:
        self._server.join()

    def add_listener(self, listener: callable) -> None:
        self._server.listened.add_listener(listener)

    def stop_listening(self) -> None:
        self._server.listened.stop_listening()
        # breakpoint() # This breakpoint disables the following warning: sys:1: RuntimeWarning: coroutine 'status_change_listener' was never awaited
        pass

    async def _on_message(self, data: dict) -> None:
        publicKey, encryptedMessage, decryptor = itemgetter('publicKey', 'encryptedMessage', 'decryptor')(data)
        decrypted = decryptor(dict_of(publicKey, encryptedMessage))
        log.debug(f'Received encrypted message {decrypted}')