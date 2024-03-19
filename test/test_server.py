from asyncio import get_event_loop
from json import dumps
from pynacl_middleware_canonical_example.manager import EngineServerManager, ServerStatus
from pynacl_middleware_canonical_example.config import ServerConfig
from test.client import Client

server_config = ServerConfig('./config.json')
esm = EngineServerManager()

async def status_change_listener(status):
    if status == ServerStatus.Running:
        client = Client(server_config.host, server_config.port, server_config.private_key.public_key)
        data = await client.sendMessage(dumps({'message': 'test'}))
        assert data == 'ws://'
        await client.sendWebSocketMessage(dumps({'message': 'test'}))
        esm.stop()

async def server_loop_handler():
    esm.add_listener(status_change_listener)
    esm.start()
    esm.join()
    esm.stop_listening()

def test_middleware():
    loop = get_event_loop()
    loop.run_until_complete(
        server_loop_handler()
    )
