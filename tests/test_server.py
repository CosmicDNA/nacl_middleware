from asyncio import get_event_loop
from collections.abc import Awaitable

from pytest import mark

from tests.client import Client
from tests.server import EngineServerManager, ServerConfig, ServerStatus, log

server_config = ServerConfig("./config.json")


async def websocket(client: Client):
    """
    Callback function for handling websocket connections.

    Args:
        client (Client): The client object representing the websocket connection.

    Returns:
        None
    """
    await client.connect_to_websocket({"messageTwo": "testTwo"})
    message = {"name": "Georgia"}
    await client.send_websocket_message(message)
    reply = await client.receive_json()
    assert reply == message


async def http(client: Client):
    """
    This function is the callback for HTTP requests.

    Args:
        client (Client): The client making the HTTP request.

    Returns:
        None
    """
    pass


@mark.parametrize("callback", [http, websocket])
def test_server(callback: Awaitable) -> None:
    """
    Test the server functionality.

    Args:
        callback (Awaitable): The callback function to be executed.

    Returns:
        None
    """
    esm = EngineServerManager()

    async def server_loop_handler() -> None:
        """
        Handles the server loop by starting the server, waiting for it to run,
        and then executing the callback function when the server is running.

        Args:
            callback (Awaitable): The callback function to be executed when the server is running.

        Returns:
            None
        """

        async def status_change_listener(status) -> None:
            """
            Listens for status changes and performs actions based on the status.

            Args:
                status: The status of the server.

            Returns:
                None
            """
            if status == ServerStatus.Running:
                client = Client(
                    server_config.host,
                    server_config.port,
                    server_config.public_key,
                    True if server_config.ssl else False,
                )
                data = await client.send_message({"messageOne": "testOne"})
                assert data == f"ws{client.protocol()}://"
                await callback(client)
                await client.disconnect()
                esm.stop()

        esm.add_listener(status_change_listener)
        esm.start()
        esm.join()
        log.info("Joining main thread...")

    loop = get_event_loop()
    loop.run_until_complete(server_loop_handler())
    log.info("Joined!")
