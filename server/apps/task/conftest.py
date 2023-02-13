import json
import requests
import subprocess


def get_new_celery_worker():
    bash_command = "celery -A worker inspect active -j"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output_string = output.decode("utf-8")[:-17]
    output_json = json.loads(output_string)
    number_of_celery_worker = 0
    if len(list(output_json.values())[0]) == 0:  # 后台celery记录为空
        pass
    else:
        for value in list(output_json.values())[0]:
            for v in value.values():
                if v == 'run_task':
                    number_of_celery_worker += 1
    return int(number_of_celery_worker / 2), output_json


def get_user_info(order_id):
    base_url = 'http://172.16.1.37:31226'
    request_url = f'{base_url}/api/v1/station/cfd_get_user_info'
    r = requests.get(request_url, params={'order_id': order_id})
    print(r)
    return r.json()


res = get_user_info('2022092900013')
email = res['data']['email']
print(email)
