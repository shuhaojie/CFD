import os
import requests
import base64


def get_token():
    base_url = "http://120.48.150.243/api/v1/auth/signin"
    password = 'fs@2022!'
    encoded_password = str(base64.b64encode(password.encode('utf-8')), 'utf-8')
    params = {'usernameOrEmail': 'admin', 'encodedPassword': encoded_password}
    r = requests.post(base_url, json=params)
    token = r.json()['accessToken']
    return token


def upload_file(task_id):
    base_url = "http://120.48.150.243/fa/api/v0/upload/"
    abs_path = os.path.join(r'C:\workspaces\data\prepare', task_id + ".zip")

    token = get_token()
    files = {
        'file': open(abs_path, 'rb'),
        'key': (None, f'dir1/{task_id}.zip'),
        'storage_id': (None, '-1'),
    }
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.post(
        base_url,
        files=files,
        headers=headers
    )
    print(r.json())


if __name__ == '__main__':
    upload_file('aaa')
