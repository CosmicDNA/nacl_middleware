from ssl import Purpose, SSLContext, create_default_context

from aiohttp import ClientError, ClientSession, TCPConnector
from aiohttp.typedefs import LooseHeaders
from multidict import MultiMapping
from nacl.public import PrivateKey

from nacl_middleware import MailBox, Nacl


class Client:
    """
    Represents a client that interacts with a server using encryption.

    Args:
        host (str): The hostname or IP address of the server.
        port (str): The port number of the server.
        server_hex_public_key (str): The server's public key in hexadecimal format.
        isTLS (bool): Indicates whether to use TLS encryption.

    Attributes:
        private_key (PrivateKey): The client's private key.
        session (ClientSession): The client's HTTP session.
        mail_box (MailBox): The client's mailbox for encryption.
        ssl_context (SSLContext): The SSL context for TLS encryption.

    """

    private_key: PrivateKey
    session: ClientSession
    mail_box: MailBox
    ssl_context: SSLContext

    def __init__(
        self, host: str, port: str, server_hex_public_key: str, isTLS: bool
    ) -> None:
        """
        Initializes a new instance of the Client class.

        Args:
            host (str): The hostname or IP address of the server.
            port (str): The port number of the server.
            server_hex_public_key (str): The server's public key in hexadecimal format.
            isTLS (bool): Indicates whether to use TLS encryption.

        """
        self.private_key = PrivateKey.generate()
        self.hex_public_key = Nacl(self.private_key).decoded_public_key()
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

    def _get_encryption_params(self, message) -> MultiMapping[str]:
        """
        Returns the encryption parameters for the given message.

        Args:
            message: The message to be encrypted.

        Returns:
            A dictionary containing the encryption parameters:
            - "publicKey": The hexadecimal representation of the public key.
            - "encryptedMessage": The encrypted message.

        """
        return {
            "publicKey": self.hex_public_key,
            "encryptedMessage": self.encrypt(message),
        }

    def protocol(self) -> str:
        """
        Returns the protocol used by the client.

        If the client is using TLS, the protocol is "s".
        If the client is not using TLS, the protocol is an empty string.

        Returns:
            str: The protocol used by the client.
        """
        return "s" if self.isTLS else ""

    def encrypt(self, message) -> str:
        """
        Encrypts the given message using the mail_box's box method.

        Args:
            message (str): The message to be encrypted.

        Returns:
            str: The encrypted message.
        """
        return self.mail_box.box(message)

    def decrypt(self, encrypted_message) -> any:
        """
        Decrypts an encrypted message using the mail_box's unbox method.

        Args:
            encrypted_message: The encrypted message to be decrypted.

        Returns:
            The decrypted message.

        """
        return self.mail_box.unbox(encrypted_message)

    async def fetch(self, url, params=None) -> any:
        """
        Fetches data from the specified URL.

        Args:
            url (str): The URL to fetch data from.
            params (dict, optional): The query parameters to include in the request. Defaults to None.

        Returns:
            any: The response from the server, or None if an error occurred.

        """
        try:
            async with self.session.get(url, params=params) as response:
                return await response.text()
        except ClientError as e:
            # Handle connection errors here
            print(f"Error fetching data: {e}")
            return None

    async def send_message(self, message) -> any:
        """
        Sends a message to the server and returns the decrypted response.

        Args:
            message: The message to be sent to the server.

        Returns:
            The decrypted response from the server.

        Raises:
            Any exceptions raised during the execution of the method.
        """
        url = f"http{self.protocol()}://{self.host}:{self.port}/protocol"

        encrypted_res = await self.fetch(
            url, params=self._get_encryption_params(message)
        )
        return self.decrypt(encrypted_res)

    async def send_websocket_message(self, message) -> None:
        """
        Sends a WebSocket message after encrypting it.

        Args:
            message: The message to be sent.

        Returns:
            None
        """
        await self.socket.send_str(self.encrypt(message))

    async def connect_to_websocket(self, message) -> None:
        """
        Connects to the websocket server.

        Args:
            message: The message to be sent to the server.

        Returns:
            None
        """
        url = f"ws{self.protocol()}://{self.host}:{self.port}/websocket"

        self.socket = await self.session.ws_connect(
            url,
            params=self._get_encryption_params(message),
            headers=self.headers,
            ssl=self.ssl_context,
        )

    async def disconnect_websocket(self) -> None:
        """
        Disconnects the websocket connection.

        This method closes the session, terminating the websocket connection.
        """
        await self.session.close()
