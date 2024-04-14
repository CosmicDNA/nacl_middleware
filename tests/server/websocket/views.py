"""The views / handlers for the server."""

from aiohttp.web import Request, Response


async def index(request: Request) -> Response:
    """Index endpoint for the server. Not really needed.

    Args:
        request: The request from the client.

    Returns:
        A Response object with the text "index".
    """

    return Response(text="index")
