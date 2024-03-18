from nacl.public import PrivateKey, PublicKey
from nacl.encoding import HexEncoder

from typing import Union

class Nacl:
	private_key: PrivateKey

	def __init__(self, private_key: PrivateKey, encoder = HexEncoder) -> None:
		self.private_key = private_key
		self.encoder = encoder

	def _decode(self, parameter: Union[PrivateKey, PublicKey]) -> str:
		return parameter.encode(encoder=self.encoder).decode()

	def decodedPrivateKey(self) -> str:
		return self._decode(self.private_key)

	def decodedPublicKey(self) -> str:
		return self._decode(self.private_key.public_key)