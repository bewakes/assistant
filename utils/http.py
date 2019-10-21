import requests
from urllib.parse import urlencode


def get(url, params, headers):
    query = urlencode(params)
    encoded_url = f'{url}?{query}'

    return requests.get(encoded_url, headers=headers)
