# Starting

To start, clone the project with:

```shell
git clone https://github.com/CosmicDNA/nacl_middleware
```

Then enter the cloned folder and create a new virtualenv:

```shell
cd nacl-middleware
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

# Testing
Run the test suite with the command:

```shell
pytest -s
```

# Testing with SSL

## Certificates Creation

> ![NOTE]
> The following topics consider the project's root folder as the working directory.

### Generate a Client Key and Certificate Signing Request (CSR)
To generate a client key and CSR, run `openssl` command in the terminal:

```shell
# Generate a private key (client.key)
openssl genpkey -algorithm RSA -out client.key

# Create a certificate signing request (client.csr)
openssl req -new -key client.key -out client.csr
```

### Generate Self-Signed SSL Certificates
For the server, generate the self signed certificates with:

```shell
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout selfsigned.key -out selfsigned.crt
```

You will be prompted to answer some questions during the certificate generation process. Make sure to set the Common Name (CN) to your server’s domain name (e.g., localhost).

### Sign the CSR using your CA's private key
Lastly, sign the CSR using the server's CA's private key

```shell
openssl x509 -req -in client.csr -CA selfsigned.crt -CAkey selfsigned.key -CAcreateserial -out client.crt -days 365
```

## Configuration
Once a pytest run has generated a `config.json` file, you can edit it and add:

```json
{
  "ssl": {
    "cert_path": "selfsigned.crt",
    "key_path": "selfsigned.key"
  }
}
```

You should now be able to perform the test with SSL enabled.

```shell
pytest -s
```

> ![TIP]
> Removing the `ssl` section from config.json deactivates SSL within both client and server modules.