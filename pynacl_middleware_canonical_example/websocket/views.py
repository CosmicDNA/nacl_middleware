"""The views / handlers for the server."""

from aiohttp.web import Request, Response, WebSocketResponse
from aiohttp import WSMsgType
from asyncio import CancelledError
from json import loads
from pynacl_middleware_canonical_example.logger import log
from pynacl_middleware_canonical_example.websocket.app_keys import app_keys

async def index(request: Request) -> Response:
    """Index endpoint for the server. Not really needed.

    Args:
        request: The request from the client.
    """

    return Response(text='index')

async def websocket_handler(request: Request) -> WebSocketResponse:
    """The main WebSocket handler.

    Args:
        request: The request from the client.
    """
    log.info('WebSocket connection starting')
    socket = WebSocketResponse()
    await socket.prepare(request)
    sockets = request.app[app_keys['websockets']]
    sockets.append(socket)
    log.info('WebSocket connection ready')

    try:
        async for message in socket:
            if message.type == WSMsgType.TEXT:
                if message.data == 'close':
                    await socket.close()
                    continue

                import json
                try:  # NOTE is this good API? What if message is not JSON/dict?
                    data = loads(message.data)
                except json.decoder.JSONDecodeError:
                    log.info(f'Receive unknown data: {message.data}')
                    continue

                if isinstance(data, dict):
                    callback = request.app[app_keys['on_message_callback']]
                    try:
                        callback(data)
                    except:
                        import traceback
                        traceback.print_exc()

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
