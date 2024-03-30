from typing import Tuple
from operator import itemgetter
from aiohttp import WSCloseCode
from nacl.public import PrivateKey
from inspect import signature
from aiohttp.web import StreamResponse, Response, WebSocketResponse, Request, HTTPUnauthorized, middleware
from traceback import format_exception
from sys import exc_info
from aiohttp.typedefs import (
    Middleware,
    Handler
)
from logging import getLogger
from .utils import is_exclude
from .nacl_utils import MailBox

mailBoxes = {}

def nacl_middleware(private_key: PrivateKey,
                    exclude_routes: Tuple = tuple(),
                    exclude_methods: Tuple = tuple(),
                    log = getLogger()
                   ) -> Middleware:

    def nacl_decryptor(public_key, encrypted_message) -> Tuple[any, MailBox]:
        if public_key in mailBoxes:
            my_mail_box = mailBoxes[public_key]
        else:
            my_mail_box = MailBox(private_key, public_key)
            mailBoxes[public_key] = my_mail_box

        log.debug(f'Decrypting message...')
        message = my_mail_box.unbox(encrypted_message)
        log.debug(f'Message {message} decrypted!')
        return message, my_mail_box

    @middleware
    async def returned_middleware(request: Request, handler: Handler) -> StreamResponse:
        if (not (is_exclude(request, exclude_routes) or
                request.method in exclude_methods)):

            try:
                log.debug(f'Retrieving publicKey and encryptedMessage from message...')
                publicKey, encryptedMessage = itemgetter('publicKey', 'encryptedMessage')(request.query)
                log.debug(f'PublicKey {publicKey} and EncryptedMessage {encryptedMessage} retrieved!')

                decrypted_message, my_mail_box = nacl_decryptor(publicKey, encryptedMessage)

                request['mail_box'] = my_mail_box
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
                        message=''.join(format_exception(exception))
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
