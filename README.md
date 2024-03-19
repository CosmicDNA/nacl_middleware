# Starting

To start, clone the project with:

```shell
git clone https://github.com/CosmicDNA/pynacl-middleware-canonical-example
```

Then enter the cloned folder and create a new virtualenv:

```shell
cd pynacl-middleware-canonical-example
python3 -m  venv .venv
```

Activate the just created virtualenv with:

```shell
. .venv/bin/activate
```

Install the dependencies with the command:


```shell
pip install -e .[test]
```

Run the test suite with the command:

```shell
pytest -s
```