from json import dumps, loads
from typing import Union

from nacl.encoding import Base64Encoder, HexEncoder
from nacl.public import Box, PrivateKey, PublicKey


class Nacl:
    """
    A class that provides utility functions for encoding and decoding Nacl keys.
    """

    private_key: PrivateKey

    def __init__(self, private_key: PrivateKey, encoder=HexEncoder) -> None:
        self.private_key = private_key
        self.encoder = encoder

    def _decode(self, parameter: Union[PrivateKey, PublicKey]) -> str:
        """
        Decode the given Nacl key parameter using the specified encoder.

        Args:
            parameter (Union[PrivateKey, PublicKey]): The Nacl key parameter to decode.

        Returns:
            str: The decoded Nacl key as a string.
        """
        return parameter.encode(encoder=self.encoder).decode()

    def decodedPrivateKey(self) -> str:
        """
        Decode the private key using the specified encoder.

        Returns:
            str: The decoded private key as a string.
        """
        return self._decode(self.private_key)

    def decodedPublicKey(self) -> str:
        """
        Decode the public key of the private key using the specified encoder.

        Returns:
            str: The decoded public key as a string.
        """
        return self._decode(self.private_key.public_key)


def custom_loads(obj) -> any:
    """
    Custom loads function that deserializes a JSON string into a Python object.

    Args:
        obj (str): The JSON string to be deserialized.

    Returns:
        any: The deserialized Python object.

    """
    if isinstance(obj, str):
        obj = f'"{obj}"'
    return loads(obj)


class MailBox:
    _private_key: PrivateKey
    _box: Box

    def __init__(self, private_key: PrivateKey, hex_public_key: str) -> None:
        """
        Initializes the MailBox with the provided private key and hex-encoded public key.

        Parameters:
        private_key (PrivateKey): The private key used for encryption and decryption.
        hex_public_key (str): The hex-encoded public key.

        Returns:
        None
        """
        self._private_key = private_key
        self._box = Box(self._private_key, PublicKey(hex_public_key, HexEncoder))

    def unbox(self, encrypted_message: str) -> any:
        """
        Decrypts the encrypted message using the private key and returns the decrypted message.

        Parameters:
        encrypted_message (str): The encrypted message to be decrypted.

        Returns:
        any: The decrypted message.
        """
        decrypted_message = self._box.decrypt(encrypted_message, encoder=Base64Encoder)
        return custom_loads(decrypted_message)

    def box(self, message: any) -> str:
        """
        Encrypts the given message using the NaCl encryption algorithm.

        Parameters:
        message (any): The message to be encrypted.

        Returns:
        str: The encrypted message as a string.
        """
        return self._box.encrypt(dumps(message).encode(), encoder=Base64Encoder).decode()
