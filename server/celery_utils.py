import json
import subprocess
from worker import celery as celery_app


def get_celery_worker():
    bash_command = "celery -A worker inspect active -j"
    process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output_string = output.decode("utf-8")
    output_json = json.loads(output_string)
    number_of_celery_worker = 0
    if len(list(output_json.values())[0]) == 0:  # 后台celery记录为空
        pass
    else:
        for value in list(output_json.values())[0]:
            for v in value.values():
                if v == 'run_task':
                    number_of_celery_worker += 1
    return int(number_of_celery_worker / 2)


def get_all_worker():
    i = celery_app.control.inspect()
    print(i.active())


get_all_worker()
