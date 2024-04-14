from aiohttp.web import AppKey


def create_app_key(key_string):
    """
    Create an application key.

    Args:
        key_string (str): The key string to create the app key from.

    Returns:
        dict: A dictionary containing the app key.

    """
    return {key_string: AppKey(key_string, str)}


def create_app_keys_from_list(key_strings):
    """
    Create a dictionary of app keys from a list of key strings.

    Args:
        key_strings (list): A list of key strings.

    Returns:
        dict: A dictionary of app keys.

    """
    app_keys = {}
    for key in key_strings:
        app_keys.update(create_app_key(key))
    return app_keys


keys_to_create = ["websockets"]
app_keys = create_app_keys_from_list(keys_to_create)
