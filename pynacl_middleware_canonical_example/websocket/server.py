"""WebSocket server definition."""

from asyncio import Event, set_event_loop, new_event_loop

from aiohttp.web import Request, Response, WebSocketResponse, Application, AppRunner, TCPSite, json_response
from aiohttp import WSCloseCode, WSMsgType
from asyncio import CancelledError
from json import loads, decoder
from aiohttp_middlewares import cors_middleware
from aiohttp_middlewares.cors import DEFAULT_ALLOW_HEADERS, DEFAULT_ALLOW_METHODS
from pynacl_middleware_canonical_example.websocket.nacl_middleware import nacl_middleware, Nacl
from pynacl_middleware_canonical_example.websocket.views import index
from pynacl_middleware_canonical_example.logger import log
from nacl.public import PrivateKey
from pynacl_middleware_canonical_example.websocket.app_keys import app_keys

from pynacl_middleware_canonical_example.errors import (
    ERROR_SERVER_RUNNING,
    ERROR_NO_SERVER
)
from pynacl_middleware_canonical_example.server import (
    EngineServer,
    ServerStatus
)

from typing import TypedDict

class SSLConfig(TypedDict):
    cert_path: str
    key_path: str

class WebSocketServer(EngineServer):
    """A server based on WebSockets."""

    _app: Application
    _ssl: SSLConfig
    _remotes: list[object]
    _private_key: PrivateKey
    _runner: AppRunner
    _site: TCPSite

    def __init__(self, host: str, port: str, ssl: dict, remotes: list[object], private_key: PrivateKey) -> None:
        """Initialize the server.

        Args:
            host: The host address for the server to run on.
            port: The port for the server to run on.
        """

        super().__init__(host, port)
        self._app = None
        self._ssl = ssl
        self._private_key = private_key
        self._remotes = remotes

    async def get_public_key(self, request: Request) -> Response:
        """Route to get the public key of the web server.

        Args:
            request: The request from the client.
        """
        log.info(f'Request to get the server public key received.')
        log.info('Decoding public key...')
        decoded_public_key = Nacl(self._private_key).decodedPublicKey()
        log.info(f'Public key {decoded_public_key} was decoded!')
        return json_response(decoded_public_key)

    async def protocol(self, request: Request) -> Response:
        """Route to get the protocol of the web server.

        Args:
            request: The request from the client.
        """
        if self._ssl:
            protocol = "wss://"
        else:
            protocol = "ws://"

        return json_response(protocol)

    async def websocket_handler(self, request: Request) -> WebSocketResponse:
        """The main WebSocket handler.

        Args:
            request: The request from the client.
        """
        log.info('WebSocket connection starting')
        socket = WebSocketResponse()
        await socket.prepare(request)
        sockets: list[WebSocketResponse] = request.app[app_keys['websockets']]
        sockets.append(socket)
        log.info('WebSocket connection ready')

        try:
            async for message in socket:
                if message.type == WSMsgType.TEXT:
                    if message.data == 'close':
                        await socket.close()
                        continue

                    try:  # NOTE is this good API? What if message is not JSON/dict?
                        self.data.status = {**loads(message.data), 'decryptor': request['decryptor']}
                    except decoder.JSONDecodeError:
                        log.info(f'Receive unknown data: {message.data}')
                        continue

                elif message.type == WSMsgType.ERROR:
                    log.info('WebSocket connection closed with exception '
                        f'{socket.exception()}')
        except CancelledError:  # https://github.com/aio-libs/aiohttp/issues/1768
            pass
        finally:
            await socket.close()


        sockets.remove(socket)
        log.info('WebSocket connection closed')
        return socket

    def _start(self) -> None:
        """Starts the server.

        Will create a blocking event loop.
        """
        if self.listened.status == ServerStatus.Running:
            raise AssertionError(ERROR_SERVER_RUNNING)

        loop = new_event_loop()
        set_event_loop(loop)
        self._loop = loop

        self._app = Application(middlewares=[
			cors_middleware(
				origins=self._remotes,
				allow_methods=DEFAULT_ALLOW_METHODS,
				allow_headers=DEFAULT_ALLOW_HEADERS
			),
			nacl_middleware(
                self._private_key,
                exclude_routes=('/getpublickey', ),
                log=log
            )
		])

        async def on_shutdown(app):
            sockets : list[WebSocketResponse] = app[app_keys['websockets']]
            for ws in set(sockets):
                await ws.close()
        self._app.on_shutdown.append(on_shutdown)

        self._app[app_keys['websockets']] = []

        self._app.router.add_get('/', index)
        self._app.router.add_get('/protocol', self.protocol)
        self._app.router.add_get('/websocket', self.websocket_handler)
        self._app.router.add_get('/getpublickey', self.get_public_key)

        self._app.on_shutdown.append(self._on_server_shutdown)

        self._stop_event = Event()

        async def run_async() -> None:
            self._runner = runner = AppRunner(self._app)
            await runner.setup()
            self._site = site = TCPSite(runner, host=self._host, port=self._port)
            await site.start()
            self.listened.status = ServerStatus.Running
            await self._stop_event.wait()
            await runner.cleanup()
            self._app = None
            self._loop = None
            self.listened.status = ServerStatus.Stopped

        loop.run_until_complete(run_async())

    async def _stop(self) -> None:
        """Stops the server.

        Performs any clean up operations as needed.
        """

        if self.listened.status != ServerStatus.Running:
            raise AssertionError(ERROR_NO_SERVER)

        self._stop_event.set()

    async def _on_server_shutdown(self, app: Application) -> None:
        """Handles pre-shutdown behavior for the server.

        Args:
            app: The web application shutting down.
        """

        sockets: list[WebSocketResponse] = app.get(app_keys['websockets'], [])
        for socket in sockets:
            await socket.close(code=WSCloseCode.GOING_AWAY,
                               message='Server shutdown')

    async def _broadcast_message(self, data: dict) -> None:
        """Broadcasts a message to connected clients.

        Args:
            data: The data to broadcast. Internally it's sent with WebSocketResponse.send_json.
        """

        if not self._app:
            return

        sockets: list[WebSocketResponse] = self._app.get(app_keys['websockets'], [])
        for socket in sockets:
            try:
                await socket.send_json(data)
            except:
                print(f'Failed to update websocket {socket} {id(socket)} {socket.closed} (this should not happen)', flush=True)
        sockets[:]=[socket for socket in sockets if not socket.closed] #this should not change sockets normally
