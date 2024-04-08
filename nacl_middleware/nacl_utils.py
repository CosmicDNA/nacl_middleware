from json import dumps, loads
from typing import Union

from nacl.encoding import Base64Encoder, HexEncoder
from nacl.public import Box, PrivateKey, PublicKey


class Nacl:
    private_key: PrivateKey

    def __init__(self, private_key: PrivateKey, encoder=HexEncoder) -> None:
        self.private_key = private_key
        self.encoder = encoder

    def _decode(self, parameter: Union[PrivateKey, PublicKey]) -> str:
        return parameter.encode(encoder=self.encoder).decode()

    def decodedPrivateKey(self) -> str:
        return self._decode(self.private_key)

    def decodedPublicKey(self) -> str:
        return self._decode(self.private_key.public_key)


def custom_loads(obj) -> any:
    if isinstance(obj, str):
        obj = f'"{obj}"'
    return loads(obj)


class MailBox:
    _private_key: PrivateKey
    _box: Box

    def __init__(self, private_key: PrivateKey, hex_public_key: str) -> None:
        self._private_key = private_key
        self._box = Box(self._private_key, PublicKey(hex_public_key, HexEncoder))

    def unbox(self, encrypted_message) -> any:
        decrypted_message = self._box.decrypt(encrypted_message, encoder=Base64Encoder)
        return custom_loads(decrypted_message)

    def box(self, message: any) -> str:
        return self._box.encrypt(dumps(message).encode(), encoder=Base64Encoder).decode()
