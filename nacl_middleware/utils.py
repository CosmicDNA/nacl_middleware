from re import fullmatch
from typing import Tuple

from aiohttp.web import Request


def is_exclude(request: Request, exclude: Tuple) -> bool:
    for pattern in exclude:
        if fullmatch(pattern, request.path):
            return True
    return False
