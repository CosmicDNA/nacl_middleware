from typing import Tuple
from multidict import MultiMapping
from json import loads
from sorcery import dict_of
from operator import itemgetter
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

def custom_loads(obj) -> any:
    if isinstance(obj, str):
        obj = f'"{obj}"'
    return loads(obj)

def nacl_middleware(private_key: PrivateKey,
                    exclude_routes: Tuple = tuple(),
                    exclude_methods: Tuple = tuple(),
                    log = getLogger()
                   ) -> Middleware:

    def nacl_decryptor(inputObject: MultiMapping[str]) -> any:
        public_key, encrypted_message = itemgetter('publicKey', 'encryptedMessage')(inputObject)
        log.debug(f'Decoding messager\'s public key hex...')
        messager_public_key = PublicKey(public_key, HexEncoder)
        log.debug(f'Messager\'s public key {messager_public_key} decoded!')

        log.debug(f'Creating Box...')
        my_mail_box = Box(private_key, messager_public_key)
        log.debug(f'Box {my_mail_box} created!')

        log.debug(f'Decrypting message...')
        decrypted_message = my_mail_box.decrypt(encrypted_message, encoder=Base64Encoder)
        message = custom_loads(decrypted_message)
        log.debug(f'Message {message} decrypted!')
        return message

    @middleware
    async def returned_middleware(request: Request, handler: Handler) -> StreamResponse:
        if (not (is_exclude(request, exclude_routes) or
                request.method in exclude_methods)):

            try:
                log.debug(f'Retrieving publicKey and encryptedMessage from message...')
                publicKey, encryptedMessage = itemgetter('publicKey', 'encryptedMessage')(request.query)
                log.debug(f'PublicKey {publicKey} and EncryptedMessage {encryptedMessage} retrieved!')

                decrypted_message = nacl_decryptor(dict_of(publicKey, encryptedMessage))

                request['decryptor'] = nacl_decryptor
                request['decrypted_message'] = decrypted_message
            except Exception:
                the_exc_info = exc_info()
                exception_str = ''.join(format_exception(*the_exc_info))
                log.debug(f'Exception body: {exception_str}')
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
