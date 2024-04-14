from re import fullmatch
from typing import Tuple

from aiohttp.web import Request


def is_exclude(request: Request, exclude: Tuple) -> bool:
    """
    Check if the request path matches any pattern in the exclude list.

    Args:
        request (Request): The request object.
        exclude (Tuple): A tuple of patterns to exclude.

    Returns:
        bool: True if the request path matches any pattern in the exclude list, False otherwise.
    """
    for pattern in exclude:
        if fullmatch(pattern, request.path):
            return True
    return False
