from typing import Tuple

from aiohttp import WSCloseCode
from nacl.public import PrivateKey, PublicKey, Box
from inspect import signature
from aiohttp.web import StreamResponse, Response, WebSocketResponse, Request, HTTPUnauthorized, middleware
from nacl.encoding import HexEncoder, Base64Encoder
from traceback import format_exception
from sys import exc_info
from aiohttp.typedefs import (
    Middleware,
    Handler
)
from logging import getLogger
from pynacl_middleware_canonical_example.websocket.nacl_middleware.utils import is_exclude

def nacl_middleware(private_key: PrivateKey,
                    exclude_routes: Tuple = tuple(),
                    exclude_methods: Tuple = tuple(),
                    log = getLogger()
                   ) -> Middleware:

    @middleware
    async def returned_middleware(request: Request, handler: Handler) -> StreamResponse:
        if (not (is_exclude(request, exclude_routes) or
                request.method in exclude_methods)):

            try:
                log.debug(f'Retrieving publicKey from message...')
                messager_public_key_hex = request.query.get('publicKey')
                log.debug(f'PublicKey {messager_public_key_hex} retrieved!')

                log.debug(f'Decoding messager\'s public key hex...')
                messager_public_key = PublicKey(messager_public_key_hex, HexEncoder)
                log.debug(f'Messager\'s public key {messager_public_key} decoded!')

                log.debug(f'Retrieving encryptedMessage from message...')
                incoming_base64_encrypted_message = request.query.get('encryptedMessage')
                log.debug(f'EncryptedMessage {incoming_base64_encrypted_message} retrieved!')

                log.debug(f'Creating Box...')
                my_mail_box = Box(private_key, messager_public_key)
                log.debug(f'Box {my_mail_box} created!')

                log.debug(f'Decrypting message...')
                decrypted_message = my_mail_box.decrypt(incoming_base64_encrypted_message, encoder=Base64Encoder)
                log.debug(f'Message {decrypted_message} decrypted!')

                request['decrypted_message'] = decrypted_message
            except Exception:
                the_exc_info = exc_info()
                exception_str = ''.join(format_exception(*the_exc_info))
                exception = HTTPUnauthorized(reason='Failed to retrieve a valid message!', body=exception_str)

                # Inspect the handler's signature
                return_annotation = signature(handler).return_annotation
                if return_annotation == WebSocketResponse:
                    log.debug(f'WebSocketResponse hook.')
                    log.debug(f'Exception is {exception_str}')
                    socket = WebSocketResponse()
                    await socket.prepare(request)
                    await socket.close(
                        code=WSCloseCode.PROTOCOL_ERROR,
                        message=exception.reason,
                        body=exception.body
                    )
                    return socket
                elif return_annotation == Response:
                    log.debug(f'Response hook.')
                    log.debug(f'headers: {exception.headers}')
                    log.debug(f'status: {exception.status}')
                    log.debug(f'reason: {exception.reason}')
                    log.debug(f'body: {exception.body}')
                    return Response(
                        headers=exception.headers,
                        status=exception.status,
                        reason=exception.reason,
                        body=exception.body
                    )

        return await handler(request)

    return returned_middleware
