import requests


def get_token():
    base_url = "http://127.0.0.1:8000/login"
    r = requests.post(base_url)
    token = r.json()['token']
    return token
