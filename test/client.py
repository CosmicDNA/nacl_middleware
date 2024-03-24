from aiohttp import ClientSession
from aiohttp.typedefs import LooseHeaders
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import HexEncoder, Base64Encoder
from multidict import MultiMapping
from json import dumps


async def fetch(session: ClientSession, url, params=None) -> any:
    async with session.get(url, params = params) as response:
        return await response.json()

class Client:
    def __init__(self, host: str, port: str, server_public_key: PublicKey) -> None:
        self.private_key = PrivateKey.generate()
        self.public_key = self.private_key.public_key
        self.host = host
        self.port = port
        self.session = ClientSession()
        self.box = Box(self.private_key, server_public_key)

    def encrypt(self, message) -> str:
        return self.box.encrypt(dumps(message).encode(), encoder=Base64Encoder).decode()

    def getEncryptionParams(self, message) -> MultiMapping[str]:
        return {
            'publicKey': self.public_key.encode(encoder=HexEncoder).decode(),
            'encryptedMessage': self.encrypt(message)
        }

    async def sendMessage(self, message) -> any:
        url = f'http://{self.host}:{self.port}/protocol'

        return await fetch(self.session, url, params=self.getEncryptionParams(message))

    async def sendWebSocketMessage(self, message) -> None:
        await self.socket.send_str(dumps(message))

    async def connectToWebsocket(self, message) -> None:
        url = f'ws://{self.host}:{self.port}/websocket'

        origin = f'http://{self.host}'
        headers: LooseHeaders = {
            'Origin': origin
        }
        self.socket = await self.session.ws_connect(url, params=self.getEncryptionParams(message), headers=headers)

    async def disconnectWebsocket(self) -> None:
        await self.session.close()