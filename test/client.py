from aiohttp import ClientSession
from aiohttp.typedefs import LooseHeaders
from nacl.public import PrivateKey
from nacl.encoding import HexEncoder
from multidict import MultiMapping
from pynacl_middleware_canonical_example.websocket.nacl_middleware.nacl_utils import MailBox


async def fetch(session: ClientSession, url, params=None) -> any:
    async with session.get(url, params = params) as response:
        return await response.json()

class Client:
    private_key: PrivateKey
    session: ClientSession
    mail_box : MailBox
    def __init__(self, host: str, port: str, server_hex_public_key: str) -> None:
        self.private_key = PrivateKey.generate()
        self.hex_public_key = self.private_key.public_key.encode(encoder=HexEncoder).decode()
        self.host = host
        self.port = port
        self.session = ClientSession()
        self.mail_box = MailBox(self.private_key, server_hex_public_key)

    def _getEncryptionParams(self, message) -> MultiMapping[str]:
        return {
            'publicKey': self.hex_public_key,
            'encryptedMessage': self.encrypt(message)
        }

    def encrypt(self, message) -> str:
        return self.mail_box.box(message)

    def decrypt(self, encrypted_message) -> any:
        return self.mail_box.unbox(encrypted_message)

    async def sendMessage(self, message) -> any:
        url = f'http://{self.host}:{self.port}/protocol'

        encrypted_res = await fetch(self.session, url, params=self._getEncryptionParams(message))
        return self.decrypt(encrypted_res)

    async def sendWebSocketMessage(self, message) -> None:
        await self.socket.send_str(self.encrypt(message))

    async def connectToWebsocket(self, message) -> None:
        url = f'ws://{self.host}:{self.port}/websocket'

        origin = f'http://{self.host}'
        headers: LooseHeaders = {
            'Origin': origin
        }
        self.socket = await self.session.ws_connect(url, params=self._getEncryptionParams(message), headers=headers)

    async def disconnectWebsocket(self) -> None:
        await self.session.close()