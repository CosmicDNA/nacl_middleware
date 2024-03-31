from aiohttp import ClientSession, TCPConnector, ClientError, log
from aiohttp.typedefs import LooseHeaders
from nacl.public import PrivateKey
from nacl.encoding import HexEncoder
from multidict import MultiMapping
from pynacl_middleware_canonical_example.websocket.nacl_middleware.nacl_utils import MailBox
from ssl import create_default_context, SSLContext, Purpose
from logging import DEBUG

log.client_logger.setLevel(DEBUG)

class Client:
    private_key: PrivateKey
    session: ClientSession
    mail_box : MailBox
    ssl_context: SSLContext

    def __init__(self, host: str, port: str, server_hex_public_key: str) -> None:
        self.private_key = PrivateKey.generate()
        self.hex_public_key = self.private_key.public_key.encode(encoder=HexEncoder).decode()
        self.isTLS = True
        self.host = host
        self.port = port
        if self.isTLS:
            self.ssl_context = create_default_context(Purpose.SERVER_AUTH, cafile='selfsigned.crt')
            self.ssl_context.load_cert_chain(certfile='client.crt', keyfile='client.key')
        else:
            self.ssl_context = None
        connector = TCPConnector(ssl=self.ssl_context)
        self.session = ClientSession(connector = connector)
        self.mail_box = MailBox(self.private_key, server_hex_public_key)

    def _getEncryptionParams(self, message) -> MultiMapping[str]:
        return {
            'publicKey': self.hex_public_key,
            'encryptedMessage': self.encrypt(message)
        }

    def protocol(self) -> str:
        return 's' if self.isTLS else ''

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
        url = f'http{self.protocol()}://{self.host}:{self.port}/protocol'

        encrypted_res = await self.fetch(url, params=self._getEncryptionParams(message))
        return self.decrypt(encrypted_res)

    async def sendWebSocketMessage(self, message) -> None:
        await self.socket.send_str(self.encrypt(message))

    async def connectToWebsocket(self, message) -> None:
        url = f'ws{self.protocol()}://{self.host}:{self.port}/websocket'

        origin = f'http{self.protocol()}://{self.host}'
        headers: LooseHeaders = {
            'Origin': origin
        }
        self.socket = await self.session.ws_connect(
            url,
            params=self._getEncryptionParams(message),
            headers=headers,
            ssl=self.ssl_context
        )

    async def disconnectWebsocket(self) -> None:
        await self.session.close()