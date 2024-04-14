from asyncio import get_event_loop

from tests.client import Client
from tests.server import EngineServerManager, ServerConfig, ServerStatus, log

server_config = ServerConfig("./config.json")
esm = EngineServerManager()


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
        data = await client.sendMessage({"messageOne": "testOne"})
        assert data == f"ws{client.protocol()}://"
        await client.connectToWebsocket({"messageTwo": "testTwo"})
        await client.sendWebSocketMessage({"name": "Georgia"})
        await client.disconnectWebsocket()
        esm.stop()


async def server_loop_handler() -> None:
    """
    Handles the server loop by adding a status change listener, starting the event service manager,
    and joining the event service manager thread. Finally, it logs a message indicating that the
    main thread is being joined.
    """
    esm.add_listener(status_change_listener)
    esm.start()
    esm.join()
    log.info("Joining main thread...")


def test_middleware() -> None:
    """
    Test the middleware function.

    This function runs the server loop handler in an event loop and logs a message when it completes.

    Returns:
        None
    """
    loop = get_event_loop()
    loop.run_until_complete(server_loop_handler())
    log.info("Joined!")
