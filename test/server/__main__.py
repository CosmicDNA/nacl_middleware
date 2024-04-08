from manager import EngineServerManager
from asyncio import get_event_loop

async def main() -> None:
    esm = EngineServerManager()
    esm.start()
    esm.join()

if __name__ == "__main__":
    loop = get_event_loop()
    loop.run_until_complete(main())