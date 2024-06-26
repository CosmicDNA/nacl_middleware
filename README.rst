The Nacl Middleware
===================

.. image:: https://readthedocs.org/projects/nacl-middleware/badge/?version=latest
    :target: https://nacl-middleware.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://github.com/CosmicDNA/nacl_middleware/actions/workflows/pytest.yml/badge.svg
    :target: https://github.com/CosmicDNA/nacl_middleware/actions/workflows/pytest.yml
    :alt: Python Tests

The Nacl Middleware is an aiohttp compatible middleware that provides NaCl encryption for authentication in both HTTP requests and websockets. It allows you to securely handle encrypted messages and sender’s public keys from query parameters. Upon successful decoding, it forwards the request to the appropriate handler, whether it’s a websocket or an HTTP request.


Usage
-----

The middleware uses assymetric keys encryption and it is installed on the server. The middleware assumes that the client will be sending the following GET parameters:


+-------------------+----------------------------------------------------+
| parameter         | Description                                        |
+===================+====================================================+
| publicKey         | The client's public key                            |
+-------------------+----------------------------------------------------+
| encryptedMessage  | The encrypted message by the client for the server |
+-------------------+----------------------------------------------------+


Server Example
^^^^^^^^^^^^^^

.. admonition:: Example
   :class: toggle

    Here is one usage example on the server side:

    .. code-block:: python

        from aiohttp.web import Application, Response, run_app
        from nacl_middleware import nacl_middleware, Nacl, MailBox

        pynacl = Nacl()
        public_key_hex = pynacl.decoded_public_key()
        print(public_key_hex)

        app = Application(middlewares=[
            nacl_middleware(pynacl.private_key)
        ])

        async def thanks_handler(request):
            decrypted_message = request['decrypted_message']
            mail_box: MailBox = request['mail_box']
            if decrypted_message == 'Thank you!':
                text = 'You are welcome!'
            text = "Pardon me?"
            return Response(text = mail_box.box(text))

        app.router.add_get('/handle_thanks', thanks_handler)

        run_app(app)


Client Example
^^^^^^^^^^^^^^

.. admonition:: Example
   :class: toggle

    And the matching usage example on the client side:

    .. code-block:: python

        from aiohttp import ClientSession
        from asyncio import run
        from nacl_middleware import MailBox, Nacl

        pynacl = Nacl()
        server_hex_public_key = "cbe3b3cf345b24bd050db13bb5f1165f47f36f7151bbba9b27bdef0922674f4d"

        async def main():
            mail_box = MailBox(pynacl.private_key, server_hex_public_key)

            def get_params(message):
                return {
                    "publicKey": pynacl.decoded_public_key(),
                    "encryptedMessage": mail_box.box(message)
                }

            async with ClientSession() as session:
                async with session.get('http://localhost:8080/handle_thanks', params=get_params('Thank you!')) as response:
                    encryted_reply = await response.text()
                    reply = mail_box.unbox(encryted_reply)
                    print("Reply:", reply)

        run(main())

    .. warning::

        Make sure the server's public key in this client code example is correctly set to the public key print by the server's example code in the console.

    .. tip::

        Add a path to get the server's public key to the middleware's route exclusion to allow the server's public key to be obtained by sending a GET request to the server's public key endpoint with, for example:

        .. code-block:: python

            from aiohttp.web import Application, Response, run_app
            from nacl_middleware import nacl_middleware, Nacl, MailBox

            pynacl = Nacl()
            public_key_hex = pynacl.decoded_public_key()
            print(public_key_hex)

            app = Application(middlewares=[
                nacl_middleware(pynacl.private_key)
            ])

            async def thanks_handler(request):
                decrypted_message = request['decrypted_message']
                mail_box: MailBox = request['mail_box']
                if decrypted_message == 'Thank you!':
                    text = 'You are welcome!'
                text = "Pardon me?"
                return Response(text = mail_box.box(text))

            app.router.add_get('/handle_thanks', thanks_handler)

            async def get_public_key(request):
                return Response(text = public_key_hex)

            app.router.add_get("/get_public_key", get_public_key)

            run_app(app)


.. important::

    For an example of usage with websockets, please refer to the client and server modules within tests folder.

Development
===========

Project Configuration
---------------------

To start, clone the project with:

.. code-block:: shell

    git clone https://github.com/CosmicDNA/nacl_middleware

Then enter the cloned folder and create a new virtualenv:

.. code-block:: shell

    cd nacl-middleware
    python3 -m  venv .venv

Activate the just created virtualenv with:

.. code-block:: shell

    . .venv/bin/activate

Install the dependencies with the command:

.. code-block:: shell

    pip install -e .[test]

Testing
-------

Run the test suite with the command:

.. code-block:: shell

    pytest -s

Testing with SSL
----------------

Certificates Creation
^^^^^^^^^^^^^^^^^^^^^

.. note::

    The following topics consider the project's root folder as the working directory.


Generate a Client Key and Certificate Signing Request (CSR)
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

To generate a client key and CSR, run ``openssl`` command in the terminal:

.. code-block:: shell

    # Generate a private key (client.key)
    openssl genpkey -algorithm RSA -out client.key

    # Create a certificate signing request (client.csr)
    openssl req -new -key client.key -out client.csr

Generate Self-Signed SSL Certificates
"""""""""""""""""""""""""""""""""""""

For the server, generate the self signed certificates with:

.. code-block:: shell

    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout selfsigned.key -out selfsigned.crt

You will be prompted to answer some questions during the certificate generation process. Make sure to set the Common Name (CN) to your server’s domain name (e.g., localhost).

Sign the CSR using your CA's private key
""""""""""""""""""""""""""""""""""""""""

Lastly, sign the CSR using the server's CA's private key

.. code-block:: shell

    openssl x509 -req -in client.csr -CA selfsigned.crt -CAkey selfsigned.key -CAcreateserial -out client.crt -days 365

Configuration
^^^^^^^^^^^^^

Once a pytest run has generated a ``config.json`` file, you can edit it and add:

.. code-block:: json

    {
        "ssl": {
            "cert_path": "selfsigned.crt",
            "key_path": "selfsigned.key"
        }
    }

You should now be able to perform the test with SSL enabled.

.. code-block:: shell

    pytest -s

.. tip::

    Removing the ``ssl`` section from config.json deactivates SSL within both client and server modules.
