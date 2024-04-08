from ssl import Purpose, SSLContext, create_default_context

from aiohttp import ClientError, ClientSession, TCPConnector
from aiohttp.typedefs import LooseHeaders
from multidict import MultiMapping
from nacl.encoding import HexEncoder
from nacl.public import PrivateKey

from nacl_middleware import MailBox


class Client:
    private_key: PrivateKey
    session: ClientSession
    mail_box: MailBox
    ssl_context: SSLContext

    def __init__(
        self, host: str, port: str, server_hex_public_key: str, isTLS: bool
    ) -> None:
        self.private_key = PrivateKey.generate()
        self.hex_public_key = self.private_key.public_key.encode(
            encoder=HexEncoder
        ).decode()
        self.isTLS = isTLS
        self.host = host
        self.port = port
        if self.isTLS:
            self.ssl_context = create_default_context(
                Purpose.SERVER_AUTH, cafile="selfsigned.crt"
            )
            self.ssl_context.load_cert_chain(certfile="client.crt", keyfile="client.key")
        else:
            self.ssl_context = None
        connector = TCPConnector(ssl=self.ssl_context)
        origin = f"http{self.protocol()}://{self.host}"
        self.headers: LooseHeaders = {"Origin": origin}
        self.session = ClientSession(connector=connector, headers=self.headers)
        self.mail_box = MailBox(self.private_key, server_hex_public_key)

    def _getEncryptionParams(self, message) -> MultiMapping[str]:
        return {
            "publicKey": self.hex_public_key,
            "encryptedMessage": self.encrypt(message),
        }

    def protocol(self) -> str:
        return "s" if self.isTLS else ""

    def encrypt(self, message) -> str:
        return self.mail_box.box(message)

    def decrypt(self, encrypted_message) -> any:
        return self.mail_box.unbox(encrypted_message)

    async def fetch(self, url, params=None) -> any:
        try:
            async with self.session.get(url, params=params) as response:
                return await response.json()
        except ClientError as e:
            # Handle connection errors here
            print(f"Error fetching data: {e}")
            return None

    async def sendMessage(self, message) -> any:
        url = f"http{self.protocol()}://{self.host}:{self.port}/protocol"

        encrypted_res = await self.fetch(url, params=self._getEncryptionParams(message))
        return self.decrypt(encrypted_res)

    async def sendWebSocketMessage(self, message) -> None:
        await self.socket.send_str(self.encrypt(message))

    async def connectToWebsocket(self, message) -> None:
        url = f"ws{self.protocol()}://{self.host}:{self.port}/websocket"

        self.socket = await self.session.ws_connect(
            url,
            params=self._getEncryptionParams(message),
            headers=self.headers,
            ssl=self.ssl_context,
        )

    async def disconnectWebsocket(self) -> None:
        await self.session.close()
