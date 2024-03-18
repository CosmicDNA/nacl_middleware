import asyncio
from pynacl_middleware_canonical_example.manager import EngineServerManager, ServerStatus

esm = EngineServerManager()

async def call_me_back(status):
    if status == ServerStatus.Running:
        assert True
        await esm.stop()

async def run_me():
    esm.add_listener(call_me_back)
    esm.start()
    esm.join()

def test_answer():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_me())
