import requests
from urllib.parse import urlencode


def get(url, params, headers):
    query = urlencode(params)
    encoded_url = f'{url}?{query}'

    return requests.get(encoded_url, headers=headers)


def post(url, data, headers):
    headers['Referer'] = 'https://expenses.bewakes.com'
    return requests.post(url, data, headers=headers)
