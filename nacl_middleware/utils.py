from re import fullmatch
from aiohttp.web import Request
from typing import Tuple

def is_exclude(request: Request, exclude: Tuple)  -> bool:
    for pattern in exclude:
        if fullmatch(pattern, request.path):
            return True
    return False