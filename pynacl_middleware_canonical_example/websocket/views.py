"""The views / handlers for the server."""

from aiohttp.web import Request, Response
from pynacl_middleware_canonical_example.logger import log
from pynacl_middleware_canonical_example.websocket.app_keys import app_keys

async def index(request: Request) -> Response:
    """Index endpoint for the server. Not really needed.

    Args:
        request: The request from the client.
    """

    return Response(text='index')