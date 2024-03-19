from aiohttp import ClientSession
from aiohttp.typedefs import LooseHeaders
from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import HexEncoder, Base64Encoder
from typing import Mapping

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

    def encrypt(self, message: str) -> str:
        return self.box.encrypt(message.encode(), encoder=Base64Encoder).decode()

    def getParams(self, message: str) -> Mapping[str, str]:
        return {
            'publicKey': self.public_key.encode(encoder=HexEncoder).decode(),
            'encryptedMessage': self.encrypt(message)
        }

    async def sendMessage(self, message: str) -> any:
        url = f'http://{self.host}:{self.port}/protocol'

        async with ClientSession() as session:
            return await fetch(session, url, params=self.getParams(message))

    async def sendWebSocketMessage(self, message: str) -> None:
        url = f'ws://{self.host}:{self.port}/websocket'

        origin = f'http://{self.host}'
        headers: LooseHeaders = {
            'Origin': origin
        }

        async with self.session.ws_connect(url, params=self.getParams(message), headers=headers) as socket:
            await socket.send_str(message)
            await self.session.close()