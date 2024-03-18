from pynacl_middleware_canonical_example.manager import EngineServerManager

def main():
  esm = EngineServerManager()
  esm.start()
  esm.join()

if __name__ == "__main__":
    main()