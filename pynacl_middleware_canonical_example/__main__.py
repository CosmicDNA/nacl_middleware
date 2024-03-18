from pynacl_middleware_canonical_example.manager import EngineServerManager
from asyncio import get_event_loop

async def main():
  esm = EngineServerManager()
  esm.start()
  esm.join()

if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(main())