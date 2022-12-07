import uuid
import json

task_id = uuid.uuid1()
hardware = 2
new_dict = {
    "task_id": str(task_id),
    "hardware": hardware,
    "username": "demo",
}
with open(r"C:\workspaces\data\archive\config.json", "w") as f:
    json.dump(new_dict, f)
