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
    return r.json()


def download_file(url: str, dest_folder: str):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)
    token = get_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    r = requests.get(url, stream=True, headers=headers)
    if r.ok:
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
    else:  # HTTP status code 4XX/5XX
        print("Download failed: status code {}\n{}".format(r.status_code, r.text))


if __name__ == '__main__':
    download_file('http://120.48.150.243/fa/api/v0/download/jobs/job-91/output/output/fluent.msh',
                  r'C:\\workspaces\\data\\prepare')
